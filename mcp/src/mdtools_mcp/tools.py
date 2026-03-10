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
