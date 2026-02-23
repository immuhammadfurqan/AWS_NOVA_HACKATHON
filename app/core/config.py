"""
AARLP Configuration Module

Environment variables and application settings using Pydantic Settings.
"""

from functools import lru_cache
from typing import Literal, List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Groups:
        - Application
        - Database
        - AI / ML
        - Voice AI
        - Email / SMTP
        - Auth
        - Scheduling
        - Redis
        - Logging
    """

    # ----------------------------
    # Core Application
    # ----------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "AARLP"
    debug: bool = False
    timezone: str = "UTC"  # default timezone

    # ----------------------------
    # Database
    # ----------------------------
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/aarlp"

    # ----------------------------
    # Pinecone / Vector DB
    # ----------------------------
    pinecone_api_key: str = ""
    pinecone_index: str = "aarlp-candidates"
    pinecone_index_nova: str = "aarlp-nova-candidates"  # For Nova 1024-dim embeddings

    # ----------------------------
    # AI Provider Selection
    # ----------------------------
    ai_provider: Literal["openai", "bedrock"] = (
        "bedrock"  # Default to AWS for hackathon
    )

    # ----------------------------
    # OpenAI (Fallback)
    # ----------------------------
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-small"
    openai_embedding_dimension: int = 1536

    # ----------------------------
    # AWS Bedrock (Nova Models)
    # ----------------------------
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "amazon.nova-lite-v1:0"
    bedrock_embedding_model_id: str = "amazon.titan-embed-text-v2:0"
    bedrock_embedding_dimension: int = 1024

    # ----------------------------
    # Voice AI
    # ----------------------------
    voice_provider: Literal["twilio", "elevenlabs"] = "twilio"

    # Twilio
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""

    # ElevenLabs
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"

    # ----------------------------
    # Google Calendar
    # ----------------------------
    google_calendar_credentials_file: str = "credentials.json"
    google_calendar_token_file: str = "token.json"

    # ----------------------------
    # Recruitment / AI settings
    # ----------------------------
    min_applicant_threshold: int = 5
    monitoring_wait_days: int = 7

    # Feature flags for unimplemented features
    job_posting_enabled: bool = False  # Browser automation for job posting
    application_monitoring_enabled: bool = False  # Auto-monitoring of applications

    llm_temperature: float = 0.7
    shortlist_similarity_threshold: float = 0.7
    max_jd_generation_attempts: int = 3
    prescreening_max_score: int = 100
    max_embedding_text_length: int = 8000

    default_interview_duration_minutes: int = 60
    working_hours_start: int = 9
    working_hours_end: int = 17

    # ----------------------------
    # CORS
    # ----------------------------
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        """Return CORS origins as a list of strings."""
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]

    # ----------------------------
    # Authentication
    # ----------------------------
    secret_key: str = "dev-secret-key-change-in-production"  # Set SECRET_KEY in .env for production
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # ----------------------------
    # Email / SMTP
    # ----------------------------
    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = "noreply@aarlp.com"
    mail_port: int = 587
    mail_server: str = "smtp.gmail.com"
    mail_starttls: bool = True
    mail_ssl_tls: bool = False
    use_credentials: bool = True
    validate_certs: bool = True

    # ----------------------------
    # Redis (Distributed Locking / OTP)
    # ----------------------------
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""  # optional

    # ----------------------------
    # Logging
    # ----------------------------
    log_level: str = "INFO"
    log_dir: str = "logs"
    log_max_bytes: int = 5 * 1024 * 1024  # 5MB
    log_backup_count: int = 5


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
