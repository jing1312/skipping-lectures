---
name: skipping-lectures
description: >-
  Turn recorded lectures into study-ready material: transcripts, key points, AI courseware PPTs and notes, so the user can skip classes and still ace exams. Use when the user mentions 录播课/网课/课程回放/不想上课/翘课, turning videos into notes or text, extracting course key points, batch transcribing lectures, exporting courseware/讲稿/笔记, or exam prep material, or when videos must be processed from a school platform (zbkt.ncu.edu.cn 香樟云课堂) or Baidu Pan (百度网盘) AI batch export. Not for generic note-taking, video editing, or unrelated ASR.
---

# skipping-lectures — 录播课 → AI 复习资料流水线

学校每节课都有录播，老师课上强调的内容几乎都出现在试卷上。本 skill 把录播视频
变成「一页纸就能复习」的资料：**转写文本 / 提炼重点 / AI 课件 PPT / 讲稿 / 笔记**。

这是**编排层**：实际干活的是两个配套工具仓库（xiangzhang-course-pipeline、
baidu-ai-batch），本 skill 负责判断走哪条路线、给出正确命令、复用共享知识
（CDP 登录态等）。

## 强制工作流

### 1. 确认目标

- 问清：视频现在在哪（平台没下 / 已下载 / 在网盘）、要什么产出
  （文本 / PPT / 讲稿 / 笔记 / 都要）。一两个问题内搞定，不要追问细节。
- 按「路由表」选路线：视频已在网盘 → B；还在平台 → A；都要 → 先 A 后 B（串行）。
- 两条路线不互斥：文本和 PPT/笔记可以都做。

### 2. 路由 Playbook

- 读 [references/route-index.md](references/route-index.md)，按场景取需要的 playbook。
- **只读当前任务需要的文件**，不要一次读完所有 playbook。

### 3. 环境检查

- 两个仓库是否在本地？常见位置：`D:\文档\学业资料\1大三\ai_test\` 下与仓库同名
  的目录；找不到就 `git clone` 或问用户。
- 调试浏览器是否开着（`curl http://127.0.0.1:9222/json/version` 能通即就绪）；
  没开先启动并请用户登录平台/网盘（见 `cdp-login` playbook）。
- `config.json` 是否已从 `config.example.json` 复制并填好 `courses` / `videoFolder`。

### 4. 计划与执行

- 每步开跑前用一句话告诉用户"现在做 X（第 N 步 / 共 M 步）"，别一次把全部命令
  砸给用户；长步骤（ASR 转写、网盘 AI 导出）说明预期耗时。
- 直链带签名会过期：抽音频/下载报 401/403 时先重跑 `rebuild_fresh_manifest.cjs`
  再重新导出 CSV，不要反复重试同一份过期清单。
- 串行执行是故意的——并发会触发网盘限流（见 `troubleshooting`）。

### 5. 验证

- 核对产物数量与预期（几门课 × 几节 = 多少份），失败项单独列出，别只报总数。
- 网盘 AI 产物注意「假成功」：85~91 字占位模板 = 服务端生成失败（见 `route-b-pan-export`）。

### 6. 收尾汇报

- 产物在哪（`transcripts/<课程>/`、`output/`、网盘视频目录的 PPT）、成功/失败数量、
  失败项的下一步（重跑或手动）。
- 文本类产物提示用户：可丢给任意 LLM 提问/总结，或按课程合并后提炼重点
  （一页纸复习）。

## 安全策略

- 密钥（火山 `VOLC_*`、MiMo `MIMO_API_KEY` 等）只走环境变量或 gitignore 的
  `config.json`，**绝不写进仓库或提交**——两个工具仓库和本 skill 仓库都是公开的。
- 不把任何平台 Cookie / 登录凭证写入代码、日志或文档。
- 只操作用户明确要求处理的课程/视频；不批量触碰无关数据。
- 平台/网盘页面改版时，按接口要点重新探测（CDP 看 Vue 组件、抓接口），不硬猜、
  不逆向平台外的东西。

## 路由表（速览）

| 场景 | Playbook |
|---|---|
| 平台录播 → 转写文本 | [route-a-transcribe](references/route-a-transcribe.md) |
| 网盘视频 → AI PPT/讲稿/笔记 | [route-b-pan-export](references/route-b-pan-export.md) |
| 调试浏览器登录态（前置） | [cdp-login](references/cdp-login.md) |
| 任何异常 | [troubleshooting](references/troubleshooting.md) |

## 用户愿景（为什么这么做）

- 老师课上强调的内容≈考点，录播是完整信息源
- 一节课的文本可能一页纸就够——为深度思考/论文/睡觉争取时间
- 本 skill 的目标是让「不上课」成为可行选择，而不是鼓励摆烂

## 常见短语映射

| 用户说 | 实际要做 |
|--------|----------|
| "把课程录播整理一下" | 先问视频在哪 → 路由 A 或 B |
| "视频太多了不想下" | 路线 A（只抽音频），或 B（视频进网盘） |
| "帮我把网盘里的课批量导 PPT" | 路线 B export-ppt |
| "AI 提炼这门课的重点" | A 转写文本后交给 LLM 总结，或 B 的笔记 |
| "学校平台不让下载" | 平台页面有直链（recordvideo 接口），用 pipeline 提取 |
