# MDTools 完善实施计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 完善 MDTools 项目的代码质量、MCP 服务器功能和 Web 服务器功能，添加测试用例、文档和必要的功能增强。

**Architecture:** 本计划分为三个独立的子系统，每个子系统可独立测试和验证：
1. 核心代码库 - 文档转换核心逻辑和 CLI/GUI 入口
2. MCP Server - Model Context Protocol 服务器，提供 AI 助手集成接口
3. Web Server - HTTP 服务，提供 REST API 和 Web 界面

**Tech Stack:** Python 3.12+, pytest, MCP SDK, python-docx, pdfplumber, weasyprint/markdown, ReportLab

---

## 文件结构概览

### 核心代码库
- `main.py` - 统一入口 (CLI + GUI)
- `pdf2md.py` - PDF 转 Markdown
- `md2pdf.py` - Markdown 转 PDF (ReportLab 版)
- `md2word.py` - Markdown 转 Word
- `tests/` - 测试目录 (新建)
  - `test_pdf2md.py`
  - `test_md2pdf.py`
  - `test_md2word.py`
  - `test_main.py`

### MCP Server
- `mcp/src/mdtools_mcp/__init__.py` - MCP 服务器主逻辑
- `mcp/src/mdtools_mcp/tools.py` - 工具定义 (新建)
- `mcp/src/mdtools_mcp/converter.py` - 转换逻辑封装 (新建)
- `mcp/tests/test_mcp.py` - MCP 测试 (新建)
- `mcp/README.md` - MCP 文档 (完善)

### Web Server
- `server/server.py` - HTTP 服务器
- `server/handlers/` - 请求处理器 (新建)
  - `__init__.py`
  - `convert_handler.py`
  - `health_handler.py`
- `server/middleware/` - 中间件 (新建)
  - `__init__.py`
  - `cors.py`
  - `logging.py`
- `server/tests/test_server.py` - 服务器测试 (新建)
- `server/README.md` - 服务器文档 (完善)

---

## Chunk 1: 核心代码库完善

### Task 1: 创建测试目录结构

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `tests/fixtures/sample.md`
- Create: `tests/fixtures/sample.txt` (用于模拟 PDF 内容)

- [ ] **Step 1: 创建 tests 目录和配置文件**

```bash
mkdir -p tests/fixtures
```

- [ ] **Step 2: 创建测试配置文件**

```python
# tests/conftest.py
import pytest
import os
import tempfile
from pathlib import Path

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def sample_md_path(temp_dir):
    md_path = Path(temp_dir) / "sample.md"
    content = """# 测试文档

这是**粗体**和*斜体*测试。

## 列表测试

- 项目 1
- 项目 2
- 项目 3

## 代码块

```python
print("Hello World")
```

## 表格

| 姓名 | 年龄 | 城市 |
|------|------|------|
| 张三 | 25   | 北京 |
| 李四 | 30   | 上海 |
"""
    md_path.write_text(content, encoding="utf-8")
    return str(md_path)

@pytest.fixture
def sample_pdf_path(temp_dir):
    # 创建模拟 PDF 文本内容（实际测试需要真实 PDF）
    txt_path = Path(temp_dir) / "sample.txt"
    txt_path.write_text("测试 PDF 内容\n第二页内容", encoding="utf-8")
    return str(txt_path)
```

- [ ] **Step 3: 创建示例 Markdown 文件**

```markdown
# tests/fixtures/sample.md

# 示例文档

这是一个示例 Markdown 文档，用于测试转换功能。

## 特性列表

- 支持中文
- 支持代码块
- 支持表格

## 代码示例

```python
def hello():
    print("Hello, World!")
```
```

- [ ] **Step 4: 提交**

```bash
git add tests/
git commit -m "test: add test infrastructure and fixtures"
```

### Task 2: PDF 转 Markdown 测试

**Files:**
- Create: `tests/test_pdf2md.py`

- [ ] **Step 1: 编写 PDF 转 Markdown 测试**

```python
# tests/test_pdf2md.py
import pytest
import os
from pathlib import Path
from pdf2md import convert_pdf_to_md, pdf_to_text


class TestPdfToText:
    def test_pdf_not_exists(self, temp_dir):
        with pytest.raises(FileNotFoundError):
            pdf_to_text("/nonexistent/file.pdf")

    def test_extract_text_from_pdf(self, sample_pdf_path):
        # 注意：实际测试需要真实 PDF 文件
        # 这里测试文本文件以验证基本逻辑
        text = pdf_to_text(sample_pdf_path)
        assert isinstance(text, str)


class TestConvertPdfToMd:
    def test_pdf_not_exists(self, temp_dir):
        with pytest.raises(FileNotFoundError):
            convert_pdf_to_md("/nonexistent/file.pdf")

    def test_convert_with_default_output(self, sample_pdf_path, temp_dir):
        # 测试自动生成输出文件名
        result_path = convert_pdf_to_md(sample_pdf_path)
        assert result_path.endswith(".md")
        assert os.path.exists(result_path)

    def test_convert_with_custom_output(self, sample_pdf_path, temp_dir):
        output_path = Path(temp_dir) / "custom.md"
        result_path = convert_pdf_to_md(sample_pdf_path, str(output_path))
        assert result_path == str(output_path)
        assert os.path.exists(result_path)

    def test_output_content_contains_header(self, sample_pdf_path, temp_dir):
        output_path = Path(temp_dir) / "output.md"
        convert_pdf_to_md(sample_pdf_path, str(output_path))
        content = Path(output_path).read_text(encoding="utf-8")
        assert "# " in content
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/test_pdf2md.py -v
# Expected: Tests pass (如果 pdf2md.py 正常工作)
```

- [ ] **Step 3: 提交**

```bash
git add tests/test_pdf2md.py
git commit -m "test: add pdf2md tests"
```

### Task 3: Markdown 转 PDF 测试

**Files:**
- Create: `tests/test_md2pdf.py`

- [ ] **Step 1: 编写 Markdown 转 PDF 测试**

```python
# tests/test_md2pdf.py
import pytest
import os
from pathlib import Path
from md2pdf import md_to_pdf_reportlab


class TestMdToPdfReportLab:
    def test_md_not_exists(self, temp_dir):
        with pytest.raises(FileNotFoundError):
            md_to_pdf_reportlab("/nonexistent/file.md", str(Path(temp_dir) / "output.pdf"))

    def test_convert_with_default_output(self, sample_md_path, temp_dir):
        output_path = Path(temp_dir) / "output.pdf"
        result_path = md_to_pdf_reportlab(sample_md_path, str(output_path))
        assert result_path == str(output_path)
        assert os.path.exists(result_path)
        assert os.path.getsize(result_path) > 0

    def test_convert_with_custom_output(self, sample_md_path, temp_dir):
        output_path = Path(temp_dir) / "custom.pdf"
        result_path = md_to_pdf_reportlab(sample_md_path, str(output_path))
        assert result_path == str(output_path)
        assert os.path.exists(result_path)
```

- [ ] **Step 2: 运行测试**

```bash
pytest tests/test_md2pdf.py -v
```

- [ ] **Step 3: 提交**

```bash
git add tests/test_md2pdf.py
git commit -m "test: add md2pdf tests"
```

### Task 4: Markdown 转 Word 测试

**Files:**
- Create: `tests/test_md2word.py`

- [ ] **Step 1: 编写 Markdown 转 Word 测试**

```python
# tests/test_md2word.py
import pytest
import os
from pathlib import Path
from md2word import md_to_word


class TestMdToWord:
    def test_md_not_exists(self, temp_dir):
        with pytest.raises(FileNotFoundError):
            md_to_word("/nonexistent/file.md")

    def test_convert_with_default_output(self, sample_md_path, temp_dir):
        result_path = md_to_word(sample_md_path)
        assert result_path.endswith(".docx")
        assert os.path.exists(result_path)
        assert os.path.getsize(result_path) > 0

    def test_convert_with_custom_output(self, sample_md_path, temp_dir):
        output_path = Path(temp_dir) / "custom.docx"
        result_path = md_to_word(sample_md_path, str(output_path))
        assert result_path == str(output_path)
        assert os.path.exists(result_path)
```

- [ ] **Step 2: 运行测试**

```bash
pytest tests/test_md2word.py -v
```

- [ ] **Step 3: 提交**

```bash
git add tests/test_md2word.py
git commit -m "test: add md2word tests"
```

### Task 5: 主入口测试

**Files:**
- Create: `tests/test_main.py`

- [ ] **Step 1: 编写主入口 CLI 测试**

```python
# tests/test_main.py
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
        assert result.returncode == 0
        assert "文档格式转换工具" in result.stdout
```

- [ ] **Step 2: 运行测试**

```bash
pytest tests/test_main.py -v
```

- [ ] **Step 3: 提交**

```bash
git add tests/test_main.py
git commit -m "test: add CLI interface tests"
```

### Task 6: 添加 Pytest 配置

**Files:**
- Create: `pytest.ini`
- Modify: `requirements.txt`

- [ ] **Step 1: 创建 pytest 配置文件**

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
```

- [ ] **Step 2: 更新 requirements.txt 添加测试依赖**

```txt
# requirements.txt
markdown>=3.4
weasyprint>=59.0
python-docx>=1.1.0
pdfplumber>=0.10.0
reportlab>=4.0.0
Pillow>=10.0.0

# Test dependencies
pytest>=8.0.0
pytest-cov>=4.0.0
```

- [ ] **Step 3: 运行完整测试套件**

```bash
pip install -r requirements.txt
pytest --cov=. --cov-report=term-missing
```

- [ ] **Step 4: 提交**

```bash
git add pytest.ini requirements.txt
git commit -m "chore: add pytest configuration and test dependencies"
```

---

## Chunk 2: MCP Server 完善

### Task 7: 重构 MCP 服务器结构

**Files:**
- Create: `mcp/src/mdtools_mcp/converter.py`
- Create: `mcp/src/mdtools_mcp/tools.py`
- Modify: `mcp/src/mdtools_mcp/__init__.py`

- [ ] **Step 1: 创建转换器封装模块**

```python
# mcp/src/mdtools_mcp/converter.py
"""文档转换核心逻辑封装"""

import os
from pathlib import Path
from typing import Optional

import pdfplumber
import markdown
from weasyprint import HTML, CSS


def pdf_to_text(pdf_path: str) -> str:
    """从 PDF 提取文本内容"""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"文件不存在：{pdf_path}")
    
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


def convert_pdf_to_md(pdf_path: str, output_path: Optional[str] = None) -> str:
    """将 PDF 转换为 Markdown"""
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
    """获取中文 PDF 样式"""
    return """
    @page {
        size: A4;
        margin: 2.5cm 2cm;
    }
    
    body {
        font-family: "Noto Serif CJK SC", "Source Han Serif CN", "SimSun", serif;
        font-size: 12pt;
        line-height: 1.8;
        text-align: justify;
        color: #333;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: "Noto Sans CJK SC", "Source Han Sans CN", "SimHei", serif;
        margin-top: 1.5em;
        margin-bottom: 0.8em;
        page-break-after: avoid;
    }
    
    h1 { font-size: 18pt; border-bottom: 2px solid #333; padding-bottom: 0.3em; }
    h2 { font-size: 16pt; border-bottom: 1px solid #ddd; padding-bottom: 0.3em; }
    h3 { font-size: 14pt; }
    
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
    """


def md_to_html(md_path: str) -> str:
    """将 Markdown 转换为 HTML"""
    if not os.path.exists(md_path):
        raise FileNotFoundError(f"文件不存在：{md_path}")
    
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()
    
    html_content = markdown.markdown(
        md_content, 
        extensions=["tables", "toc", "fenced_code", "codehilite"]
    )
    
    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{os.path.basename(md_path)}</title>
</head>
<body>
{html_content}
</body>
</html>"""
    
    return full_html


def convert_md_to_pdf(
    md_path: str, 
    output_path: Optional[str] = None,
    css_path: Optional[str] = None
) -> str:
    """将 Markdown 转换为 PDF"""
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


def convert_md_to_word(md_path: str, output_path: Optional[str] = None) -> str:
    """将 Markdown 转换为 Word"""
    if not os.path.exists(md_path):
        raise FileNotFoundError(f"文件不存在：{md_path}")
    
    if output_path is None:
        base_name = os.path.splitext(md_path)[0]
        output_path = f"{base_name}.docx"
    
    # 使用主项目的 md2word 函数
    from docx import Document
    from docx.shared import Pt, Cm
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    import re
    
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()
    
    doc = Document()
    
    def set_font_style(paragraph, font_name="微软雅黑", font_size=12):
        for run in paragraph.runs:
            run.font.name = font_name
            run.font.size = Pt(font_size)
            rPr = run._element.get_or_add_rPr()
            rFonts = OxmlElement("w:rFonts")
            rFonts.set(qn("w:eastAsia"), font_name)
            rPr.insert(0, rFonts)
    
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
            p.italic = True
        
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
                p.style.font.name = "Courier New"
                p.paragraph_format.left_indent = Cm(0.5)
        
        elif line.strip() == "":
            flush_paragraph()
        
        else:
            current_paragraph.append(line)
        
        i += 1
    
    flush_paragraph()
    doc.save(output_path)
    return output_path
```

- [ ] **Step 2: 创建工具定义模块**

```python
# mcp/src/mdtools_mcp/tools.py
"""MCP 工具定义"""

import mcp.types as types

TOOLS = [
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
                    "description": "输出 Markdown 文件路径（可选）",
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
                    "description": "输出 PDF 文件路径（可选）",
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
                    "description": "输出 Word 文件路径（可选）",
                },
            },
            "required": ["md_path"],
        },
    ),
]

TOOL_NAMES = {tool.name for tool in TOOLS}
```

- [ ] **Step 3: 重构 __init__.py**

```python
# mcp/src/mdtools_mcp/__init__.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档格式转换工具 MCP Server
支持 PDF <-> Markdown <-> Word 之间的转换
"""

from .converter import (
    convert_pdf_to_md,
    convert_md_to_pdf,
    convert_md_to_word,
)
from .tools import TOOLS, TOOL_NAMES
import mcp.types as types


async def create_server():
    """创建并配置 MCP 服务器"""
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    
    server = Server("mdtools")
    
    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return TOOLS
    
    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        if name not in TOOL_NAMES:
            raise ValueError(f"未知工具：{name}")
        
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
        
        raise ValueError(f"未知工具：{name}")
    
    return server, stdio_server


async def main():
    """MCP 服务器入口"""
    server, stdio_server = await create_server()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main_sync():
    """同步入口"""
    import asyncio
    asyncio.run(main())


if __name__ == "__main__":
    main_sync()
```

- [ ] **Step 4: 验证模块导入**

```bash
cd mcp
python -c "from src.mdtools_mcp import converter, tools; print('OK')"
```

- [ ] **Step 5: 提交**

```bash
git add mcp/src/mdtools_mcp/
git commit -m "refactor(mcp): split into converter and tools modules"
```

### Task 8: 添加 MCP 测试

**Files:**
- Create: `mcp/tests/__init__.py`
- Create: `mcp/tests/test_converter.py`
- Create: `mcp/tests/test_tools.py`

- [ ] **Step 1: 创建 MCP 测试目录**

```bash
mkdir -p mcp/tests
```

- [ ] **Step 2: 创建转换器测试**

```python
# mcp/tests/test_converter.py
import pytest
from pathlib import Path
from src.mdtools_mcp.converter import (
    convert_pdf_to_md,
    convert_md_to_pdf,
    convert_md_to_word,
    pdf_to_text,
)


class TestPdfConversion:
    def test_pdf_not_exists(self):
        with pytest.raises(FileNotFoundError):
            convert_pdf_to_md("/nonexistent/file.pdf")

    def test_pdf_to_text_not_exists(self):
        with pytest.raises(FileNotFoundError):
            pdf_to_text("/nonexistent/file.pdf")


class TestMdConversion:
    def test_md_not_exists_pdf(self, temp_dir):
        with pytest.raises(FileNotFoundError):
            convert_md_to_pdf("/nonexistent/file.md", str(Path(temp_dir) / "output.pdf"))

    def test_md_not_exists_word(self):
        with pytest.raises(FileNotFoundError):
            convert_md_to_word("/nonexistent/file.md")
```

- [ ] **Step 3: 创建工具定义测试**

```python
# mcp/tests/test_tools.py
from src.mdtools_mcp.tools import TOOLS, TOOL_NAMES


class TestToolDefinitions:
    def test_three_tools_defined(self):
        assert len(TOOLS) == 3

    def test_tool_names(self):
        assert "pdf2md" in TOOL_NAMES
        assert "md2pdf" in TOOL_NAMES
        assert "md2doc" in TOOL_NAMES

    def test_tool_has_required_attributes(self):
        for tool in TOOLS:
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'description')
            assert hasattr(tool, 'inputSchema')
```

- [ ] **Step 4: 提交**

```bash
git add mcp/tests/
git commit -m "test(mcp): add converter and tools tests"
```

### Task 9: 完善 MCP README 文档

**Files:**
- Modify: `mcp/README.md`

- [ ] **Step 1: 编写完整的 README 文档**

```markdown
# MDTools MCP Server

文档格式转换工具的 MCP (Model Context Protocol) 服务器实现，支持 AI 助手通过 MCP 协议调用文档转换功能。

## 功能特性

- **pdf2md**: PDF 转 Markdown
- **md2pdf**: Markdown 转 PDF（支持中文）
- **md2doc**: Markdown 转 Word

## 安装

```bash
# 使用 uv
cd mcp
uv sync

# 或使用 pip
pip install -e .
```

## 配置

在 Claude Desktop 配置中添加：

```json
{
  "mcpServers": {
    "mdtools": {
      "command": "python",
      "args": ["-m", "mdtools_mcp"],
      "cwd": "/path/to/mdtools/mcp"
    }
  }
}
```

## 使用方法

### 在 Claude Desktop 中使用

安装配置后，可以在对话中直接使用：

- "将这个 PDF 转换为 Markdown"
- "把这个文档转成 PDF"
- "生成 Word 文档"

### 编程使用

```python
from mcp.server import Server
from mdtools_mcp import create_server

server, stdio_server = await create_server()
```

## 开发

```bash
# 运行测试
pytest

# 类型检查
mypy src/

# 代码格式化
ruff format src/
```

## API 参考

### pdf2md

将 PDF 文件转换为 Markdown 格式。

**参数:**
- `pdf_path` (必需): PDF 文件路径
- `output_path` (可选): 输出 Markdown 文件路径

### md2pdf

将 Markdown 文件转换为 PDF 格式。

**参数:**
- `md_path` (必需): Markdown 文件路径
- `output_path` (可选): 输出 PDF 文件路径
- `css_path` (可选): 自定义 CSS 样式文件路径

### md2doc

将 Markdown 文件转换为 Word 格式。

**参数:**
- `md_path` (必需): Markdown 文件路径
- `output_path` (可选): 输出 Word 文件路径
```

- [ ] **Step 2: 提交**

```bash
git add mcp/README.md
git commit -m "docs(mcp): add comprehensive README"
```

---

## Chunk 3: Web Server 完善

### Task 10: 重构服务器结构

**Files:**
- Create: `server/handlers/__init__.py`
- Create: `server/handlers/convert_handler.py`
- Create: `server/handlers/health_handler.py`
- Create: `server/middleware/__init__.py`
- Create: `server/middleware/cors.py`
- Create: `server/middleware/logging.py`

- [ ] **Step 1: 创建处理器目录结构**

```bash
mkdir -p server/handlers server/middleware
```

- [ ] **Step 2: 创建 CORS 中间件**

```python
# server/middleware/cors.py
"""CORS 中间件"""


class CORSMiddleware:
    """处理跨域请求"""
    
    ALLOWED_ORIGINS = ["*"]
    ALLOWED_METHODS = ["GET", "POST", "OPTIONS"]
    ALLOWED_HEADERS = ["Content-Type", "Authorization"]
    
    @staticmethod
    def add_cors_headers(handler):
        """添加 CORS 头到响应"""
        def wrapper(self, *args, **kwargs):
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", ", ".join(CORSMiddleware.ALLOWED_METHODS))
            self.send_header("Access-Control-Allow-Headers", ", ".join(CORSMiddleware.ALLOWED_HEADERS))
            return handler(self, *args, **kwargs)
        return wrapper
```

- [ ] **Step 3: 创建日志中间件**

```python
# server/middleware/logging.py
"""日志中间件"""

import logging
from datetime import datetime

logger = logging.getLogger("mdtools.server")


class RequestLogger:
    """记录请求日志"""
    
    @staticmethod
    def log_request(handler, status_code=None):
        """记录 HTTP 请求日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        method = handler.command
        path = handler.path
        client = handler.client_address[0] if hasattr(handler, 'client_address') else 'unknown'
        
        log_msg = f"[{timestamp}] {client} {method} {path}"
        if status_code:
            log_msg += f" {status_code}"
        
        logger.info(log_msg)
        print(log_msg)  # 同时输出到控制台
```

- [ ] **Step 4: 创建健康检查处理器**

```python
# server/handlers/health_handler.py
"""健康检查处理器"""

import json


class HealthHandler:
    """处理健康检查请求"""
    
    @staticmethod
    def handle(handler):
        """处理 GET /health 请求"""
        handler.send_response(200)
        handler.send_header("Content-Type", "application/json")
        handler.send_header("Access-Control-Allow-Origin", "*")
        handler.end_headers()
        handler.wfile.write(json.dumps({"status": "healthy"}).encode())
```

- [ ] **Step 5: 创建转换处理器**

```python
# server/handlers/convert_handler.py
"""文件转换处理器"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConvertHandler:
    """处理文件转换请求"""
    
    SCRIPT_DIR = Path(__file__).parent.parent.parent
    UPLOAD_DIR = SCRIPT_DIR / "uploads"
    
    SUPPORTED_FORMATS = {
        "md2pdf": "md2pdf.py",
        "md2word": "md2word.py",
        "pdf2md": "pdf2md.py",
    }
    
    @classmethod
    def handle_json_request(cls, handler, request_data: Dict[str, Any]):
        """处理 JSON 格式请求"""
        try:
            input_path = request_data.get("input_path")
            output_path = request_data.get("output_path")
            format_type = request_data.get("format")
            
            if not input_path or not format_type:
                cls._send_error(handler, 400, "input_path and format are required")
                return
            
            result_path = cls._run_conversion(handler, input_path, output_path, format_type)
            cls._send_success(handler, result_path)
            
        except Exception as e:
            cls._send_error(handler, 500, str(e))
    
    @classmethod
    def handle_file_upload(cls, handler, file_data: bytes, file_name: str, format_type: str):
        """处理文件上传"""
        try:
            cls.UPLOAD_DIR.mkdir(exist_ok=True)
            input_path = cls.UPLOAD_DIR / file_name
            
            with open(input_path, "wb") as f:
                f.write(file_data)
            
            result_path = cls._run_conversion(handler, str(input_path), "", format_type)
            cls._send_success(handler, result_path)
            
        except Exception as e:
            cls._send_error(handler, 500, str(e))
    
    @classmethod
    def _run_conversion(cls, handler, input_path: str, output_path: str, format_type: str) -> str:
        """执行转换"""
        import subprocess
        import sys
        
        if format_type not in cls.SUPPORTED_FORMATS:
            raise ValueError(f"不支持的格式：{format_type}")
        
        script = cls.SCRIPT_DIR / cls.SUPPORTED_FORMATS[format_type]
        if not script.exists():
            raise FileNotFoundError(f"脚本不存在：{script}")
        
        args = [sys.executable, str(script), input_path]
        
        if output_path:
            args.extend(["-o", output_path])
        
        result = subprocess.run(args, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"转换失败：{result.stderr or result.stdout}")
        
        if not output_path:
            base_name = os.path.splitext(input_path)[0]
            extensions = {"md2pdf": ".pdf", "md2word": ".docx", "pdf2md": ".md"}
            output_path = base_name + extensions[format_type]
        
        return output_path
    
    @staticmethod
    def _send_success(handler, output_path: str):
        """发送成功响应"""
        handler.send_response(200)
        handler.send_header("Content-Type", "application/json")
        handler.send_header("Access-Control-Allow-Origin", "*")
        handler.end_headers()
        handler.wfile.write(json.dumps({
            "success": True,
            "message": "Conversion successful",
            "output_path": output_path,
        }).encode())
    
    @staticmethod
    def _send_error(handler, status: int, error: str):
        """发送错误响应"""
        handler.send_response(status)
        handler.send_header("Content-Type", "application/json")
        handler.send_header("Access-Control-Allow-Origin", "*")
        handler.end_headers()
        handler.wfile.write(json.dumps({
            "success": False,
            "error": error,
        }).encode())
```

- [ ] **Step 6: 提交**

```bash
git add server/handlers/ server/middleware/
git commit -m "refactor(server): create handlers and middleware modules"
```

### Task 11: 重构主服务器文件

**Files:**
- Modify: `server/server.py`

- [ ] **Step 1: 重构 server.py 使用新的处理器**

```python
# server/server.py 重构后的关键部分
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MDTools Web Server
Markdown 转换工具的 Web 服务接口
"""

import os
import sys
import argparse
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

from handlers import HealthHandler, ConvertHandler
from middleware import CORSMiddleware, RequestLogger


SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent


class ConvertHandler(BaseHTTPRequestHandler):
    """HTTP 请求处理器"""
    
    @CORSMiddleware.add_cors_headers
    def do_OPTIONS(self):
        """处理 CORS 预检请求"""
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        """处理 GET 请求"""
        RequestLogger.log_request(self)
        
        if self.path == "/health":
            HealthHandler.handle(self)
        elif self.path == "/" or self.path == "/index.html":
            self._serve_html_page()
        else:
            self._send_404()
    
    def do_POST(self):
        """处理 POST 请求"""
        RequestLogger.log_request(self)
        
        if self.path == "/convert":
            content_type = self.headers.get("Content-Type", "")
            
            if "application/json" in content_type:
                self._handle_json_request()
            elif "multipart/form-data" in content_type:
                self._handle_file_upload()
            else:
                ConvertHandler._send_error(self, 400, "Unsupported content type")
        else:
            self._send_404()
    
    def _handle_json_request(self):
        """处理 JSON 请求"""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        
        try:
            request_data = json.loads(body)
            ConvertHandler.handle_json_request(self, request_data)
        except json.JSONDecodeError as e:
            ConvertHandler._send_error(self, 400, f"Invalid JSON: {e}")
    
    def _handle_file_upload(self):
        """处理文件上传"""
        # 解析 multipart/form-data
        content_type = self.headers.get("Content-Type", "")
        boundary = content_type.split("boundary=")[1].strip() if "boundary=" in content_type else None
        
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
                            file_data = part[header_end + 4:].rstrip(b"\r\n-")
                
                if b'name="format"' in part:
                    header_end = part.find(b"\r\n\r\n")
                    if header_end != -1:
                        format_type = part[header_end + 4:].rstrip(b"\r\n-").decode("utf-8").strip()
        
        if file_data and file_name and format_type:
            ConvertHandler.handle_file_upload(self, file_data, file_name, format_type)
        else:
            ConvertHandler._send_error(self, 400, "Missing file or format")
    
    def _serve_html_page(self):
        """服务 HTML 页面"""
        html_page = """<!DOCTYPE html>..."""  # 保持原有 HTML
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(html_page.encode("utf-8"))
    
    def _send_404(self):
        """发送 404 响应"""
        self.send_response(404)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        RequestLogger.log_request(self)
```

- [ ] **Step 2: 验证导入**

```bash
cd server
python -c "from handlers import HealthHandler, ConvertHandler; print('OK')"
```

- [ ] **Step 3: 提交**

```bash
git add server/server.py
git commit -m "refactor(server): use handlers and middleware"
```

### Task 12: 添加服务器测试

**Files:**
- Create: `server/tests/__init__.py`
- Create: `server/tests/test_server.py`

- [ ] **Step 1: 创建服务器测试**

```python
# server/tests/test_server.py
import pytest
import json
from unittest.mock import Mock, MagicMock
from handlers.health_handler import HealthHandler
from handlers.convert_handler import ConvertHandler


class TestHealthHandler:
    def test_health_response(self):
        mock_handler = Mock()
        mock_handler.wfile = Mock()
        
        HealthHandler.handle(mock_handler)
        
        assert mock_handler.send_response.called
        assert mock_handler.send_response.call_args[0][0] == 200
        
        response_data = json.loads(mock_handler.wfile.write.call_args[0][0].decode())
        assert response_data["status"] == "healthy"


class TestConvertHandler:
    def test_error_response(self):
        mock_handler = Mock()
        mock_handler.wfile = Mock()
        
        ConvertHandler._send_error(mock_handler, 400, "Test error")
        
        assert mock_handler.send_response.called
        assert mock_handler.send_response.call_args[0][0] == 400
        
        response_data = json.loads(mock_handler.wfile.write.call_args[0][0].decode())
        assert response_data["success"] is False
        assert response_data["error"] == "Test error"
    
    def test_success_response(self, temp_dir):
        mock_handler = Mock()
        mock_handler.wfile = Mock()
        
        output_path = f"{temp_dir}/output.pdf"
        ConvertHandler._send_success(mock_handler, output_path)
        
        assert mock_handler.send_response.called
        assert mock_handler.send_response.call_args[0][0] == 200
        
        response_data = json.loads(mock_handler.wfile.write.call_args[0][0].decode())
        assert response_data["success"] is True
        assert response_data["output_path"] == output_path
```

- [ ] **Step 2: 提交**

```bash
git add server/tests/
git commit -m "test(server): add handler tests"
```

### Task 13: 完善服务器 README 文档

**Files:**
- Modify: `server/README.md`

- [ ] **Step 1: 更新 README 文档**

```markdown
# MDTools Server

文档格式转换工具的 Web 服务接口，提供 REST API 和 Web 界面。

## 功能特性

- **Web 界面**: 直观的网页界面进行文件转换
- **REST API**: JSON API 和文件上传两种方式
- **CORS 支持**: 允许跨域请求
- **请求日志**: 记录所有 HTTP 请求

## 启动服务

```bash
# 使用默认端口 (8080)
cd server
python server.py

# 自定义端口
python server.py --port 3000

# 指定监听地址
python server.py --host 127.0.0.1 --port 8080
```

## Web 界面

访问 `http://localhost:8080/` 可使用网页界面进行文件转换。

## API 接口

### POST /convert

支持两种请求方式：

**1. JSON 请求:**
```bash
curl -X POST http://localhost:8080/convert \
  -H "Content-Type: application/json" \
  -d '{"input_path": "document.md", "format": "md2pdf"}'
```

**2. 表单上传:**
```bash
curl -X POST http://localhost:8080/convert \
  -F "file=@document.md" \
  -F "format=md2pdf"
```

**参数:**
- `input_path` / `file` (必需): 输入文件路径或上传的文件
- `output_path` (可选): 输出文件路径
- `format` (必需): 转换格式 (md2pdf, md2word, pdf2md)

**响应:**
```json
{
  "success": true,
  "message": "Conversion successful",
  "output_path": "document.pdf"
}
```

### GET /health

健康检查

```bash
curl http://localhost:8080/health
```

**响应:**
```json
{
  "status": "healthy"
}
```

## 开发

```bash
# 运行测试
pytest server/tests/

# 代码格式化
ruff format server/
```

## Docker 部署

```bash
cd server/docker

# 构建镜像
./build.sh

# 使用 docker-compose
./run.sh

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```
```

- [ ] **Step 2: 提交**

```bash
git add server/README.md
git commit -m "docs(server): update README with comprehensive documentation"
```

---

## Chunk 4: 文档和工具完善

### Task 14: 添加项目根目录 README

**Files:**
- Create: `README.md`

- [ ] **Step 1: 创建项目根目录 README**

```markdown
# MDTools

文档格式转换工具 - 支持 PDF <-> Markdown <-> Word 之间的相互转换

## 功能特性

- **PDF 转 Markdown**: 提取 PDF 内容并转换为 Markdown 格式，支持表格
- **Markdown 转 PDF**: 将 Markdown 转换为美观的 PDF 文档，支持中文
- **Markdown 转 Word**: 将 Markdown 转换为 Word 文档，支持中文格式

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 命令行使用

```bash
# PDF 转 Markdown
python main.py pdf2md document.pdf

# Markdown 转 PDF
python main.py md2pdf document.md

# Markdown 转 Word
python main.py md2doc document.md
```

### GUI 界面

```bash
python main.py
# 或
python main.py --gui
```

### Web 服务

```bash
cd server
python server.py --port 8080
```

访问 http://localhost:8080/

### MCP 服务器

```bash
cd mcp
uv sync
python -m mdtools_mcp
```

## 子项目

- **核心工具**: `main.py`, `pdf2md.py`, `md2pdf.py`, `md2word.py`
- **MCP Server**: `mcp/` - Model Context Protocol 集成
- **Web Server**: `server/` - HTTP REST API

## 开发

```bash
# 运行测试
pytest

# 代码格式化
ruff format .

# 类型检查
mypy .
```

## 打包

```bash
pyinstaller mdtools.spec
```

## 许可证

MIT License
```

- [ ] **Step 2: 提交**

```bash
git add README.md
git commit -m "docs: add project root README"
```

### Task 15: 添加预提交钩子配置

**Files:**
- Create: `.pre-commit-config.yaml`

- [ ] **Step 1: 创建 pre-commit 配置**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.14
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies:
          - types-all
```

- [ ] **Step 2: 提交**

```bash
git add .pre-commit-config.yaml
git commit -m "chore: add pre-commit configuration"
```

---

## 执行检查清单

完成所有任务后，运行以下验证：

```bash
# 1. 运行所有测试
pytest -v

# 2. 测试 CLI
python main.py --help
python main.py pdf2md --help

# 3. 测试 MCP 导入
cd mcp && python -c "from src.mdtools_mcp import main; print('MCP OK')"

# 4. 测试 Server 导入
cd server && python -c "from handlers import HealthHandler; print('Server OK')"

# 5. 检查代码质量
ruff check .
mypy .
```

---

## 审查循环

每个 Chunk 完成后：

1. 运行 `plan-document-reviewer` 子代理审查当前 Chunk
2. 如果发现问题，修复后重新审查
3. 审查通过后继续下一个 Chunk

---

计划完成后保存到：`docs/superpowers/plans/2026-03-10-mdtools-improvements.md`
