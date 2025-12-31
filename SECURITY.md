# 安全性指南 / Security Guide

## 🔒 安全最佳實踐

### 1. 環境變量管理

**切勿將敏感資訊提交到 Git！**

```bash
# ❌ 錯誤
SECRET_KEY = "my-secret-123"  # 寫死在代碼中

# ✅ 正確
SECRET_KEY = os.environ.get('SECRET_KEY')  # 從環境變量讀取
```

**生成強密鑰**：
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 2. HTTPS 強制使用

生產環境**必須**使用 HTTPS：

```python
# config.py
class ProductionConfig(Config):
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
```

### 3. 輸入驗證

所有用戶輸入都應該驗證：

```python
# 文件大小限制
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# 文字長度限制
if len(text) > 100000:  # 10萬字符
    return jsonify({'error': '輸入過長'}), 400
```

### 4. API 速率限制

防止 API 濫用：

```bash
# 安裝 Flask-Limiter
pip install Flask-Limiter

# app.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/parse')
@limiter.limit("10 per minute")
def parse_references():
    # ...
```

### 5. CORS 設置

如果需要跨域訪問：

```python
from flask_cors import CORS

# 限制允許的來源
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://your-domain.com"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})
```

### 6. 防止 XSS 攻擊

- 使用 Jinja2 自動轉義
- 前端使用 `escapeHtml()` 函數
- 設置 Content Security Policy (CSP)

```python
@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

### 7. 依賴安全

定期更新依賴套件：

```bash
# 檢查安全漏洞
pip install safety
safety check

# 更新套件
pip list --outdated
pip install --upgrade <package-name>
```

### 8. 日誌安全

**不要記錄敏感資訊**：

```python
# ❌ 錯誤
logger.info(f"User password: {password}")

# ✅ 正確
logger.info(f"User login attempt: {username}")
```

## 🚨 安全檢查清單

部署前檢查：

- [ ] SECRET_KEY 使用強隨機值
- [ ] FLASK_ENV=production（關閉 DEBUG）
- [ ] 使用 HTTPS
- [ ] 設置 CORS 限制
- [ ] 實施速率限制
- [ ] 限制文件上傳大小
- [ ] 設置安全 HTTP 標頭
- [ ] 定期更新依賴
- [ ] 使用非 root 用戶運行
- [ ] 設置防火牆規則
- [ ] 實施日誌監控
- [ ] 備份重要數據

## 🔐 常見安全問題

### Q: 如何防止 SQL 注入？
A: 本應用不使用資料庫，但如果添加資料庫功能，請使用 ORM（如 SQLAlchemy）或參數化查詢。

### Q: 如何防止 DDoS 攻擊？
A:
1. 使用 Cloudflare 等 CDN
2. 實施速率限制
3. 設置 Nginx 連接限制

### Q: API 密鑰應該如何管理？
A: 使用環境變量或專門的密鑰管理服務（AWS Secrets Manager、HashiCorp Vault）

## 📋 安全更新流程

1. **監控漏洞**：訂閱 GitHub Security Advisories
2. **定期審核**：每月檢查依賴更新
3. **測試更新**：先在開發環境測試
4. **逐步部署**：使用藍綠部署或金絲雀發布
5. **監控日誌**：觀察異常活動

## 🆘 安全事件響應

如發現安全漏洞：

1. **不要公開披露**，請發郵件至 security@your-domain.com
2. 提供詳細的漏洞描述和復現步驟
3. 我們將在 48 小時內回應
4. 修復後會在 Release Notes 中致謝

## 📚 參考資源

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/latest/security/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)

---

**安全是持續的過程，不是一次性的任務！** 🔐
