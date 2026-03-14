# MDTools 服务端设计文档

## 概述

将 MDTools 从命令行工具改造为 FastAPI 服务端应用，支持 Docker 容器化部署，通过 GitHub Actions 自动发布到 GHCR。

## 架构设计

```
┌─────────────────┐
│   Client        │
│   (Browser/CLI) │
└────────┬────────┘
         │ HTTP + multipart/form-data
         ▼
┌─────────────────────────────────────┐
│   FastAPI Application (Port 8000)   │
│  ┌─────────────────────────────┐    │
│  │  /api/pdf2md  (POST)        │    │
│  │  /api/md2pdf  (POST)        │    │
│  │  /api/md2doc  (POST)        │    │
│  │  /api/doc2md  (POST)        │    │
│  └─────────────────────────────┘    │
│  ┌─────────────────────────────┐    │
│  │  /docs (Swagger UI)         │    │
│  │  /openapi.json              │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│   Pandoc        │
│   poppler-utils │
└─────────────────┘
```

## API 端点设计

### 文件上传方式
所有端点使用 `multipart/form-data` 接收文件。

### 端点列表

| 端点 | 方法 | 输入 | 输出 |
|------|------|------|------|
| `/api/pdf2md` | POST | `file: UploadFile` (PDF) | `application/octet-stream` (Markdown) |
| `/api/md2pdf` | POST | `file: UploadFile` (Markdown) | `application/pdf` |
| `/api/md2doc` | POST | `file: UploadFile` (Markdown) | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` |
| `/api/doc2md` | POST | `file: UploadFile` (Word) | `application/octet-stream` (Markdown) |

### 响应头

```
Content-Disposition: attachment; filename="converted.ext"
```

### 错误响应

```json
{
  "detail": "错误描述"
}
```

状态码：
- `400` - 文件格式错误/不支持的格式
- `500` - 转换失败（Pandoc/poppler 错误）

## 项目结构

```
mdtools/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI 应用入口
│   ├── converters.py     # 转换逻辑封装
│   └── dependencies.py   # 依赖检查（Pandoc, poppler）
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .github/
│   └── workflows/
│       └── docker-publish.yml
├── docs/
│   └── superpowers/
│       └── specs/
│           └── 2026-03-14-mdtools-server-design.md
├── mdtools.py            # 保留 CLI（向后兼容）
└── README.md             # 更新使用说明
```

## Docker 配置

### 基础镜像
`python:3.11-alpine`

### 多阶段构建

**Stage 1 - Build:**
- 安装系统依赖（Pandoc, poppler-utils, texlive）
- 安装 Python 依赖

**Stage 2 - Runtime:**
- 复制依赖和代码
- 最小化运行时环境

### Dockerfile 关键配置

```dockerfile
FROM python:3.11-alpine AS builder

# 安装系统依赖
RUN apk add --no-cache \
    pandoc \
    poppler-utils \
    texlive

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-alpine

RUN apk add --no-cache \
    pandoc \
    poppler-utils \
    texlive

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY --from=builder /usr/bin/pandoc /usr/bin/pandoc
COPY app/ ./app/

ENV PATH=/root/.local/bin:$PATH

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `PORT` | `8000` | 监听端口 |
| `WORKERS` | `1` | Uvicorn worker 数量 |

## GitHub Actions 配置

### 触发条件
仅 release/tag 触发

### 镜像标签策略
- `ghcr.io/{owner}/mdtools:{version}` - 版本号
- 不推送 latest 标签

### Workflow 步骤

1. 检出代码
2. 登录 GHCR
3. 构建 Docker 镜像
4. 推送镜像到 GHCR

## 错误处理

### 依赖检查
启动时检查 Pandoc 和 poppler 是否可用，不可用时拒绝启动。

### 文件验证
- 检查文件是否存在
- 检查文件类型（通过 magic bytes 或扩展名）
- 文件大小限制（默认 50MB，可通过环境变量配置）

### 转换超时
单个转换操作超时限制 120 秒，防止长时间占用资源。

## 测试策略

### 单元测试
- 转换器逻辑测试
- 依赖检查测试

### 集成测试
- API 端点测试（使用 TestClient）
- 文件上传/下载测试

### Docker 测试
- 镜像构建测试
- 容器启动测试

## 安全考虑

- 无认证（最小可用方案）
- 临时文件存储在 `/tmp`，请求结束后自动清理
- 无文件持久化，容器重启后数据清空
- 建议生产环境在 Docker 前加 Nginx 反向代理

## 成功标准

- [ ] 4 个 API 端点正常工作
- [ ] Swagger UI (`/docs`) 可访问
- [ ] Docker 镜像可构建并运行
- [ ] GitHub Actions 在 release 时自动发布到 GHCR
- [ ] 镜像大小 < 200MB
