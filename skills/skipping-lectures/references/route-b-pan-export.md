---
name: route-b-pan-export
description: 百度网盘视频 → 批量导出 AI 课件 PPT/讲稿/笔记（baidu-ai-batch 全流程）
---

# 路线 B：网盘视频 → AI 课件/讲稿/笔记

仓库：`https://github.com/jing1312/baidu-ai-batch`（公开，master，MIT）

## 前置

- Node 18+，只需 `npm install`（仅依赖 `ws`）
- 调试浏览器登录百度网盘（见 `cdp-login` playbook）
- `cp config.example.json config.json`，字段：
  - `videoFolder`：网盘内视频目录（以 `/` 结尾）
  - `skipList`：跳过名单（黑屏/损坏的视频）
  - `minContentLen`：防假成功字数阈值（默认 100）

## 任务

```bash
node bin/list-files.cjs           # 生成视频清单 video-list.txt（用网盘 API）
node bin/export-ppt.cjs           # ① 批量导出 AI 课件 PPT（存回网盘视频目录）
node bin/extract-manuscript.cjs   # ② 批量提取 AI 讲稿 → output/*.txt
node bin/export-notes.cjs         # ③ 批量生成并导出 AI 笔记（PDF 存网盘 + 本地 TXT）
# 全部支持断点续传；--force 强制重跑已完成项
```

油猴版：`userscript/baidu-ai-batch.user.js`（Tampermonkey，免 Node，
在网盘文件列表页点「收集本目录视频」→「开始跑批」）

## 与 pipeline 衔接

- pipeline 的 `media_urls/all_fresh_media_urls.csv` 提供全部视频直链
- 网盘离线下载对内网域名（`*.ncu.edu.cn`）不保证可用 → 本地批量下载改名后上传，
  传完本地删（视频只在网盘）
- 流程：直链 CSV → 下载 → 改名 → 上传网盘 → baidu-ai-batch 批量产出

## 关键坑

- 串行执行，别并发（限流）；单节失败自动跳过，可事后重跑
- 假成功：生成失败留 85~91 字占位模板，按 `minContentLen` 判定，不会存空壳
- PPT 导出要点课件区右上角导出图标（`.ai-course__export-container`），聊天框快捷指令必挂
- 笔记在 `#noteIframe`（跨域读不到）→ iframe URL 单独开标签页读
- 重复跑会积累带时间戳的重复 PPT 文件，记得清理
- 服务端生成失败的重跑也没用（黑屏/无内容/整门课挂掉），需网页端手动重试
