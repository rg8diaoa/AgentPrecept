# agent-compass 🧭

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

> **Agent A 的产出（图+依据+状态）→ Agent B 无缝接手。**
>
> 不是"写文档的方法论"。把 Agent 协作从散文式沟通升级为结构化数据流通。

---

## 项目思想

Agent 不是不够聪明——是**没有外部记忆**。

每次新会话，Agent 都要重新遍历源码理解项目结构，重新猜测"去年为什么这样设计"，重新摸索"上个人做到哪了"。

agent-compass 给 Agent 三样它天生没有的东西：

| 缺失能力 | agent-compass 给什么 | 效果 |
|------|------|------|
| 项目结构记忆 | project-graph.yaml（结构/关系/稳定性） | 30 秒读取 vs 20 分钟遍历源码 |
| 决策历史记忆 | L4_O01 设计依据（决策/来源/证据） | 不再提议已被否决的方案 |
| 跨会话记忆 | HANDOFF（状态/上下文/下一步） | 下一个 Agent 知道从哪开始 |

---

## 项目独特性

| 市面上所有 Agent 工具 | agent-compass |
|------|------|
| 散文指令（Agent 读一次就忘） | **结构化数据**——project-graph.yaml 是数据，Agent 30 秒重建心智模型 |
| 只强化 Agent 能力 | **人也审 Agent**——8 阶段退出标准 + 4 项及格线，不懂架构也能判断产出好坏 |
| "你应该"的道德说教 | **教训驱动**——每条规则背后有实际踩过的坑，三轮审计从 12 问题收敛到 0 |
| 绑定特定工具 | **跨工具**——一个 AGENTS.md 覆盖 Claude Code / Cursor / CodeWhale / OpenCode / Copilot |
| 一次性使用 | **渐进接入**——第 1 天 3 个文件，第 1 周建图，按需扩展 |

---

## 项目功能

### 核心机制

| 文件 | 作用 | Agent 何时消费 |
|------|------|------|
| `AGENTS.md` | 硬规则 8 条 + 软建议 + 自动动作 + 工作模式 | 每次会话开始 |
| `docs/project-graph.yaml` | 三层项目图（结构/关系/演变 + stability 字段） | 写代码前 30 秒 |
| `docs/L4_O01` | 设计依据（每决策一行：什么/来源/证据） | 做技术决策前 |
| `docs/HANDOFF.md` | 会话交接（5 状态标记 + 上下文用量） | 会话结束时重写 |
| `docs/MEMORY.md` | 持久偏好和项目约束 | 每次会话开始 |

### 完整循环

```
研究 → 想法 → 设计 → 文档 → 开发 → 测试 → 审计 → 修复 → 维护 → (循环)
```

每阶段有退出标准（14-production-readiness），Agent 自检后才提交。

### 可执行工具

```bash
pip install agent-compass
agent-compass init    # 一键初始化核心文件到目标项目
agent-compass sync    # 从代码自动同步 project-graph
agent-compass audit   # 快速审计（命名/断链/骨架残留）
agent-compass doctor  # 诊断：检查缺少哪些文件
```

### 方法论 + 模板

- 15 篇方法论（完整循环 + 文档/命名/设计依据/审计/交接/图/工作流/工程化/安全/性能/接入/人机协作/自我管理/生产就绪）
- 35 个模板（16/16 分类全齐，5 个核心模板 Agent 自动加载）
- 5 个 Skill（project-graph / design-rationale / session-handoff / test-cases / architecture-design）
- Python + Node.js 双语言示例

---

## 如何使用

### 路径 A：快速上手（30 秒）

```bash
pip install agent-compass
agent-compass init /path/to/your-project
```

复制 AGENTS.md + project-graph.yaml + HANDOFF.md + L4_O01 到你的项目。Agent 自动遵循。

### 路径 B：自动初始化（1 分钟）

复制 `examples/first-run.md` 中的 prompt 发给 Agent。Agent 自动生成 project-graph、反推设计依据、生成架构图。

### 路径 C：完整体系（30 分钟）

```bash
cp -r templates/* /your-project/docs/
```

35 个模板，16/16 分类全齐。按 `templates/INDEX.md` 逐项填充。

### 已有项目接入

见 `methodology/11-existing-project.md`——第 1 天只搬 3 文件，第 1 周建图，第 2 周建设计依据，按需扩展。

### 体验 demo

```bash
make todo-api-test   # 4/4 测试绿
```

---

## 对比

| 场景 | 没有 agent-compass | 有 agent-compass |
|------|------|------|
| Agent 接手项目 | 遍历源码 20 分钟才敢动手 | 读 project-graph 30 秒知道结构 |
| Agent 修 bug | 不知道改了会影响谁 | 读 relations 层 → 知道影响 2 个文件 |
| Agent 提方案 | 提议已被否决的方案 | 读 L4_O01 → "去年已证明不行" |
| 换了一个 Agent | 不知道上个人做了什么 | 读 HANDOFF → 从下一步继续 |
| 人审 Agent | "看起来差不多" | 4 项及格线 → 能说"补一下这里" |

---

## 实战验证

源自一个 41 文档/46 配置的多 Agent 架构设计项目。三轮系统性审计从 12 个问题收敛到 0 阻塞项。外部评审综合评分 9.0/10。

---

## 目录

```
agent-compass/
├── AGENTS.md          ← Agent 入口（硬规则 + 自动动作 + 工作模式）
├── SKILL.md           ← Skill 工具入口
├── README.md
├── pyproject.toml     ← pip install agent-compass
├── Makefile
│
├── agent_compass/     ← CLI（init/sync/audit/doctor）
├── scripts/           ← 辅助脚本（同步/审计/可视化/命名检查）
├── skills/            ← 5 个核心 Skill
│
├── methodology/       ← 15 篇方法论（人类阅读）
├── templates/         ← 35 个模板（Agent 按需读取按指令产出）
├── examples/          ← Python/Node 示例 + Prompt 模板 + 初始化向导
├── reference/         ← 审计案例 + 多维图案例 + 横向对比 + 速查卡片
├── docs/              ← agent-compass 自身文档（吃自己的狗粮）
│
└── .github/           ← CI（审计 + 示例测试）
```

## 许可证

MIT
