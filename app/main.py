import os
import sys
import tempfile
import base64
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, Response

from . import converters
from .dependencies import check_pandoc, check_poppler

app = FastAPI(
    title="MDTools API",
    description="文档格式转换 API - 支持 PDF <-> Markdown <-> Word",
    version="1.0.0",
)

MAX_FILE_SIZE = 50 * 1024 * 1024


@app.on_event("startup")
async def startup_event():
    """启动时检查依赖"""
    if not check_pandoc():
        print("[ERROR] 未找到 pandoc", file=sys.stderr)
        sys.exit(1)
    if not check_poppler():
        print("[ERROR] 未找到 poppler-utils", file=sys.stderr)
        sys.exit(1)


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


async def process_file(file: UploadFile, converter, output_ext: str, content_type: str = "application/octet-stream", input_ext: str | None = None):
    """处理文件上传和转换"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名为空")
    
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件大小超过 50MB 限制")
    
    # 使用正确的输入文件后缀，让 pandoc 识别格式
    if input_ext is None:
        input_ext = os.path.splitext(file.filename)[1] or ".txt"
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=input_ext) as tmp:
        tmp.write(contents)
        tmp.flush()
        tmp_path = tmp.name
    
    output_path = None
    try:
        output_path = converter(tmp_path)
        with open(output_path, "rb") as f:
            file_content = f.read()
        
        # 使用 RFC 5987 编码处理中文文件名
        filename = os.path.splitext(file.filename)[0] + output_ext
        encoded_filename = base64.b64encode(filename.encode('utf-8')).decode('ascii')
        return Response(
            content=file_content,
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
            }
        )
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        if output_path and os.path.exists(output_path):
            os.unlink(output_path)
