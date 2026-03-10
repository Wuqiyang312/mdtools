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
