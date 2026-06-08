"""agentprecept MCP Server

启动: agentprecept-mcp
提供 6 个 tool: query / audit / diff / decision / handoff / design_gate
"""
import sys
from pathlib import Path

try:
    from fastmcp import FastMCP
except ImportError:
    print("需要安装 fastmcp: pip install fastmcp", file=sys.stderr)
    sys.exit(1)

_scripts = Path(__file__).resolve().parent.parent / "scripts"


def _load_script(name):
    path = _scripts / f"{name}.py"
    from importlib import util
    mod_spec = util.spec_from_file_location(name, path)
    mod = util.module_from_spec(mod_spec)
    mod_spec.loader.exec_module(mod)
    return mod


basic_audit = _load_script("basic-audit")
sync_graph = _load_script("sync-graph")

mcp = FastMCP("agentprecept")


@mcp.tool
def project_graph_query(module: str = "", query_type: str = "relations") -> dict:
    graph_path = Path("docs/project-graph.yaml")
    if not graph_path.exists():
        return {"error": "project-graph.yaml not found—run agentprecept sync first"}
    import yaml
    doc = yaml.safe_load(graph_path.read_text(encoding="utf-8")) or {}
    result = {}
    if query_type in ("relations", "all"):
        rels = doc.get("relations") or []
        if module:
            rels = [r for r in rels if r.get("from","").startswith(module) or r.get("to","").startswith(module)]
        result["relations"] = rels
        result["count"] = len(rels)
    if query_type in ("structure", "all"):
        st = doc.get("structure") or {}
        if module:
            st = {k:v for k,v in st.items() if k.startswith(module)}
        result["structure"] = st
    if query_type in ("evolution", "all"):
        result["evolution"] = doc.get("evolution") or []
    return result


@mcp.tool
def audit_run(docs_dir: str = "docs") -> dict:
    import io
    old = sys.stdout
    sys.stdout = io.StringIO()
    results = []
    for check, name in [
        (basic_audit.check_naming, "naming"),
        (basic_audit.check_broken_links, "broken_links"),
        (basic_audit.check_numbering, "numbering"),
        (basic_audit.check_skeleton, "skeleton"),
        (basic_audit.check_graph_schema, "graph_schema"),
        (basic_audit.check_design_trace, "design_trace"),
        (basic_audit.check_coverage, "coverage"),
        (basic_audit.check_dogfood, "dogfood"),
    ]:
        findings = check(docs_dir)
        has_fail = any(f["severity"] == "FAIL" for f in findings)
        results.append({"dimension": name, "status": "PASS" if not findings else "FAIL" if has_fail else "WARN", "findings": findings})
    sys.stdout = old
    fail = sum(1 for r in results if r["status"] == "FAIL")
    warn = sum(1 for r in results if r["status"] == "WARN")
    return {"results": results, "summary": {"FAIL": fail, "WARN": warn, "PASS": 8 - fail - warn}}


@mcp.tool
def sync_diff(src_dir: str = "src") -> dict:
    graph_path = Path("docs/project-graph.yaml")
    old = {}
    if graph_path.exists():
        import yaml
        existing = yaml.safe_load(graph_path.read_text(encoding="utf-8")) or {}
        old = {"structure": existing.get("structure",{}), "relations": existing.get("relations",[])}
    new_structure = sync_graph.build_structure(src_dir)
    all_relations = []
    for fn in [sync_graph.build_python_relations, sync_graph.build_js_relations, sync_graph.build_db_relations, sync_graph.build_api_relations, sync_graph.build_frontend_relations, sync_graph.build_external_relations]:
        all_relations.extend(fn(src_dir))
    old_keys = set(old.get("structure",{}).keys())
    new_keys = set(new_structure.keys())
    old_rels = {(r.get("from"), r.get("to"), r.get("type")) for r in old.get("relations",[])}
    new_rels = {(r["from"], r["to"], r["type"]) for r in all_relations}
    from collections import Counter
    types = Counter(r["type"] for r in all_relations)
    return {"structure": {"added": sorted(new_keys - old_keys), "removed": sorted(old_keys - new_keys)}, "relations": {"added": len(new_rels - old_rels), "removed": len(old_rels - new_rels), "total": len(all_relations)}, "type_counts": dict(types), "needs_sync": len(new_rels) != len(old_rels)}


@mcp.tool
def decision_search(query: str = "") -> list:
    p = Path("docs/L4_O01_design-rationale_设计依据.md")
    if not p.exists():
        return []
    return [l.strip() for l in p.read_text(encoding="utf-8").split("\n") if l.strip().startswith("| 为什么") and (query.lower() in l.lower() if query else True)]


@mcp.tool
def handoff_read() -> dict:
    p = Path("docs/HANDOFF.md")
    if not p.exists():
        return {"status": "HANDOFF not found"}
    content = p.read_text(encoding="utf-8")
    status = [l.replace("> 状态:", "").strip() for l in content.split("\n") if l.startswith("> 状态:")]
    next_lines = []
    in_next = False
    for l in content.split("\n"):
        if "## 下一步" in l:
            in_next = True
        elif in_next and l.strip().startswith(("1.","2.","3.","4.")):
            next_lines.append(l.strip())
    return {"status": status[0] if status else "", "next_step": " ".join(next_lines)}


@mcp.tool
def design_gate(module: str = "", operation: str = "modify") -> dict:
    """Agent 准备修改代码前调用。返回模块的前置设计文档状态。"""
    import json, subprocess, sys as _sys
    result = subprocess.run(
        [_sys.executable, str(_scripts / "design_gate_check.py"), "--module", module, "--json"],
        capture_output=True, text=True, timeout=10
    )
    if result.returncode not in (0, 1, 2):
        return {"status": "ERROR", "gates": [], "message": result.stderr}
    return json.loads(result.stdout)


def main():
    mcp.run()


if __name__ == "__main__":
    main()