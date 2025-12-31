# 性能優化指南 / Performance Guide

## ⚡ 性能優化建議

### 1. 使用緩存

#### Redis 緩存 API 查詢結果

```bash
# 安裝 Redis 和 Flask-Caching
pip install redis flask-caching
```

```python
# app.py
from flask_caching import Cache

cache_config = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
    'CACHE_DEFAULT_TIMEOUT': 3600  # 1 小時
}
cache = Cache(app, config=cache_config)

# 在 api_client.py 中使用
@cache.memoize(timeout=3600)
def query_by_doi(self, doi: str):
    # ... 原有代碼
```

#### 內存緩存（簡單方案）

```python
# 使用 functools.lru_cache
from functools import lru_cache

@lru_cache(maxsize=1000)
def format_reference(ref_data, style):
    # ...
```

### 2. 資料庫優化（如果需要）

如果添加用戶系統或歷史記錄：

```python
# 使用連接池
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'postgresql://user:pass@localhost/dbname',
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

### 3. 異步處理

對於耗時的 API 查詢，使用異步：

```python
# 安裝 Celery
pip install celery redis

# tasks.py
from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379/0')

@celery.task
def enrich_references_async(references):
    # 異步處理文獻補完
    results = []
    for ref in references:
        enriched = api_client.enrich_reference(ref)
        results.append(enriched)
    return results
```

### 4. 靜態資源優化

#### 使用 CDN

```html
<!-- 在 index.html 中 -->
<!-- Tailwind CSS 從 CDN 載入（已實現） -->
<script src="https://cdn.tailwindcss.com"></script>
```

#### 壓縮和合併

```python
# 安裝 Flask-Assets
pip install flask-assets cssmin jsmin

# app.py
from flask_assets import Environment, Bundle

assets = Environment(app)

js = Bundle('js/*.js', filters='jsmin', output='gen/packed.js')
css = Bundle('css/*.css', filters='cssmin', output='gen/packed.css')

assets.register('js_all', js)
assets.register('css_all', css)
```

### 5. Gzip 壓縮

```python
# app.py
from flask_compress import Compress

Compress(app)
```

或在 Nginx 中配置：

```nginx
# nginx.conf
gzip on;
gzip_types text/plain text/css application/json application/javascript;
gzip_min_length 1000;
```

### 6. 資料庫查詢優化

```python
# 批次查詢而非循環查詢
# ❌ 慢
for ref in references:
    result = db.query(ref.doi)

# ✅ 快
dois = [ref.doi for ref in references]
results = db.query_batch(dois)
```

### 7. Worker 配置優化

```python
# gunicorn.conf.py
import multiprocessing

# CPU 密集型任務
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"

# I/O 密集型任務（推薦）
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"  # 需要：pip install gevent
worker_connections = 1000
```

### 8. 前端優化

#### 懶加載

```javascript
// 只在需要時載入大型庫
async function loadHeavyLibrary() {
    const module = await import('./heavy-library.js');
    return module;
}
```

#### 防抖動（Debounce）

```javascript
// 減少 API 調用頻率
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
}

// 使用
const debouncedSearch = debounce(searchReferences, 500);
```

## 📊 性能監控

### 1. 應用性能監控 (APM)

推薦工具：
- **New Relic** - 全面的 APM 解決方案
- **Datadog** - 雲端監控
- **Prometheus + Grafana** - 開源方案

#### 添加 Prometheus 監控

```bash
pip install prometheus-flask-exporter
```

```python
# app.py
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application info', version='1.0.0')
```

訪問 `/metrics` 查看指標。

### 2. 日誌分析

```python
# app.py
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

### 3. 錯誤追蹤

```bash
pip install sentry-sdk[flask]
```

```python
# app.py
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[FlaskIntegration()],
    traces_sample_rate=0.1  # 10% 的請求進行性能追蹤
)
```

## 🧪 性能測試

### 使用 Locust 進行負載測試

```bash
pip install locust
```

創建 `locustfile.py`：

```python
from locust import HttpUser, task, between

class ReferenceFormatterUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def parse_reference(self):
        self.client.post("/parse", json={
            "text": "Smith, J. (2020). Test article. Nature, 582, 123-145.",
            "format": "apa",
            "enrich": False
        })

    @task(1)
    def export_docx(self):
        self.client.post("/export/docx", json={
            "references": [{"formatted": "Test reference"}],
            "style": "apa"
        })

    @task(1)
    def index(self):
        self.client.get("/")
```

運行測試：

```bash
locust -f locustfile.py --host=http://localhost:8080
```

訪問 http://localhost:8089 查看測試結果。

### 使用 ab (Apache Bench)

```bash
# 100 個請求，10 個並發
ab -n 100 -c 10 http://localhost:8080/

# POST 請求測試
ab -n 100 -c 10 -p post.json -T application/json http://localhost:8080/parse
```

## 📈 性能基準

### 目標指標

| 指標 | 目標值 | 備註 |
|------|--------|------|
| 首頁載入時間 | < 2s | TTFB + 渲染 |
| API 響應時間 | < 500ms | 不含外部 API |
| 含 API 補完 | < 3s | 包含 CrossRef 查詢 |
| 並發處理能力 | 100 req/s | 單機配置 |
| 記憶體使用 | < 512MB | 空閒狀態 |
| CPU 使用率 | < 70% | 正常負載 |

### 性能瓶頸識別

1. **慢端點識別**
```python
import time
from functools import wraps

def timing_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = f(*args, **kwargs)
        end = time.time()
        app.logger.info(f'{f.__name__} took {end-start:.2f}s')
        return result
    return wrapper

@app.route('/parse')
@timing_decorator
def parse_references():
    # ...
```

2. **資料庫查詢分析**（如果使用資料庫）
```python
from sqlalchemy import event
from sqlalchemy.engine import Engine
import logging

logging.basicConfig()
logger = logging.getLogger("sqlalchemy.engine")
logger.setLevel(logging.INFO)
```

## 🎯 優化優先級

### 高優先級（立即實施）
1. ✅ 啟用 Gzip 壓縮
2. ✅ 添加 API 響應緩存
3. ✅ 優化 Gunicorn worker 配置
4. ✅ 使用 CDN 託管靜態資源

### 中優先級（流量增長後）
1. 添加 Redis 緩存
2. 實施速率限制
3. 異步處理長時間任務
4. 添加性能監控

### 低優先級（大規模部署）
1. 使用負載均衡器
2. 實施資料庫讀寫分離
3. 使用專門的搜索引擎（Elasticsearch）
4. 微服務架構改造

## 💡 最佳實踐

1. **測量先於優化**：先測量性能，找到真正的瓶頸
2. **逐步優化**：一次優化一個問題
3. **持續監控**：部署後持續監控性能指標
4. **用戶體驗優先**：優化用戶感知的性能（首屏時間、交互響應）

## 📚 參考資源

- [Flask Performance Tips](https://flask.palletsprojects.com/en/latest/tutorial/deploy/#configure-the-secret-key)
- [Gunicorn Performance](https://docs.gunicorn.org/en/stable/design.html)
- [Web.dev Performance](https://web.dev/performance/)

---

**記住：過早優化是萬惡之源，先讓它運行，再讓它更快！** ⚡
