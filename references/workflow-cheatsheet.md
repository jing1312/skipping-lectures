# 两仓库速查（在 SKILL.md 触发后按需读取）

## xiangzhang-course-pipeline

仓库：`https://github.com/jing1312/xiangzhang-course-pipeline`（公开，main）

### 前置
- Node 18+、Python 3.10+、ffmpeg（PATH 或 `FFMPEG_PATH`）
- `npm install playwright`、`pip install -r requirements.txt`
- 调试浏览器：`msedge --remote-debugging-port=9222 --user-data-dir=%LOCALAPPDATA%\edge-debug-profile`，登录平台
- `cp config.example.json config.json`，关键字段：
  - `platform.signKey`：接口签名密钥（与平台一致，实测 `123123`）
  - `courses`：课程名数组，支持部分匹配（如平台显示「临床药理学（1班）」可配「临床药理学」）
  - `paths.*`：courseItemsDir/manifestsDir/urlsDir

### 完整链路（每步都在仓库根目录跑）
```bash
# 1. 课程列表采集（从实录列表页按课程拉全，翻页自动）
node 01_links/collect_course_items.cjs --config config.json --cdp
#    输出 downloads_by_course/<课程>/video-items.json + urls.txt
#    --all 额外生成全部课程的合并清单 collected-video-items.json

# 2. 抓每节详情（读 Vue 组件 videoDetailObj 或 recordvideo 接口），选最优视角/声道
node 01_links/collect_media_details.cjs --config config.json --cdp --courses=全部
#    输出 media_manifests/<课程>/media-manifest.json（status=ok/failed、selected.url 直链）

# 3. 导出直链 CSV（路线 A 入口，也是 B 的取 URL 入口）
node 01_links/export_fresh_media_urls.cjs --config config.json
#    输出 media_urls/all_fresh_media_urls.csv（10 列带 BOM）

# 4. 抽音频（ffmpeg 从直链只取音频流，不下载视频）
python 02_download/extract_audio.py --config config.json --courses=全部
#    输出 transcripts/audio/<课程>/*.wav（16kHz 单声道）

# 5. ASR 转写（火山豆包主 / MiMo 备）
export VOLC_APP_ID=... VOLC_ACCESS_TOKEN=...
python 03_asr/batch_transcribe.py --csv media_urls/all_fresh_media_urls.csv --out transcripts
#    或吃本地音频：--dir transcripts/audio/临床药理学
#    输出 transcripts/<课程>/<课程名>_<时间>.txt（含 [mm:ss] 分句）

# 5b. MiMo 备选（单次 ≤7MB/20 分钟，超长自动切片）
export MIMO_API_KEY=...
python 03_asr/mimo_asr_batch.py --csv media_urls/all_fresh_media_urls.csv --out transcripts_mimo
#    或吃本地音频：--dir transcripts/audio/临床药理学

# 可选：要本地视频副本时
python 02_download/download_videos.py --csv media_urls/all_fresh_media_urls.csv --out downloads
python 02_download/rename_videos.py --dir downloads --csv media_urls/all_fresh_media_urls.csv
python 02_download/rename_final.py --dir downloads --short-names '{"课程":"简称"}'
```

### 常见故障
| 现象 | 处理 |
|------|------|
| 抽音频/下载 401/403 | 直链过期 → `node 01_links/rebuild_fresh_manifest.cjs --config config.json --courses=...` 后重导 CSV |
| CDP 连不上 | Edge 需带 `--remote-debugging-port=9222` 启动并保持页面打开 |
| 未登录 | 在调试浏览器里重新登录 |
| validCode 不匹配 | 检查 `platform.signKey`；recordvideo 的 validCode=md5(`id=<videoId>&signKey=<signKey>`) |
| ASR 失败 | 检查 `X-Api-Status-Code`（20000000=成功）、`volc.seedasr.auc` 资源 ID、密钥 |

### 平台接口要点（来自实测，改版需重新探测）
- 实录列表页：`#/teacherVideoResource.htm`，组件 `.box-video`（Vue），
  `$staticConfig()` 提供 `teachingApi`/`validCode`，`weeklyList` 是课程表
- 课程分页接口：`POST {teachingApi}/v1/videoinfos/page?validCode=...`
  body: `{userId, groupIds, openStatus:'1', week:null, schoolYear, term, validCode, page, pageSize}`
- 详情接口：`GET {teachingApi}/v1/recordvideo/{videoId}?validCode=<md5>`
  返回 `teacherViewFiles/studentViewFiles/vgaViewFiles`（老师/学生/屏幕三视角）
- 实录页 URL 的 `mouth` 参数是**上课月份**（从 startTime 取，不是周数）

---

## baidu-ai-batch

仓库：`https://github.com/jing1312/baidu-ai-batch`（公开，master，MIT）

### 前置
- Node 18+，只需 `npm install`（仅依赖 `ws`）
- 调试浏览器登录百度网盘（任意浏览器带 `--remote-debugging-port=9222`）
- `cp config.example.json config.json`，字段：
  - `videoFolder`：网盘内视频目录（以 `/` 结尾）
  - `skipList`：跳过名单（黑屏/损坏的视频）
  - `minContentLen`：防假成功字数阈值（默认 100）

### 任务
```bash
node bin/list-files.cjs           # 生成视频清单 video-list.txt（用网盘 API）
node bin/export-ppt.cjs           # ① 批量导出 AI 课件 PPT（存回网盘视频目录）
node bin/extract-manuscript.cjs   # ② 批量提取 AI 讲稿 → output/*.txt
node bin/export-notes.cjs         # ③ 批量生成并导出 AI 笔记（PDF 存网盘 + 本地 TXT）
# 全部支持断点续传；--force 强制重跑已完成项
```

油猴版：`userscript/baidu-ai-batch.user.js`（Tampermonkey，免 Node，
在网盘文件列表页点「收集本目录视频」→「开始跑批」）

### 关键坑
- 串行执行，别并发（限流）；单节失败自动跳过，可事后重跑
- 假成功：生成失败留 85~91 字占位模板，按 `minContentLen` 判定，不会存空壳
- PPT 导出要点课件区右上角导出图标（`.ai-course__export-container`），聊天框快捷指令必挂
- 笔记在 `#noteIframe`（跨域读不到）→ iframe URL 单独开标签页读
- 重复跑会积累带时间戳的重复 PPT 文件，记得清理
- 服务端生成失败的重跑也没用（黑屏/无内容/整门课挂掉），需网页端手动重试

### 与 pipeline 衔接
- pipeline 的 `media_urls/all_fresh_media_urls.csv` 提供全部视频直链
- 网盘离线下载对内网域名（`*.ncu.edu.cn`）不保证可用 → 本地批量下载改名后上传，
  传完本地删（视频只在网盘）
- 流程：直链 CSV → 下载 → 改名 → 上传网盘 → baidu-ai-batch 批量产出
