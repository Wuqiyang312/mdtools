#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MDTools Web Server
Markdown 转换工具的 Web 服务接口
"""

import os
import sys
import argparse
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

from handlers import HealthHandler, ConvertHandler
from middleware import CORSMiddleware, RequestLogger


SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent


HTML_PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MDTools - 文档转换工具</title>
</head>
<body>
    <h1>MDTools 文档转换</h1>
    
    <form id="convertForm" enctype="multipart/form-data">
        <div>
            <label for="file">选择文件:</label>
            <input type="file" id="file" name="file" required>
        </div>
        
        <div>
            <label for="format">转换格式:</label>
            <select id="format" name="format" required>
                <option value="md2pdf">Markdown → PDF</option>
                <option value="md2word">Markdown → Word</option>
                <option value="pdf2md">PDF → Markdown</option>
            </select>
        </div>
        
        <div>
            <button type="submit">转换</button>
        </div>
    </form>
    
    <div id="result"></div>
    
    <hr>
    <h2>API 信息</h2>
    <p>POST /convert - 转换文件</p>
    <p>GET /health - 健康检查</p>
    
    <script>
        document.getElementById('convertForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const resultDiv = document.getElementById('result');
            const fileInput = document.getElementById('file');
            const formatSelect = document.getElementById('format');
            
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('format', formatSelect.value);
            
            resultDiv.innerHTML = '<p>转换中...</p>';
            
            try {
                const response = await fetch('/convert', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                
                if (data.success) {
                    resultDiv.innerHTML = '<p>✓ 转换成功!</p><p>输出：' + data.output_path + '</p>';
                } else {
                    resultDiv.innerHTML = '<p>✗ 转换失败：' + data.error + '</p>';
                }
            } catch (err) {
                resultDiv.innerHTML = '<p>✗ 请求错误：' + err + '</p>';
            }
        });
    </script>
</body>
</html>
"""


class ConvertHandler(BaseHTTPRequestHandler):
    """HTTP 请求处理器"""
    
    @CORSMiddleware.add_cors_headers
    def do_OPTIONS(self):
        """处理 CORS 预检请求"""
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        """处理 GET 请求"""
        RequestLogger.log_request(self)
        
        if self.path == "/health":
            HealthHandler.handle(self)
        elif self.path == "/" or self.path == "/index.html":
            self._serve_html_page()
        else:
            self._send_404()
    
    def do_POST(self):
        """处理 POST 请求"""
        RequestLogger.log_request(self)
        
        if self.path == "/convert":
            content_type = self.headers.get("Content-Type", "")
            
            if "application/json" in content_type:
                self._handle_json_request()
            elif "multipart/form-data" in content_type:
                self._handle_file_upload()
            else:
                ConvertHandler._send_error(self, 400, "Unsupported content type")
        else:
            self._send_404()
    
    def _handle_json_request(self):
        """处理 JSON 请求"""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        
        try:
            request_data = json.loads(body)
            ConvertHandler.handle_json_request(self, request_data)
        except json.JSONDecodeError as e:
            ConvertHandler._send_error(self, 400, f"Invalid JSON: {e}")
    
    def _handle_file_upload(self):
        """处理文件上传"""
        content_type = self.headers.get("Content-Type", "")
        boundary = content_type.split("boundary=")[1].strip() if "boundary=" in content_type else None
        
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        
        file_data = None
        file_name = None
        format_type = None
        
        if boundary:
            parts = body.split(boundary.encode())
            for part in parts:
                if b'name="file"' in part:
                    header_end = part.find(b"\r\n\r\n")
                    if header_end != -1:
                        header = part[:header_end].decode("utf-8", errors="ignore")
                        if 'filename="' in header:
                            file_name = header.split('filename="')[1].split('"')[0]
                            file_data = part[header_end + 4:].rstrip(b"\r\n-")
                
                if b'name="format"' in part:
                    header_end = part.find(b"\r\n\r\n")
                    if header_end != -1:
                        format_type = part[header_end + 4:].rstrip(b"\r\n-").decode("utf-8").strip()
        
        if file_data and file_name and format_type:
            ConvertHandler.handle_file_upload(self, file_data, file_name, format_type)
        else:
            ConvertHandler._send_error(self, 400, "Missing file or format")
    
    def _serve_html_page(self):
        """服务 HTML 页面"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(HTML_PAGE.encode("utf-8"))
    
    def _send_404(self):
        """发送 404 响应"""
        self.send_response(404)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        RequestLogger.log_request(self)


def main():
    parser = argparse.ArgumentParser(description="MDTools Web Server")
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("PORT", 8080)),
        help="Server port (default: 8080)",
    )
    parser.add_argument(
        "--host", type=str, default="0.0.0.0", help="Server host (default: 0.0.0.0)"
    )
    args = parser.parse_args()

    server = HTTPServer((args.host, args.port), ConvertHandler)

    print(f"Starting server on {args.host}:{args.port}")
    print("Endpoints:")
    print("  GET  /        - Web 界面")
    print("  POST /convert - Convert files (md2pdf, md2word, pdf2md)")
    print("  GET  /health  - Health check")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()


if __name__ == "__main__":
    main()
