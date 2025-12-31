#!/bin/bash

# 學術文獻格式整理工具 - 一鍵部署腳本
# Reference Formatter - Quick Deploy Script

set -e  # 遇到錯誤立即退出

echo "=========================================="
echo "學術文獻格式整理工具 - 部署腳本"
echo "Reference Formatter Deployment"
echo "=========================================="
echo ""

# 檢測操作系統
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

echo "🖥️  檢測到系統: ${MACHINE}"
echo ""

# 1. 檢查 Python 版本
echo "📦 檢查 Python 版本..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 未安裝，請先安裝 Python 3.9+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python 版本: ${PYTHON_VERSION}"
echo ""

# 2. 創建虛擬環境
echo "🔧 創建虛擬環境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ 虛擬環境已創建"
else
    echo "ℹ️  虛擬環境已存在"
fi
echo ""

# 3. 激活虛擬環境並安裝依賴
echo "📥 安裝依賴套件..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ 依賴安裝完成"
echo ""

# 4. 設置環境變量
echo "⚙️  配置環境變量..."
if [ ! -f ".env" ]; then
    cp .env.example .env

    # 生成隨機 SECRET_KEY
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

    # 替換 .env 中的密鑰
    if [[ "$MACHINE" == "Mac" ]]; then
        sed -i '' "s/your-secret-key-here-change-this/${SECRET_KEY}/" .env
    else
        sed -i "s/your-secret-key-here-change-this/${SECRET_KEY}/" .env
    fi

    echo "✅ 環境變量已創建（.env）"
    echo "⚠️  請編輯 .env 文件以配置其他選項"
else
    echo "ℹ️  .env 文件已存在"
fi
echo ""

# 5. 創建必要的目錄
echo "📁 創建必要目錄..."
mkdir -p logs data uploads
echo "✅ 目錄創建完成"
echo ""

# 6. 詢問部署模式
echo "🚀 選擇部署模式："
echo "1) 開發模式（使用 Flask 內建服務器）"
echo "2) 生產模式（使用 Gunicorn）"
echo "3) Docker 部署"
read -p "請選擇 (1/2/3): " DEPLOY_MODE

case $DEPLOY_MODE in
    1)
        echo ""
        echo "🔄 啟動開發服務器..."
        export FLASK_ENV=development
        python3 app.py
        ;;
    2)
        echo ""
        echo "🔄 啟動生產服務器（Gunicorn）..."
        export FLASK_ENV=production

        # 檢查是否安裝了 gunicorn
        if ! command -v gunicorn &> /dev/null; then
            echo "📦 安裝 Gunicorn..."
            pip install gunicorn
        fi

        # 詢問端口
        read -p "請輸入端口號 (默認 8080): " PORT
        PORT=${PORT:-8080}

        echo "✅ 在端口 ${PORT} 上啟動..."
        gunicorn --config gunicorn.conf.py --bind 0.0.0.0:${PORT} wsgi:app
        ;;
    3)
        echo ""
        echo "🐳 Docker 部署..."

        # 檢查 Docker
        if ! command -v docker &> /dev/null; then
            echo "❌ Docker 未安裝，請先安裝 Docker"
            exit 1
        fi

        # 構建映像
        echo "📦 構建 Docker 映像..."
        docker build -t reference-formatter:latest .

        # 詢問端口
        read -p "請輸入端口號 (默認 8080): " PORT
        PORT=${PORT:-8080}

        # 運行容器
        echo "🔄 啟動 Docker 容器..."
        docker run -d \
            --name reference-formatter \
            -p ${PORT}:8080 \
            -e FLASK_ENV=production \
            -e SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))") \
            --restart unless-stopped \
            reference-formatter:latest

        echo ""
        echo "✅ Docker 容器已啟動"
        echo "📊 查看日誌: docker logs -f reference-formatter"
        echo "🛑 停止容器: docker stop reference-formatter"
        echo ""
        ;;
    *)
        echo "❌ 無效的選項"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "✨ 部署完成！"
echo ""
echo "📍 應用地址: http://localhost:${PORT:-8080}"
echo "📖 API 文檔: http://localhost:${PORT:-8080}/health"
echo ""
echo "📚 更多資訊請查看:"
echo "   - README.md - 專案介紹"
echo "   - DEPLOYMENT.md - 詳細部署指南"
echo "   - SECURITY.md - 安全性指南"
echo "   - PERFORMANCE.md - 性能優化指南"
echo "=========================================="
