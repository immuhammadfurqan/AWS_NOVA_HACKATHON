"""
Interviews App Router (API Routes)
"""

from fastapi import APIRouter

# Placeholder router for Interviews app
# Future endpoints: Webhook for voice call results, listing interviews, etc.
router = APIRouter()

@router.get("/", tags=["Interviews"])
async def list_interviews():
    """List scheduled interviews (Placeholder)."""
    return {"message": "Interview listing endpoint"}
