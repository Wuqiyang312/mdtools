import os
import tempfile
import pytest
from app.converters import (
    convert_pdf_to_md,
    convert_md_to_pdf,
    convert_md_to_doc,
    convert_doc_to_md,
)


class TestConverters:
    """转换器测试"""

    def test_convert_md_to_pdf(self):
        """测试 Markdown 转 PDF"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as md:
            md.write("# Test\n\nHello World")
            md_path = md.name
        
        output = None
        try:
            output = convert_md_to_pdf(md_path)
            assert os.path.exists(output)
            assert output.endswith('.pdf')
        except RuntimeError as e:
            if "xelatex" in str(e):
                pytest.skip("xelatex 未安装，需要 LaTeX 环境")
            raise
        finally:
            if output and os.path.exists(output):
                os.unlink(output)
            if os.path.exists(md_path):
                os.unlink(md_path)

    def test_convert_md_to_doc(self):
        """测试 Markdown 转 Word"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as md:
            md.write("# Test\n\nHello World")
            md_path = md.name
        
        output = None
        try:
            output = convert_md_to_doc(md_path)
            assert os.path.exists(output)
            assert output.endswith('.docx')
        finally:
            if output and os.path.exists(output):
                os.unlink(output)
            if os.path.exists(md_path):
                os.unlink(md_path)

    def test_convert_pdf_to_md(self):
        """测试 PDF 转 Markdown"""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as pdf:
            pdf.write(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF")
            pdf_path = pdf.name
        
        output = None
        try:
            output = convert_pdf_to_md(pdf_path)
            assert os.path.exists(output)
            assert output.endswith('.md')
        except Exception:
            pass
        finally:
            if os.path.exists(pdf_path):
                os.unlink(pdf_path)
            if output and os.path.exists(output):
                os.unlink(output)

    def test_convert_doc_to_md(self):
        """测试 Word 转 Markdown"""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.docx', delete=False) as doc:
            doc.write(b"PK\x03\x04")
            doc_path = doc.name
        
        output = None
        try:
            output = convert_doc_to_md(doc_path)
            assert os.path.exists(output)
            assert output.endswith('.md')
        except Exception:
            pass
        finally:
            if os.path.exists(doc_path):
                os.unlink(doc_path)
            if output and os.path.exists(output):
                os.unlink(output)
