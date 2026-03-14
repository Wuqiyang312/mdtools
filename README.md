# MDTools

文档格式转换工具 - 基于 Pandoc，支持 PDF <-> Markdown <-> Word 之间的转换

## 功能

| 端点 | 输入 | 输出 | 状态 |
|------|------|------|------|
| `/api/pdf2md` | PDF | Markdown | ✅ |
| `/api/md2pdf` | Markdown | PDF | ⚠️ 需 xelatex |
| `/api/md2doc` | Markdown | Word | ✅ |
| `/api/doc2md` | Word | Markdown | ✅ |

## 快速开始

### 1. 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 访问 API 文档
open http://localhost:8000/docs
```

### 2. Docker 运行

```bash
# 构建镜像
docker build -t mdtools .

# 运行容器
docker run -d -p 8000:8000 mdtools
```

### 3. 使用示例

```bash
# Markdown 转 Word
curl -X POST "http://localhost:8000/api/md2doc" \
  -F "file=@document.md" \
  -o output.docx

# Word 转 Markdown
curl -X POST "http://localhost:8000/api/doc2md" \
  -F "file=@document.docx" \
  -o output.md

# PDF 转 Markdown
curl -X POST "http://localhost:8000/api/pdf2md" \
  -F "file=@document.pdf" \
  -o output.md
```

## 依赖

| 工具 | 用途 | 必需 |
|------|------|------|
| [Pandoc](https://pandoc.org) | 文档转换引擎 | ✅ |
| [poppler-utils](https://poppler.freedesktop.org) | PDF 文本提取 | ✅ (pdf2md) |
| [TeX Live / MiKTeX](https://www.tug.org) | PDF 生成 | ⚠️ (md2pdf) |

## 系统依赖安装

### Windows

```bash
# 使用 winget 安装
winget install JohnMacFarlane.Pandoc
winget install poppler

# 或使用 choco
choco install pandoc poppler miktex
```

### macOS

```bash
brew install pandoc poppler mactex
```

### Linux (Debian/Ubuntu)

```bash
sudo apt install pandoc poppler-utils texlive-xetex
```

## 配置

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `PORT` | `8000` | 服务端口 |
| `WORKERS` | `1` | Uvicorn worker 数 |

## 开发

```bash
# 运行测试
pytest tests/ -v

# 检查代码
pre-commit run --all-files
```

## 发布

### GitHub Actions 自动发布

创建 release 时自动构建并推送 Docker 镜像到 GHCR：

```bash
git tag v1.0.0
git push origin v1.0.0
# 在 GitHub 上创建 release
```

### 镜像地址

```
ghcr.io/<owner>/mdtools:<version>
```

## 错误处理

| 状态码 | 说明 |
|--------|------|
| `400` | 文件格式错误/不支持的格式 |
| `500` | 转换失败（依赖缺失） |

## 许可证

MIT License
