# 舒心好運籤 (Shuxin-Fortune)

> 給正在努力的你：你不孤單 💛

一個可愛風格的抽籤網頁，透過隨機抽籤給予學生鼓勵。採用 Alpine.js + Tailwind CSS (前端) + Django (後端) 架構。

## ✨ 特色

- 🎋 **Q版台灣廟宇風格**：溫柔可愛的紅黃色調
- 🔊 **音效互動**：輕柔的搖籤聲
- 👩‍🏫 **便捷管理介面**：老師可透過 Django Admin 輕鬆編輯籤詩

## 🏗️ 專案架構

```bash
.
├── backend
│   ├── accounts
│   ├── config
│   ├── data
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── lottery
│   ├── manage.py
│   ├── poetry.lock
│   ├── pyproject.toml
│   └── staticfiles
├── compose-prod.yaml
├── compose.yaml
├── frontend
│   ├── assets
│   ├── Dockerfile
│   ├── index.html
│   └── styles.css
└── README.md
```

## 🚀 快速開始

### 前置需求

- Docker
- Docker Compose

### 啟動開發環境

```bash
# 啟動所有服務
docker compose up

# 或在背景執行
docker compose up -d

# 初始化資料庫（首次啟動）
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```

**訪問應用**：

- 🎋 前端抽籤頁面：<http://localhost:8080>
- 🔧 後端管理介面：<http://localhost:8000/admin>

**停止服務**：

```bash
docker compose down
```

## 📝 使用說明

### 學生端

1. 打開網頁
2. 點擊籤筒
3. 享受搖籤動畫和星星特效
4. 查看鼓勵的籤詩
5. 可以無限次抽籤

### 老師端

1. 訪問 `/admin`
2. 登入管理介面
3. 新增/編輯籤詩分類
4. 新增/編輯籤詩內容
5. 啟用/停用籤詩

## 🎨 技術堆疊

- **前端**
  - Alpine.js
  - Tailwind CSS
  - Vanilla JavaScript

- **後端**
  - Django
  - SQLite
  - Poetry

## 🌐 部署

部署架構：

- Nginx 作為反向代理
- 前端靜態檔案由 Nginx 直接服務
- 後端 API 透過 Gunicorn 運行
- 前後端整合在同一域名，避免 CORS 問題

## 📄 授權

MIT License

## 👥 作者

atwolin - [tzuchien@nlplab.cc](mailto:tzuchien@nlplab.cc)
