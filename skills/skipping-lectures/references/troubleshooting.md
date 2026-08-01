---
name: troubleshooting
description: 跨路线的常见故障表：直链过期、CDP 连不上、假成功、限流、ASR 失败、脚本失效
---

# 排障

## 常见故障表

| 现象 | 处理 |
|------|------|
| 抽音频/下载 401/403 | 直链过期 → `node 01_links/rebuild_fresh_manifest.cjs --config config.json --courses=...` 后重导 CSV |
| CDP 连不上 | Edge 需带 `--remote-debugging-port=9222` 启动并保持页面打开 |
| 未登录 | 在调试浏览器里重新登录平台/网盘 |
| validCode 不匹配 | 检查 `platform.signKey`；recordvideo 的 validCode=md5(`id=<videoId>&signKey=<signKey>`) |
| ASR 失败 | 检查 `X-Api-Status-Code`（20000000=成功）、`volc.seedasr.auc` 资源 ID、密钥 |
| 网盘离线下载链接无效 | 平台 URL 是内网地址（`*.ncu.edu.cn`），改走「本地下载 → 上传网盘 → 本地删」 |
| 网盘文件重复 | 下载/上传两次会产生原始名+改名两套文件，手动删原始名那套 |
| PPT/笔记是空壳（85~91 字占位） | 服务端生成失败；重跑也没用，需网页端手动重试那节 |
| 脚本卡住不动 | 断点续传：PPT 看 `state.json`；讲稿/笔记按文件存在跳过，`--force` 重跑 |

## 根本性原则

- **串行执行是故意的**：网盘 AI 并发会触发限流（早期 20 路并发 PPT 失败率 80%，
  改串行后近 100%）。任何"改成并发加速"的冲动都要压回去。
- **平台/网盘结构变了**：两仓库都是实测得出的 DOM/接口逻辑，页面改版就失效——
  按 `route-a-transcribe` 的接口要点（CDP 看 Vue 组件、抓接口）重新适配，不要硬猜。
- **密钥只走环境变量或 gitignore 的 config.json**：仓库是公开的，密钥提交=泄露。
