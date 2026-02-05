"""
Careers App Package

Public career pages and job listings for Google for Jobs integration.
No authentication required for this module.
"""

from app.careers.router import router

__all__ = ["router"]
