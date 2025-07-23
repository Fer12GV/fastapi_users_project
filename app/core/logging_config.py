import logging
import logging.config
import sys
from typing import Dict, Any
from app.core.config import settings

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
        return super().format(record)

def setup_logging() -> None:
    """Setup logging configuration"""
    
    log_level = "DEBUG" if settings.DEBUG else "INFO"
    
    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "colored": {
                "()": ColoredFormatter,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "module": "%(module)s", "function": "%(funcName)s", "line": %(lineno)d, "message": "%(message)s"}',
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "colored" if settings.DEBUG else "default",
                "stream": sys.stdout,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "detailed",
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": "logs/error.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            }
        },
        "loggers": {
            "": {  # Root logger
                "level": log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            "app": {
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }
    
    # Add file handlers only in production
    if not settings.DEBUG:
        logging_config["loggers"][""]["handlers"].extend(["file", "error_file"])
        logging_config["loggers"]["app"]["handlers"].extend(["error_file"])
    
    # Create logs directory
    import os
    os.makedirs("logs", exist_ok=True)
    
    logging.config.dictConfig(logging_config)

# Create logger instance
logger = logging.getLogger("app")

# Utility functions for structured logging
def log_request(method: str, path: str, status_code: int, duration: float):
    """Log HTTP request"""
    logger.info(f"HTTP {method} {path} - {status_code} - {duration:.3f}s")

def log_database_operation(operation: str, table: str, duration: float = None):
    """Log database operation"""
    if duration:
        logger.debug(f"DB {operation} on {table} - {duration:.3f}s")
    else:
        logger.debug(f"DB {operation} on {table}")

def log_authentication(email: str, success: bool, reason: str = None):
    """Log authentication attempt"""
    if success:
        logger.info(f"Authentication successful for {email}")
    else:
        logger.warning(f"Authentication failed for {email}: {reason}")

def log_error(error: Exception, context: str = None):
    """Log error with context"""
    if context:
        logger.error(f"Error in {context}: {str(error)}", exc_info=True)
    else:
        logger.error(f"Error: {str(error)}", exc_info=True)
