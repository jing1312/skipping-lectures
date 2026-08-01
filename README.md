<div align="center">
  <img src="assets/skipping-lectures-cover.svg" alt="skipping-lectures：录播课 → AI 复习资料" width="100%" />
</div>

<div align="center">

# 🎓 skipping-lectures

### 让 Agent 把录播课变成一页纸——先转写，再提炼，不上课也能备考。

一个可安装到 opencode、Claude Code、Codex 等 Agent 的录播课学习流水线 Skill。

[![Validate Skill](https://github.com/jing1312/skipping-lectures/actions/workflows/validate.yml/badge.svg)](https://github.com/jing1312/skipping-lectures/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

[xiangzhang-course-pipeline](https://github.com/jing1312/xiangzhang-course-pipeline) · [baidu-ai-batch](https://github.com/jing1312/baidu-ai-batch)

</div>

> [!NOTE]
> 课程录播、网课回放、不想上课、AI 提炼重点、批量导 PPT、复习备考……直接用自然语言描述，Agent 会先问清视频在哪、要什么产出，再按路线自动跑。

## ✨ 为什么选择 skipping-lectures

- **两条路线，互不打架**：平台录播走「抽音频 → ASR 转写」拿文本；网盘视频走「网盘 AI」拿 PPT/讲稿/笔记。文本和 PPT 可以都做。
- **不占本地空间**：路线 A 用 ffmpeg 从直链只抽音频（16kHz 单声道，一节课不到 100MB），不下载视频本体。
- **按需加载**：4 个专项 Playbook 通过路由索引按场景加载，减少无关上下文，也方便维护。
- **串行执行是故意的**：网盘 AI 并发会触发限流（20 路并发 PPT 失败率 80%，改串行后近 100%），skill 会压住任何"改成并发"的冲动。
- **可验证可回滚**：CI 自动校验结构、索引一致性和密钥泄露；安装器覆盖前自动备份，失败自动回滚。
- **不上课 ≠ 摆烂**：老师课上强调的内容≈考点，录播是完整信息源——把时间留给深度思考和创造。

## 🖥️ 能力范围

| 路线 | 覆盖 | 产出 |
|---|---|---|
| **A 转写为主** | 教学平台（香樟云课堂 zbkt.ncu.edu.cn 等）课程实录 → 列表 → 直链 → 抽音频 → 火山/MiMo ASR | 每节课一份带时间戳的 txt |
| **B 网盘 AI 产出** | 百度网盘视频 → AI 课件/讲稿/笔记批量生成与导出（Node 版 + 油猴版） | PPT（存网盘）、讲稿/笔记（本地 TXT） |

## 🚀 安装

### 方式一：把一句话交给 Agent（最适合新手）

打开你正在使用的 opencode、Claude Code、Codex 或其他支持 Agent Skills 的工具，把下面这句话直接发给它：

```text
请安装这个 Agent Skill：https://github.com/jing1312/skipping-lectures
先审查仓库内容和 SKILL.md，再安装到你当前 Agent 的 Skills 目录；如果已经安装旧版本，先备份再更新。
完成后告诉我实际安装路径、目标 Agent 和验证结果。
```

<details>
<summary>方式二：仓库安装器（推荐，可控制路径）</summary>

```bash
git clone https://github.com/jing1312/skipping-lectures.git
cd skipping-lectures
```

Windows PowerShell：

```powershell
.\scripts\install.ps1 -Target agents          # ~/.agents/skills（opencode 等）
.\scripts\install.ps1 -Target claude          # ~/.claude/skills
.\scripts\install.ps1 -Target codex           # ~/.codex/skills
```

macOS / Linux：

```bash
./scripts/install.sh --target agents
./scripts/install.sh --target claude
./scripts/install.sh --target codex
```

需要自定义位置时：

```powershell
.\scripts\install.ps1 -Target custom -Destination "D:\path\to\skills"
```

```bash
./scripts/install.sh --target custom --destination "/path/to/skills"
```

目标目录已存在时，安装器默认拒绝覆盖；确认升级时显式加 `-Force` 或 `--force`，旧版本会先备份到相邻的 `external/skipping-lectures/backups`。

</details>

<details>
<summary>方式三：手动复制</summary>

把仓库中的 [`skills/skipping-lectures`](skills/skipping-lectures) 整个目录复制到目标 Agent 的 Skills 根目录：

```text
~/.agents/skills/skipping-lectures/
~/.claude/skills/skipping-lectures/
~/.codex/skills/skipping-lectures/
```

目录中必须保留 `SKILL.md` 和 `references/`，不要只复制某一个 Playbook。复制后重启 Agent 会话即可触发。

</details>

## 🧭 如何使用

安装后直接说需求，不需要记命令。描述越具体，路由越准确：**视频在哪 + 想要什么 + 约束**。

```text
把「临床药理学」的课程录播整理一下，每节课一份转写文本。
```

```text
帮我把网盘里的课批量导 PPT，只要这学期四门课的，别的不要动。
```

```text
AI 提炼「生物药剂与药物动力学」的重点，考前一周用。
```

```text
平台视频太多了不想下载，本地只留音频和文本就行。
```

标准工作顺序是：确认目标 → 路由 Playbook → 环境检查（CDP 登录态）→ 分步执行 → 验证产物 → 收尾汇报。

## 🧰 功能总览

本 Skill 内置 4 个可按需加载的专项 Playbook，分类与[完整路由索引](skills/skipping-lectures/references/route-index.md)一致。

| 分类 | 主要内容 |
|---|---|
| 路线 A：转写 | 课程列表、直链导出、抽音频、火山/MiMo ASR 全流程 |
| 路线 B：网盘 AI | PPT/讲稿/笔记批量导出、油猴版、与 A 的衔接 |
| 共享前置 | 调试浏览器（CDP 9222）登录态，两路线共用 |
| 排障 | 直链过期、限流、假成功、CDP 断连 |

## 💬 你能这样问

| 场景 | 你可以这样问 |
|---|---|
| 整理课程录播 | “把临床药理学的录播整理成文本，先看一下有多少节。” |
| 导出课件 PPT | “网盘里这学期课程的视频，帮我批量导出 AI 课件 PPT。” |
| 提炼课程重点 | “把《药物分析》的转写文本合并后提炼重点，做成复习提纲。” |
| 备考突击 | “明天考生物药剂，把这门课的笔记和讲稿给我整理成一页纸。” |
| 直链失效 | “抽音频报 401，帮我刷新直链后继续，别从头跑。” |

## 🛡️ 安全边界

- 密钥（火山 `VOLC_*`、MiMo `MIMO_API_KEY` 等）只走环境变量或 gitignore 的 `config.json`，绝不写进仓库或提交——两个工具仓库和本 skill 仓库都是公开的。
- 不把平台 Cookie / 登录凭证写入代码、日志或文档。
- 只操作用户明确要求处理的课程/视频；不批量触碰无关数据。
- 平台/网盘页面改版时，按接口要点重新探测（CDP 看 Vue 组件、抓接口），不硬猜、不逆向平台外的东西。

## 🧱 项目结构

```text
skills/skipping-lectures/
├── SKILL.md                 # 触发描述 + 强制工作流 + 安全策略
└── references/              # 按需加载的 Playbook（索引路由）
    ├── route-index.md       # 路由表：场景 → playbook
    ├── route-a-transcribe.md
    ├── route-b-pan-export.md
    ├── cdp-login.md
    └── troubleshooting.md
assets/
└── skipping-lectures-cover.svg  # README 封面图
scripts/
├── install.ps1              # Windows 安装器
└── install.sh               # macOS/Linux 安装器
tests/validate_skill.py      # 无第三方依赖的仓库验证器
```

## 🧪 开发与验证

修改 Skill 或 Playbook 后，在仓库根目录运行：

```powershell
python tests\validate_skill.py
```

验证器会检查 Skill frontmatter、description 长度、references 索引一致性、占位符、疑似凭据和危险 shell 管道。GitHub Actions 在每次 push 自动重复验证，并测试安装器的首次安装、拒绝覆盖、备份和强制更新路径。

## ❓ 常见问题

**这是一个桌面软件吗？**

不是。它是给 Agent 读取的 Skill 包，提供流程、命令和安全边界。实际执行依赖两个配套工具仓库（`xiangzhang-course-pipeline`、`baidu-ai-batch`，均公开 MIT）。

**视频必须留在本地吗？**

不用。路线 A 只抽音频；路线 B 视频进网盘后本地可删。

**百度网盘离线下载不好使怎么办？**

平台视频是内网地址（`*.ncu.edu.cn`），网盘离线下载不保证可用——改成「本地下载 → 改名 → 上传网盘 → 本地删」。

**页面改版了脚本还能用吗？**

两仓库都是实测得出的 DOM/接口逻辑，改版就失效。skill 里记录了探测思路（CDP 看 Vue 组件、抓接口），按思路重新适配即可。

## 📄 来源与许可证

项目按 [MIT](LICENSE) 分发。实际工作由两个公开仓库完成：
[xiangzhang-course-pipeline](https://github.com/jing1312/xiangzhang-course-pipeline)（平台录播 → 转写）与
[baidu-ai-batch](https://github.com/jing1312/baidu-ai-batch)（网盘 AI 批量导出），本 skill 是它们的编排层。

欢迎提交经过验证的流程改进、新平台适配和实战案例。
