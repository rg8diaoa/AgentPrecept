# 方法论索引

agent-compass 的完整方法论文档。

## 阅读路线

**最小路线（15 分钟）**：`00 → 07`（理解完整循环 + 最常用的开发/修复阶段）

**完整路线（45 分钟）**：`00 → 01 → 02 → 03 → 07 → 04 → 05 → 06`

---

## 核心文档

| 编号 | 文件 | 回答什么问题 |
|:--|------|------|
| **00** | [**00-lifecycle.md**](00-lifecycle.md) | **从想法到维护的完整循环——Agent 在每个阶段该做什么** |
| 01 | [01-why-docs-first.md](01-why-docs-first.md) | 为什么 Agent 需要结构化上下文？ |
| 02 | [02-naming-is-navigation.md](02-naming-is-navigation.md) | 文件怎么命名才能让 Agent 秒找到？ |
| 03 | [03-design-rationale.md](03-design-rationale.md) | 怎样防止 Agent 推翻已验证的决策？ |
| 04 | [04-audit-framework.md](04-audit-framework.md) | Agent 的产出怎么系统性检查质量？ |
| 05 | [05-handoff-pattern.md](05-handoff-pattern.md) | 多个 Agent 会话之间怎么交接上下文？ |
| 06 | [06-three-layer-graph.md](06-three-layer-graph.md) | 怎么用图让 Agent 理解项目结构？ |
| 07 | [07-dev-workflow.md](07-dev-workflow.md) | 修 bug / 加功能 / 重构时具体怎么做 |
| 08 | [08-engineering.md](08-engineering.md) | CI/CD + 审计自动化 + 版本发布 + 并发安全 |
| 09 | [09-security.md](09-security.md) | Agent 安全基线：硬编码/注入/认证/输入验证/依赖扫描 |
| 10 | [10-performance.md](10-performance.md) | Agent 性能优化：测量→基线→优化→验证→记录 |
| 11 | [11-existing-project.md](11-existing-project.md) | 已有项目渐进接入指南 |
| 12 | [12-human-agent-collaboration.md](12-human-agent-collaboration.md) | 人机协作：什么时候停下/追问/等确认 |
| 13 | [13-agent-self-management.md](13-agent-self-management.md) | Agent 自我管理：上下文/漂移/死循环/并行 |
| 14 | [14-production-readiness.md](14-production-readiness.md) | **8 阶段退出标准 + 人类评判 Agent 产出及格线** |
> 04-06 是支撑型方法论，按需阅读。07-14 是操作型和进阶篇。 |

---

## 按循环阶段查找

| 阶段 | 文档 |
|---|---|
| 1. 想法 → 需求 | 00 §阶段1 |
| 2. 设计 → 架构 | 00 §阶段2 + 03 + 06 |
| 3. 文档初始化 | 00 §阶段3 + 01 + 02 |
| 4. 开发 → 写代码 | 00 §阶段4 + 07 |
| 5. 测试 → 验证 | 00 §阶段5 |
| 6. 审计 → 质量检查 | 00 §阶段6 + 04 |
| 7. 修复 → bug | 00 §阶段7 + 07 场景1 |
| 8. 维护 → 长期 | 00 §阶段8 + 08 |

---

## 不在此目录

- **模板文件** — 在 `../templates/` 中，可直接拷贝使用
- **参考案例** — 在 `../reference/` 中
- **示例项目** — 在 `../examples/todo-api/` 中
