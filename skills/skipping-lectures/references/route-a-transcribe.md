---
name: route-a-transcribe
description: 学校平台录播 → 直链 → 抽音频 → ASR 转写文本（xiangzhang-course-pipeline 全流程）
---

# 路线 A：平台录播 → 转写文本

仓库：`https://github.com/jing1312/xiangzhang-course-pipeline`（公开，main）

## 前置

- Node 18+、Python 3.10+、ffmpeg（PATH 或 `FFMPEG_PATH`）
- `npm install playwright`、`pip install -r requirements.txt`
- 调试浏览器已开并登录平台（见 `cdp-login` playbook）
- `cp config.example.json config.json`，关键字段：
  - `platform.signKey`：接口签名密钥（与平台一致，实测 `123123`）
  - `courses`：课程名数组，支持部分匹配（如平台显示「临床药理学（1班）」可配「临床药理学」）
  - `paths.*`：courseItemsDir/manifestsDir/urlsDir

## 完整链路（每步都在仓库根目录跑）

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
```

## 可选：要本地视频副本时

```bash
python 02_download/download_videos.py --csv media_urls/all_fresh_media_urls.csv --out downloads
python 02_download/rename_videos.py --dir downloads --csv media_urls/all_fresh_media_urls.csv
python 02_download/rename_final.py --dir downloads --short-names '{"课程":"简称"}'
# 备选：不改名，只给原文件加 简称_序号_ 前缀
python 02_download/add_prefix.py --dir downloads --short-names '{"课程":"简称"}'
```

## 平台接口要点（来自实测，改版需重新探测）

- 实录列表页：`#/teacherVideoResource.htm`，组件 `.box-video`（Vue），
  `$staticConfig()` 提供 `teachingApi`/`validCode`，`weeklyList` 是课程表
- 课程分页接口：`POST {teachingApi}/v1/videoinfos/page?validCode=...`
  body: `{userId, groupIds, openStatus:'1', week:null, schoolYear, term, validCode, page, pageSize}`
- 详情接口：`GET {teachingApi}/v1/recordvideo/{videoId}?validCode=<md5>`
  返回 `teacherViewFiles/studentViewFiles/vgaViewFiles`（老师/学生/屏幕三视角）
- 实录页 URL 的 `mouth` 参数是**上课月份**（从 startTime 取，不是周数）
- ASR 状态码在响应 Header `X-Api-Status-Code`，`20000000`=成功
- 选流规则：优先 `voiceStatus==1` → `preferredView` 视角 → 声道 → 视角顺序 → 大小
