import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "name": record.name,
        }
        
        # Add extra fields if they exist
        if hasattr(record, "job_id"):
            log_record["job_id"] = record.job_id
            
        if record.exc_info:
            log_record["error_details"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

def setup_logging():
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate logs if handlers already exist
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(JSONFormatter())
        logger.addHandler(console_handler)
        
    return logger

logger = setup_logging()
