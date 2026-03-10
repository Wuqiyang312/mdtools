"""文件转换处理器"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConvertHandler:
    """处理文件转换请求"""
    
    SCRIPT_DIR = Path(__file__).parent.parent.parent
    UPLOAD_DIR = SCRIPT_DIR / "uploads"
    
    SUPPORTED_FORMATS = {
        "md2pdf": "md2pdf.py",
        "md2word": "md2word.py",
        "pdf2md": "pdf2md.py",
    }
    
    @classmethod
    def handle_json_request(cls, handler, request_data: Dict[str, Any]):
        """处理 JSON 格式请求"""
        try:
            input_path = request_data.get("input_path")
            output_path = request_data.get("output_path")
            format_type = request_data.get("format")
            
            if not input_path or not format_type:
                cls._send_error(handler, 400, "input_path and format are required")
                return
            
            result_path = cls._run_conversion(handler, input_path, output_path, format_type)
            cls._send_success(handler, result_path)
            
        except Exception as e:
            cls._send_error(handler, 500, str(e))
    
    @classmethod
    def handle_file_upload(cls, handler, file_data: bytes, file_name: str, format_type: str):
        """处理文件上传"""
        try:
            cls.UPLOAD_DIR.mkdir(exist_ok=True)
            input_path = cls.UPLOAD_DIR / file_name
            
            with open(input_path, "wb") as f:
                f.write(file_data)
            
            result_path = cls._run_conversion(handler, str(input_path), "", format_type)
            cls._send_success(handler, result_path)
            
        except Exception as e:
            cls._send_error(handler, 500, str(e))
    
    @classmethod
    def _run_conversion(cls, handler, input_path: str, output_path: str, format_type: str) -> str:
        """执行转换"""
        import subprocess
        import sys
        
        if format_type not in cls.SUPPORTED_FORMATS:
            raise ValueError(f"不支持的格式：{format_type}")
        
        script = cls.SCRIPT_DIR / cls.SUPPORTED_FORMATS[format_type]
        if not script.exists():
            raise FileNotFoundError(f"脚本不存在：{script}")
        
        args = [sys.executable, str(script), input_path]
        
        if output_path:
            args.extend(["-o", output_path])
        
        result = subprocess.run(args, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"转换失败：{result.stderr or result.stdout}")
        
        if not output_path:
            base_name = os.path.splitext(input_path)[0]
            extensions = {"md2pdf": ".pdf", "md2word": ".docx", "pdf2md": ".md"}
            output_path = base_name + extensions[format_type]
        
        return output_path
    
    @staticmethod
    def _send_success(handler, output_path: str):
        """发送成功响应"""
        handler.send_response(200)
        handler.send_header("Content-Type", "application/json")
        handler.send_header("Access-Control-Allow-Origin", "*")
        handler.end_headers()
        handler.wfile.write(json.dumps({
            "success": True,
            "message": "Conversion successful",
            "output_path": output_path,
        }).encode())
    
    @staticmethod
    def _send_error(handler, status: int, error: str):
        """发送错误响应"""
        handler.send_response(status)
        handler.send_header("Content-Type", "application/json")
        handler.send_header("Access-Control-Allow-Origin", "*")
        handler.end_headers()
        handler.wfile.write(json.dumps({
            "success": False,
            "error": error,
        }).encode())
