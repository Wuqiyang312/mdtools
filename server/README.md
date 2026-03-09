# MDTools Server

Markdown 转换工具的 Web 服务接口

## 启动服务

```bash
# 使用默认端口 (8080)
./server/run.sh

# 自定义端口
PORT=3000 ./server/run.sh

# 或直接运行
python3 server/server.py --port 8080
```

## Web 界面

访问 `http://localhost:8080/` 可使用网页界面进行文件转换。

## API 接口

### POST /convert

支持两种请求方式：

**1. JSON 请求:**
```json
{
  "input_path": "document.md",
  "output_path": "output.pdf",
  "format": "md2pdf"
}
```

**2. 表单上传 (multipart/form-data):**
- `file`: 上传的文件
- `format`: 转换格式 (md2pdf, md2word, pdf2md)

**参数:**
- `input_path` / `file` (必需): 输入文件路径或上传的文件
- `output_path` (可选): 输出文件路径，不提供则自动生成
- `format` (必需): 转换格式，支持:
  - `md2pdf` - Markdown 转 PDF
  - `md2word` - Markdown 转 Word
  - `pdf2md` - PDF 转 Markdown

**响应:**
```json
{
  "success": true,
  "message": "Conversion successful",
  "output_path": "document.pdf"
}
```

### GET /health

健康检查

**响应:**
```json
{
  "status": "healthy"
}
```

## 使用示例

```bash
# JSON 方式 - Markdown 转 PDF
curl -X POST http://localhost:8080/convert \
  -H "Content-Type: application/json" \
  -d '{"input_path": "readme.md", "format": "md2pdf"}'

# 文件上传方式 - Markdown 转 PDF
curl -X POST http://localhost:8080/convert \
  -F "file=@readme.md" \
  -F "format=md2pdf"

# Markdown 转 Word
curl -X POST http://localhost:8080/convert \
  -F "file=@readme.md" \
  -F "format=md2word"

# PDF 转 Markdown
curl -X POST http://localhost:8080/convert \
  -F "file=@document.pdf" \
  -F "format=pdf2md"

# 健康检查
curl http://localhost:8080/health
```

## Docker 部署

```bash
cd server/docker

# 构建镜像
./build.sh

# 或使用 docker-compose
./run.sh

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```
