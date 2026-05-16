"""
Structured logging system for Kavach AI.
Provides detailed tracing for production debugging.
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Optional, Dict

# Structured logger for JSON output (Cloud Run compatible)


class StructuredFormatter(logging.Formatter):
    """Format logs as JSON for Cloud Run."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        
        # Add custom fields
        if hasattr(record, "extra_data"):
            log_obj.update(record.extra_data)
        
        return json.dumps(log_obj)


def setup_logging(level: str = "INFO"):
    """Configure logging for production."""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Stdout handler with structured format
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(getattr(logging, level))
    
    # Use structured formatter for production, simple for development
    if level == "DEBUG":
        formatter = logging.Formatter(
            '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
        )
    else:
        formatter = StructuredFormatter()
    
    stdout_handler.setFormatter(formatter)
    root_logger.addHandler(stdout_handler)


def get_logger(name: str) -> logging.LoggerAdapter:
    """Get a logger with structured logging support."""
    base_logger = logging.getLogger(name)
    return StructuredLoggerAdapter(base_logger)


class StructuredLoggerAdapter(logging.LoggerAdapter):
    """Adapter that supports extra data for structured logging."""
    
    def __init__(self, logger: logging.Logger):
        super().__init__(logger, {})
    
    def log_event(self, level: int, event: str, **kwargs):
        """Log an event with structured data."""
        extra = logging.LogRecord(
            name=self.logger.name,
            level=level,
            pathname="",
            lineno=0,
            msg=event,
            args=(),
            exc_info=None
        )
        extra.extra_data = kwargs
        self.logger.handle(extra)
    
    def debug_event(self, event: str, **kwargs):
        self.log_event(logging.DEBUG, event, **kwargs)
    
    def info_event(self, event: str, **kwargs):
        self.log_event(logging.INFO, event, **kwargs)
    
    def warning_event(self, event: str, **kwargs):
        self.log_event(logging.WARNING, event, **kwargs)
    
    def error_event(self, event: str, **kwargs):
        self.log_event(logging.ERROR, event, **kwargs)


# Component-specific loggers
logger_startup = get_logger("startup")
logger_websocket = get_logger("websocket")
logger_ai = get_logger("ai")
logger_auth = get_logger("auth")
logger_database = get_logger("database")
logger_api = get_logger("api")


def log_startup(component: str, status: str):
    """Log startup progress."""
    logger_startup.info_event(
        "startup_component",
        component=component,
        status=status
    )


def log_websocket_event(event: str, session_id: str, **kwargs):
    """Log WebSocket events."""
    logger_websocket.info_event(
        "websocket_event",
        event=event,
        session_id=session_id,
        **kwargs
    )


def log_ai_request(agent: str, input_length: int, model: str = "unknown"):
    """Log AI request."""
    logger_ai.info_event(
        "ai_request",
        agent=agent,
        input_length=input_length,
        model=model
    )


def log_ai_response(agent: str, output_length: int, latency_ms: float, success: bool):
    """Log AI response."""
    level = "info_event" if success else "error_event"
    getattr(logger_ai, level)(
        "ai_response",
        agent=agent,
        output_length=output_length,
        latency_ms=latency_ms,
        success=success
    )


def log_ai_error(agent: str, error: str, error_type: str):
    """Log AI error."""
    logger_ai.error_event(
        "ai_error",
        agent=agent,
        error=error,
        error_type=error_type
    )


def log_auth_event(event: str, user_id: Optional[str] = None, **kwargs):
    """Log authentication events."""
    logger_auth.info_event(
        f"auth_{event}",
        user_id=user_id,
        **kwargs
    )


def log_database_event(event: str, table: str, **kwargs):
    """Log database events."""
    logger_database.info_event(
        f"db_{event}",
        table=table,
        **kwargs
    )


def log_api_request(endpoint: str, method: str, user_id: Optional[str] = None):
    """Log API request."""
    logger_api.info_event(
        "api_request",
        endpoint=endpoint,
        method=method,
        user_id=user_id
    )


def log_api_response(endpoint: str, status_code: int, latency_ms: float):
    """Log API response."""
    logger_api.info_event(
        "api_response",
        endpoint=endpoint,
        status_code=status_code,
        latency_ms=latency_ms
    )
