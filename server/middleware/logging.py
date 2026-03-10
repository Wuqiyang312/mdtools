"""日志中间件"""

import logging
from datetime import datetime

logger = logging.getLogger("mdtools.server")


class RequestLogger:
    """记录请求日志"""
    
    @staticmethod
    def log_request(handler, status_code=None):
        """记录 HTTP 请求日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        method = handler.command
        path = handler.path
        client = handler.client_address[0] if hasattr(handler, 'client_address') else 'unknown'
        
        log_msg = f"[{timestamp}] {client} {method} {path}"
        if status_code:
            log_msg += f" {status_code}"
        
        logger.info(log_msg)
        print(log_msg)
