import pytest
import subprocess
import sys
from pathlib import Path


class TestCLI:
    def test_help_command(self):
        result = subprocess.run(
            [sys.executable, "main.py", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "文档格式转换工具" in result.stdout

    def test_pdf2md_subcommand_help(self):
        result = subprocess.run(
            [sys.executable, "main.py", "pdf2md", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "PDF 文件路径" in result.stdout

    def test_md2pdf_subcommand_help(self):
        result = subprocess.run(
            [sys.executable, "main.py", "md2pdf", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0

    def test_md2doc_subcommand_help(self):
        result = subprocess.run(
            [sys.executable, "main.py", "md2doc", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0

    def test_no_command_shows_help(self):
        result = subprocess.run(
            [sys.executable, "main.py"],
            capture_output=True,
            text=True
        )
        # 无命令时显示帮助（输出到 stderr）或退出
        assert result.returncode == 0
