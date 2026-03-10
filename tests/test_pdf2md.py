import pytest
import os
from pathlib import Path
from pdf2md import convert_pdf_to_md, pdf_to_text


class TestPdfToText:
    def test_pdf_not_exists(self, temp_dir):
        with pytest.raises(FileNotFoundError):
            pdf_to_text("/nonexistent/file.pdf")

    def test_extract_text_from_pdf(self, sample_pdf_path):
        text = pdf_to_text(sample_pdf_path)
        assert isinstance(text, str)


class TestConvertPdfToMd:
    def test_pdf_not_exists(self, temp_dir):
        with pytest.raises(FileNotFoundError):
            convert_pdf_to_md("/nonexistent/file.pdf")

    def test_convert_with_default_output(self, sample_pdf_path, temp_dir):
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
