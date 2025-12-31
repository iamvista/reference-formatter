# 免費主機方案完整比較

## 📊 平台比較總覽

| 平台 | 免費額度 | 休眠 | HTTPS | 自定義域名 | 難度 | 推薦度 |
|------|---------|------|-------|-----------|------|--------|
| **Render** | 512MB RAM<br/>750 小時/月 | ✅ 15分鐘 | ✅ | ❌ | ⭐ | ⭐⭐⭐⭐⭐ |
| **PythonAnywhere** | 512MB RAM<br/>100 秒 CPU/天 | ❌ | ❌ | ❌ | ⭐ | ⭐⭐⭐⭐ |
| **Fly.io** | 3 個 VM<br/>256MB RAM | ❌ | ✅ | ✅ | ⭐⭐ | ⭐⭐⭐⭐ |
| **Railway** | $5 額度/月 | ❌ | ✅ | ❌ | ⭐ | ⭐⭐⭐ |
| **Vercel** | 無限 | ❌ | ✅ | ✅ | ⭐⭐⭐ | ⭐⭐ |

---

## 1️⃣ Render（最推薦）

### ✨ 優點
- 🆓 完全免費，不需信用卡
- 🚀 Git 推送自動部署
- 🔒 免費 HTTPS
- 📊 內建監控和日誌
- 🌍 全球 CDN

### ⚠️ 缺點
- 閒置 15 分鐘後休眠
- 喚醒需要 30-60 秒

### 📋 適用場景
✅ 個人作品集
✅ 學術項目展示
✅ API 測試
✅ 低到中流量應用

### 🚀 快速部署

詳細步驟請查看：[RENDER_DEPLOY.md](./RENDER_DEPLOY.md)

**精簡步驟**：
```bash
# 1. 推送到 GitHub
git init && git add . && git commit -m "Initial"
git remote add origin <your-repo>
git push -u origin main

# 2. 在 render.com 創建 Web Service
# 3. 連接倉庫，設置環境變量
# 4. 部署！
```

---

## 2️⃣ PythonAnywhere

### ✨ 優點
- 🐍 專為 Python 設計
- 💤 **不休眠**
- 🎓 適合學術用途
- 🖥️ 提供 SSH 和控制台

### ⚠️ 缺點
- CPU 時間限制（100 秒/天）
- 免費版無 HTTPS
- 網絡訪問受限（只能訪問白名單網站）
- 域名固定為 `.pythonanywhere.com`

### 📋 適用場景
✅ 學術研究項目
✅ 教學演示
✅ 內部工具
❌ 需要調用外部 API（CrossRef 可能受限）

### 🚀 快速部署

```bash
# 1. 註冊 PythonAnywhere 帳號
# 訪問 https://www.pythonanywhere.com

# 2. 創建新的 Web App
# Dashboard → Web → Add a new web app → Flask → Python 3.10

# 3. 上傳代碼
# 使用 Git 或直接上傳檔案

# 4. 配置 WSGI
# 編輯 /var/www/<username>_pythonanywhere_com_wsgi.py
```

**WSGI 配置**：
```python
import sys
path = '/home/<username>/reference-formatter'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

**安裝依賴**：
```bash
# 在 Bash 控制台中
cd ~/reference-formatter
python3 -m pip install --user -r requirements.txt
```

**重新載入**：
在 Web 標籤點擊 "Reload"

### ⚠️ 重要限制

**網絡白名單問題**：
免費版只能訪問白名單上的網站。CrossRef API 可能不在白名單上。

**解決方案**：
在 `app.py` 中添加：
```python
# 檢測 PythonAnywhere 環境
import os
IS_PYTHONANYWHERE = 'PYTHONANYWHERE_DOMAIN' in os.environ

# 修改 parse 端點
if IS_PYTHONANYWHERE:
    # 禁用 API 查詢
    enrich = False
```

---

## 3️⃣ Fly.io

### ✨ 優點
- 🌍 全球邊緣網絡
- 💤 **不休眠**
- 🆓 3 個免費 VM
- 🔒 自動 HTTPS
- ⚡ 性能優秀

### ⚠️ 缺點
- 需要信用卡驗證（不會扣款）
- 配置稍複雜
- 命令行操作

### 📋 適用場景
✅ 需要全球加速
✅ 多區域部署
✅ 追求性能
✅ 技術用戶

### 🚀 快速部署

**1. 安裝 Fly CLI**：
```bash
# macOS
brew install flyctl

# Linux
curl -L https://fly.io/install.sh | sh

# Windows
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

**2. 登入**：
```bash
flyctl auth login
```

**3. 創建應用**：
```bash
cd reference-formatter
flyctl launch

# 回答問題：
# App name: reference-formatter
# Region: Singapore (or closest)
# PostgreSQL: No
# Redis: No
```

**4. 配置 fly.toml**：

Fly.io 會自動生成，但需要調整：

```toml
app = "reference-formatter"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8080"
  FLASK_ENV = "production"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = false  # 防止自動停止
  auto_start_machines = true

[[vm]]
  memory = '256mb'
  cpu_kind = 'shared'
  cpus = 1
```

**5. 設置密鑰**：
```bash
flyctl secrets set SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
```

**6. 部署**：
```bash
flyctl deploy
```

**7. 訪問**：
```bash
flyctl open
```

---

## 4️⃣ Railway

### ✨ 優點
- 🎨 超簡單的 UI
- 🚀 一鍵部署
- 💤 **不休眠**
- 🔒 自動 HTTPS

### ⚠️ 缺點
- 只有 $5 免費額度/月（約 300 小時）
- 用完需要付費
- 價格較高（$5/月起）

### 📋 適用場景
✅ 快速測試
✅ 短期項目
✅ Demo 展示
❌ 長期免費使用

### 🚀 快速部署

**1. 訪問 Railway**：
https://railway.app

**2. 登入 GitHub**

**3. 部署**：
- 點擊 "New Project"
- 選擇 "Deploy from GitHub repo"
- 選擇 `reference-formatter`

**4. 添加環境變量**：
- FLASK_ENV: `production`
- SECRET_KEY: `<生成的密鑰>`

**5. 自動部署完成**

---

## 5️⃣ Vercel（不推薦 Flask）

### ⚠️ 注意
Vercel 主要是為 Next.js/前端設計的，雖然支援 Python，但：
- 需要改寫為 Serverless 函數
- 有執行時間限制（10 秒）
- 不適合我們的應用架構

**建議**：不要選擇 Vercel

---

## 🎯 最終推薦

### 🥇 首選：Render
**理由**：
- 完全免費
- 配置簡單
- 功能完整
- 適合大多數場景

**缺點可接受**：
- 休眠可用 UptimeRobot 解決
- 對於測試和展示完全足夠

### 🥈 次選：Fly.io
**理由**：
- 不休眠
- 性能優秀
- 全球加速

**適合**：技術用戶、追求性能

### 🥉 學術用途：PythonAnywhere
**理由**：
- 不休眠
- 專為 Python 設計

**注意**：API 調用可能受限

---

## 💡 組合方案

### 方案 1：Render + UptimeRobot
```
Render（主機）+ UptimeRobot（防休眠）
= 完美的免費方案
```

### 方案 2：測試後升級
```
Render Free（測試）
→ 用戶增長 →
Render Starter $7/月（生產）
```

### 方案 3：多平台備份
```
主站：Render
備份：PythonAnywhere
= 雙保險
```

---

## 📊 成本對比（如需升級）

| 平台 | 入門方案 | 標準方案 |
|------|---------|---------|
| Render | $7/月 | $25/月 |
| Railway | $5/月 | $20/月 |
| Fly.io | $1.94/月 | 按需 |
| DigitalOcean | $6/月 | $12/月 |

---

## 🔄 遷移方案

### 從 Render 免費 → Render 付費
✅ 零停機時間
✅ 一鍵升級
✅ 無需更改代碼

### 從 Render → VPS
需要：
1. 設置服務器
2. 配置 Nginx
3. 設置 SSL
4. 遷移資料
⏰ 預計 2-3 小時

---

## 📞 總結

**我的建議**：

1. **立即開始**：使用 **Render 免費方案**
2. **防止休眠**：設置 UptimeRobot
3. **監控使用**：觀察流量和性能
4. **適時升級**：當需要時再考慮付費

**Render 免費方案足夠用於**：
- ✅ 個人作品集
- ✅ 畢業專題展示
- ✅ 學術研究工具
- ✅ 中小型項目測試

**何時需要升級**：
- ⚠️ 每天有持續的用戶訪問
- ⚠️ 需要即時響應（不能等喚醒）
- ⚠️ 商業用途

---

**開始部署吧！** 🚀

建議從 [Render](./RENDER_DEPLOY.md) 開始，這是最簡單且最可靠的免費方案。
