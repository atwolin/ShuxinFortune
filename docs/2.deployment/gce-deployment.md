# Google Compute Engine 部署指南

本指南說明如何在 Google Compute Engine (GCE) 上使用 Container-Optimized OS 部署 ShuxinFortune 應用程式，並透過 cloud-init 自動化 Docker Compose 設置。

## 📋 前置準備

- Google Cloud Platform (GCP) 帳號
- 本地安裝 `gcloud` CLI

---

## 🚀 完整部署步驟

### 第一部分：GCP 專案與資源設置

#### 1️⃣ 建立 GCP 專案

```bash
# 設定專案名稱變數
export PROJECT_ID="shuxin-fortune"
export PROJECT_NAME="ShuxinFortune"

# 建立新專案
gcloud projects create $PROJECT_ID \
  --name="$PROJECT_NAME"

# 設定為當前專案
gcloud config set project $PROJECT_ID

# 查看專案資訊
gcloud projects describe $PROJECT_ID
```

**注意事項:**

- 專案 ID 必須在全球範圍內唯一
- 專案 ID 一旦建立無法更改
- 如果您有組織，可以使用 `--organization=ORGANIZATION_ID` 參數

#### 2️⃣ 啟用必要的 API

```bash
# 啟用 Compute Engine API
gcloud services enable compute.googleapis.com

# 啟用其他可能需要的 API
gcloud services enable storage-api.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable monitoring.googleapis.com

# 查看已啟用的服務
gcloud services list --enabled
```

#### 3️⃣ 設定計費帳戶（必須）

```bash
# 列出可用的計費帳戶
gcloud billing accounts list

# 將計費帳戶連結到專案（替換為您的計費帳戶 ID）
gcloud billing projects link $PROJECT_ID \
  --billing-account=0X0X0X-0X0X0X-0X0X0X
```

**重要:** 沒有連結計費帳戶，即使在免費額度內也無法建立資源。

#### 4️⃣ 設定防火牆規則

```bash
# 允許 HTTP 流量（port 80）
gcloud compute firewall-rules create allow-http \
  --allow=tcp:80 \
  --target-tags=http-server \
  --description="Allow HTTP traffic" \
  --direction=INGRESS

# 允許 HTTPS 流量（port 443）
gcloud compute firewall-rules create allow-https \
  --allow=tcp:443 \
  --target-tags=https-server \
  --description="Allow HTTPS traffic" \
  --direction=INGRESS

# 查看防火牆規則
gcloud compute firewall-rules list
```

#### 5️⃣ 預留靜態外部 IP

```bash
# 預留靜態 IP
gcloud compute addresses create shuxin-static-ip \
  --region=us-central1

# 查看靜態 IP 資訊
gcloud compute addresses describe shuxin-static-ip \
  --region=us-central1 \
  --format='get(address)'

# 列出所有靜態 IP
gcloud compute addresses list
```

**注意事項:**

- 靜態 IP 分配給運行中的 VM 時是免費的
- 未使用的靜態 IP 會產生費用（約 $0.01/小時）
- 可以在 GCP Console 中查看 IP 使用狀態

---

### 第二部分：應用程式部署

#### 6️⃣ 生成 Django Secret Key

在本地機器上執行：

```bash
# 進入後端目錄
cd backend

# 啟動 Poetry 虛擬環境
poetry shell

# 生成新的 secret key
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# 複製輸出，下一步會用到
```

#### 7️⃣ 更新 cloud-init.yaml

複製 `cloud-init.example.yaml`，重新命名為 `cloud-init.yaml`。

將 `REPLACE_WITH_YOUR_SECRET_KEY` 替換為上一步生成的 secret key，並更新 `DJANGO_CORS_ALLOWED_ORIGINS`, `DJANGO_CORS_ALLOWED_ORIGINS`。

```bash
# 編輯檔案
nano cloud-init.yaml

# 找到這幾行:
# DJANGO_SECRET_KEY=REPLACE_WITH_YOUR_SECRET_KEY
# DJANGO_CORS_ALLOWED_ORIGINS=YOUR_ALLOWED_ORIGINS
# DJANGO_CSRF_TRUSTED_ORIGINS=YOUR_TRUSTED_ORIGINS

# 替換為實際的 key:
# DJANGO_SECRET_KEY=your-generated-secret-key-here
# DJANGO_CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
# DJANGO_CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

#### 8️⃣ 刪除舊 VM（如果存在）

```bash
# 刪除現有 VM（如果存在）
gcloud compute instances delete shuxin-fortune-vm \
  --zone=us-central1-a \
  --quiet
```

#### 9️⃣ 建立 VM 實例

```bash
gcloud compute instances create shuxin-fortune-vm \
  --zone=us-central1-a \
  --machine-type=e2-micro \
  --image-family=cos-stable \
  --image-project=cos-cloud \
  --boot-disk-size=30GB \
  --tags=http-server,https-server \
  --metadata-from-file=user-data=cloud-init.yaml
```

**這個命令做了什麼:**

- 建立一個 Container-Optimized OS VM
- 使用 cloud-init 寫入 docker-compose.yaml 和 .env 檔案
- 建立 systemd service 透過 Docker 容器執行 docker-compose
- systemd service 會在開機時自動啟動
- 使用 `/var/run/docker.sock` 掛載來控制主機 Docker daemon
- 這種方法避免使用已棄用的 `create-with-container` 命令

**機器類型說明:**

- `e2-micro`: 免費額度內（每月 744 小時）
- `f1-micro`: 較舊的免費方案（不推薦）
- `e2-small`: 需要付費，但效能更好

#### 🔟 分配靜態 IP

等待約 30 秒讓 VM 建立完成，然後分配預留的靜態 IP：

```bash
gcloud compute instances delete-access-config shuxin-fortune-vm \
  --zone=us-central1-a \
  --access-config-name="external-nat"

gcloud compute instances add-access-config shuxin-fortune-vm \
  --zone=us-central1-a \
  --access-config-name="external-nat" \
  --address=$(gcloud compute addresses describe shuxin-static-ip --region=us-central1 --format='get(address)')
```

---

### 第三部分：驗證與測試

#### 1️⃣1️⃣ 檢查 VM 狀態

```bash
# 查看 VM 狀態和 IP
gcloud compute instances describe shuxin-fortune-vm \
  --zone=us-central1-a \
  --format='get(status,networkInterfaces[0].accessConfigs[0].natIP)'
```

#### 1️⃣2️⃣ SSH 進入 VM 並檢查容器

```bash
# SSH 進入 VM
gcloud compute ssh shuxin-fortune-vm --zone=us-central1-a

# 檢查 docker-compose sidecar 容器
docker ps | grep docker

# 等待幾分鐘讓構建完成，然後檢查應用容器
docker ps

# 查看特定容器的日誌
docker logs <container-name>

# 查看所有容器（包括已停止的）
docker ps -a

# 退出 SSH
exit
```

#### 1️⃣3️⃣ 測試應用程式

```bash
# 測試前端（從本地機器執行）
curl http://your-ip-address

# 測試後端 API
curl http://your-ip-address/admin/login/

# 使用瀏覽器訪問
# Frontend: http://your-ip-address
# Backend Admin: http://your-ip-address/admin/
```

**注意:** 首次部署後，Docker 需要 5-10 分鐘來拉取映像和構建容器。

---

### 第四部分：HTTPS 設定

#### 1️⃣4️⃣ 取得 SSL 認證

**注意:** 確認已註解掉 nginx-prod.conf 中 HTTPS 的設定

```bash
# SSH 進入 VM
gcloud compute ssh shuxin-fortune-vm --zone=us-central1-a

# 取得前端容器名稱
FRONTEND_CONTAINER=$(docker ps --filter "name=frontend" --format "{{.Names}}")

# 使用 Certbot 取得 SSL 認證
docker exec -it $FRONTEND_CONTAINER sh -c "certbot certonly --webroot \
  -w /var/www/certbot \
  -d shuxin-fortune.ddns.net \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email"
```

範例輸出

```bash
Saving debug log to /var/log/letsencrypt/letsencrypt.log
Account registered.
Requesting a certificate for your-domain.com

Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/your-domain.com/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/your-domain.com/privkey.pem
This certificate expires on 2026-04-23.
These files will be updated when the certificate renews.

NEXT STEPS:
- The certificate will need to be renewed before it expires. Certbot can automatically renew the certificate in the background, but you may need to take steps to enable that functionality. See https://certbot.org/renewal-setup for instructions.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
If you like Certbot, please consider supporting our work by:
 * Donating to ISRG / Let's Encrypt:   https://letsencrypt.org/donate
 * Donating to EFF:                    https://eff.org/donate-le
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
```

#### 1️⃣5️⃣ 檢查 SSL 認證

```bash
# 檢查 SSL 認證
ls /etc/letsencrypt/live/your-domain.com/
```

#### 1️⃣6️⃣ 更新 cloud-init.yaml 並重建 VM

啟動 HTTP 重新導向 HTTPS。找到這幾行：

```bash
# ======================
# Security Settings (Production)
# ======================

# DJANGO_SECURE_SSL_REDIRECT=True
# DJANGO_SESSION_COOKIE_SECURE=True
# DJANGO_CSRF_COOKIE_SECURE=True
# DJANGO_SECURE_HSTS_SECONDS=2592000
# DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=True
# DJANGO_SECURE_HSTS_PRELOAD=True

# ======================
# Security Settings (Development)
# ======================

DJANGO_SECURE_SSL_REDIRECT=False
DJANGO_SESSION_COOKIE_SECURE=False
DJANGO_CSRF_COOKIE_SECURE=False
DJANGO_SECURE_HSTS_SECONDS=0
DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=False
DJANGO_SECURE_HSTS_PRELOAD=False
```

更新為：

```bash
# ======================
# Security Settings (Production - HTTPS enabled, but Nginx handles redirect)
# ======================

# Let Nginx handle SSL redirect (allows IP access via HTTP)
DJANGO_SECURE_SSL_REDIRECT=False
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
DJANGO_SECURE_HSTS_SECONDS=2592000
DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=True
DJANGO_SECURE_HSTS_PRELOAD=True
```

重做一次步驟 8️⃣ ～ 1️⃣3️⃣ 。

#### 1️⃣7️⃣ 更新 Nginx HTTPS 設定

取消 nginx-prod.conf 中 HTTPS 的註解後，重啟 docker-compose-app.service

```bash
sudo systemctl restart docker-compose-app.service
```

---

## 🔧 常用維護命令

### 查看日誌

```bash
# SSH 進入 VM
gcloud compute ssh shuxin-fortune-vm --zone=us-central1-a

# 查看 systemd service 日誌（即時）
sudo journalctl -u docker-compose-app.service -f

# 查看 systemd service 日誌（最後 50 行）
sudo journalctl -u docker-compose-app.service -n 50

# 查看 cloud-init 日誌
sudo journalctl -u google-startup-scripts.service
```

### 更新應用程式

當您推送新程式碼到 GitHub 後：

```bash
# 方法 1: 重啟 systemd service（推薦）
gcloud compute ssh shuxin-fortune-vm --zone=us-central1-a
sudo systemctl restart docker-compose-app.service
exit

# 方法 2: 手動重建容器
gcloud compute ssh shuxin-fortune-vm --zone=us-central1-a
cd /home/compose
sudo docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /home/compose:/workdir \
  -w /workdir \
  docker/compose:latest \
  down
sudo docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /home/compose:/workdir \
  -w /workdir \
  docker/compose:latest \
  up -d --build --force-recreate --pull always
exit
```

### 重啟 VM

```bash
# 停止 VM
gcloud compute instances stop shuxin-fortune-vm --zone=us-central1-a

# 啟動 VM
gcloud compute instances start shuxin-fortune-vm --zone=us-central1-a

# 重新啟動 VM
gcloud compute instances reset shuxin-fortune-vm --zone=us-central1-a
```

### 檢查服務狀態

```bash
# SSH 進入 VM
gcloud compute ssh shuxin-fortune-vm --zone=us-central1-a

# 檢查 systemd service 狀態
sudo systemctl status docker-compose-app.service

# 檢查 service 是否啟用（開機自動啟動）
sudo systemctl is-enabled docker-compose-app.service

# 查看所有容器
docker ps -a

# 檢查 Docker daemon 狀態
sudo systemctl status docker
```

---

## 🐛 疑難排解

### 應用容器無法啟動

SSH 進入 VM 並檢查 docker-compose sidecar 日誌：

```bash
gcloud compute ssh shuxin-fortune-vm --zone=us-central1-a

# 找到 docker-compose 容器
docker ps -a | grep docker

# 查看容器日誌
docker logs <docker-compose-container-id>

# 檢查 systemd service
sudo systemctl status docker-compose-app.service
sudo journalctl -u docker-compose-app.service -n 100

# 若日誌顯示找不到 docker-compose，則手動拉取最新版本
docker pull docker/compose:latest
```

### 檢查 cloud-init 是否成功執行

```bash
gcloud compute ssh shuxin-fortune-vm --zone=us-central1-a

# 查看 cloud-init 日誌
sudo journalctl -u google-startup-scripts.service

# 檢查檔案是否已建立
ls -la /home/compose/
cat /home/compose/docker-compose.yaml
cat /home/compose/.env
```

### 手動重建容器

如果需要完全重建：

```bash
gcloud compute ssh shuxin-fortune-vm --zone=us-central1-a

# 停止所有容器
cd /home/compose
sudo docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /home/compose:/workdir \
  -w /workdir \
  docker/compose:latest \
  down

# 刪除舊映像（可選）
docker images
docker rmi <image-id>

# 重新啟動
sudo systemctl restart docker-compose-app.service
```

### 檢查磁碟空間

```bash
gcloud compute ssh shuxin-fortune-vm --zone=us-central1-a

# 查看磁碟使用情況
df -h

# 查看 Docker 磁碟使用
docker system df

# 清理未使用的 Docker 資源
docker system prune -a
```

---

## 💰 費用說明與成本優化

### 免費額度（Always Free）

Google Cloud 提供永久免費額度：

- ✅ **e2-micro 實例**: 每月 744 小時（足夠運行一個持續運行的 VM）
  - 地區限制：美國地區（us-west1, us-central1, us-east1）
  - 規格：0.25-1 vCPU, 1 GB RAM

- ✅ **靜態 IP**: 綁定到運行中的 VM 時免費
  - 未使用時收費：約 $0.01/小時 或 $7.2/月

- ✅ **標準持久磁碟**: 每月 30 GB
  - 超過部分：約 $0.04/GB/月

- ✅ **網路流量（Egress）**:
  - 北美到所有地區：每月 1 GB
  - 超過部分價格依目的地而定

### 成本優化建議

1. **選擇正確的地區**

   ```bash
   # 使用 us-central1, us-west1, or us-east1 享受免費額度
   --zone=us-central1-a
   ```

2. **監控使用量**

   ```bash
   # 在 GCP Console 中設定預算警報
   # Billing > Budgets & alerts
   ```

3. **停止未使用的 VM**

   ```bash
   # 停止 VM（保留磁碟，只收磁碟費用）
   gcloud compute instances stop shuxin-fortune-vm --zone=us-central1-a
   ```

4. **釋放未使用的靜態 IP**

   ```bash
   # 如果不再需要，釋放靜態 IP
   gcloud compute addresses delete shuxin-static-ip --region=us-central1
   ```

5. **清理 Docker 資源**

   ```bash
   # 定期清理未使用的映像和容器
   docker system prune -a
   ```

### 查看費用

```bash
# 查看當前專案的費用
gcloud billing accounts list
gcloud billing projects describe $PROJECT_ID

# 或在 GCP Console 查看:
# https://console.cloud.google.com/billing
```

---

## ❓ 常見問題 (FAQ)

### Q: 為什麼選擇 Container-Optimized OS？

A: Container-Optimized OS 是針對運行容器優化的輕量級作業系統，具有：

- 自動安全更新
- 更小的攻擊面
- 更快的啟動時間
- Docker 預先安裝

### Q: 可以使用其他機器類型嗎？

A: 可以，但請注意：

- `e2-micro` 是免費額度內的最佳選擇
- `e2-small` 或更大的實例會產生費用
- 可以使用 `--machine-type` 參數更改

### Q: 如何更改部署地區？

A: 修改所有命令中的 `--zone` 和 `--region` 參數。建議使用 us-central1, us-west1, 或 us-east1 以符合免費額度資格。
