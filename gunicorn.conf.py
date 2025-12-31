"""
Gunicorn 配置文件
生產環境 WSGI 伺服器設定
"""

import multiprocessing

# 綁定地址
bind = "0.0.0.0:8080"

# Worker 進程數（建議：CPU 核心數 * 2 + 1）
workers = multiprocessing.cpu_count() * 2 + 1

# Worker 類型（sync 適合 CPU 密集，gevent 適合 I/O 密集）
worker_class = "sync"

# 每個 worker 的線程數
threads = 2

# Worker 超時時間（秒）
timeout = 120

# 最大請求數（防止記憶體洩漏）
max_requests = 1000
max_requests_jitter = 50

# 日誌
accesslog = "-"  # 輸出到 stdout
errorlog = "-"   # 輸出到 stderr
loglevel = "info"

# 保持連接
keepalive = 5

# 優雅重啟
graceful_timeout = 30
