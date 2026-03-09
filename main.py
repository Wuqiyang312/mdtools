#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档格式转换工具 - 统一入口
支持 PDF <-> Markdown <-> Word 之间的转换
"""

import os
import sys
import argparse
import re
import pdfplumber
import markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def get_resource_path(relative_path: str) -> str:
    """获取资源的绝对路径，支持 PyInstaller 单文件模式"""
    if hasattr(sys, "_MEIPASS"):  # type: ignore
        return os.path.join(sys._MEIPASS, relative_path)  # type: ignore
    return os.path.join(os.path.abspath("."), relative_path)


# ==================== PDF 转 Markdown ====================
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


# ==================== Markdown 转 PDF ====================
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


# ==================== Markdown 转 Word ====================
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


# ==================== Tkinter GUI ====================
def run_gui():
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox

    class ConverterApp:
        def __init__(self, root):
            self.root = root
            self.root.title("文档格式转换工具")
            self.root.geometry("500x300")
            self.root.resizable(False, False)

            self.input_file = tk.StringVar()
            self.output_file = tk.StringVar()
            self.convert_type = tk.StringVar(value="pdf2md")

            self.create_widgets()

        def create_widgets(self):
            main_frame = ttk.Frame(self.root, padding="10")
            main_frame.grid(row=0, column=0, sticky="nsew")

            ttk.Label(
                main_frame, text="文档格式转换工具", font=("微软雅黑", 16, "bold")
            ).grid(row=0, column=0, columnspan=3, pady=(0, 20))

            ttk.Label(main_frame, text="转换类型:").grid(
                row=1, column=0, sticky="w", pady=5
            )
            type_combo = ttk.Combobox(
                main_frame,
                textvariable=self.convert_type,
                values=["pdf2md", "md2pdf", "md2doc"],
                state="readonly",
                width=25,
            )
            type_combo.grid(row=1, column=1, columnspan=2, sticky="w", pady=5)
            type_combo.set("pdf2md")

            ttk.Label(main_frame, text="输入文件:").grid(
                row=2, column=0, sticky="w", pady=5
            )
            ttk.Entry(main_frame, textvariable=self.input_file, width=35).grid(
                row=2, column=1, columnspan=2, sticky="w", pady=5
            )
            ttk.Button(main_frame, text="浏览...", command=self.browse_input).grid(
                row=2, column=2, sticky="e", pady=5
            )

            ttk.Label(main_frame, text="输出文件:").grid(
                row=3, column=0, sticky="w", pady=5
            )
            ttk.Entry(main_frame, textvariable=self.output_file, width=35).grid(
                row=3, column=1, columnspan=2, sticky="w", pady=5
            )
            ttk.Button(main_frame, text="浏览...", command=self.browse_output).grid(
                row=3, column=2, sticky="e", pady=5
            )

            btn_frame = ttk.Frame(main_frame)
            btn_frame.grid(row=4, column=0, columnspan=3, pady=20)
            ttk.Button(btn_frame, text="开始转换", command=self.convert).pack(
                side="left", padx=5
            )
            ttk.Button(btn_frame, text="退出", command=self.root.quit).pack(
                side="left", padx=5
            )

            self.status_label = ttk.Label(main_frame, text="", foreground="green")
            self.status_label.grid(row=5, column=0, columnspan=3, pady=10)

        def browse_input(self):
            file_types = {
                "pdf2md": [("PDF 文件", "*.pdf")],
                "md2pdf": [("Markdown 文件", "*.md")],
                "md2doc": [("Markdown 文件", "*.md")],
            }
            file_path = filedialog.askopenfilename(
                title="选择输入文件",
                filetypes=file_types.get(self.convert_type.get(), [("所有文件", "*.*")]),
            )
            if file_path:
                self.input_file.set(file_path)
                if not self.output_file.get():
                    base, _ = os.path.splitext(file_path)
                    ext_map = {"pdf2md": ".md", "md2pdf": ".pdf", "md2doc": ".docx"}
                    self.output_file.set(base + ext_map.get(self.convert_type.get(), ""))

        def browse_output(self):
            file_types = {
                "pdf2md": [("Markdown 文件", "*.md")],
                "md2pdf": [("PDF 文件", "*.pdf")],
                "md2doc": [("Word 文件", "*.docx")],
            }
            file_path = filedialog.asksaveasfilename(
                title="选择输出文件",
                filetypes=file_types.get(self.convert_type.get(), [("所有文件", "*.*")]),
            )
            if file_path:
                self.output_file.set(file_path)

        def convert(self):
            input_path = self.input_file.get().strip()
            output_path = self.output_file.get().strip()

            if not input_path:
                messagebox.showerror("错误", "请选择输入文件")
                return

            if not os.path.exists(input_path):
                messagebox.showerror("错误", "输入文件不存在")
                return

            try:
                if self.convert_type == "pdf2md":
                    result = convert_pdf_to_md(
                        input_path, output_path if output_path else None
                    )
                elif self.convert_type == "md2pdf":
                    result = convert_md_to_pdf(
                        input_path, output_path if output_path else None
                    )
                elif self.convert_type == "md2doc":
                    result = convert_md_to_word(
                        input_path, output_path if output_path else None
                    )
                else:
                    messagebox.showerror("错误", "未知的转换类型")
                    return

                self.status_label.config(text=f"✓ 转换成功：{result}")
                messagebox.showinfo("成功", f"转换成功!\n{result}")

            except Exception as e:
                self.status_label.config(text=f"✗ 转换失败：{e}", foreground="red")
                messagebox.showerror("失败", f"转换失败:\n{e}")

    root = tk.Tk()
    ConverterApp(root)
    root.mainloop()


# ==================== 命令行接口 ====================
def run_cli():
    parser = argparse.ArgumentParser(
        description="文档格式转换工具 - 支持 PDF <-> Markdown <-> Word",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # PDF 转 Markdown
  mdtools pdf2md document.pdf
  mdtools pdf2md document.pdf -o output.md

  # Markdown 转 PDF
  mdtools md2pdf document.md
  mdtools md2pdf document.md -o output.pdf

  # Markdown 转 Word
  mdtools md2doc document.md
  mdtools md2doc document.md -o output.docx
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="转换命令")

    pdf2md_parser = subparsers.add_parser("pdf2md", help="PDF 转 Markdown")
    pdf2md_parser.add_argument("pdf_file", help="PDF 文件路径")
    pdf2md_parser.add_argument("-o", "--output", help="输出文件路径")

    md2pdf_parser = subparsers.add_parser("md2pdf", help="Markdown 转 PDF")
    md2pdf_parser.add_argument("md_file", help="Markdown 文件路径")
    md2pdf_parser.add_argument("-o", "--output", help="输出文件路径")
    md2pdf_parser.add_argument("--css", help="自定义 CSS 样式文件路径")

    md2doc_parser = subparsers.add_parser("md2doc", help="Markdown 转 Word")
    md2doc_parser.add_argument("md_file", help="Markdown 文件路径")
    md2doc_parser.add_argument("-o", "--output", help="输出文件路径")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    try:
        if args.command == "pdf2md":
            output_path = convert_pdf_to_md(args.pdf_file, args.output)
            print(f"✓ PDF 转 Markdown 成功：{output_path}")

        elif args.command == "md2pdf":
            output_path = convert_md_to_pdf(args.md_file, args.output, args.css)
            print(f"✓ Markdown 转 PDF 成功：{output_path}")

        elif args.command == "md2doc":
            output_path = convert_md_to_word(args.md_file, args.output)
            print(f"✓ Markdown 转 Word 成功：{output_path}")

    except Exception as e:
        print(f"✗ 转换失败：{e}", file=sys.stderr)
        sys.exit(1)


def main():
    if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] in ["--gui", "-g"]):
        run_gui()
    else:
        run_cli()


if __name__ == "__main__":
    main()
