# AGENTS.md — agent-compass 项目指令

> 复制到项目根目录。Agent 自动读取。本文档描述 Agent 的操作规则——不仅仅是文档规范，更重要的是**什么时候停下、什么时候问人、什么时候自己动手**。

---

## 🎯 工作模式

[EXPLORE] 探索模式（默认）: 用户说"做一个 X"→ 直接出 MVP，标注假设和边界。
           遇到明显歧义时才追问。适用于快速原型和 vibecoding。

[PRECISE] 精确模式: 用户说"重构 X"/"修复 X 的 bug"/"精确模式" →
           严格遵循硬规则：动工前复述、> 2 文件列影响范围、先问再动手。
           适用于生产级变动。

Agent 默认为 EXPLORE。用户说"精确模式"或"go"时切换。

## 能力自适应

如果无法执行 shell 命令 → 跳过自动动作中的 git diff/上下文用量评估。
如果无法确认模型类型 → 跳过硬规则 6（上下文评估）。
弱 Agent 不必因无法完成全部指令而停止。

## 🔴 硬规则（MUST — 违反就阻断）

1. **不懂就停**。任何不确定的概念/工具/术语 → 复述理解 → 等人类确认再动手。不许猜
2. **动工前复述**。涉及 > 2 个文件的改动 → 列出影响范围 → 等确认
3. **任何新需求 → 至少问 1 个澄清问题再动手**
4. **同一问题排查 3 轮无进展 → 停止**，HANDOFF 记录排查路径，状态改为 [BLOCKED]
5. **提交前安全自检** — 6 项 checkbox（硬编码/参数化/认证/授权/验证/依赖扫描）
6. **上下文 > 60% → 全量重写 HANDOFF**，提示人类切新会话
7. **修改 > 5 个模块 → 停下**，HANDOFF 列出影响清单，标注 [NEEDS_HUMAN_DECISION]
8. **两个方案无优劣 → 列出双方证据**，标注 [NEEDS_HUMAN_DECISION]，不自己做主

---

## 🟡 软规则（SHOULD — 遵守但可跳过）

- 写代码前读取 project-graph 查影响范围
- 写代码前读取 L4_O01 查已有决策
- 新建模块 → 用构造器注入，定义 `__all__`
- 函数 > 50 行考虑拆分，文件 > 400 行考虑拆分

---

## 🤖 自动动作（AUTO — 不等人类）

| 你做了什么 | Agent 自动 |
|---|---|
| 每次代码变更 | 运行 `python scripts/sync-graph.py src/ docs/project-graph.yaml` |
| 新建模块且含认证/核心逻辑 | stability=critical |
| 做了设计决策 | 追加 L4_O01 一行（决策 / 来源 / 证据） |
| 会话结束 | 全量重写 HANDOFF：git diff + 上下文评估 + 状态标记 |
| 提交代码 | 检查 HANDOFF 状态 + 对照 14-production-readiness 退出标准 |

---

## 与人类对话规则

```
用户: "加一个优先级字段"

❌ 直接写 ALTER TABLE

✅ 追问: "P0-P3 够用？排序在数据库层还是应用层？默认值？"

规则: 任何新需求 → 至少问 1 个问题 → 人类回复后才能动工
```

```
用户: "用 CQRS 模式"

✅ "我对 CQRS 的理解是读写分离。确认是这个吗？"

规则: 不确定的概念 → 复述理解 → 等确认
```

---

## 渐进加载：Agent 按需读取

```
会话开始 → 只读本文档 + docs/project-graph.yaml + docs/HANDOFF.md
写代码   → 读 🔥 核心模板（project-graph/L4_O01/HANDOFF/测试用例/架构）
做决策   → 读 methodology/03-design-rationale.md + docs/L4_O01
跑审计   → 读 methodology/04-audit-framework.md
初始化   → 读 examples/first-run.md
评估产出 → 读 methodology/14-production-readiness.md
```

🔥 核心模板 = project-graph.yaml / L4_O01 / HANDOFF / 测试用例 / 架构设计
📋 扩展模板 = templates/ 中其余 26 个——人类说"建 X 文档"时才读

---

## 状态标记（写入 HANDOFF 第一行）

| 标记 | 何时用 |
|------|------|
| [IN_PROGRESS] | 正常 |
| [NEEDS_HUMAN_REVIEW] | 完成 > 3 文件 / 改图结构层 / 做新决策 |
| [NEEDS_HUMAN_DECISION] | 两方案无优劣 / 影响 > 5 模块 / 破坏 API |
| [BLOCKED] | 排查 3 轮无进展 / 等外部依赖 |
| [CLOSING] | 上下文 > 80% / 人类说"今天到这" |

---

## 8 阶段循环速查

| 阶段 | 做什么 | 产出 |
|------|------|------|
| 1. 想法 | 展开需求 | L1_C01 |
| 2. 设计 | 架构 + 技术选型 | L2_D01 + project-graph(初建) + L4_O01(初建) |
| 3. 文档初始化 | 复制模板 | INDEX + 命名规范 + 术语表 |
| 4. 开发 | 写代码 | 代码 + 更新 project-graph + 追加 L4_O01 |
| 5. 测试 | 写测试 + 跑 | 测试文件 + project-graph(tests边) |
| 6. 审计 | 14维审计 | 审计报告 |
| 7. 修复 | 定位根因 → 修 | 代码 + 追加 L4_O01(如系统级bug) |
| 8. 维护 | 升级/迁移 | 全量测试 + project-graph 更新 |

---

## 完整方法论

详见 `methodology/INDEX.md`。14 篇专题覆盖从文档优先到人机协作到自我管理到生产就绪。

## 产量验收

每个阶段结束前对照 `methodology/14-production-readiness.md` 退出标准。不通过 → 不进入下一阶段。
