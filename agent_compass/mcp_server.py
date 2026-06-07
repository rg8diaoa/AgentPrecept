"""agent-compass MCP Server — 将 agent-compass 功能暴露为 MCP tools

启动: compass-mcp
或: python -m agent_compass.mcp_server

提供 5 个 tool:
  - project_graph_query   查询项目图（structure / relations / evolution）
  - audit_run             运行 8 维审计并返回结构化报告
  - sync_diff             dry-run 同步, 返回待变更清单
  - decision_search       搜索 L4_O01 设计依据
  - handoff_read          读取当前会话交接状态
"""
import sys
from pathlib import Path

try:
    from fastmcp import FastMCP
except ImportError:
    print("需要安装 fastmcp: pip install fastmcp", file=sys.stderr)
    sys.exit(1)

# 把 scripts/ 加入 path, 以便复用现有函数
_scripts = Path(__file__).resolve().parent.parent / "scripts"
if str(_scripts) not in sys.path:
    sys.path.insert(0, str(_scripts))

import basic_audit
import sync_graph

mcp = FastMCP("agent-compass")


@mcp.tool
def project_graph_query(
    module: str = "",
    query_type: str = "relations",
) -> dict:
    """查询项目图信息。

    Args:
        module: 模块名（留空返回全部）, 如 "src/services"
        query_type: 查询类型 — "structure" / "relations" / "evolution" / "all"
    """
    graph_path = Path("docs/project-graph.yaml")
    if not graph_path.exists():
        return {"error": "project-graph.yaml 不存在, 请先运行 compass sync"}

    import yaml
    doc = yaml.safe_load(graph_path.read_text(encoding="utf-8")) or {}
    result = {}

    if query_type in ("relations", "all"):
        relations = doc.get("relations") or []
        if module:
            relations = [
                r for r in relations
                if r.get("from", "").startswith(module) or r.get("to", "").startswith(module)
            ]
        result["relations"] = relations
        result["count"] = len(relations)

    if query_type in ("structure", "all"):
        structure = doc.get("structure") or {}
        if module:
            structure = {k: v for k, v in structure.items() if k.startswith(module)}
        result["structure"] = structure

    if query_type in ("evolution", "all"):
        result["evolution"] = doc.get("evolution") or []

    return result


@mcp.tool
def audit_run(docs_dir: str = "docs") -> dict:
    """运行 8 维自动化审计, 返回结构化报告。

    Args:
        docs_dir: 文档目录路径, 默认 "docs"
    """
    import io
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()

    results = []
    for check, name in [
        (basic_audit.check_naming, "命名一致性"),
        (basic_audit.check_broken_links, "交叉引用完整性"),
        (basic_audit.check_numbering, "编号连续性"),
        (basic_audit.check_skeleton, "骨架残留"),
        (basic_audit.check_graph_schema, "项目图格式"),
        (basic_audit.check_design_trace, "设计追溯"),
        (basic_audit.check_coverage, "覆盖率"),
        (basic_audit.check_dogfood, "狗粮审计"),
    ]:
        findings = check(docs_dir)
        has_fail = any(item["severity"] == "FAIL" for item in findings)
        status = "PASS" if not findings else "FAIL" if has_fail else "WARN"
        results.append({
            "dimension": name,
            "status": status,
            "findings": findings,
        })

    sys.stdout = old_stdout
    total_fail = sum(1 for r in results if r["status"] == "FAIL")
    total_warn = sum(1 for r in results if r["status"] == "WARN")

    return {
        "results": results,
        "summary": {"FAIL": total_fail, "WARN": total_warn, "PASS": 8 - total_fail - total_warn},
        "docs_dir": docs_dir,
    }


@mcp.tool
def sync_diff(src_dir: str = "src") -> dict:
    """dry-run 同步: 扫描代码后返回待变更清单, 不写入文件。

    Args:
        src_dir: 源码目录, 默认 "src"
    """
    old = {}
    graph_path = Path("docs/project-graph.yaml")
    if graph_path.exists():
        import yaml
        existing = yaml.safe_load(graph_path.read_text(encoding="utf-8")) or {}
        old = {
            "structure": existing.get("structure", {}),
            "relations": existing.get("relations", []),
        }

    new_structure = sync_graph.build_structure(src_dir)
    all_relations = []
    all_relations.extend(sync_graph.build_python_relations(src_dir))
    all_relations.extend(sync_graph.build_js_relations(src_dir))
    all_relations.extend(sync_graph.build_db_relations(src_dir))
    all_relations.extend(sync_graph.build_api_relations(src_dir))
    all_relations.extend(sync_graph.build_frontend_relations(src_dir))
    all_relations.extend(sync_graph.build_external_relations(src_dir))

    # 比较变化
    old_structure_keys = set(old.get("structure", {}).keys())
    new_structure_keys = set(new_structure.keys())
    old_relations_set = {(r.get("from"), r.get("to"), r.get("type")) for r in old.get("relations", [])}
    new_relations_set = {(r["from"], r["to"], r["type"]) for r in all_relations}

    from collections import Counter
    type_counts = Counter(r["type"] for r in all_relations)

    return {
        "structure": {
            "added": sorted(new_structure_keys - old_structure_keys),
            "removed": sorted(old_structure_keys - new_structure_keys),
        },
        "relations": {
            "added": len(new_relations_set - old_relations_set),
            "removed": len(old_relations_set - new_relations_set),
            "total_new": len(all_relations),
        },
        "type_counts": dict(type_counts),
        "needs_sync": len(new_relations_set) != len(old_relations_set),
    }


@mcp.tool
def decision_search(query: str = "") -> list[dict]:
    """搜索 L4_O01 设计依据中的决策条目。

    Args:
        query: 搜索关键词（留空返回全部决策条目）
    """
    l4_path = Path("docs/L4_O01_design-rationale_设计依据.md")
    if not l4_path.exists():
        return []

    content = l4_path.read_text(encoding="utf-8")
    decisions = []
    for line in content.split("\n"):
        if line.strip().startswith("| 为什么") or line.strip().startswith("|为什么"):
            if query.lower() in line.lower() if query else True:
                decisions.append(line.strip())
    return decisions


@mcp.tool
def handoff_read() -> dict:
    """读取 docs/HANDOFF.md 的会话交接状态"""
    handoff_path = Path("docs/HANDOFF.md")
    if not handoff_path.exists():
        return {"status": "HANDOFF 不存在", "next_step": ""}

    content = handoff_path.read_text(encoding="utf-8")
    lines = content.split("\n")

    status = ""
    next_step = ""
    current_section = ""

    for line in lines:
        if line.startswith("> 状态:"):
            status = line.replace("> 状态:", "").strip()
        elif "## 下一步" in line:
            current_section = "next"
        elif current_section == "next" and line.strip().startswith(("1.", "2.", "3.", "4.")):
            next_step += line.strip() + " "

    return {
        "status": status,
        "next_step": next_step.strip(),
        "file_exists": True,
    }


def main():
    mcp.run()


if __name__ == "__main__":
    main()
