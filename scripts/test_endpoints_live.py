#!/usr/bin/env python3
"""
Live Endpoint Tests - Hit a running AARLP server.

Usage:
    # Start the server first: uvicorn app.main:app --reload
    python scripts/test_endpoints_live.py [--base-url http://localhost:8000]

    # Include E2E: login + create job + wait for JD
    python scripts/test_endpoints_live.py --with-job-create

    # Use existing user (skip register)
    python scripts/test_endpoints_live.py --with-job-create --email user@example.com --password YourPass123

Tests all endpoints against a live server. Requires backend + DB to be running.
"""

import argparse
import sys
import time
from typing import Optional

import httpx

# Valid JobInput for create endpoint
SAMPLE_JOB_INPUT = {
    "role_title": "Senior Backend Engineer",
    "department": "Engineering",
    "company_name": "TechCorp Inc.",
    "company_description": "A leading technology company",
    "key_requirements": ["Python", "FastAPI", "PostgreSQL", "Docker"],
    "nice_to_have": ["Kubernetes", "AWS", "GraphQL"],
    "experience_years": 5,
    "location": "Remote",
    "salary_range": "$150,000 - $200,000",
    "prescreening_questions": [
        "Tell me about your experience with Python (at least 10 chars).",
        "Describe a challenging bug you fixed successfully.",
    ],
}


def wait_for_server(base: str, timeout: float = 60.0) -> bool:
    """Poll until server responds to /health/liveness."""
    start = time.monotonic()
    while (time.monotonic() - start) < timeout:
        try:
            r = httpx.get(f"{base}/health/liveness", timeout=5.0)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(1.0)
    return False


def test_endpoint(
    client: httpx.Client,
    method: str,
    path: str,
    *,
    expect_status: int = 200,
    json: Optional[dict] = None,
    headers: Optional[dict] = None,
) -> tuple[bool, str]:
    """Test a single endpoint."""
    try:
        resp = client.request(method, path, json=json, headers=headers)
        ok = resp.status_code == expect_status
        msg = f"{method} {path} -> {resp.status_code} (expected {expect_status})"
        return ok, msg
    except Exception as e:
        return False, f"{method} {path} -> Error: {e}"


def run_e2e_job_create(
    base: str,
    email: Optional[str] = None,
    password: Optional[str] = None,
    poll_timeout: int = 180,
) -> tuple[int, int]:
    """
    E2E: Register (or use existing user) -> Login -> Create job -> Poll until JD ready.
    Returns (passed, failed) counts.
    """
    passed = 0
    failed = 0
    # Use 90s per request - status/jd endpoints can be slow during Bedrock JD generation
    timeout = 90.0

    with httpx.Client(base_url=base, timeout=timeout) as client:
        auth_headers: Optional[dict] = None

        if email and password:
            # Use existing user - login only
            print("\n  [E2E] Logging in with provided credentials...")
            r = client.post("/auth/login", json={"email": email, "password": password})
            if r.status_code != 200:
                print(f"  FAIL [E2E] Login failed: {r.status_code} - {r.text[:200]}")
                failed += 1
                return passed, failed
            token = r.json()["access_token"]
            auth_headers = {"Authorization": f"Bearer {token}"}
            print("  OK   [E2E] Login successful")
            passed += 1
        else:
            # Register new user, verify, then login
            test_email = f"test-live-{int(time.time())}@example.com"
            test_password = "TestPass123"

            print("\n  [E2E] Registering test user...")
            r = client.post(
                "/auth/register",
                json={"email": test_email, "full_name": "Live Test", "password": test_password},
            )
            if r.status_code not in (200, 201):
                print(f"  FAIL [E2E] Register failed: {r.status_code} - {r.text[:200]}")
                failed += 1
                return passed, failed

            data = r.json()
            otp = data.get("otp")
            if not otp:
                print("  FAIL [E2E] No OTP in register response")
                failed += 1
                return passed, failed

            print("  OK   [E2E] Registered, verifying OTP...")
            r = client.post("/auth/verify-otp", json={"email": test_email, "otp": otp})
            if r.status_code != 200:
                print(f"  FAIL [E2E] Verify OTP failed: {r.status_code}")
                failed += 1
                return passed, failed

            print("  OK   [E2E] Verified, logging in...")
            r = client.post("/auth/login", json={"email": test_email, "password": test_password})
            if r.status_code != 200:
                print(f"  FAIL [E2E] Login failed: {r.status_code}")
                failed += 1
                return passed, failed

            token = r.json()["access_token"]
            auth_headers = {"Authorization": f"Bearer {token}"}
            passed += 3
            print("  OK   [E2E] Login successful")

        # Create job
        print("  [E2E] Creating job...")
        r = client.post("/jobs/create", json=SAMPLE_JOB_INPUT, headers=auth_headers or {})
        if r.status_code != 200:
            print(f"  FAIL [E2E] Create job failed: {r.status_code} - {r.text[:300]}")
            failed += 1
            return passed, failed

        data = r.json()
        job_id = data.get("job_id")
        if not job_id:
            print("  FAIL [E2E] No job_id in create response")
            failed += 1
            return passed, failed

        print(f"  OK   [E2E] Job created: {job_id}")
        passed += 1

        # Poll for JD
        print(f"  [E2E] Polling for JD (timeout {poll_timeout}s, check every 5s)...")
        start = time.monotonic()
        jd_ready = False
        last_status = None
        poll_count = 0

        while (time.monotonic() - start) < poll_timeout:
            poll_count += 1
            elapsed = int(time.monotonic() - start)
            try:
                r = client.get(f"/jobs/status/{job_id}", headers=auth_headers or {})
            except httpx.ReadTimeout:
                print(f"  [E2E] Status check #{poll_count} timed out ({elapsed}s) - retrying...")
                time.sleep(2)
                continue

            if r.status_code != 200:
                print(f"  FAIL [E2E] Status check failed: {r.status_code}")
                failed += 1
                return passed, failed

            last_status = r.json()
            if last_status.get("error_message"):
                print(f"  FAIL [E2E] JD generation failed: {last_status['error_message']}")
                failed += 1
                return passed, failed

            if last_status.get("has_generated_jd"):
                jd_ready = True
                break

            if poll_count <= 3 or poll_count % 6 == 0:
                print(f"  [E2E]   {elapsed}s - node={last_status.get('current_node')}, waiting...")
            time.sleep(5)

        if not jd_ready:
            print(f"  FAIL [E2E] JD not ready after {poll_timeout}s (node: {last_status.get('current_node', '?')})")
            failed += 1
            return passed, failed

        print(f"  OK   [E2E] JD generated (node: {last_status.get('current_node')})")
        passed += 1

        # Fetch JD content
        r = client.get(f"/jobs/{job_id}/jd", headers=auth_headers or {})
        if r.status_code != 200:
            print(f"  FAIL [E2E] Fetch JD failed: {r.status_code}")
            failed += 1
            return passed, failed

        jd = r.json()
        if not jd.get("job_title") or not jd.get("description"):
            print("  FAIL [E2E] JD missing job_title or description")
            failed += 1
            return passed, failed

        print(f"  OK   [E2E] JD retrieved: {jd.get('job_title')}, {len(jd.get('description', ''))} chars")
        passed += 1

    return passed, failed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL of running AARLP server",
    )
    parser.add_argument(
        "--with-job-create",
        action="store_true",
        help="Run E2E: login, create job, wait for JD",
    )
    parser.add_argument(
        "--email",
        help="Existing user email (use with --password to skip register)",
    )
    parser.add_argument(
        "--password",
        help="Existing user password (use with --email)",
    )
    parser.add_argument(
        "--jd-timeout",
        type=int,
        default=180,
        help="Seconds to wait for JD generation (default 180)",
    )
    args = parser.parse_args()
    base = args.base_url.rstrip("/")

    if args.with_job_create and args.email and not args.password:
        print("ERROR: --email requires --password")
        return 1
    if args.with_job_create and args.password and not args.email:
        print("ERROR: --password requires --email")
        return 1

    print("Waiting for server...")
    if not wait_for_server(base):
        print("ERROR: Server not ready after 60s")
        return 1
    print("Server ready.\n")

    passed = 0
    failed = 0

    with httpx.Client(base_url=base, timeout=30.0) as client:
        # Health endpoints (no auth)
        tests = [
            ("GET", "/", 200),
            ("GET", "/health", (200, 503)),  # 503 if DB down
            ("GET", "/health/readiness", (200, 503)),
            ("GET", "/health/liveness", 200),
        ]
        for method, path, expected in tests:
            if isinstance(expected, tuple):
                ok = any(
                    test_endpoint(client, method, path, expect_status=s)[0]
                    for s in expected
                )
                statuses = " or ".join(str(s) for s in expected)
            else:
                ok, _ = test_endpoint(client, method, path, expect_status=expected)
            msg = f"{method} {path} -> {'ok' if ok else 'fail'}"
            if ok:
                passed += 1
                print(f"  OK  {msg}")
            else:
                failed += 1
                print(f"  FAIL {msg}")

        # Public careers
        ok, msg = test_endpoint(client, "GET", "/careers/", expect_status=200)
        if ok:
            passed += 1
            print(f"  OK  {msg}")
        else:
            failed += 1
            print(f"  FAIL {msg}")

        ok, msg = test_endpoint(client, "GET", "/careers/feed", expect_status=200)
        if ok:
            passed += 1
            print(f"  OK  {msg}")
        else:
            failed += 1
            print(f"  FAIL {msg}")

        # Auth validation (422)
        ok, msg = test_endpoint(client, "POST", "/auth/register", json={}, expect_status=422)
        if ok:
            passed += 1
            print(f"  OK  {msg}")
        else:
            failed += 1
            print(f"  FAIL {msg}")

        # Jobs require auth
        ok, msg = test_endpoint(client, "GET", "/jobs/", expect_status=401)
        if ok:
            passed += 1
            print(f"  OK  {msg}")
        else:
            failed += 1
            print(f"  FAIL {msg}")

        # Docs
        for path in ["/docs", "/redoc"]:
            ok, msg = test_endpoint(client, "GET", path, expect_status=200)
            if ok:
                passed += 1
                print(f"  OK  {msg}")
            else:
                failed += 1
                print(f"  FAIL {msg}")

        # Interviews (public placeholder)
        ok, msg = test_endpoint(client, "GET", "/interviews/", expect_status=200)
        if ok:
            passed += 1
            print(f"  OK  {msg}")
        else:
            failed += 1
            print(f"  FAIL {msg}")

        # Users require auth
        ok, msg = test_endpoint(client, "GET", "/users/me", expect_status=401)
        if ok:
            passed += 1
            print(f"  OK  {msg}")
        else:
            failed += 1
            print(f"  FAIL {msg}")

        # Careers detail - fake UUID returns 404
        ok, msg = test_endpoint(
            client,
            "GET",
            "/careers/00000000-0000-0000-0000-000000000000",
            expect_status=404,
        )
        if ok:
            passed += 1
            print(f"  OK  {msg}")
        else:
            failed += 1
            print(f"  FAIL {msg}")

        # Candidates list (no auth required in current impl)
        ok, msg = test_endpoint(client, "GET", "/candidates", expect_status=200)
        if ok:
            passed += 1
            print(f"  OK  {msg}")
        else:
            failed += 1
            print(f"  FAIL {msg}")

        # Job status without auth -> 401
        ok, msg = test_endpoint(
            client,
            "GET",
            "/jobs/status/00000000-0000-0000-0000-000000000000",
            expect_status=401,
        )
        if ok:
            passed += 1
            print(f"  OK  {msg}")
        else:
            failed += 1
            print(f"  FAIL {msg}")

    # E2E: login + create job + wait for JD
    if args.with_job_create:
        ep, ef = run_e2e_job_create(
            base,
            email=args.email,
            password=args.password,
            poll_timeout=args.jd_timeout,
        )
        passed += ep
        failed += ef

    print(f"\n--- {passed} passed, {failed} failed ---")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
