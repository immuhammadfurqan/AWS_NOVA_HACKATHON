"""Core module constants."""

# Application
APP_NAME = "AARLP"
APP_VERSION = "1.0.0"

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Timeouts (seconds)
DEFAULT_TIMEOUT = 30
AI_REQUEST_TIMEOUT = 60

# HTTP Status Messages
MSG_NOT_FOUND = "Resource not found"
MSG_FORBIDDEN = "Access denied"
MSG_VALIDATION_ERROR = "Validation failed"
MSG_INTERNAL_ERROR = "An unexpected error occurred"

# Health Check
HEALTH_STATUS_HEALTHY = "healthy"
HEALTH_STATUS_UNHEALTHY = "unhealthy"
HEALTH_STATUS_READY = "ready"
HEALTH_STATUS_NOT_READY = "not_ready"
HEALTH_STATUS_ALIVE = "alive"
