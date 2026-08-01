# skipping-lectures

把录播课视频变成可复习的 AI 资料（转写文本 / 提炼重点 / AI 课件 PPT / 讲稿 / 笔记），
让你不上课也能备考。

这是一个 **Claude Code / opencode 等 AI 编程工具的 skill**（编排层）：实际干活的是
两个配套工具仓库，本 skill 负责判断走哪条路线、给出正确命令、复用两边共享知识
（CDP 登录态等）。

- **路线 A（转写为主）**：[xiangzhang-course-pipeline](https://github.com/jing1312/xiangzhang-course-pipeline)
  学校教学平台（香樟云课堂 zbkt.ncu.edu.cn 等）课程实录 → 直链 → 抽音频（不下载视频）
  → 火山/MiMo ASR → 每节课一份文本
- **路线 B（网盘 AI 产出）**：[baidu-ai-batch](https://github.com/jing1312/baidu-ai-batch)
  百度网盘里视频的 AI 课件 PPT / 讲稿 / 笔记批量生成与导出（Node 版 + 油猴版）

两条路线不互斥：文本和 PPT/笔记可以都做。

## 安装

把本仓库放到 AI 编程工具的全局 skills 目录：

```powershell
# Windows（示例）：
git clone https://github.com/jing1312/skipping-lectures.git `
  "$env:USERPROFILE\.agents\skills\skipping-lectures"

# macOS / Linux：
git clone https://github.com/jing1312/skipping-lectures.git ~/.agents/skills/skipping-lectures
```

> 不同工具的技能目录不同（如 Claude Code 是 `~/.claude/skills/`），放对目录后
> 重启会话即可触发。

## 用法

直接对 AI 说类似这样的话：

- "把课程录播整理一下" / "把录播课转成笔记"
- "帮我把网盘里的课批量导 PPT"
- "AI 提炼这门课的重点"
- "复习备考资料整理"

skill 会先问清视频在哪、要什么产出，然后按固定协议执行：
**澄清需求 → 环境检查 → 分步执行 → 收尾汇报**。

详细流程见 [SKILL.md](SKILL.md)，命令速查见 [references/workflow-cheatsheet.md](references/workflow-cheatsheet.md)。

## 依赖

- 两个工具仓库（见上，均公开）
- 调试浏览器（Edge/Chrome 带 `--remote-debugging-port=9222`，复用登录态）
- Node 18+ / Python 3.10+ / ffmpeg（按所用路线）

## 为什么做这个

- 老师课上强调的内容 ≈ 考点，录播是完整信息源
- 一节课的文本可能一页纸就够——为深度思考/论文/睡觉争取时间
- 让「不上课」成为可行选择，而不是鼓励摆烂

## License

MIT
