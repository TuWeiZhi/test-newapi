import logging
import json
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Dict, Any

try:
    from log_broadcaster import broadcast_log
except ImportError:
    def broadcast_log(message: str, log_type: str = 'info'):
        pass


class APILogger:
    def __init__(self, config: Dict[str, Any]):
        self.log_path = Path(config.get('path', './logs'))
        self.log_path.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger('newapi_keeper')
        self.logger.setLevel(config.get('level', 'INFO'))
        
        log_format = config.get('format', '%(asctime)s - %(levelname)s - %(message)s')
        formatter = logging.Formatter(log_format)
        
        log_file = self.log_path / 'newapi_keeper.log'
        max_bytes = config.get('max_file_size', 10485760)
        backup_count = config.get('backup_count', 5)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def log_request(self, strategy_type: str, result: Dict[str, Any]):
        timestamp = datetime.now().isoformat()
        api_name = result.get('api_name', 'Unknown')
        
        if result.get('success'):
            msg = (f"API: {api_name} | Strategy: {strategy_type} | "
                   f"Tokens: {result['usage']['total_tokens']} | "
                   f"Model: {result['model']}")
            self.logger.info(msg)
            broadcast_log(msg, 'info')
            
            detail_log = self.log_path / 'request_details.jsonl'
            with open(detail_log, 'a', encoding='utf-8') as f:
                log_entry = {
                    'timestamp': timestamp,
                    'api_name': api_name,
                    'strategy': strategy_type,
                    'prompt': result['prompt'],
                    'response': result['response'],
                    'usage': result['usage'],
                    'model': result['model']
                }
                json_str = json.dumps(log_entry, ensure_ascii=False)
                f.write(json_str + '\n')
                broadcast_log(json_str, 'detail')
        else:
            msg = (f"API: {api_name} | Strategy: {strategy_type} | "
                   f"Error: {result.get('error', 'Unknown error')}")
            self.logger.error(msg)
            broadcast_log(msg, 'error')
    
    def log_strategy_failure(self, strategy_type: str, error: str):
        msg = f"Strategy {strategy_type} failed: {error}"
        self.logger.warning(msg)
        broadcast_log(msg, 'warning')
    
    def log_info(self, message: str):
        self.logger.info(message)
        broadcast_log(message, 'info')
    
    def log_error(self, message: str):
        self.logger.error(message)
        broadcast_log(message, 'error')
