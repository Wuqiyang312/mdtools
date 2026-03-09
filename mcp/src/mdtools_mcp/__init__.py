#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档格式转换工具 MCP Server
支持 PDF <-> Markdown <-> Word 之间的转换
"""

import os
import re
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

import pdfplumber
import markdown
from weasyprint import HTML, CSS
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def pdf_to_text(pdf_path: str) -> str:
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


def get_chinese_css() -> str:
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
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()
    html_content = markdown.markdown(
        md_content, extensions=["tables", "toc", "fenced_code", "codehilite", "nl2br"]
    )
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
    if not os.path.exists(md_path):
        raise FileNotFoundError(f"文件不存在：{md_path}")
    if output_path is None:
        base_name = os.path.splitext(md_path)[0]
        output_path = f"{base_name}.pdf"
    html_content = md_to_html(md_path)
    if css_path and os.path.exists(css_path):
        css = CSS(filename=css_path)
    else:
        css = CSS(string=get_chinese_css())
    html_doc = HTML(string=html_content)
    html_doc.write_pdf(output_path, stylesheets=[css])
    return output_path


def set_font_style(paragraph, font_name="微软雅黑", font_size=12):
    for run in paragraph.runs:
        run.font.name = font_name
        run.font.size = Pt(font_size)
        rPr = run._element.get_or_add_rPr()
        rFonts = OxmlElement("w:rFonts")
        rFonts.set(qn("w:eastAsia"), font_name)
        rPr.insert(0, rFonts)


def convert_md_to_word(md_path, output_path=None):
    md_path = os.path.abspath(md_path)
    if not os.path.exists(md_path):
        raise FileNotFoundError(f"文件不存在：{md_path}")
    if output_path is None:
        output_path = os.path.splitext(md_path)[0] + ".docx"

    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    doc = Document()

    def add_normal_paragraph(text):
        p = doc.add_paragraph(text)
        set_font_style(p, "微软雅黑", 12)
        return p

    def add_heading_paragraph(text, level, size_map=None):
        if size_map is None:
            size_map = {1: 24, 2: 18, 3: 16, 4: 14, 5: 12, 6: 12}
        p = doc.add_heading(text, level=level)
        set_font_style(p, "微软雅黑", size_map.get(level, 12))
        return p

    lines = md_content.split("\n")
    current_paragraph = []

    def flush_paragraph():
        if current_paragraph:
            text = " ".join(current_paragraph)
            if text.strip():
                p = add_normal_paragraph(text)
                p.paragraph_format.space_after = Pt(6)
            current_paragraph.clear()

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        if re.match(r"^#{1,6}\s", line):
            flush_paragraph()
            match = re.match(r"^(#{1,6})\s+(.*)", line)
            if match:
                level = len(match.group(1))
                text = match.group(2)
                add_heading_paragraph(text, level)

        elif line.startswith("- ") or line.startswith("* "):
            flush_paragraph()
            text = line[2:].strip()
            p = add_normal_paragraph(text)
            p.style = "List Bullet"

        elif re.match(r"^\d+\.\s", line):
            flush_paragraph()
            text = re.sub(r"^\d+\.\s", "", line).strip()
            p = add_normal_paragraph(text)
            p.style = "List Number"

        elif line.startswith("> "):
            flush_paragraph()
            text = line[2:].strip()
            p = add_normal_paragraph(text)
            p.paragraph_format.left_indent = Cm(1)
            setattr(p, "italic", True)

        elif line.startswith("```"):
            flush_paragraph()
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            if code_lines:
                code_text = "\n".join(code_lines)
                p = add_normal_paragraph(code_text)
                if p.style and p.style.font:
                    p.style.font.name = "Courier New"
                p.paragraph_format.left_indent = Cm(0.5)
                p.paragraph_format.space_before = Pt(6)
                p.paragraph_format.space_after = Pt(6)

        elif line.strip() == "":
            flush_paragraph()

        else:
            current_paragraph.append(line)

        i += 1

    flush_paragraph()
    doc.save(output_path)
    return output_path


async def main():
    server = Server("mdtools")

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="pdf2md",
                description="将 PDF 文件转换为 Markdown 格式",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "pdf_path": {
                            "type": "string",
                            "description": "PDF 文件路径",
                        },
                        "output_path": {
                            "type": "string",
                            "description": "输出 Markdown 文件路径（可选，默认为同名.md 文件）",
                        },
                    },
                    "required": ["pdf_path"],
                },
            ),
            types.Tool(
                name="md2pdf",
                description="将 Markdown 文件转换为 PDF 格式",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "md_path": {
                            "type": "string",
                            "description": "Markdown 文件路径",
                        },
                        "output_path": {
                            "type": "string",
                            "description": "输出 PDF 文件路径（可选，默认为同名.pdf 文件）",
                        },
                        "css_path": {
                            "type": "string",
                            "description": "自定义 CSS 样式文件路径（可选）",
                        },
                    },
                    "required": ["md_path"],
                },
            ),
            types.Tool(
                name="md2doc",
                description="将 Markdown 文件转换为 Word 格式",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "md_path": {
                            "type": "string",
                            "description": "Markdown 文件路径",
                        },
                        "output_path": {
                            "type": "string",
                            "description": "输出 Word 文件路径（可选，默认为同名.docx 文件）",
                        },
                    },
                    "required": ["md_path"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        if name == "pdf2md":
            pdf_path = arguments.get("pdf_path")
            output_path = arguments.get("output_path")
            result = convert_pdf_to_md(pdf_path, output_path if output_path else None)
            return [types.TextContent(type="text", text=f"转换成功：{result}")]

        elif name == "md2pdf":
            md_path = arguments.get("md_path")
            output_path = arguments.get("output_path")
            css_path = arguments.get("css_path")
            result = convert_md_to_pdf(
                md_path,
                output_path if output_path else None,
                css_path if css_path else None,
            )
            return [types.TextContent(type="text", text=f"转换成功：{result}")]

        elif name == "md2doc":
            md_path = arguments.get("md_path")
            output_path = arguments.get("output_path")
            result = convert_md_to_word(md_path, output_path if output_path else None)
            return [types.TextContent(type="text", text=f"转换成功：{result}")]

        else:
            raise ValueError(f"未知工具：{name}")

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main_sync():
    import asyncio

    asyncio.run(main())


if __name__ == "__main__":
    main_sync()
