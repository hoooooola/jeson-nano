# ADR-0003: GPU Access for Gazebo Harmonic in Docker (Intel iGPU)

## Status
**Accepted** (2026-01-13)

## Context
在 Ubuntu 22.04 host 上，使用 Docker 執行 Gazebo Harmonic（Intel integrated GPU），並與 ArduPilot SITL、MAVProxy 進行聯合模擬時，發生以下問題：

- `libEGL warning: failed to open /dev/dri/renderD128: Permission denied`
- Gazebo 啟動但 Render thread 失敗
- ArduPilot Gazebo plugin 持續 reset
- MAVProxy 顯示 `Waiting for heartbeat`

即使在 Host 端將 `/dev/dri/*` 設為 `chmod 666`，問題仍持續存在。

## Problem
Docker container 內：
- Dockerfile 使用 `USER dev` 將使用者寫死
- `dev` 使用者未加入 `video` / `render` 群組
- Docker Compose 的 `user:` 設定被 Dockerfile `USER` 覆蓋
- Intel GPU 環境中誤設 NVIDIA 環境變數

Mesa / EGL / DRM 在初始化時需要：
- 正確的 UID / GID
- 正確的 DRM 群組（`render` / `video`）
- 非 NVIDIA runtime 誤導

導致 EGL 在 DRM authentication 階段失敗，而非單純 POSIX 權限錯誤。

## Decision
採取以下設計決策：

1. **Dockerfile 不寫死 USER**
   - GPU 權限由 runtime（docker-compose）決定
   - Container user UID/GID 與 Host 對齊

2. **Container user 必須屬於 `video` 與 `render` 群組**

3. **Intel GPU 環境完全移除 NVIDIA 相關環境變數**

4. **Gazebo / SITL / MAVProxy 拆分為獨立 container**

## Implementation

### Dockerfile 原則
- 僅建立使用者，不設定 `USER`
- 不 hardcode `/home/dev` 路徑於 entrypoint
- GPU 群組在 build-time 與 runtime 皆可對齊

### docker-compose 原則
```yaml
user: "${UID}:${GID}"
group_add:
  - video
  - render
devices:
  - /dev/dri:/dev/dri
# 不設定 NVIDIA_VISIBLE_DEVICES 等變數
```

## Consequences

### 正面影響
- Gazebo Harmonic GPU 渲染穩定
- ArduPilot plugin timing 穩定
- MAVProxy heartbeat 正常
- 架構可擴充至 Jetson / discrete GPU

### 負面影響
- Compose 設定略為複雜
- 需要在 Host `export UID/GID`

## Notes
> `chmod 666 /dev/dri/*` 為**不可靠** workaround。
> DRM / EGL 需通過 kernel authentication，非純檔案權限。
