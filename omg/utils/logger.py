import logging
import os
from datetime import datetime

def setup_logger(log_dir="logs"):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    log_file = os.path.join(log_dir, f"omg_{datetime.now().strftime('%Y%m%d')}.log")
    
    # Configure logging
    # Use UTF-8 for file handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    # Use a custom handler for stream to handle potential console encoding issues
    import sys
    stream_handler = logging.StreamHandler(sys.stdout)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[file_handler, stream_handler]
    )
    
    logging.info("OMG Logger initialized.")
