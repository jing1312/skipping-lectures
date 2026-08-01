---
name: platform-internals
description: 教学平台的接口与 DOM 要点（来自实测），页面改版或适配新平台时按此重新探测
---

# 平台接口要点（来自实测，改版需重新探测）

- 实录列表页：`#/teacherVideoResource.htm`，组件 `.box-video`（Vue），
  `$staticConfig()` 提供 `teachingApi`/`validCode`，`weeklyList` 是课程表
- 课程分页接口：`POST {teachingApi}/v1/videoinfos/page?validCode=...`
  body: `{userId, groupIds, openStatus:'1', week:null, schoolYear, term, validCode, page, pageSize}`
- 详情接口：`GET {teachingApi}/v1/recordvideo/{videoId}?validCode=<md5>`
  返回 `teacherViewFiles/studentViewFiles/vgaViewFiles`（老师/学生/屏幕三视角）
- 实录页 URL 的 `mouth` 参数是**上课月份**（从 startTime 取，不是周数）
- ASR 状态码在响应 Header `X-Api-Status-Code`，`20000000`=成功
- 选流规则：优先 `voiceStatus==1` → `preferredView` 视角 → 声道 → 视角顺序 → 大小
- 签名：`validCode=md5(id=<videoId>&signKey=<signKey>)`，`signKey` 在 config 的 `platform.signKey`
