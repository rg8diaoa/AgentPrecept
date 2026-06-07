# 变更日志

## [0.2.0] — 2026-06-07

### MCP Server 上线

- **MCP Server**：FastMCP 实现，注册 5 个 Tool（project_graph_query / audit_run / sync_diff / decision_search / handoff_read）
- **MCP 自动配置**：首次邂逅检测自动配置 mcp.json（含 cwd + PYTHONIOENCODING Windows 兼容）
- **双向 MCP 检测**：全局 instructions 检测"MCP 可用+项目未 init"→提示初始化；项目 AGENTS 检测"有规则+无 MCP"→提示配置
- **mcp-tools.md**：完整 Tool API 参考文档，CodeWhale 配置示例从 TOML 改为 mcp.json

### MEMORY 机制重新设计

- **自动生长**：MEMORY.md 从静态填空模板改为引导型模板，Agent 在对话中自动追加偏好/约束/教训
- **全局偏好分离**：agent-compass 自身 MEMORY 瘦身为纯项目约束，用户全局偏好移至 CodeWhale note
- **init 脚本升级**：一等公民 4→5（新增 MEMORY.md），init.ps1 和 init.sh 双平台同步

### 项目图补全

- **project-graph relations**：从空列表补全为 14 条边（import/reference/read/write），覆盖 agent_compass/↔scripts/↔docs/
- **structure 修复**：agent_compass/ 去重 + 补 mcp_server.py；新增 scripts/ 包；docs/ 补 mcp-tools.md
- **templates 补文件**：创建 templates/HANDOFF.md 和 templates/L4_O01_design-rationale_设计依据.md（init 脚本引用的空白模板）

### 规则加固

- **"go" 语义钉死**：确认的是上一轮的设计草稿，不是讨论；两步确认不可合并
- **狗粮自检 4 项**：L2_D01 架构 + init 模板完整性 + project-graph relations + 规则一致性
- **审计缓存陷阱**：MCP tool 返回 TOOL_RESULT_REF 必须重新获取实际结果
- **讨论阶段拦截强化**：agent-compass 自身变更不豁免设计先行
- **模板外脑**：Agent 知道 templates/（36 个）和 methodology/（16 篇）按需取用

### 全维度审计

- 8 维自动化审计全 PASS
- 修复 12+ 处过时引用：methodology/ 和根目录文件中 14-dim→8 维自动、audit.py→basic-audit.py、gen-changelog.py→注释化
- INDEX.md 数字修正：14 维审计→8 自动+6 按需、35+→44+ ADR、35→36 模板、15→16 方法论
- methodology/ 和根目录 GitHub 文档全部交叉引用验证

### README 全面同步

- 安装方式双路线（Agent 自动装 / 手动装）
- 数字同步：核心文档 7→8、方法论 15→16、模板 35→36
- 去重 docs/ 目录树行
- 审计描述：14 维中能自动化→8 维自动+6 维按需
- 核心文件表补 mcp-tools.md
- MEMORY 描述加"Agent 自动生长"

---

## [0.1.0] — 2026-06-06

### 核心机制

- **结构化项目图**（project-graph.yaml）：三层模型 + stability 字段（critical/stable/volatile）
- **设计依据**（L4_O01）：每决策一行表格，从 git log 反推
- **会话交接**（HANDOFF）：5 状态标记 + 上下文用量 + Agent 自我判断
- **AGENTS.md**：硬规则 8 条 + 软建议 + 自动动作 + 渐进加载

### 方法论（15 篇）

- 00 完整循环（8 阶段）
- 01-14 专题：文档/命名/设计依据/审计/交接/图/工作流/工程化/安全/性能/接入/人机协作/自我管理/生产就绪
- 14 维审计（8 维自动）框架（含狗粮/用户旅程/体验/定位/复用/社区）

### 模板（35 个，16/16 分类全齐）

- 31 编号模板 + 4 工具文件
- 🔥 核心 5 个：project-graph / L4_O01 / HANDOFF / 测试用例 / 架构设计
- 6 个模板深挖为 Agent 可执行指令

### 可执行物

- `scripts/`：init.sh / init.ps1 / basic-audit.py / sync-graph.py / graph-to-mermaid.py / check-naming.py
- `skills/`：5 个核心 skill（project-graph/design-rationale/session-handoff/test-cases/architecture-design）
- `templates/MEMORY.md`：跨会话持久记忆模板
- `Makefile`：make init / make audit / make todo-api-test
- `.github/workflows/`：audit.yml + test-examples.yml
- `examples/todo-api/`：可运行的 FastAPI demo（4 测试全绿）

### 参考与对比

- 审计收敛历程 + 多维图案例
- 横向对比（vs AGENTS.md / CLAUDE.md / Cursor Rules / CrewAI / CodeWhale Skill / ECC / Karpathy Skills）
- Agent 自身评估（deepseek-v4-pro 真实看法）
- 速查卡片（cheatsheet.md）

### 开源元文件

LICENSE (MIT) / CONTRIBUTING / CODE_OF_CONDUCT / README / SKILL / .gitignore
