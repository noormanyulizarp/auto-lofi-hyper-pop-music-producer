from loguru import logger
import sys
from .config import settings

def setup_logger():
    """Setup loguru logger with custom configuration"""
    
    # Remove default logger
    logger.remove()
    
    # Add custom logger configuration
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True
    )
    
    # Add file logger
    logger.add(
        settings.LOG_FILE,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.LOG_LEVEL,
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )
    
    logger.info("Logger configured successfully")

def get_logger(name: str):
    """Get logger instance for a specific module"""
    return logger.bind(name=name)