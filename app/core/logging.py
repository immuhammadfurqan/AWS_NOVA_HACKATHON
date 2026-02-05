"""
AARLP Logging Configuration

Structured logging setup using Python's logging module with:
- JSON formatting for production
- Colored console output for development
- File-based logging with rotation
- Request correlation IDs
- Performance metrics logging
"""

import logging
import sys
from datetime import datetime
from typing import Any
import json
from contextvars import ContextVar
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.config import get_settings


# Context variable for request correlation ID
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging in production."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": correlation_id_var.get(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)
        
        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """Colored console formatter for development."""
    
    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        correlation = correlation_id_var.get()
        correlation_str = f"[{correlation[:8]}] " if correlation else ""
        
        formatted = (
            f"{color}{record.levelname:8}{self.RESET} | "
            f"{record.name:25} | "
            f"{correlation_str}"
            f"{record.getMessage()}"
        )
        
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted


def setup_logging() -> None:
    """Configure application logging based on environment."""
    settings = get_settings()
    
    # Determine log level
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    if settings.debug:
        log_level = logging.DEBUG
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Use colored formatter for debug, JSON for production
    if settings.debug:
        console_handler.setFormatter(ColoredFormatter())
    else:
        console_handler.setFormatter(JSONFormatter())
    
    root_logger.addHandler(console_handler)
    
    # Create logs directory
    logs_dir = Path(settings.log_dir)
    logs_dir.mkdir(exist_ok=True)
    
    # Per-module file handlers
    module_log_files = {
        "app.jobs": "jobs.log",
        "app.candidates": "candidates.log",
        "app.interviews": "interviews.log",
        "": "app.log",  # Root logger fallback for core, main, etc.
    }
    
    for module_name, log_file in module_log_files.items():
        file_handler = RotatingFileHandler(
            logs_dir / log_file,
            maxBytes=settings.log_max_bytes,
            backupCount=settings.log_backup_count,
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(JSONFormatter())
        
        if module_name:
            # Add handler to specific module logger
            module_logger = logging.getLogger(module_name)
            module_logger.addHandler(file_handler)
        else:
            # Add to root logger for everything else
            root_logger.addHandler(file_handler)
    
    # Set log levels for noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name."""
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """Logger adapter with extra context support."""
    
    def process(
        self, msg: str, kwargs: dict[str, Any]
    ) -> tuple[str, dict[str, Any]]:
        # Add extra data to record
        extra = kwargs.get("extra", {})
        extra["extra_data"] = self.extra
        kwargs["extra"] = extra
        return msg, kwargs


def get_context_logger(name: str, **context: Any) -> LoggerAdapter:
    """Get a logger with additional context fields."""
    logger = get_logger(name)
    return LoggerAdapter(logger, context)


# ============================================================================
# Performance Logging
# ============================================================================

import time
from functools import wraps
from typing import Callable, TypeVar

T = TypeVar("T")


def log_performance(
    logger_name: str = "performance",
    threshold_ms: float = 1000.0,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to log function execution time.
    
    Args:
        logger_name: Name of the logger to use
        threshold_ms: Log warning if execution exceeds this threshold
    """
    logger = get_logger(logger_name)
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            start = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                elapsed_ms = (time.perf_counter() - start) * 1000
                log_msg = f"{func.__name__} completed in {elapsed_ms:.2f}ms"
                
                if elapsed_ms > threshold_ms:
                    logger.warning(f"SLOW: {log_msg}")
                else:
                    logger.debug(log_msg)
        
        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                elapsed_ms = (time.perf_counter() - start) * 1000
                log_msg = f"{func.__name__} completed in {elapsed_ms:.2f}ms"
                
                if elapsed_ms > threshold_ms:
                    logger.warning(f"SLOW: {log_msg}")
                else:
                    logger.debug(log_msg)
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator
