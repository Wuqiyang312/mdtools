import os
import subprocess
from typing import Optional


def convert_pdf_to_md(pdf_path: str, output_path: Optional[str] = None) -> str:
    """PDF 转 Markdown"""
    if output_path is None:
        output_path = os.path.splitext(pdf_path)[0] + ".md"
    
    cmd = ["pdftotext", "-layout", pdf_path, output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"转换失败：{result.stderr or result.stdout}")
    
    return output_path


def convert_md_to_pdf(md_path: str, output_path: Optional[str] = None) -> str:
    """Markdown 转 PDF"""
    if output_path is None:
        output_path = os.path.splitext(md_path)[0] + ".pdf"
    
    cmd = ["pandoc", md_path, "-o", output_path, "--pdf-engine=xelatex"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"转换失败：{result.stderr or result.stdout}")
    
    return output_path


def convert_md_to_doc(md_path: str, output_path: Optional[str] = None) -> str:
    """Markdown 转 Word"""
    if output_path is None:
        output_path = os.path.splitext(md_path)[0] + ".docx"
    
    cmd = ["pandoc", md_path, "-o", output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        error_msg = result.stderr or result.stdout
        if "couldn't unpack" in error_msg or "central directory" in error_msg:
            raise RuntimeError("pandoc 内部错误：无法创建 DOCX 文件")
        raise RuntimeError(f"转换失败：{error_msg}")
    
    return output_path


def convert_doc_to_md(doc_path: str, output_path: Optional[str] = None) -> str:
    """Word 转 Markdown"""
    if output_path is None:
        output_path = os.path.splitext(doc_path)[0] + ".md"
    
    cmd = ["pandoc", doc_path, "-o", output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        error_msg = result.stderr or result.stdout
        if "couldn't unpack" in error_msg or "central directory" in error_msg:
            raise RuntimeError("文件格式无效：不是有效的 DOCX 文件")
        raise RuntimeError(f"转换失败：{error_msg}")
    
    return output_path
