# 快速开始

> 分类: A | 层级: L1 | 编号: L1_A01
> 状态: 📝 撰写中 | 目标读者: 开发者

---

## 这是什么

agent-compass 是一套 Agent 开发方法论。本文档是 agent-compass 自身的快速开始——如何贡献、修改、扩展这套方法论。

## 项目结构

```
agent-compass/
├── methodology/      ← 方法论核心（12 篇 + 循环总览）
├── templates/        ← 31 个编号模板 + 4 个工具文件
├── examples/         ← 示例项目 + prompt 模板
├── reference/        ← 参考案例
├── docs/             ← 自身文档（你正在看）
└── AGENTS.md         ← Agent 入口
```

## 如何贡献

1. Fork → 修改 → PR
2. 新增方法论文档：遵循 `methodology/` 中的编号规则
3. 新增模板：遵循 `L{Level}_{CAT}{NN}_{Slug}_{Title}.md` 格式
4. 更新 `docs/INDEX.md` 和 `templates/INDEX.md` 同步

## 如何修改方法论

1. 如果修改已锁定文档（✅）→ 同步更新 `docs/L4_M01_changelog.md`
2. 如果新增方法论 → `NN` 编号追加到现有末尾
3. 修改后跑 `methodology/04-audit-framework.md` 中的审计清单
