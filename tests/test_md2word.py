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
        assert str(result_path).endswith(".docx")
        assert os.path.exists(result_path)
        assert os.path.getsize(result_path) > 0

    def test_convert_with_custom_output(self, sample_md_path, temp_dir):
        output_path = Path(temp_dir) / "custom.docx"
        result_path = md_to_word(sample_md_path, str(output_path))
        assert result_path == output_path
        assert os.path.exists(result_path)
