import pytest
from pathlib import Path
import sys
import os

sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "mdtools_mcp"))

import converter


class TestPdfConversion:
    def test_pdf_not_exists(self):
        with pytest.raises(FileNotFoundError):
            converter.convert_pdf_to_md("/nonexistent/file.pdf")

    def test_pdf_to_text_not_exists(self):
        with pytest.raises(FileNotFoundError):
            converter.pdf_to_text("/nonexistent/file.pdf")


class TestMdConversion:
    def test_md_not_exists_word(self):
        with pytest.raises(FileNotFoundError):
            converter.convert_md_to_word("/nonexistent/file.md")
