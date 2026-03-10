#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import argparse
from markdown import Markdown
from markdown.extensions import tables, fenced_code
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem,
    Table, TableStyle, Image as RLImage
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.colors import Color
from xml.sax.saxutils import escape

def create_styles():
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    
    # 注册中文字体（需要字体文件存在）
    font_dir = r"C:\Windows\Fonts"
    try:
        pdfmetrics.registerFont(TTFont('SimSun', os.path.join(font_dir, 'simsun.ttc')))
        pdfmetrics.registerFont(TTFont('SimHei', os.path.join(font_dir, 'simhei.ttf')))
    except:
        pass
    
    styles = getSampleStyleSheet()
    base_font = "SimSun"
    heading_font = "SimHei"

    styles["Normal"].fontName = base_font
    styles["Normal"].fontSize = 12
    styles["Normal"].leading = 18
    styles["Normal"].alignment = TA_JUSTIFY
    styles["Normal"].spaceAfter = 6

    if "MyHeading1" not in styles:
        styles.add(ParagraphStyle(
            name="MyHeading1",
            parent=styles["Heading1"],
            fontName=heading_font,
            fontSize=18,
            spaceAfter=12,
            keepWithNext=True
        ))
    if "MyHeading2" not in styles:
        styles.add(ParagraphStyle(
            name="MyHeading2",
            parent=styles["Heading2"],
            fontName=heading_font,
            fontSize=16,
            spaceAfter=10,
            keepWithNext=True
        ))
    if "MyHeading3" not in styles:
        styles.add(ParagraphStyle(
            name="MyHeading3",
            parent=styles["Heading3"],
            fontName=heading_font,
            fontSize=14,
            spaceAfter=8,
            keepWithNext=True
        ))
    return styles

def md_to_pdf_reportlab(md_path, output_path):
    if not os.path.exists(md_path):
        raise FileNotFoundError(f"文件不存在：{md_path}")
    
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    md = Markdown(extensions=["tables", "fenced_code"])
    md.convert(md_text)

    from html.parser import HTMLParser

    class MDHTMLToReportLab(HTMLParser):
        def __init__(self):
            super().__init__()
            self.elements = []
            self.styles = create_styles()
            self.current_tag = None
            self.list_stack = []

        def handle_starttag(self, tag, attrs):
            self.current_tag = tag
            if tag == 'ul':
                self.list_stack.append([])
            elif tag == 'ol':
                self.list_stack.append([])
            elif tag in ('h1', 'h2', 'h3', 'p', 'li'):
                pass
            elif tag == 'img':
                src = dict(attrs).get('src')
                if src and os.path.exists(src):
                    try:
                        from PIL import Image as PILImage
                        with PILImage.open(src) as img:
                            width, height = img.size
                        max_width = 6 * inch
                        scale = min(max_width / width, 1.0)
                        img_width = width * scale
                        img_height = height * scale
                        rl_img = RLImage(src, width=img_width, height=img_height)
                        self.elements.append(rl_img)
                        self.elements.append(Spacer(1, 12))
                    except:
                        pass

        def handle_endtag(self, tag):
            if tag in ('ul', 'ol'):
                if self.list_stack:
                    items = self.list_stack.pop()
                    list_flow = ListFlowable(
                        items,
                        bulletType='bullet' if tag=='ul' else '1',
                        start='circle'
                    )
                    self.elements.append(list_flow)
                    self.elements.append(Spacer(1, 12))
            self.current_tag = None

        def handle_data(self, data):
            text = data.strip()
            if not text:
                return
            style_map = {'h1': 'MyHeading1', 'h2': 'MyHeading2', 'h3': 'MyHeading3', 'p': 'Normal'}
            if self.current_tag == 'li':
                if self.list_stack:
                    para = Paragraph(escape(text), self.styles['Normal'])
                    self.list_stack[-1].append(ListItem(para))
            elif self.current_tag in style_map:
                para = Paragraph(escape(text), self.styles[style_map[self.current_tag]])
                self.elements.append(para)
                self.elements.append(Spacer(1, 12))

    html_content = md.convert(md_text)
    parser = MDHTMLToReportLab()
    parser.feed(html_content)

    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            topMargin=0.75*inch, bottomMargin=0.75*inch,
                            leftMargin=1*inch, rightMargin=1*inch)
    doc.build(parser.elements)
    
    return output_path

def main():
    parser = argparse.ArgumentParser(description="Markdown 转 PDF（ReportLab 版，无浏览器依赖）")
    parser.add_argument("md_file", help="Markdown 文件路径")
    parser.add_argument("-o", "--output", help="输出 PDF 路径")
    args = parser.parse_args()

    output = args.output or (os.path.splitext(args.md_file)[0] + ".pdf")
    try:
        md_to_pdf_reportlab(args.md_file, output)
        print(f"[OK] Conversion successful: {output}")
    except Exception as e:
        print(f"[ERROR] Conversion failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
