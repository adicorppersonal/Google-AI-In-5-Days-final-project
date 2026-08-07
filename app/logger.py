import logging
import json
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

class JsonFormatter(logging.Formatter):
    """Formats log records as structured JSON capturing intent vs outcome."""
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(ZoneInfo("UTC")).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Capture intent and outcome if provided in record attributes or extra dict
        if hasattr(record, "agent"):
            log_data["agent"] = record.agent
        if hasattr(record, "intent"):
            log_data["intent"] = record.intent
        if hasattr(record, "outcome"):
            log_data["outcome"] = record.outcome
        if hasattr(record, "metadata") and isinstance(record.metadata, dict):
            log_data["metadata"] = record.metadata
            
        return json.dumps(log_data)

def get_structured_logger(name: str) -> logging.Logger:
    """Returns a logger configured with structured JSON formatting."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger
