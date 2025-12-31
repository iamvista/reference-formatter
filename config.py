"""
應用配置文件
Production Configuration
"""

import os
from datetime import timedelta


class Config:
    """基礎配置"""

    # 安全性
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-please-change-in-production'

    # 文件上傳
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = True  # 僅 HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # CSRF 保護
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

    # API 配置
    CROSSREF_EMAIL = os.environ.get('CROSSREF_EMAIL', 'support@example.com')

    # 速率限制
    RATELIMIT_ENABLED = os.environ.get('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
    RATELIMIT_DEFAULT = "100/hour"
    RATELIMIT_STORAGE_URL = "memory://"

    # 日誌
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')


class DevelopmentConfig(Config):
    """開發環境配置"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """生產環境配置"""
    DEBUG = False
    TESTING = False

    # 確保設定了密鑰
    if not os.environ.get('SECRET_KEY'):
        raise ValueError("生產環境必須設定 SECRET_KEY 環境變量！")


class TestingConfig(Config):
    """測試環境配置"""
    TESTING = True
    WTF_CSRF_ENABLED = False


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
