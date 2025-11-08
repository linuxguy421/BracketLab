# core/logger.py

import sys
from loguru import logger
from pathlib import Path
# Import the ConfigManager instance we created earlier
from core.config_manager import config_manager 

# --- Setup Logging Paths ---
LOG_DIR = Path('logs')
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE_PATH = LOG_DIR / 'bracketlab.log'

# --- Configure Loguru ---
def setup_logger():
    """Removes default loguru handlers and configures logging based on config."""
    
    # Remove default handler
    logger.remove()

    # Add console sink
    logger.add(
        sys.stderr, 
        level="INFO", # Show INFO and above in the console for immediate feedback
        format="<green>{time:HH:mm:ss}</green> | {level} | {message}",
        colorize=True
    )

    # Add file sink using the configured level
    try:
        # Get log level from the validated config model
        log_level = config_manager.config.logging_level
    except RuntimeError:
        # Fallback if config failed to load for some reason
        log_level = "DEBUG" 
    
    logger.add(
        LOG_FILE_PATH,
        level=log_level,
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        enqueue=True, # Essential for performance, especially with a GUI
        serialize=False 
    )

    logger.debug("Logger initialized successfully.")

# Initialize the logger on import
setup_logger()
