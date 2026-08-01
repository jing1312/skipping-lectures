---
name: route-index
description: 路由表：按用户意图和场景选择正确的 playbook，只读取当前任务需要的文件
---

# 路由索引

先判断用户视频在哪、要什么产出，再按表取对应 playbook。**只读取当前任务需要的
文件，不要一次读完所有 playbook。**

## 路由表

| Playbook | 场景 | 文件 |
|---|---|---|
| `route-a-transcribe` | 平台录播 → 转写文本（pipeline：列表/直链/抽音频/ASR） | [route-a-transcribe.md](route-a-transcribe.md) |
| `route-b-pan-export` | 网盘视频 → AI 课件 PPT/讲稿/笔记（baidu-ai-batch） | [route-b-pan-export.md](route-b-pan-export.md) |
| `cdp-login` | 调试浏览器（CDP 9222）登录态，任何路线的前置 | [cdp-login.md](cdp-login.md) |
| `troubleshooting` | 直链过期/CDP 连不上/假成功/限流等排障 | [troubleshooting.md](troubleshooting.md) |

## 路由规则

1. **视频已在百度网盘** → 只读 `route-b-pan-export`（必要时 + `cdp-login`）
2. **视频还在学校平台** → 只读 `route-a-transcribe`（必要时 + `cdp-login`），
   需要 PPT 再补 `route-b-pan-export` 的「与 pipeline 衔接」一节
3. **出现异常现象**（401/403、卡住、空壳文件）→ 补读 `troubleshooting`
4. 两路线不互斥：文本和 PPT/笔记可以都做，但**串行执行、分步汇报**
5. 平台/网盘页面改版导致脚本失效 → 按 `route-a-transcribe` 的接口要点重新探测，
   不要硬猜
