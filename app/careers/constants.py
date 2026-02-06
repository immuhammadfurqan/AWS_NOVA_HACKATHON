"""Careers module constants."""

from pathlib import Path

# File Upload
UPLOADS_DIR = Path("uploads/resumes")
MAX_RESUME_SIZE_MB = 10
MAX_RESUME_SIZE_BYTES = MAX_RESUME_SIZE_MB * 1024 * 1024
ALLOWED_RESUME_EXTENSIONS = {".pdf"}

# Application Status
APPLICATION_STATUS_PENDING = "pending"
APPLICATION_STATUS_REVIEWED = "reviewed"
APPLICATION_STATUS_SHORTLISTED = "shortlisted"
APPLICATION_STATUS_REJECTED = "rejected"

# Similarity Score Thresholds
SIMILARITY_HIGH_THRESHOLD = 0.80  # 80%+
SIMILARITY_MEDIUM_THRESHOLD = 0.50  # 50-79%
