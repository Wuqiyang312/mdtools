#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档格式转换工具 - 统一入口
支持 PDF <-> Markdown <-> Word 之间的转换
"""

import os
import sys
import argparse
from pathlib import Path

from pdf2md import convert_pdf_to_md
from md2word import md_to_word
from md2pdf import md_to_pdf_reportlab


def run_cli():
    """命令行接口"""
    parser = argparse.ArgumentParser(
        description="文档格式转换工具 - 支持 PDF <-> Markdown <-> Word",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # PDF 转 Markdown
  python main.py pdf2md document.pdf
  python main.py pdf2md document.pdf -o output.md

  # Markdown 转 PDF
  python main.py md2pdf document.md
  python main.py md2pdf document.md -o output.pdf

  # Markdown 转 Word
  python main.py md2doc document.md
  python main.py md2doc document.md -o output.docx
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="转换命令")

    pdf2md_parser = subparsers.add_parser("pdf2md", help="PDF 转 Markdown")
    pdf2md_parser.add_argument("pdf_file", help="PDF 文件路径")
    pdf2md_parser.add_argument("-o", "--output", help="输出文件路径")

    md2pdf_parser = subparsers.add_parser("md2pdf", help="Markdown 转 PDF")
    md2pdf_parser.add_argument("md_file", help="Markdown 文件路径")
    md2pdf_parser.add_argument("-o", "--output", help="输出文件路径")

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
            print(f"[OK] PDF 转 Markdown 成功：{output_path}")

        elif args.command == "md2pdf":
            output_path = md_to_pdf_reportlab(args.md_file, args.output or os.path.splitext(args.md_file)[0] + ".pdf")
            print(f"[OK] Markdown 转 PDF 成功：{output_path}")

        elif args.command == "md2doc":
            output_path = md_to_word(args.md_file, args.output)
            print(f"[OK] Markdown 转 Word 成功：{output_path}")

    except Exception as e:
        print(f"[ERROR] 转换失败：{e}", file=sys.stderr)
        sys.exit(1)


def run_gui():
    """Tkinter GUI 接口"""
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
                    result = md_to_pdf_reportlab(
                        input_path, output_path if output_path else None
                    )
                elif self.convert_type == "md2doc":
                    result = md_to_word(
                        input_path, output_path if output_path else None
                    )
                else:
                    messagebox.showerror("错误", "未知的转换类型")
                    return

                self.status_label.config(text=f"[OK] 转换成功：{result}")
                messagebox.showinfo("成功", f"转换成功!\n{result}")

            except Exception as e:
                self.status_label.config(text=f"[ERROR] 转换失败：{e}", foreground="red")
                messagebox.showerror("失败", f"转换失败:\n{e}")

    root = tk.Tk()
    ConverterApp(root)
    root.mainloop()


def main():
    if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] in ["--gui", "-g"]):
        run_gui()
    else:
        run_cli()


if __name__ == "__main__":
    main()
