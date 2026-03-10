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
