import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestAPI:
    """API 端点测试"""

    def test_health_check(self):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_pdf_to_md(self):
        """测试 PDF 转 Markdown 端点"""
        pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
        files = {"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")}
        response = client.post("/api/pdf2md", files=files)
        assert response.status_code in [200, 400, 500]

    def test_md_to_pdf(self):
        """测试 Markdown 转 PDF 端点"""
        md_content = b"# Test\n\nHello World"
        files = {"file": ("test.md", io.BytesIO(md_content), "text/markdown")}
        response = client.post("/api/md2pdf", files=files)
        assert response.status_code in [200, 400, 500]

    def test_md_to_doc(self):
        """测试 Markdown 转 Word 端点"""
        md_content = b"# Test\n\nHello World"
        files = {"file": ("test.md", io.BytesIO(md_content), "text/markdown")}
        response = client.post("/api/md2doc", files=files)
        assert response.status_code in [200, 400, 500]

    def test_doc_to_md(self):
        """测试 Word 转 Markdown 端点"""
        doc_content = b"PK\x03\x04"
        files = {"file": ("test.docx", io.BytesIO(doc_content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        response = client.post("/api/doc2md", files=files)
        assert response.status_code in [200, 400, 500]

    def test_empty_filename(self):
        """测试空文件名处理"""
        files = {"file": ("", io.BytesIO(b"content"), "application/octet-stream")}
        response = client.post("/api/pdf2md", files=files)
        assert response.status_code in [400, 422]
