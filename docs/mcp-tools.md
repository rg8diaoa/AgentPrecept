# MCP Tools 参考

agent-compass 通过 MCP Server 暴露 5 个 tool，供任何支持 MCP 的 Agent 调用。

## 启动

```bash
compass-mcp
# 或
python -m agent_compass.mcp_server
```

前置条件：`pip install fastmcp`

## Tool 列表

### 1. project_graph_query

查询项目图信息。

```json
// 请求
{
  "module": "src/services",
  "query_type": "relations"
}

// 响应
{
  "relations": [
    {"from": "src/services/diary_service.py", "to": "src.models.diary.DiaryEntry", "type": "depends_on"},
    ...
  ],
  "count": 15
}
```

| 参数 | 类型 | 说明 |
|------|------|------|
| module | string | 模块名（留空=全部），如 "src/services" |
| query_type | string | "structure" / "relations" / "evolution" / "all" |

### 2. audit_run

运行 8 维自动化审计。

```json
// 请求
{
  "docs_dir": "docs"
}

// 响应
{
  "results": [
    {"dimension": "命名一致性", "status": "PASS", "findings": []},
    ...
  ],
  "summary": {"FAIL": 0, "WARN": 1, "PASS": 7}
}
```

| 参数 | 类型 | 默认 |
|------|------|------|
| docs_dir | string | "docs" |

### 3. sync_diff

dry-run 同步——不写文件，返回待变更清单。

```json
// 请求
{
  "src_dir": "src"
}

// 响应
{
  "structure": {"added": ["src/new_module"], "removed": []},
  "relations": {"added": 5, "removed": 1, "total_new": 84},
  "type_counts": {"depends_on": 76, "maps_to": 5, "calls": 2, "mounts": 1},
  "needs_sync": true
}
```

### 4. decision_search

搜索设计依据。

```json
// 请求
{
  "query": "Peewee"
}

// 响应
[
  "| 为什么选择 Peewee 而非 SQLAlchemy | ORM 选型 | 项目规模小（5 model），Peewee 更轻量；未来如有复杂查询需求再迁移 |"
]
```

### 5. handoff_read

读取会话交接状态。

```json
// 请求
{}

// 响应
{
  "status": "[IN_PROGRESS]",
  "next_step": "1. 完成 MCP Server 验证 2. 切到 gnhf 集成分支",
  "file_exists": true
}
```

## 在 Code Agent 中配置

### Claude Code

```json
// .mcp.json
{
  "mcpServers": {
    "agent-compass": {
      "command": "python",
      "args": ["-m", "agent_compass.mcp_server"]
    }
  }
}
```

### CodeWhale

在 CodeWhale 配置文件中添加：

```toml
[mcp_servers.agent-compass]
command = "compass-mcp"
```

### Cursor / OpenCode

```json
{
  "mcpServers": {
    "agent-compass": {
      "command": "python",
      "args": ["-m", "agent_compass.mcp_server"],
      "args": []
    }
  }
}
```
