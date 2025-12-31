# 使用官方 Python 映像
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 複製依賴文件
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# 複製應用代碼
COPY . .

# 創建非 root 用戶
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 8080

# 啟動命令
CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:app"]
