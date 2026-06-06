# scripts/ — agent-compass 辅助脚本

| 脚本 | 用途 | 用法 |
|------|------|------|
| `init.sh` | Linux/macOS 一键复制核心文件到目标项目 | `bash init.sh /path/to/project` |
| `init.ps1` | Windows 一键复制 | `.\init.ps1 C:\path\to\project` |
| `basic-audit.py` | 快速审计（命名/断链/骨架 3 维） | `python basic-audit.py docs/` |
| `sync-graph.py` | 从代码自动同步 project-graph | `python sync-graph.py src/ docs/project-graph.yaml` |
| `check-naming.py` | 命名规范检查 | `python check-naming.py docs/` |

## 审计说明

`basic-audit.py` 只检查 3 维（命名/断链/骨架残留）。
完整 14 维审计需 Agent 读取 `methodology/04-audit-framework.md` 手动执行。

## 集成到 CI

```yaml
- name: 命名检查
  run: python scripts/check-naming.py templates/
- name: 快速审计
  run: python scripts/basic-audit.py templates/
```
