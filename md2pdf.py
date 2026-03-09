#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown 转 PDF 工具
支持中文，保证文字编码正确
"""

import os
import sys
import argparse
import markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration


def get_chinese_css() -> str:
    """返回支持中文的 CSS 样式"""
    return """
    @page {
        size: A4;
        margin: 2.5cm 2cm;
    }
    
    body {
        font-family: "Noto Serif CJK SC", "Source Han Serif CN", "SimSun", "Songti SC", serif;
        font-size: 12pt;
        line-height: 1.8;
        text-align: justify;
        color: #333;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: "Noto Sans CJK SC", "Source Han Sans CN", "SimHei", "Heiti SC", sans-serif;
        margin-top: 1.5em;
        margin-bottom: 0.8em;
        page-break-after: avoid;
    }
    
    h1 { font-size: 18pt; border-bottom: 2px solid #333; padding-bottom: 0.3em; }
    h2 { font-size: 16pt; border-bottom: 1px solid #ddd; padding-bottom: 0.3em; }
    h3 { font-size: 14pt; }
    
    p { margin: 0.8em 0; }
    
    code {
        font-family: "Courier New", Consolas, monospace;
        background-color: #f5f5f5;
        padding: 0.2em 0.4em;
        border-radius: 3px;
    }
    
    pre {
        background-color: #f5f5f5;
        padding: 1em;
        border-radius: 5px;
        overflow-x: auto;
        font-size: 10pt;
    }
    
    pre code {
        background: none;
        padding: 0;
    }
    
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 1em 0;
        font-size: 10pt;
    }
    
    th, td {
        border: 1px solid #ddd;
        padding: 0.5em;
        text-align: left;
    }
    
    th {
        background-color: #f5f5f5;
        font-weight: bold;
    }
    
    blockquote {
        margin: 1em 0;
        padding: 0.5em 1em;
        border-left: 4px solid #ddd;
        color: #666;
    }
    
    ul, ol {
        margin: 0.8em 0;
        padding-left: 2em;
    }
    
    li {
        margin: 0.4em 0;
    }
    
    a {
        color: #0066cc;
        text-decoration: none;
    }
    
    img {
        max-width: 100%;
        height: auto;
    }
    """


def md_to_html(md_path: str) -> str:
    """
    将 Markdown 转换为 HTML

    Args:
        md_path: Markdown 文件路径

    Returns:
        HTML 字符串
    """
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    # 使用 markdown 库转换，启用表格、目录等扩展
    html_content = markdown.markdown(
        md_content, extensions=["tables", "toc", "fenced_code", "codehilite", "nl2br"]
    )

    # 添加完整的 HTML 结构
    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{os.path.basename(md_path)}</title>
</head>
<body>
{html_content}
</body>
</html>"""

    return full_html


def convert_md_to_pdf(
    md_path: str, output_path: str | None = None, css_path: str | None = None
) -> str:
    """
    将 Markdown 转换为 PDF 文件

    Args:
        md_path: Markdown 文件路径
        output_path: 输出 PDF 文件路径（可选）
        css_path: 自定义 CSS 文件路径（可选）

    Returns:
        输出文件路径
    """
    if not os.path.exists(md_path):
        raise FileNotFoundError(f"文件不存在：{md_path}")

    if output_path is None:
        base_name = os.path.splitext(md_path)[0]
        output_path = f"{base_name}.pdf"

    # 转换为 HTML
    html_content = md_to_html(md_path)

    # 准备 CSS
    if css_path and os.path.exists(css_path):
        css = CSS(filename=css_path)
    else:
        css = CSS(string=get_chinese_css())

    # 生成 PDF
    html_doc = HTML(string=html_content)
    html_doc.write_pdf(output_path, stylesheets=[css])

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Markdown 转 PDF 工具（支持中文）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python md2pdf.py document.md
  python md2pdf.py document.md -o output.pdf
  python md2pdf.py document.md --css custom.css
        """,
    )

    parser.add_argument("md_file", help="Markdown 文件路径")
    parser.add_argument("-o", "--output", help="输出 PDF 文件路径")
    parser.add_argument("--css", help="自定义 CSS 样式文件路径")

    args = parser.parse_args()

    try:
        output_path = convert_md_to_pdf(args.md_file, args.output, args.css)
        print(f"✓ 转换成功：{output_path}")
    except Exception as e:
        print(f"✗ 转换失败：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
