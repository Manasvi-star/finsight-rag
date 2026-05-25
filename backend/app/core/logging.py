import contextvars
import json
import logging
import sys
import time
from typing import Any, Dict, Optional

# Context variables for request-scoped logging details
request_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("request_id", default=None)
user_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("user_id", default=None)


class JSONFormatter(logging.Formatter):
    """
    Custom formatter that outputs log records as structured JSON.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }

        # Inject contextvars if available
        request_id = request_id_var.get()
        user_id = user_id_var.get()

        if request_id:
            log_data["request_id"] = request_id
        if user_id:
            log_data["user_id"] = user_id

        # Merge extra keys if provided
        if hasattr(record, "extra_info") and isinstance(record.extra_info, dict):
            log_data.update(record.extra_info)

        # Include exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logging() -> logging.Logger:
    """
    Configures the root logger to output structured JSON logs.
    """
    root_logger = logging.getLogger()
    
    # Avoid duplicate handlers if already configured
    if root_logger.handlers:
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            
    handler = logging.StreamHandler(sys.stdout)
    formatter = JSONFormatter()
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
    
    # Silence third-party logs slightly
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    return logging.getLogger("finsight_rag")


logger = logging.getLogger("finsight_rag")
