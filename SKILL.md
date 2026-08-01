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
（CDP 登录态等）。密钥只走环境变量或 gitignore 的 `config.json`，**绝不写进仓库**。

## 两条路线

| 路线 | 适用场景 | 产出 | 工具 |
|------|----------|------|------|
| **A 转写为主** | 平台录播还在学校平台、本地磁盘紧张 | 每节课一份文本（复习用） | xiangzhang-course-pipeline（抽音频 + ASR） |
| **B 网盘 AI 产出** | 视频已在百度网盘（或愿意上传） | AI 课件 PPT / 讲稿 / 笔记 | baidu-ai-batch |

两条路线不互斥：文本和 PPT/笔记可以都做。视频**已**在网盘 → 直接 B；
还没下载/抽过音频 → 默认先 A 拿文本（省空间），需要 PPT 再走 B。

## 工作流

1. **确认目标**：问清视频现在在哪（平台没下/已下载/在网盘）、要什么产出（一两个
   问题内搞定，别追问细节）。照上表选路线，两路线可并行。
2. **环境检查**：两仓库是否在本地（常见位置 `D:\文档\学业资料\1大三\ai_test\`，
   找不到就 clone 或问用户）；调试浏览器是否开着（`curl http://127.0.0.1:9222/json/version`
   能通即就绪，没开先启动并请用户登录平台/网盘）；`config.json` 是否已从
   `config.example.json` 复制并填好 `courses`/`videoFolder`。
3. **分步执行**：每步开跑前告诉用户"现在做 X（第 N 步 / 共 M 步）"，长步骤
   （ASR、网盘导出）说明预期耗时；**串行执行是故意的**——并发会触发网盘限流。
4. **失败即改道**：

   | 失败现象 | 直接改道 |
   |---|---|
   | 抽音频/下载 401/403 | 直链过期：重跑 `rebuild_fresh_manifest.cjs` 再导 CSV，不重采列表 |
   | CDP 连不上 | 检查 9222 端口与调试浏览器是否保持打开 |
   | ASR 失败/无结果 | 查 `X-Api-Status-Code` 与 `volc.seedasr.auc` 资源 ID；不行换 MiMo |
   | 产物是 85~91 字占位 | 服务端生成失败：重跑无用，网页端手动重试该节后跳过 |
   | 页面改版脚本失效 | 按 [references/platform-internals.md](references/platform-internals.md) 重新探测，不硬猜 |

   其余异常见 [references/troubleshooting.md](references/troubleshooting.md)。
   断点续传：PPT 看 `state.json`，讲稿/笔记按本地文件存在跳过，`--force` 重跑。
5. **验证**：核对产物数量（几门课 × 几节 = 多少份），失败项单独列出，别只报总数。
6. **收尾汇报**：产物在哪（`transcripts/<课程>/`、`output/`、网盘视频目录的 PPT）、
   成功/失败数量、失败项下一步；文本类产物提示可丢给任意 LLM 提问/总结，或按课程
   合并后提炼重点（一页纸复习）。

## 共享前置：调试浏览器（CDP）

两个工具都通过 CDP 复用**已登录**的浏览器会话，不用登录两次：

```powershell
msedge --remote-debugging-port=9222 --user-data-dir=%LOCALAPPDATA%\edge-debug-profile
```

独立 user-data-dir（与日常浏览器分开），启动后在浏览器里登录平台/网盘，保持开着；
脚本跑批时**新建标签页**干活，不影响正常上网。pipeline 的 01_links 脚本用 `--cdp`
flag（端口走 config 的 `cdp.port`）；baidu-ai-batch 无 flag，读 config 的
`host`/`port`（默认 `127.0.0.1:9222`）。

## 路线 A：平台录播 → 转写文本

在 xiangzhang-course-pipeline 仓库根目录（步骤详见该仓库 README）：

```bash
node 01_links/collect_course_items.cjs --config config.json --cdp   # ① 课程列表 → video-items.json
node 01_links/collect_media_details.cjs --config config.json --cdp  # ② 详情/直链 → media-manifest.json
node 01_links/export_fresh_media_urls.cjs --config config.json      # ③ 直链 CSV
python 02_download/extract_audio.py --config config.json --courses=全部  # ④ 抽音频（不下载视频）
python 03_asr/batch_transcribe.py --csv media_urls/all_fresh_media_urls.csv --out transcripts  # ⑤ ASR
```

- `cp config.example.json config.json` 后填 `courses`（课程名支持部分匹配，
  如平台显示「临床药理学（1班）」可配「临床药理学」）
- 火山密钥：`VOLC_APP_ID` / `VOLC_ACCESS_TOKEN`（环境变量）；MiMo 备选：`MIMO_API_KEY`
- 直链带签名会过期（下载 401/403）→ 重跑 `rebuild_fresh_manifest.cjs` 再导 CSV
- ASR 状态码在响应 Header `X-Api-Status-Code`，`20000000`=成功

## 路线 B：网盘视频 → AI 课件/讲稿/笔记

视频进网盘（离线下载或本地上传），然后在 baidu-ai-batch 仓库：

```bash
npm install && cp config.example.json config.json   # 填 videoFolder 等
node bin/list-files.cjs                # ① 从网盘 API 生成视频清单
node bin/export-ppt.cjs                # ② 批量导出 AI 课件 PPT（存回网盘）
node bin/extract-manuscript.cjs        # ③ 批量提取 AI 讲稿 → 本地 TXT
node bin/export-notes.cjs              # ④ 批量生成并导出 AI 笔记
```

不装 Node 也行：装 Tampermonkey 后用 `userscript/baidu-ai-batch.user.js`
（在网盘文件列表页点「收集本目录视频」→「开始跑批」）。

### 路线 B 的坑（先读，能省几小时）

- **串行执行是故意的**：并发触发限流（早期 20 路并发 PPT 失败率 80%，改串行后近 100%）
- **假成功检测**：生成失败时页面留 85~91 字占位模板，按 `minContentLen`（默认 100）判死
- **PPT 导出要点课件区右上角导出图标**（`.ai-course__export-container`），聊天框快捷指令必挂
- **笔记在 `#noteIframe` 里读不到**：把 iframe 的 URL 单独开标签页，iframe 变顶层页就能读 DOM
- 重复跑会积累带时间戳的重复 PPT，记得清理
- 服务端生成失败的重跑也没用（黑屏/无内容/整门课挂掉），需网页端手动重试

### 与 pipeline 衔接（视频进网盘）

平台 URL 是内网地址（`*.ncu.edu.cn`），网盘离线下载不保证可用 → 本地批量下载
（`download_videos.py`）→ 改名（`rename_videos.py`）→ 网盘客户端上传 →
**传完本地删**（视频只在网盘）。直链来源：`media_urls/all_fresh_media_urls.csv`。

## 安全策略

- 密钥（火山 `VOLC_*`、MiMo `MIMO_API_KEY` 等）只走环境变量或 gitignore 的
  `config.json`——所有仓库都是公开的，密钥提交=直接泄露。
- 不把平台 Cookie / 登录凭证写入代码、日志或文档。
- 只操作用户明确要求处理的课程/视频；不批量触碰无关数据。
- 平台/网盘页面改版时按 `platform-internals` 重新探测，不硬猜、不逆向平台外的东西。

## 用户愿景（为什么这么做）

- 老师课上强调的内容≈考点，录播是完整信息源
- 一节课的文本可能一页纸就够——为深度思考/论文/睡觉争取时间
- 本 skill 的目标是让「不上课」成为可行选择，而不是鼓励摆烂

## 常见短语映射

| 用户说 | 实际要做 |
|--------|----------|
| "把课程录播整理一下" | 先问视频在哪 → A 或 B |
| "视频太多了不想下" | 路线 A（只抽音频），或 B（视频进网盘） |
| "帮我把网盘里的课批量导 PPT" | 路线 B export-ppt |
| "AI 提炼这门课的重点" | A 转写文本后交给 LLM 总结，或 B 的笔记 |
| "学校平台不让下载" | 平台页面有直链（recordvideo 接口），用 pipeline 提取 |
