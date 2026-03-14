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
