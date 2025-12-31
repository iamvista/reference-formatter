# Render 免費部署詳細指南

## 🆓 Render Free Tier 說明

### 免費方案特點
- **價格**: 完全免費
- **RAM**: 512MB
- **CPU**: 共享
- **流量**: 無限制
- **休眠**: 閒置 15 分鐘後自動休眠
- **喚醒**: 首次訪問需 30-60 秒
- **限制**: 每月 750 小時服務時間

### 適用場景
✅ 個人作品集展示
✅ 學術專案演示
✅ 開發測試環境
✅ 低流量應用

❌ 生產環境（推薦付費方案）
❌ 需要即時響應的服務

---

## 📋 部署步驟

### 步驟 1：準備 Git 倉庫

```bash
# 1. 初始化 Git（如果還沒有）
cd /Users/vista/reference-formatter
git init

# 2. 添加所有文件
git add .

# 3. 提交
git commit -m "Initial commit - Reference Formatter"

# 4. 推送到 GitHub
# 先在 GitHub 創建一個新倉庫，然後：
git remote add origin https://github.com/你的用戶名/reference-formatter.git
git branch -M main
git push -u origin main
```

### 步驟 2：註冊 Render 帳號

1. 訪問 [render.com](https://render.com)
2. 點擊右上角 **"Get Started"** 或 **"Sign Up"**
3. 選擇使用 **GitHub 登入**（推薦）或郵箱註冊
4. 授權 Render 訪問你的 GitHub 倉庫

### 步驟 3：創建 Web Service

1. 登入後，點擊 **"New +"** → **"Web Service"**

2. 連接你的 GitHub 倉庫：
   - 找到 `reference-formatter` 倉庫
   - 點擊 **"Connect"**

3. 配置服務：

   **基本設定**：
   ```
   Name: reference-formatter
   Region: Singapore (或選擇離你最近的)
   Branch: main
   Runtime: Python 3
   ```

   **Build & Deploy 設定**：
   ```
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn --config gunicorn.conf.py wsgi:app
   ```

   **選擇方案**：
   ```
   Instance Type: Free
   ```

4. 添加**環境變量** (Environment Variables)：

   點擊 **"Advanced"** → **"Add Environment Variable"**

   添加以下變量：

   | Key | Value |
   |-----|-------|
   | `FLASK_ENV` | `production` |
   | `SECRET_KEY` | [生成的密鑰]* |
   | `PYTHON_VERSION` | `3.11.0` |

   **生成 SECRET_KEY：**
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```
   複製輸出的值

5. 點擊 **"Create Web Service"**

### 步驟 4：等待部署

部署過程約需 3-5 分鐘，你會看到：

1. ⏳ Installing dependencies...
2. ⏳ Building...
3. ⏳ Starting service...
4. ✅ Live（部署成功）

部署完成後，Render 會給你一個 URL：
```
https://reference-formatter-xxxx.onrender.com
```

---

## 🧪 測試部署

### 1. 訪問你的應用

在瀏覽器中打開 Render 提供的 URL

### 2. 測試健康檢查

```bash
curl https://你的應用URL.onrender.com/health
```

應該返回：
```json
{
  "status": "healthy",
  "service": "reference-formatter",
  "version": "1.0.0"
}
```

### 3. 測試文獻解析

在網頁上輸入測試文獻：
```
Smith, J. (2020). The impact of climate change. Nature, 582(7812), 123-145. https://doi.org/10.1038/nature12345
```

點擊「解析並格式化」，測試各種格式切換。

---

## 🔄 更新應用

每次推送代碼到 GitHub，Render 會自動重新部署：

```bash
# 修改代碼後
git add .
git commit -m "Update: 添加新功能"
git push origin main

# Render 會自動檢測並重新部署（約 3-5 分鐘）
```

---

## 📊 監控和管理

### 查看日誌

1. 在 Render Dashboard 找到你的服務
2. 點擊 **"Logs"** 標籤
3. 實時查看應用日誌

### 查看指標

在 **"Metrics"** 標籤可以看到：
- CPU 使用率
- 記憶體使用
- 請求數量
- 響應時間

### 手動重啟

如果需要重啟服務：
1. 點擊右上角 **"Manual Deploy"**
2. 選擇 **"Clear build cache & deploy"**（如果遇到問題）

---

## ⚠️ 免費方案限制處理

### 休眠問題

**問題**：應用閒置 15 分鐘後會休眠，首次訪問需要等待 30-60 秒

**解決方案**：

#### 方案 1：外部喚醒服務（推薦）

使用免費的 Cron Job 服務定期喚醒：

**UptimeRobot**（推薦）：
1. 訪問 [uptimerobot.com](https://uptimerobot.com)
2. 註冊免費帳號
3. 添加新的監控：
   - Monitor Type: HTTP(s)
   - URL: `https://你的應用URL.onrender.com/health`
   - Monitoring Interval: 5 分鐘
4. 這樣每 5 分鐘會自動訪問一次，保持應用活躍

**Cron-job.org**：
```
URL: https://你的應用URL.onrender.com/health
Interval: */10 * * * *  (每 10 分鐘)
```

#### 方案 2：在首頁添加提示

在 `templates/index.html` 添加載入提示：

```html
<!-- 在 <body> 開頭添加 -->
<div id="loading-notice" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center" style="display: none;">
    <div class="bg-white p-8 rounded-lg shadow-lg text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p class="text-lg font-semibold">應用正在喚醒中...</p>
        <p class="text-gray-600 mt-2">首次載入約需 30 秒，請稍候</p>
    </div>
</div>

<script>
// 檢測載入時間，超過 3 秒顯示提示
setTimeout(() => {
    if (document.readyState !== 'complete') {
        document.getElementById('loading-notice').style.display = 'flex';
    }
}, 3000);

window.addEventListener('load', () => {
    document.getElementById('loading-notice').style.display = 'none';
});
</script>
```

---

## 🆙 升級到付費方案

當你的應用需要更好的性能時，可以升級：

### Render 付費方案

| 方案 | 價格 | RAM | 特點 |
|------|------|-----|------|
| **Starter** | $7/月 | 512MB | 不休眠 |
| **Standard** | $25/月 | 2GB | 更好性能 |
| **Pro** | $85/月 | 4GB | 專業級 |

**升級方法**：
1. 在 Dashboard 點擊你的服務
2. 點擊 **"Settings"** → **"Instance Type"**
3. 選擇新方案
4. 確認付款方式

---

## 🐛 常見問題

### Q: 部署失敗怎麼辦？

**檢查清單**：
1. 確認 `requirements.txt` 正確
2. 確認 `gunicorn.conf.py` 存在
3. 確認 `wsgi.py` 正確
4. 查看 Render 日誌中的錯誤訊息

**常見錯誤**：

```
Error: No module named 'flask'
→ 檢查 requirements.txt 是否包含 Flask
```

```
Error: Failed to bind to 0.0.0.0:10000
→ Render 使用內部端口，需要在 gunicorn.conf.py 中設置
```

### Q: 如何查看錯誤日誌？

1. Render Dashboard → 你的服務
2. 點擊 **"Logs"** 標籤
3. 篩選 Error 級別

### Q: 如何連接資料庫？

免費方案可以連接：
- PostgreSQL（Render 提供免費 90 天）
- MongoDB Atlas（免費）
- Supabase（免費）

### Q: 可以使用自定義域名嗎？

**免費方案**：只能使用 `.onrender.com` 子域名

**付費方案**：可以綁定自己的域名（需要 Starter 以上）

---

## 📱 移動端優化

確保你的應用在手機上也能正常使用：

1. 已使用響應式設計（Tailwind CSS）
2. 設置了 viewport meta 標籤
3. 測試不同螢幕尺寸

---

## 🎯 下一步

部署成功後：

1. ✅ 分享你的應用 URL
2. ✅ 設置 UptimeRobot 防止休眠
3. ✅ 收集用戶反饋
4. ✅ 監控性能指標
5. ✅ 根據需要升級方案

---

## 📞 需要幫助？

- Render 文檔: https://render.com/docs
- Render 社群: https://community.render.com
- 專案 Issues: [在你的 GitHub 倉庫]

---

**祝部署順利！** 🎉

如果遇到任何問題，請查看 Render 日誌或聯繫支援。
