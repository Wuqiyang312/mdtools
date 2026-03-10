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
