# 架构设计

> 分类: D | 层级: L2 | 编号: L2_D01
> 状态: 📝 撰写中 | 目标读者: 设计审查

---

## 四层结构

```
agent-compass/
│
├── 方法论层 (methodology/)    ← 给人类阅读的原理和原则
│   └── 00-lifecycle → 01-why → ... → 13-self-management
│
├── 模板层 (templates/)       ← 给 Agent 的可执行产出模板
│   └── 31 编号 + 4 工具，16/16 分类
│
├── 示例层 (examples/)        ← 给用户的 onboarding
│   └── Python + Node.js + Prompt 模板 + first-run
│
└── 参考层 (reference/)       ← 证明方法论有效
    └── 审计收敛 + 多维图案例
```

## 模块依赖

```
README → AGENTS → methodology/00 → methodology/07,08,12,13
                                    ↓
                              templates/（Agent 按需读取并产出）
                              examples/first-run（用户初始化工单）
```

## 关键设计决策

见 `docs/L4_O01_design-rationale.md`。
