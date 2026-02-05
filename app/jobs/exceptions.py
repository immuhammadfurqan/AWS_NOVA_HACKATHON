"""
Jobs and Workflow Exceptions
"""

from app.core.exceptions import ValidationError, AARLPException, ExternalServiceError


class InvalidJobInputError(ValidationError):
    """Raised when job input is invalid."""

    def __init__(self, message: str, field: str) -> None:
        super().__init__(message, field)
        self.error_code = "INVALID_JOB_INPUT"


class JDNotGeneratedError(AARLPException):
    """Raised when JD is expected but not yet generated."""

    def __init__(self, job_id: str) -> None:
        super().__init__(
            message=f"Job description not yet generated for job {job_id}",
            error_code="JD_NOT_GENERATED",
            details={"job_id": job_id},
        )


class EmbeddingOperationError(ExternalServiceError):
    """Raised when embedding operations (Pinecone) fail."""

    def __init__(self, operation: str, job_id: str, original_error: str) -> None:
        super().__init__(
            service="Pinecone",
            message=f"Failed to {operation} embeddings for job {job_id}: {original_error}",
        )
        self.error_code = "EMBEDDING_OPERATION_ERROR"
        self.details["operation"] = operation
        self.details["job_id"] = job_id
