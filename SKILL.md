---
name: skipping-lectures
description: >-
  Turn recorded lecture videos into study-ready material (AI-generated notes, key points, transcripts, PPTs) so the user can skip live classes and still ace exams. Trigger whenever the user mentions 录播课/课程录播/网课视频/不想上课/翘课/划水、把视频转成笔记、AI 提炼课程重点、导出课件 PPT/讲稿/笔记、批量转写课程语音、复习备考资料整理、或 asks to process videos from a school platform (zbkt.ncu.edu.cn 香樟云课堂 etc.) or from Baidu Pan (百度网盘) with pan-AI batch export. Use this skill even if the user only mentions one half of the workflow (e.g. only 转写 or only 网盘 AI 导出) — route them to the right half. Do NOT use for generic note-taking, general video editing, or unrelated ASR tasks.
---

# skipping-lectures — 录播课 → AI 复习资料流水线

学校每节课都有录播，老师课上强调的内容几乎都出现在试卷上。本 skill 把录播视频
变成「一页纸就能复习」的资料：**转写文本 / 提炼重点 / AI 课件 PPT / 讲稿 / 笔记**，
让用户不上课也能快速备考。这是**编排层**：实际干活的是两个配套工具仓库，
本 skill 负责判断走哪条路线、给出正确命令、并复用两边的共享知识（CDP 登录态等）。

## 核心判断：两条路线

先问清用户的视频现在在哪里、想要什么产出，然后走对应路线：

| 路线 | 适用场景 | 产出 | 工具 |
|------|----------|------|------|
| **A 转写为主** | 平台录播还在学校平台、本地磁盘紧张 | 每节课一份文本（复习用） | xiangzhang-course-pipeline（抽音频 + ASR） |
| **B 网盘 AI 产出** | 视频已在百度网盘（或愿意上传） | AI 课件 PPT / 讲稿 / 笔记 | baidu-ai-batch |

两条路线不互斥：路线 A 的音频/文本和路线 B 的 PPT/笔记可以都做。
若用户视频**已**在百度网盘 → 直接走 B，不用 A。
若视频**还没下载/抽过音频** → 默认先 A 拿文本（省空间），需要 PPT 再走 B。

## 两个工具仓库

- **xiangzhang-course-pipeline** — https://github.com/jing1312/xiangzhang-course-pipeline
  教学平台（如香樟云课堂 zbkt.ncu.edu.cn）课程实录 → 课程列表 → 媒体直链 →
  抽音频（不下载视频）→ 火山/MiMo ASR 转写 → 每节 txt。平台是学校私有部署，
  接口签名/组件结构以仓库实测为准。
- **baidu-ai-batch** — https://github.com/jing1312/baidu-ai-batch
  百度网盘里视频的 AI 课件/讲稿/笔记**批量**生成与导出（服务端按需生成，无批量入口，
  必须逐节触发）。含 Node 版与油猴版。

安装：两仓库都 `git clone` 到本地（公开仓库，无密钥）。密钥走环境变量/本机
`config.json`（已 gitignore），**绝不把密钥写进仓库或提交**。

## 共享前置：调试浏览器（CDP）

两个工具都通过 CDP 复用**已登录**的浏览器会话，不用逆向、不用登录两次：

```powershell
msedge --remote-debugging-port=9222 --user-data-dir=%LOCALAPPDATA%\edge-debug-profile
```

- 用独立 user-data-dir（与日常浏览器分开），启动后在浏览器里登录平台/网盘，保持开着
- 脚本跑批时**新建标签页**干活，不影响用户正常上网
- 端口默认 9222，两仓库都支持 `--cdp` / `cdp.port` 配置

## 路线 A：平台录播 → 转写文本

在 xiangzhang-course-pipeline 仓库根目录（步骤详见该仓库 README）：

```bash
node 01_links/collect_course_items.cjs --config config.json --cdp   # ① 课程列表 → video-items.json
node 01_links/collect_media_details.cjs --config config.json --cdp  # ② 详情/直链 → media-manifest.json
node 01_links/export_fresh_media_urls.cjs --config config.json      # ③ 直链 CSV
python 02_download/extract_audio.py --config config.json --courses=全部  # ④ 抽音频（不下载视频）
python 03_asr/batch_transcribe.py --csv media_urls/all_fresh_media_urls.csv --out transcripts  # ⑤ ASR
```

- `cp config.example.json config.json` 后填 `courses`（课程名，支持部分匹配）
- 火山密钥：`VOLC_APP_ID` / `VOLC_ACCESS_TOKEN`（环境变量）；MiMo 备选：`MIMO_API_KEY`
- 直链带签名会过期（下载 401/403）→ 重跑 `rebuild_fresh_manifest.cjs` 再导 CSV
- ASR 状态码在响应 Header `X-Api-Status-Code`，`20000000`=成功

## 路线 B：网盘视频 → AI 课件/讲稿/笔记

视频进网盘（离线下载或本地上传），然后在 baidu-ai-batch 仓库：

```bash
npm install && cp config.example.json config.json   # 填 videoFolder 等
node bin/list-files.cjs                # ① 从网盘 API 生成视频清单
node bin/export-ppt.cjs                # ② 批量导出 AI 课件 PPT（存网盘）
node bin/extract-manuscript.cjs        # ③ 批量提取 AI 讲稿 → 本地 TXT
node bin/export-notes.cjs              # ④ 批量生成并导出 AI 笔记
```

不装 Node 也行：装 Tampermonkey 后用 `userscript/baidu-ai-batch.user.js`。

## 关键踩坑（先读，能省几小时）

1. **串行执行是故意的**——并发会触发网盘限流（早期 20 路并发 PPT 失败率 80%，改串行后近 100%）。别改成并发。
2. **「假成功」检测**：AI 生成失败时页面留 85~91 字占位模板，脚本按字数阈值（`minContentLen`，默认 100）判死。手动导出时也这样判断。
3. **PPT 导出有两个按钮**：AI 聊天框快捷指令会调错 API 必挂；真正有效的是课件区右上角导出图标（`.ai-course__export-container`）。
4. **笔记在 iframe 里读不到**：把 `#noteIframe` 的 URL 单独开标签页，iframe 变顶层页面就能读 DOM。
5. **断点续传**：PPT 进度写 `state.json`；讲稿/笔记按本地文件是否存在跳过，`--force` 重跑。中断后重跑只处理没完成的。
6. **视频太大别都下载**：路线 A 用 ffmpeg 从直链只抽音频（16kHz 单声道，一节课 <100MB），不下载视频本体。
7. **ASR 上传慢/读取不完**：长视频先切片或抽音频后转写；MiMo 有 7MB/20 分钟上限，超长自动切片。
8. **平台/网盘结构变了**：两仓库都是实测得出的 DOM/接口逻辑，页面改版就失效——此时按仓库 README 的探测思路（CDP 看 Vue 组件、抓接口）重新适配，而不是硬猜。

## 产出组织建议

- 转写文本：`transcripts/<课程>/<课程名>_<上课时间>.txt`（含时间戳分句）
- 网盘侧：PPT 存回网盘视频目录；讲稿/笔记本地 `output/`
- 考前复习：让用户把文本丢给任意 LLM 提问/总结，或按课程合并文本后提炼重点

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
