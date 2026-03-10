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
pip install -e .
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
