"""CORS 中间件"""


class CORSMiddleware:
    """处理跨域请求"""
    
    ALLOWED_ORIGINS = ["*"]
    ALLOWED_METHODS = ["GET", "POST", "OPTIONS"]
    ALLOWED_HEADERS = ["Content-Type", "Authorization"]
    
    @staticmethod
    def add_cors_headers(handler):
        """添加 CORS 头到响应"""
        def wrapper(self, *args, **kwargs):
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", ", ".join(CORSMiddleware.ALLOWED_METHODS))
            self.send_header("Access-Control-Allow-Headers", ", ".join(CORSMiddleware.ALLOWED_HEADERS))
            return handler(self, *args, **kwargs)
        return wrapper
