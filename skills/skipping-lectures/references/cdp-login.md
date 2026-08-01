---
name: cdp-login
description: 调试浏览器（CDP）登录态：两条路线的共享前置，如何启动、检查、复用
---

# 共享前置：调试浏览器（CDP）

两个工具都通过 CDP 复用**已登录**的浏览器会话，不用逆向、不用登录两次：

```powershell
msedge --remote-debugging-port=9222 --user-data-dir=%LOCALAPPDATA%\edge-debug-profile
```

- 用独立 user-data-dir（与日常浏览器分开），启动后在浏览器里登录平台/网盘，保持开着
- 脚本跑批时**新建标签页**干活，不影响用户正常上网
- 检查是否就绪：`curl http://127.0.0.1:9222/json/version` 能通说明 CDP 在线
- pipeline 的 01_links 脚本用 `--cdp` flag 连接（端口走 config 的 `cdp.port`）；
  baidu-ai-batch 没有 flag，直接读 config 的 `host`/`port`（默认 `127.0.0.1:9222`）

## 登录检查顺序

1. 确认浏览器带 `--remote-debugging-port=9222` 启动（不是普通打开）
2. 在调试浏览器里打开平台实录列表页 / 网盘文件列表页，确认登录态有效
3. 脚本报「未登录」时优先回浏览器手动登录，而不是改脚本
