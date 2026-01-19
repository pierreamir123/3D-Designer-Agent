import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
logs_dir = "logs"
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Create a unique log file for each session
log_filename = f"logs/session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)

def get_logger(name):
    """Returns a logger instance with the specified name."""
    return logging.getLogger(name)

# Initial log entry
logger = get_logger("System")
logger.info("=== 3D Designer Agent Session Started ===")
logger.info(f"Logging to {log_filename}")
