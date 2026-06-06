# agent-compass 🧭

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![CI](https://github.com/user/agent-compass/actions/workflows/audit.yml/badge.svg)](https://github.com/user/agent-compass/actions)

> **Agent A 产出的代码 + 图 + 依据 + 交接 → Agent B 无缝接手。**
>
> 不是"写文档的方法论"。是让多个 Agent 在同一个项目上协作不踩脚、不推翻、不迷路。

## 快速开始

### 第一选择：路径 A — 3 文件，30 秒

```bash
pip install agent-compass
agent-compass init /path/to/your-project
# 或 make init PROJECT=/path/to/your-project
```

只要 AGENTS.md + project-graph.yaml + HANDOFF.md。Agent 自动干活。适合 90% 的用户。

### 完整体验：路径 C — 完整文档体系

```bash
cp -r templates/* /your-project/docs/
```

35 个模板，16/16 分类全齐。很少需要——新项目初始化时用。

### 跑 demo

```bash
make todo-api-test    # 4/4 测试全绿
```


## 核心机制

```
Agent A 写完代码 → 自动更新 project-graph（改了哪些模块/谁依赖谁）
                → 自动追加 L4_O01（为什么这样设计）
                → 自动重写 HANDOFF（做到哪了/下一步/上下文还剩多少）

Agent B 打开项目 → 读 project-graph（秒懂项目结构，不用遍历源码）
                → 读 L4_O01（知道哪些决策不能推翻）
                → 读 HANDOFF（知道从哪继续，不用从头来）
```

## 对比

| 场景 | 没有 agent-compass | 有 agent-compass |
|------|------|------|
| Agent 接手别人的项目 | 遍历源码 20 分钟才敢动手 | 读 project-graph 30 秒知道项目结构 |
| Agent 修 bug | 不知道改了会影响谁 | 读 relations 层→知道影响 2 个文件 |
| Agent 加功能 | 命名随意，三个月后另一个 Agent 叫不同名字 | 查术语表→复用已有术语 |
| 换了一个 Agent | 不知道上个人做了什么 | 读 HANDOFF→知道做到哪了 |
| Agent 提了已否决的方案 | 人类一遍遍解释"这个不行" | Agent 读 L4_O01→自觉不提 |
| Agent 做完没人审 | 默默改完没人知道 | HANDOFF 标记 [NEEDS_HUMAN_REVIEW] |

> methodology/ 使用纯数字编号（00-14）——教学材料保持线性阅读顺序。项目文档遵循 L 格式（见 `templates/L1_A02`）。参见 `docs/L4_O01` ADR-002。

## 目录

```
agent-compass/
├── AGENTS.md          ← Agent 入口（硬规则 + 软建议 + 自动动作）
├── SKILL.md           ← Skill 工具入口
│
├── methodology/       ← 12 篇方法论（人类阅读）
├── templates/         ← 35 个模板（Agent 按需读取按指令产出）
├── examples/          ← 初始化 prompt + Python/Node 示例
├── reference/         ← 实战案例
├── docs/              ← agent-compass 自身文档（狗粮）
│
├── LICENSE (MIT) / CONTRIBUTING / CODE_OF_CONDUCT / CHANGELOG
```

## 为什么选 agent-compass

市场上有很多"给 Agent 写指令"的项目，但 agent-compass 做了三件别人没做的事：

1. **结构化交接**：project-graph.yaml + L4_O01 是数据，不是散文。Agent 30 秒重建项目心智模型，不用遍历源码
2. **人类审 Agent**：14-production-readiness 给每个阶段设了退出标准——你不懂架构也能判断 Agent 的产出是否合格
3. **教训驱动**：每条规则背后有实际踩过的坑，不是"你应该"的道德说教

横向对比见 `reference/comparison.md`。

## 适用场景

- ✅ 多人 + 多 Agent 协作
- ✅ 开源项目接受外部贡献
- ✅ 项目已运行半年以上，需要留存设计决策
- ✅ 团队有人不太懂代码但要审 Agent 产出
- ❌ 单人 + < 5 模块——直接用 AGENTS.md 一段话

## 实战验证

源自一个 41 文档/46 配置的多 Agent 项目。三轮审计从 12 问题收敛到 0。外部评审 9.0/10。

## 许可证

MIT
