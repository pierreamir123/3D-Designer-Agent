import logging
import os
import sys
import traceback
from datetime import datetime

# ANSI Color Codes
class Colors:
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"

class DetailedColorFormatter(logging.Formatter):
    """
    Custom formatter that adds colors to console output and 
    provides detailed info for errors.
    """
    
    LEVEL_COLORS = {
        logging.DEBUG: Colors.CYAN,
        logging.INFO: Colors.GREEN,
        logging.WARNING: Colors.YELLOW,
        logging.ERROR: Colors.RED,
        logging.CRITICAL: Colors.RED + Colors.BOLD
    }

    def format(self, record):
        # Color based on level
        color = self.LEVEL_COLORS.get(record.levelno, Colors.RESET)
        
        # Prepare components
        timestamp = self.formatTime(record, self.datefmt)
        level_name = f"{color}{record.levelname:8}{Colors.RESET}"
        logger_name = f"{Colors.BLUE}{record.name}{Colors.RESET}"
        message = record.getMessage()

        # Handle Exception info
        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        
        if record.exc_text:
            # Add some "Error Details" styling
            message = f"{message}\n{Colors.RED}--- Traceback Details ---{Colors.RESET}\n{record.exc_text}\n{Colors.RED}-------------------------{Colors.RESET}"

        return f"{timestamp} [{level_name}] {logger_name}: {message}"

# Create logs directory if it doesn't exist
logs_dir = "logs"
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Create a unique log file for each session
log_filename = f"logs/session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Setup root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Clear existing handlers
if root_logger.hasHandlers():
    root_logger.handlers.clear()

# File Handler (No colors in file)
file_handler = logging.FileHandler(log_filename, encoding='utf-8')
file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
file_handler.setFormatter(file_formatter)
root_logger.addHandler(file_handler)

# Console Handler (With colors)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(DetailedColorFormatter())
root_logger.addHandler(console_handler)

def get_logger(name):
    """Returns a logger instance with the specified name."""
    return logging.getLogger(name)

# Initial log entry
system_logger = get_logger("System")
system_logger.info("=== 3D Designer Agent Session Started ===")
system_logger.info(f"Logging to {log_filename}")
