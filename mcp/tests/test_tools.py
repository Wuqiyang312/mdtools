import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "mdtools_mcp"))

import tools


class TestToolDefinitions:
    def test_three_tools_defined(self):
        assert len(tools.TOOLS) == 3

    def test_tool_names(self):
        assert "pdf2md" in tools.TOOL_NAMES
        assert "md2pdf" in tools.TOOL_NAMES
        assert "md2doc" in tools.TOOL_NAMES

    def test_tool_has_required_attributes(self):
        for tool in tools.TOOLS:
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'description')
            assert hasattr(tool, 'inputSchema')
