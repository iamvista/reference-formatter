# 快速部署指南 - 給完全新手

## 📍 您現在的位置

您已經註冊了 Render 帳號，太棒了！現在讓我們一步步完成部署。

---

## 🎯 部署步驟總覽

```
步驟 1: 上傳代碼到 GitHub (10分鐘)
   ↓
步驟 2: 在 Render 創建服務 (5分鐘)
   ↓
步驟 3: 設置環境變量 (3分鐘)
   ↓
完成！🎉
```

---

## 步驟 1：上傳代碼到 GitHub

### 1.1 註冊 GitHub（如果還沒有帳號）

1. 訪問：https://github.com
2. 點擊 **"Sign up"**
3. 填寫：
   - Email（電子郵件）
   - Password（密碼）
   - Username（用戶名）
4. 完成驗證
5. 登入

### 1.2 創建新倉庫

1. 登入 GitHub 後，點擊右上角的 **"+"** → **"New repository"**

2. 填寫：
   ```
   Repository name: reference-formatter
   Description: 學術文獻格式整理工具

   選擇: ● Public (公開 - 免費)

   不要勾選任何選項！
   ```

3. 點擊綠色按鈕 **"Create repository"**

4. 創建後，**保留這個頁面**（等下會用到）

### 1.3 上傳代碼

#### 方法 A：使用終端機（推薦）

**打開終端機**：
- **Mac**: 按 `Command + 空格`，輸入 "Terminal"
- **Windows**: 按 `Windows + R`，輸入 "cmd"

**輸入以下命令**（一行一行複製貼上，每行按 Enter）：

```bash
# 1. 進入專案目錄
cd /Users/vista/reference-formatter

# 2. 初始化 Git
git init

# 3. 添加所有文件
git add .

# 4. 提交
git commit -m "Initial commit: Multi-format reference formatter"

# 5. 設置分支名稱
git branch -M main

# 6. 連接到 GitHub（替換下面的網址！）
# 從 GitHub 頁面複製你的倉庫網址，應該像這樣：
# https://github.com/你的用戶名/reference-formatter.git
git remote add origin https://github.com/你的用戶名/reference-formatter.git

# 7. 推送代碼
git push -u origin main
```

**重要說明**：

第 6 步的網址要替換成**你自己的**！

在 GitHub 創建倉庫後的頁面上，找到這段：
```
…or push an existing repository from the command line

git remote add origin https://github.com/你的用戶名/reference-formatter.git
git branch -M main
git push origin main
```

複製那個網址使用。

**如果要求輸入帳號密碼**：
- Username: 你的 GitHub 用戶名
- Password: **不是密碼！** 需要使用 Personal Access Token

#### 如何創建 GitHub Token（如果需要）

1. GitHub → 右上角頭像 → **Settings**
2. 左側最下方 → **Developer settings**
3. **Personal access tokens** → **Tokens (classic)**
4. **Generate new token (classic)**
5. 勾選 **repo** (所有子選項)
6. 點擊最下方 **Generate token**
7. **複製 token**（只會顯示一次！）
8. 在終端機中，用這個 token 當作密碼

---

#### 方法 B：使用 GitHub Desktop（更簡單）

如果終端機太複雜，可以用圖形介面：

1. 下載 GitHub Desktop：https://desktop.github.com
2. 安裝並登入 GitHub 帳號
3. 點擊 **"Add"** → **"Add existing repository"**
4. 選擇 `/Users/vista/reference-formatter`
5. 點擊 **"Publish repository"**
6. 確認名稱為 `reference-formatter`
7. 取消勾選 **"Keep this code private"**
8. 點擊 **"Publish repository"**

完成！

---

## 步驟 2：在 Render 創建 Web Service

### 2.1 連接 GitHub

1. 訪問：https://dashboard.render.com

2. 點擊右上角 **"New +"** → **"Web Service"**

3. 如果還沒連接 GitHub：
   - 點擊 **"Connect GitHub"**
   - 授權 Render 訪問你的倉庫
   - 選擇 **"All repositories"** 或只選 `reference-formatter`

4. 找到並點擊 **"reference-formatter"** 旁的 **"Connect"** 按鈕

### 2.2 配置服務

現在會進入配置頁面，按照以下填寫：

#### 基本設定

```
Name: reference-formatter
(或任何你喜歡的名字，但建議用英文)

Region: Singapore
(選擇離你最近的區域)

Branch: main
(保持預設)

Runtime: Python 3
(如果沒有自動選擇，手動選擇)
```

#### 構建設定

**往下滾動**，找到這兩個欄位：

```
Build Command:
pip install -r requirements.txt

Start Command:
gunicorn --config gunicorn.conf.py wsgi:app
```

**完全照抄**，不要改動！

#### 選擇方案

**繼續往下滾動**，找到 **"Instance Type"**：

```
選擇: Free
(不要選其他的！)
```

### 2.3 設置環境變量

在同一頁面，找到 **"Environment Variables"** 區塊：

點擊 **"Add Environment Variable"** 按鈕

添加以下兩個變量：

**變量 1**：
```
Key: FLASK_ENV
Value: production
```

**變量 2**：
```
Key: SECRET_KEY
Value: (需要生成，見下方)
```

#### 如何生成 SECRET_KEY

**在終端機中執行**：
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

會輸出一串像這樣的文字：
```
a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456
```

**複製這串文字**，貼到 SECRET_KEY 的 Value 欄位中。

### 2.4 開始部署

檢查所有設定：
- ✅ Build Command 正確
- ✅ Start Command 正確
- ✅ Instance Type 是 Free
- ✅ 環境變量已添加

確認無誤後，點擊最下方的綠色按鈕：
```
Create Web Service
```

---

## 步驟 3：等待部署完成

### 3.1 觀察部署過程

點擊 Create 後，會跳轉到部署日誌頁面。

你會看到這些訊息（需要 3-5 分鐘）：

```
==> Building...
==> Downloading dependencies...
==> Installing Python packages...
==> Starting service...
==> Deploy live ✓
```

**如果看到綠色的 "Live"**，恭喜！部署成功了！🎉

### 3.2 獲取網址

部署成功後，在頁面頂部會看到你的網址：

```
https://reference-formatter-xxxx.onrender.com
```

**點擊這個網址**，應該會打開你的應用！

---

## 步驟 4：測試應用

### 4.1 基本測試

1. 打開你的應用網址
2. **第一次打開可能需要等待 30-60 秒**（這是正常的）
3. 應該會看到文獻格式整理工具的介面

### 4.2 功能測試

在輸入框中貼上這段測試文獻：

```
Smith, J. (2020). The impact of climate change on biodiversity. Nature, 582(7812), 123-145. https://doi.org/10.1038/nature12345
```

1. 選擇格式（APA / MLA / Chicago / Harvard）
2. 點擊「解析並格式化」
3. 應該會看到格式化後的結果
4. 試試切換不同格式

如果一切正常，**部署完成**！🎊

---

## 步驟 5：防止休眠（重要！）

### 5.1 問題說明

Render 免費方案會在閒置 15 分鐘後**自動休眠**。
下次訪問時需要等待 30-60 秒喚醒。

### 5.2 解決方案：UptimeRobot

使用免費的 UptimeRobot 每 5 分鐘自動喚醒你的應用。

**設置步驟**：

1. 訪問：https://uptimerobot.com

2. 點擊 **"Register for FREE"** 註冊

3. 登入後，點擊 **"+ Add New Monitor"**

4. 填寫：
   ```
   Monitor Type: HTTP(s)

   Friendly Name: Reference Formatter

   URL: https://你的應用網址.onrender.com/health
   (替換成你的實際網址，記得加上 /health)

   Monitoring Interval: 5 minutes
   ```

5. 點擊 **"Create Monitor"**

完成！現在你的應用每 5 分鐘會被自動訪問一次，永不休眠！

---

## 🎉 恭喜！部署完成

你現在擁有：
- ✅ 一個運行中的網頁應用
- ✅ 免費的 HTTPS 網址
- ✅ 自動部署（推送代碼到 GitHub 就會更新）
- ✅ 永不休眠的服務

### 你的應用網址：
```
https://你的應用名稱.onrender.com
```

---

## 🔄 如何更新應用

以後如果要更新代碼：

```bash
# 1. 修改代碼後
cd /Users/vista/reference-formatter

# 2. 提交更改
git add .
git commit -m "更新說明"

# 3. 推送到 GitHub
git push origin main
```

Render 會自動檢測更新並重新部署（約 3-5 分鐘）。

---

## 🆘 遇到問題？

### 問題 1：部署失敗

**檢查清單**：
1. GitHub 上的代碼完整嗎？
2. Build Command 和 Start Command 正確嗎？
3. 環境變量設置了嗎？

**查看日誌**：
- Render Dashboard → 你的服務 → Logs

### 問題 2：網頁打不開

**可能原因**：
1. 第一次訪問需要等待（30-60 秒）
2. 服務休眠了，刷新頁面等待喚醒
3. 部署失敗，查看 Render 日誌

### 問題 3：功能不正常

**檢查**：
1. 瀏覽器控制台有錯誤嗎？（F12 打開）
2. Render 日誌有錯誤訊息嗎？

---

## 📚 下一步

1. **分享你的應用**
   - 複製網址分享給朋友
   - 添加到簡歷或作品集

2. **持續改進**
   - 收集用戶反饋
   - 添加新功能
   - 優化使用體驗

3. **監控使用**
   - Render Dashboard 可以看到訪問統計
   - UptimeRobot 可以看到運行時間

---

## 💡 小技巧

### 自定義網址（付費功能）

免費版只能用 `.onrender.com` 網址。
如果想要自己的域名（如 `myapp.com`），需要升級到付費方案。

### 查看訪問統計

Render Dashboard → 你的服務 → Metrics
可以看到：
- 請求數量
- 響應時間
- 記憶體使用

---

**祝您使用順利！** 🚀

有任何問題隨時問我！
