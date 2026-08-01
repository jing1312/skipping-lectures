# skipping-lectures

把录播课视频变成可复习的 AI 资料（转写文本 / 提炼重点 / AI 课件 PPT / 讲稿 / 笔记），
让你不上课也能备考。

这是一个 **Claude Code / opencode / Codex 等 AI 编程工具的 skill**（编排层）：
实际干活的是两个配套工具仓库，本 skill 负责判断走哪条路线、给出正确命令、
复用两边共享知识（CDP 登录态等）。

- **路线 A（转写为主）**：[xiangzhang-course-pipeline](https://github.com/jing1312/xiangzhang-course-pipeline)
  学校教学平台（香樟云课堂 zbkt.ncu.edu.cn 等）课程实录 → 直链 → 抽音频（不下载视频）
  → 火山/MiMo ASR → 每节课一份文本
- **路线 B（网盘 AI 产出）**：[baidu-ai-batch](https://github.com/jing1312/baidu-ai-batch)
  百度网盘里视频的 AI 课件 PPT / 讲稿 / 笔记批量生成与导出（Node 版 + 油猴版）

两条路线不互斥：文本和 PPT/笔记可以都做。

## 目录结构

```
skipping-lectures/
├── skills/
│   └── skipping-lectures/       # skill 本体
│       ├── SKILL.md             # 触发描述 + 强制工作流 + 安全策略
│       └── references/          # 按需加载的 playbook（索引路由）
│           ├── route-index.md         # 路由表：场景 → playbook
│           ├── route-a-transcribe.md  # 路线 A：平台录播 → 转写
│           ├── route-b-pan-export.md  # 路线 B：网盘 AI 产出
│           ├── cdp-login.md          # 调试浏览器（CDP）登录态
│           └── troubleshooting.md    # 排障
├── scripts/
│   ├── install.ps1              # Windows 一键安装（多 agent 目标、备份回滚）
│   └── install.sh               # macOS/Linux 一键安装
├── tests/
│   └── validate_skill.py        # 结构/安全校验（CI 自动跑）
└── .github/workflows/validate.yml
```

## 安装

```powershell
# Windows（默认装到 opencode/agents 全局目录）：
powershell -ExecutionPolicy Bypass -File scripts/install.ps1

# 其他目标：-Target claude / -Target codex / -Target custom -Destination <目录>
# 覆盖已安装版本：-Force（旧版本自动备份）

# macOS / Linux：
bash scripts/install.sh            # 默认 ~/.agents/skills
bash scripts/install.sh --target claude --force
```

> 手动安装也简单：把 `skills/skipping-lectures/` 目录复制到你的 agent 的
> skills 目录（如 `~/.agents/skills/`、`~/.claude/skills/`），重启会话即可触发。

## 用法

直接对 AI 说类似这样的话：

- "把课程录播整理一下" / "把录播课转成笔记"
- "帮我把网盘里的课批量导 PPT"
- "AI 提炼这门课的重点"
- "复习备考资料整理"

skill 会先问清视频在哪、要什么产出，然后按强制工作流执行：
**确认目标 → 路由 playbook → 环境检查 → 计划与执行 → 验证 → 收尾汇报**。
细节见 [SKILL.md](skills/skipping-lectures/SKILL.md)。

## 校验

```bash
python tests/validate_skill.py
```

检查：frontmatter 完整性、description 长度、references 索引一致性、
密钥泄露、危险 shell 管道、TODO 占位符。GitHub Actions 在每次 push 自动运行。

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
