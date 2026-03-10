#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 转 Markdown 工具
支持中文 PDF 文件转换，保证文字编码正确
"""

import os
import sys
import argparse
import pdfplumber


def pdf_to_text(pdf_path: str) -> str:
    """
    使用 pdfplumber 提取 PDF 文本内容

    Args:
        pdf_path: PDF 文件路径

    Returns:
        提取的文本内容
    """
    text_content = []

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            page_text = page.extract_text()
            if page_text:
                text_content.append(f"## 第 {i} 页\n")
                text_content.append(page_text)
                text_content.append("\n")

            tables = page.extract_tables()
            for j, table in enumerate(tables, 1):
                if table:
                    text_content.append(f"**表格 {j}**\n")
                    for row in table:
                        cleaned_row = [
                            str(cell).strip() if cell is not None else ""
                            for cell in row
                        ]
                        text_content.append("| " + " | ".join(cleaned_row) + " |")
                    text_content.append("\n")

    return "\n".join(text_content)


def convert_pdf_to_md(pdf_path: str, output_path: str | None = None) -> str:
    """
    将 PDF 转换为 Markdown 文件

    Args:
        pdf_path: PDF 文件路径
        output_path: 输出文件路径（可选，默认为同名.md 文件）

    Returns:
        输出文件路径
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"文件不存在：{pdf_path}")

    if output_path is None:
        base_name = os.path.splitext(pdf_path)[0]
        output_path = f"{base_name}.md"

    content = pdf_to_text(pdf_path)
    md_content = f"# {os.path.basename(pdf_path)}\n\n" + content

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="PDF 转 Markdown 工具（支持中文）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python pdf2md.py document.pdf
  python pdf2md.py document.pdf -o output.md
        """,
    )

    parser.add_argument("pdf_file", help="PDF 文件路径")
    parser.add_argument("-o", "--output", help="输出文件路径（默认：同名.md 文件）")

    args = parser.parse_args()

    try:
        output_path = convert_pdf_to_md(args.pdf_file, args.output)
        print(f"[OK] Conversion successful: {output_path}")
    except Exception as e:
        print(f"[ERROR] Conversion failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
