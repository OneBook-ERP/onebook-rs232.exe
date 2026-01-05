"""
Logging configuration for Waybridge Agent
Provides structured logging with rotation and multiple handlers
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional
from config_manager import get_config


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        """Format log record with colors"""
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{log_color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


class WaybridgeLogger:
    """Centralized logger for Waybridge Agent"""
    
    def __init__(self, name: str = "waybridge_agent"):
        """
        Initialize logger
        
        Args:
            name: Logger name
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
        
        # Load config
        try:
            config = get_config()
            log_config = config.get_section('logging')
        except Exception:
            # Fallback to defaults if config fails
            log_config = {
                'level': 'INFO',
                'file': 'waybridge_agent.log',
                'max_size_mb': 10,
                'backup_count': 5
            }
        
        # Set logger level
        level = getattr(logging, log_config.get('level', 'INFO').upper())
        self.logger.setLevel(level)
        
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler with rotation
        log_file = log_config.get('file', 'waybridge_agent.log')
        max_bytes = log_config.get('max_size_mb', 10) * 1024 * 1024
        backup_count = log_config.get('backup_count', 5)
        
        try:
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(level)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            self.logger.warning(f"Could not create file handler: {e}")
    
    def get_logger(self) -> logging.Logger:
        """
        Get logger instance
        
        Returns:
            Logger instance
        """
        return self.logger


# Singleton instance
_logger_instance: Optional[WaybridgeLogger] = None


def get_logger(name: str = "waybridge_agent") -> logging.Logger:
    """
    Get singleton logger instance
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    global _logger_instance
    
    if _logger_instance is None:
        _logger_instance = WaybridgeLogger(name)
    
    return _logger_instance.get_logger()


if __name__ == "__main__":
    # Test logger
    logger = get_logger()
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
