"""健康检查处理器"""

import json


class HealthHandler:
    """处理健康检查请求"""
    
    @staticmethod
    def handle(handler):
        """处理 GET /health 请求"""
        handler.send_response(200)
        handler.send_header("Content-Type", "application/json")
        handler.send_header("Access-Control-Allow-Origin", "*")
        handler.end_headers()
        handler.wfile.write(json.dumps({"status": "healthy"}).encode())
