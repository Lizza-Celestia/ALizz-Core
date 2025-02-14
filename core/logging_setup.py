"""
File Location: core/logging_setup.py
Author: Lizza Celestia
Version: ALizz_AI_V0_9
Created Date: 2025-02-12
Modified Date: 2025-02-14
Description:
"""
# core/logging_setup.py
import logging
import sys
import os
from datetime import datetime

def setup_logging(log_level=logging.INFO):
    """
    Configures the Python logging module for the entire application.
    Creates a new log file each time the script is run, stored in 'logs/'.
    """
    # 1. Ensure the logs directory exists
    os.makedirs("logs", exist_ok=True)

    # 2. Generate a timestamped log filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"ALizz_{timestamp}.log"
    log_path = os.path.join("logs", log_filename)

    # 3. Get the root logger and set the log level
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # 4. Define a log format
    formatter = logging.Formatter(
        fmt='[%(asctime)s] [%(levelname)s] %(name)s.%(lineno)d: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 5. Console handler (prints to stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 6. File handler (writes to a new file in logs/)
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 7. Log a startup message
    logger.info("Logging initialized at level %s", logging.getLevelName(log_level))
    logger.info("All logs for this session will be stored in: %s", log_path)

