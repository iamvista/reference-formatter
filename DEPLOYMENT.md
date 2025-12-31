# 部署指南 / Deployment Guide

本文檔提供將學術文獻格式整理工具部署到生產環境的詳細步驟。

## 📋 目錄

1. [快速部署（Render）](#快速部署render推薦)
2. [Docker 部署](#docker-部署)
3. [傳統主機部署](#傳統主機部署)
4. [安全性檢查清單](#安全性檢查清單)
5. [性能優化建議](#性能優化建議)

---

## 🚀 快速部署（Render，推薦）

### 步驟 1：準備 Git 倉庫

```bash
# 初始化 Git（如果還沒有）
git init
git add .
git commit -m "Initial commit"

# 推送到 GitHub/GitLab
git remote add origin <your-repo-url>
git push -u origin main
```

### 步驟 2：部署到 Render

1. 訪問 [Render.com](https://render.com) 並註冊
2. 點擊「New +」→「Web Service」
3. 連接你的 Git 倉庫
4. 配置如下：
   - **Name**: reference-formatter
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --config gunicorn.conf.py wsgi:app`
   - **Plan**: Free（或付費方案以獲得更好性能）

5. 添加環境變量：
   - `FLASK_ENV`: `production`
   - `SECRET_KEY`: （生成一個隨機密鑰，見下方）

6. 點擊「Create Web Service」

### 生成安全的 SECRET_KEY

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🐳 Docker 部署

### 本地測試

```bash
# 構建映像
docker build -t reference-formatter .

# 運行容器
docker run -p 8080:8080 \
  -e FLASK_ENV=production \
  -e SECRET_KEY=your-secret-key \
  reference-formatter
```

### Docker Compose

創建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8080:8080"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/"]
      interval: 30s
      timeout: 10s
      retries: 3
```

運行：
```bash
docker-compose up -d
```

---

## 🖥️ 傳統主機部署

### 系統要求

- Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- Python 3.9+
- Nginx（可選，用於反向代理）

### 步驟 1：設置環境

```bash
# 更新系統
sudo apt update && sudo apt upgrade -y

# 安裝依賴
sudo apt install python3 python3-pip python3-venv nginx -y

# 創建應用目錄
sudo mkdir -p /var/www/reference-formatter
cd /var/www/reference-formatter

# 上傳代碼或克隆倉庫
git clone <your-repo-url> .

# 創建虛擬環境
python3 -m venv venv
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt
```

### 步驟 2：配置環境變量

```bash
# 創建 .env 文件
cp .env.example .env
nano .env

# 填入以下內容：
FLASK_ENV=production
SECRET_KEY=<生成的密鑰>
CROSSREF_EMAIL=your-email@example.com
```

### 步驟 3：設置 Systemd 服務

創建 `/etc/systemd/system/reference-formatter.service`：

```ini
[Unit]
Description=Reference Formatter Web Service
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/reference-formatter
Environment="PATH=/var/www/reference-formatter/venv/bin"
EnvironmentFile=/var/www/reference-formatter/.env
ExecStart=/var/www/reference-formatter/venv/bin/gunicorn \
    --config gunicorn.conf.py wsgi:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

啟動服務：

```bash
sudo systemctl daemon-reload
sudo systemctl enable reference-formatter
sudo systemctl start reference-formatter
sudo systemctl status reference-formatter
```

### 步驟 4：配置 Nginx 反向代理

創建 `/etc/nginx/sites-available/reference-formatter`：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替換為你的域名

    # 安全標頭
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # 限制請求大小
    client_max_body_size 16M;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 超時設置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 靜態文件緩存
    location /static/ {
        alias /var/www/reference-formatter/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

啟用站點：

```bash
sudo ln -s /etc/nginx/sites-available/reference-formatter /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 步驟 5：設置 HTTPS（使用 Let's Encrypt）

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## 🔒 安全性檢查清單

部署前請確認以下事項：

- [ ] ✅ 已設置強隨機 `SECRET_KEY`
- [ ] ✅ `FLASK_ENV=production`（關閉調試模式）
- [ ] ✅ 使用 HTTPS（生產環境必須）
- [ ] ✅ 設置了防火牆規則（只開放 80/443 端口）
- [ ] ✅ 定期更新依賴套件
- [ ] ✅ 限制上傳文件大小（已設為 16MB）
- [ ] ✅ 添加速率限制（防止濫用）
- [ ] ✅ 設置日誌監控
- [ ] ✅ 備份配置和數據
- [ ] ✅ 使用非 root 用戶運行應用

---

## ⚡ 性能優化建議

### 1. 添加緩存

考慮添加 Redis 緩存常用的 API 查詢結果：

```python
# 安裝：pip install flask-caching redis
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
})

@cache.memoize(timeout=3600)  # 緩存 1 小時
def query_crossref(doi):
    # ...
```

### 2. 使用 CDN

將靜態資源放到 CDN：
- Cloudflare（免費）
- AWS CloudFront
- Vercel

### 3. 數據庫（如果需要）

如果需要保存用戶數據或歷史記錄：
- PostgreSQL（推薦）
- MongoDB（文檔型）

### 4. 監控和日誌

推薦工具：
- **Sentry** - 錯誤追蹤（有免費方案）
- **Prometheus + Grafana** - 性能監控
- **Papertrail** - 日誌聚合

### 5. 負載測試

部署前進行壓力測試：

```bash
# 安裝 locust
pip install locust

# 創建 locustfile.py 並運行
locust -f locustfile.py --host=http://your-domain.com
```

---

## 📊 成本估算

### 免費方案
- **Render Free**: $0/月
  - 限制：服務閒置後會休眠
  - 適合：個人項目、演示

### 低成本方案（推薦）
- **Render Starter**: $7/月
  - 無休眠
  - 512MB RAM
  - 適合：小型團隊使用

### 中等流量方案
- **Render Standard**: $25/月
  - 2GB RAM
  - 適合：中型組織

### 自建方案
- **VPS（Linode/DigitalOcean）**: $5-12/月
  - 完全控制
  - 需要自行維護

---

## 🆘 常見問題

### Q: 如何查看日誌？

**Render**: 在儀表板中點擊「Logs」
**Systemd**: `sudo journalctl -u reference-formatter -f`
**Docker**: `docker logs -f <container-id>`

### Q: 如何更新應用？

**Render**: 推送代碼到 Git，自動部署
**手動**:
```bash
cd /var/www/reference-formatter
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart reference-formatter
```

### Q: 應用無法啟動？

1. 檢查日誌
2. 確認環境變量設置正確
3. 確認端口未被佔用
4. 檢查文件權限

---

## 📞 支援

遇到問題？
- 查看日誌文件
- 檢查 GitHub Issues
- 聯繫開發團隊

---

**祝部署順利！** 🎉
