import logging
import sys
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    return logging.getLogger(name)

def log_api_call(logger: logging.Logger, endpoint: str, method: str, **kwargs: Any) -> None:
    """Log an API call with relevant details."""
    logger.info(
        f"API Call - Endpoint: {endpoint}, Method: {method}, "
        f"Details: {', '.join(f'{k}={v}' for k, v in kwargs.items())}"
    )

def log_error(logger: logging.Logger, error: Exception, context: str = None) -> None:
    """Log an error with context if provided."""
    if context:
        logger.error(f"Error in {context}: {str(error)}", exc_info=True)
    else:
        logger.error(str(error), exc_info=True)
