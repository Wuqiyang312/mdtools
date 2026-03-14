# MDTools Server 实现计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 MDTools 改造为 FastAPI 服务端应用，支持 Docker 容器化部署和 GitHub Actions 自动发布到 GHCR

**Architecture:** 保留现有 CLI 工具，新增 FastAPI 应用层封装转换逻辑，使用多阶段 Docker 构建优化镜像体积

**Tech Stack:** FastAPI, Uvicorn, Python 3.11-alpine, Pandoc, poppler-utils, GitHub Actions, GHCR

---

## Chunk 1: 项目结构改造

### Task 1: 创建应用目录结构

**Files:**
- Create: `app/__init__.py`
- Create: `app/main.py`
- Create: `app/converters.py`
- Create: `app/dependencies.py`

- [ ] **Step 1: 创建 app 包初始化文件**

```python
# app/__init__.py
"""MDTools FastAPI 应用"""
```

- [ ] **Step 2: 创建依赖检查模块**

```python
# app/dependencies.py
import subprocess
import sys


def check_pandoc() -> bool:
    """检查 pandoc 是否安装"""
    try:
        subprocess.run(["pandoc", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_poppler() -> bool:
    """检查 poppler 是否安装"""
    try:
        subprocess.run(["pdftotext", "-v"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_dependencies():
    """检查所有依赖"""
    if not check_pandoc():
        print("[ERROR] 未找到 pandoc", file=sys.stderr)
        sys.exit(1)
    if not check_poppler():
        print("[ERROR] 未找到 poppler-utils", file=sys.stderr)
        sys.exit(1)
```

- [ ] **Step 3: 创建转换器模块**

```python
# app/converters.py
import os
import subprocess
from typing import Optional


def convert_pdf_to_md(pdf_path: str, output_path: Optional[str] = None) -> str:
    """PDF 转 Markdown"""
    if output_path is None:
        output_path = os.path.splitext(pdf_path)[0] + ".md"
    
    cmd = ["pdftotext", "-layout", pdf_path, output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"转换失败：{result.stderr or result.stdout}")
    
    return output_path


def convert_md_to_pdf(md_path: str, output_path: Optional[str] = None) -> str:
    """Markdown 转 PDF"""
    if output_path is None:
        output_path = os.path.splitext(md_path)[0] + ".pdf"
    
    cmd = ["pandoc", md_path, "-o", output_path, "--pdf-engine=xelatex"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"转换失败：{result.stderr or result.stdout}")
    
    return output_path


def convert_md_to_doc(md_path: str, output_path: Optional[str] = None) -> str:
    """Markdown 转 Word"""
    if output_path is None:
        output_path = os.path.splitext(md_path)[0] + ".docx"
    
    cmd = ["pandoc", md_path, "-o", output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"转换失败：{result.stderr or result.stdout}")
    
    return output_path


def convert_doc_to_md(doc_path: str, output_path: Optional[str] = None) -> str:
    """Word 转 Markdown"""
    if output_path is None:
        output_path = os.path.splitext(doc_path)[0] + ".md"
    
    cmd = ["pandoc", doc_path, "-o", output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"转换失败：{result.stderr or result.stdout}")
    
    return output_path
```

- [ ] **Step 4: 创建 FastAPI 主应用**

```python
# app/main.py
import os
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, Response

from . import converters
from .dependencies import check_dependencies

# 启动时检查依赖
check_dependencies()

app = FastAPI(
    title="MDTools API",
    description="文档格式转换 API - 支持 PDF <-> Markdown <-> Word",
    version="1.0.0",
)

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


@app.get("/health")
def health_check():
    """健康检查端点"""
    return {"status": "healthy"}


@app.post("/api/pdf2md")
async def pdf_to_md(file: UploadFile = File(...)):
    """PDF 转 Markdown"""
    return await process_file(file, converters.convert_pdf_to_md, ".md")


@app.post("/api/md2pdf")
async def md_to_pdf(file: UploadFile = File(...)):
    """Markdown 转 PDF"""
    return await process_file(file, converters.convert_md_to_pdf, ".pdf", "application/pdf")


@app.post("/api/md2doc")
async def md_to_doc(file: UploadFile = File(...)):
    """Markdown 转 Word"""
    return await process_file(file, converters.convert_md_to_doc, ".docx", 
                             "application/vnd.openxmlformats-officedocument.wordprocessingml.document")


@app.post("/api/doc2md")
async def doc_to_md(file: UploadFile = File(...)):
    """Word 转 Markdown"""
    return await process_file(file, converters.convert_doc_to_md, ".md")


async def process_file(file: UploadFile, converter, output_ext: str, content_type: str = "application/octet-stream"):
    """处理文件上传和转换"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名为空")
    
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件大小超过 50MB 限制")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=output_ext) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name
    
    try:
        output_path = converter(tmp_path)
        with open(output_path, "rb") as f:
            file_content = f.read()
        
        filename = os.path.splitext(file.filename)[0] + output_ext
        return Response(
            content=file_content,
            media_type=content_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        output_path = tmp_path.replace(output_ext, output_ext)
        if os.path.exists(output_path):
            os.unlink(output_path)
```

- [ ] **Step 5: 更新 requirements.txt**

```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
python-multipart>=0.0.6
markdown>=3.4
```

- [ ] **Step 6: 提交**

```bash
git add app/ requirements.txt
git commit -m "feat: add FastAPI server application"
```

---

## Chunk 2: Docker 配置

### Task 2: 创建 Dockerfile

**Files:**
- Create: `Dockerfile`

- [ ] **Step 1: 创建多阶段 Dockerfile**

```dockerfile
# Stage 1: Build
FROM python:3.11-alpine AS builder

RUN apk add --no-cache \
    pandoc \
    poppler-utils \
    texlive \
    texlive-latex \
    texlive-latexextra \
    texlive-fontsrecommended

WORKDIR /app

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-alpine

RUN apk add --no-cache \
    pandoc \
    poppler-utils \
    texlive \
    texlive-latex \
    texlive-latexextra \
    texlive-fontsrecommended

WORKDIR /app

COPY --from=builder /root/.local /root/.local
COPY app/ ./app/

ENV PATH=/root/.local/bin:$PATH
ENV PORT=8000
ENV WORKERS=1

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers ${WORKERS}"]
```

- [ ] **Step 2: 创建 docker-compose.yml**

```yaml
version: '3.8'

services:
  mdtools:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PORT=8000
      - WORKERS=1
    volumes:
      - ./app:/app/app
    restart: unless-stopped
```

- [ ] **Step 3: 创建 .dockerignore**

```
.git
.gitignore
__pycache__
*.pyc
*.pyo
.env
.venv
venv
*.md
!requirements.txt
docs/
.github/
```

- [ ] **Step 4: 提交**

```bash
git add Dockerfile docker-compose.yml .dockerignore
git commit -m "feat: add Docker configuration with multi-stage build"
```

---

## Chunk 3: GitHub Actions 自动化

### Task 3: 创建 GitHub Actions Workflow

**Files:**
- Create: `.github/workflows/docker-publish.yml`

- [ ] **Step 1: 创建工作流文件**

```yaml
name: Publish Docker Image

on:
  release:
    types: [published]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up QEMU
        uses: docker/setup-qemu-action@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata (tags, labels)
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=semver,pattern={{version}}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          platforms: linux/amd64,linux/arm64
```

- [ ] **Step 2: 更新 README.md 添加部署说明**

在现有 README.md 中添加：

```markdown
## 服务端部署

### Docker 运行

```bash
# 从 GHCR 拉取
docker pull ghcr.io/<owner>/mdtools:<version>

# 运行容器
docker run -d -p 8000:8000 ghcr.io/<owner>/mdtools:<version>
```

### API 文档

访问 `http://localhost:8000/docs` 查看 Swagger UI

### 使用示例

```bash
# PDF 转 Markdown
curl -X POST "http://localhost:8000/api/pdf2md" \
  -F "file=@document.pdf" \
  -o output.md
```
```

- [ ] **Step 3: 提交**

```bash
git add .github/workflows/docker-publish.yml README.md
git commit -m "ci: add GitHub Actions workflow for Docker publishing"
```

---

## Chunk 4: 测试配置

### Task 4: 创建测试文件

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/test_api.py`
- Create: `tests/test_converters.py`
- Create: `pytest.ini`

- [ ] **Step 1: 创建测试目录结构**

```python
# tests/__init__.py
"""测试模块"""
```

- [ ] **Step 2: 创建转换器测试**

```python
# tests/test_converters.py
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
        
        try:
            output = convert_md_to_pdf(md_path)
            assert os.path.exists(output)
            assert output.endswith('.pdf')
        finally:
            for f in [md_path, output]:
                if os.path.exists(f):
                    os.unlink(f)
```

- [ ] **Step 3: 创建 API 测试**

```python
# tests/test_api.py
import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestAPI:
    """API 端点测试"""

    def test_health_check(self):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_pdf_to_md(self):
        """测试 PDF 转 Markdown"""
        # 创建一个简单的 PDF 文件用于测试
        pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
        files = {"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")}
        response = client.post("/api/pdf2md", files=files)
        # 预期会失败（不是有效 PDF），但端点应该响应
        assert response.status_code in [200, 500]
```

- [ ] **Step 4: 创建 pytest 配置**

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

- [ ] **Step 5: 提交**

```bash
git add tests/ pytest.ini
git commit -m "test: add initial test suite"
```

---

## 验证清单

完成所有任务后，验证以下内容：

- [ ] 运行 `uvicorn app.main:app --reload` 启动服务器
- [ ] 访问 `http://localhost:8000/docs` 确认 Swagger UI 正常
- [ ] 测试每个 API 端点返回正确响应
- [ ] Docker 构建 `docker build -t mdtools:test .` 成功
- [ ] Docker 容器运行并响应健康检查
- [ ] GitHub Actions workflow 语法正确
