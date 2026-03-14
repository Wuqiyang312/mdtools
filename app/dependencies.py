import subprocess
import sys


def check_pandoc() -> bool:
    """检查 pandoc 是否安装"""
    try:
        subprocess.run(["pandoc", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_poppler() -> bool:
    """检查 poppler 是否安装"""
    try:
        subprocess.run(["pdftotext", "-v"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_dependencies():
    """检查所有依赖"""
    if not check_pandoc():
        print("[ERROR] 未找到 pandoc", file=sys.stderr)
        sys.exit(1)
    if not check_poppler():
        print("[ERROR] 未找到 poppler-utils", file=sys.stderr)
        sys.exit(1)
