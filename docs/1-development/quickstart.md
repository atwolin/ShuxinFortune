# 開發指南

> 舒心好運籤使用 Docker 進行開發和部署

## 📋 前置需求

- [Docker](https://docs.docker.com/get-docker/) >= 29.0.0

---

## 🚀 啟動開發環境

### 1. 首次啟動

#### 環境變數

建立 `.env` 檔案（參考 `.env.example`）：

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

#### 啟動服務

```bash
# Clone 專案
git clone https://github.com/atwolin/ShuxinFortune.git
cd ShuxinFortune

# 啟動所有服務
docker compose up -d --build

# 初始化資料庫
docker compose exec backend python manage.py migrate

# 建立管理員帳號
docker compose exec backend python manage.py createsuperuser
```

### 2. 訪問應用

- **前端**：<http://localhost:8080>
- **後端 API**：<http://localhost:8000/api/draw/>
- **管理介面**：<http://localhost:8000/admin>

---

## 資料管理

### 匯出資料

```bash
# 匯出所有資料
docker compose exec backend python manage.py dumpdata > backup.json

# 匯出特定 app
docker compose exec backend python manage.py dumpdata lottery > lottery_backup.json

# 排除某些 app
docker compose exec backend python manage.py dumpdata --exclude auth.permission > backup.json
```

### 匯入資料

```bash
# 複製備份檔到容器
docker cp backup.json shuxin-backend-dev:/app/

# 匯入資料
docker compose exec backend python manage.py loaddata backup.json
```

---

## 🧪 測試與品質控制

### 執行測試

```bash
# 後端測試
docker compose exec backend python manage.py test

# 測試覆蓋率
docker compose exec backend pip install coverage
docker compose exec backend coverage run --source='.' manage.py test
docker compose exec backend coverage report
```

### 程式碼檢查

```bash
# 使用 ruff（已在 pyproject.toml 配置）
docker compose exec backend ruff check .

# 自動修正
docker compose exec backend ruff check --fix .
```

---

## 🔄 更新專案

### 調整資源限制

編輯 `docker compose.yml`：

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```
