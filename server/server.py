#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MDTools Web Server
Markdown 转换工具的 Web 服务接口
"""

import os
import sys
import subprocess
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from pathlib import Path


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
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        if self.path == "/health":
            self._set_headers()
            self.wfile.write(json.dumps({"status": "healthy"}).encode())
        elif self.path == "/" or self.path == "/index.html":
            self._set_headers(200, "text/html; charset=utf-8")
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def do_POST(self):
        if self.path == "/convert":
            content_type = self.headers.get("Content-Type", "")

            if "multipart/form-data" in content_type:
                self.handle_file_upload()
            elif "application/json" in content_type:
                self.handle_json_request()
            else:
                self._set_headers(400)
                self.wfile.write(
                    json.dumps({"error": "Unsupported content type"}).encode()
                )
            return

        self._set_headers(404)
        self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def handle_json_request(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            req = json.loads(body)
        except json.JSONDecodeError as e:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": f"Invalid JSON: {e}"}).encode())
            return

        input_path = req.get("input_path")
        output_path = req.get("output_path")
        format_type = req.get("format")

        if not input_path or not format_type:
            self._set_headers(400)
            self.wfile.write(
                json.dumps(
                    {"success": False, "error": "input_path and format are required"}
                ).encode()
            )
            return

        try:
            result_path = run_conversion(input_path, output_path, format_type)
            self._set_headers()
            self.wfile.write(
                json.dumps(
                    {
                        "success": True,
                        "message": "Conversion successful",
                        "output_path": result_path,
                    }
                ).encode()
            )
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

    def handle_file_upload(self):
        content_type = self.headers.get("Content-Type", "")
        boundary = None

        if "boundary=" in content_type:
            boundary = content_type.split("boundary=")[1].strip()

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
                            file_data = part[header_end + 4 :].rstrip(b"\r\n-")

                if b'name="format"' in part:
                    header_end = part.find(b"\r\n\r\n")
                    if header_end != -1:
                        format_type = (
                            part[header_end + 4 :]
                            .rstrip(b"\r\n-")
                            .decode("utf-8")
                            .strip()
                        )

        if file_data and file_name and format_type:
            upload_dir = PROJECT_DIR / "uploads"
            upload_dir.mkdir(exist_ok=True)

            input_path = upload_dir / file_name
            with open(input_path, "wb") as f:
                f.write(file_data)

            try:
                result_path = run_conversion(str(input_path), "", format_type)
                self._set_headers()
                self.wfile.write(
                    json.dumps(
                        {
                            "success": True,
                            "message": "Conversion successful",
                            "output_path": result_path,
                        }
                    ).encode()
                )
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(
                    json.dumps({"success": False, "error": str(e)}).encode()
                )
        else:
            self._set_headers(400)
            self.wfile.write(
                json.dumps(
                    {"success": False, "error": "Missing file or format"}
                ).encode()
            )

    def log_message(self, format, *args):
        print(f"[{self.address_string()}] {args[0]}")


def run_conversion(input_path: str, output_path: str, format_type: str) -> str:
    venv_python = PROJECT_DIR / "venv" / "bin" / "python"

    if not venv_python.exists():
        venv_python = sys.executable

    scripts = {"md2pdf": "md2pdf.py", "md2word": "md2word.py", "pdf2md": "pdf2md.py"}

    if format_type not in scripts:
        raise ValueError(
            f"Unsupported format: {format_type} (supported: {', '.join(scripts.keys())})"
        )

    script = PROJECT_DIR / scripts[format_type]
    if not script.exists():
        raise FileNotFoundError(f"Script not found: {script}")

    args = [str(venv_python), str(script), input_path]

    if output_path:
        if format_type in ["md2pdf", "pdf2md"]:
            args.extend(["-o", output_path])
        else:
            args.append(output_path)

    result = subprocess.run(args, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"Conversion failed: {result.stderr or result.stdout}")

    if not output_path:
        base_name = os.path.splitext(input_path)[0]
        extensions = {"md2pdf": ".pdf", "md2word": ".docx", "pdf2md": ".md"}
        output_path = base_name + extensions[format_type]

    return output_path


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
