---
description: Automate job posting to job boards using browser automation
---

# Job Posting Workflow

This workflow automates posting job descriptions to job boards using browser automation.

## Prerequisites
- Generated JD from the AARLP system
- Valid credentials for the target job board

## Steps

### 1. Navigate to Job Board
Navigate to the mock job board login page.

```
URL: https://jobs.example.com/login
```

### 2. Login
Fill in the login form with credentials:
- Username field: `#username`
- Password field: `#password`
- Submit button: `#login-btn`

### 3. Navigate to Post Job
Click on "Post a Job" or navigate to:
```
URL: https://jobs.example.com/post-job
```

### 4. Fill Job Details
Fill the job posting form with the generated JD data:

| Field | Selector | Data Source |
|-------|----------|-------------|
| Job Title | `#job-title` | `generated_jd.job_title` |
| Description | `#job-description` | `generated_jd.description` |
| Requirements | `#requirements` | `generated_jd.requirements` (joined) |
| Location | `#location` | `generated_jd.location` |
| Salary | `#salary-range` | `generated_jd.salary_range` |

### 5. Submit Posting
Click the submit button:
- Selector: `#submit-job`
- Wait for confirmation message

### 6. Capture Confirmation
- Capture the job posting URL from the confirmation page
- Return the URL to update the graph state

## Error Handling
- If login fails, retry up to 3 times
- If form submission fails, capture screenshot and report error
- Return error status with details if posting fails

## Return Data
```json
{
  "success": true,
  "job_posting_url": "https://jobs.example.com/jobs/12345",
  "posted_at": "2024-01-20T12:00:00Z"
}
```
