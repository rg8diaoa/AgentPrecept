"""从代码自动同步 project-graph.yaml 的结构层和关系层

用法: python scripts/sync-graph.py src/ docs/project-graph.yaml

用 tree 生成结构层（不覆盖 stability 和 description），
用 grep import 生成关系层（追加到现有 relations）。
不覆盖 evolution 层和人类手动修改的条目。
"""
import os, re, sys, yaml
from pathlib import Path


def build_structure(src_dir: str) -> dict:
    """从目录树生成结构层"""
    structure = {}
    src = Path(src_dir)
    if not src.exists():
        return structure

    for d in sorted(src.glob("**/")):
        if d.name.startswith(".") or d.name.startswith("_"):
            continue
        rel = str(d.relative_to(src.parent))
        children = [f.name for f in sorted(d.glob("*.py")) if not f.name.startswith("_")]
        if children or d == src:
            structure[rel] = {
                "type": "package",
                "stability": "stable",  # Agent 自动推断，未人工确认
                "children": children,
            }
    return structure


def build_relations(src_dir: str) -> list:
    """从 import 语句生成关系层"""
    import_pattern = re.compile(r'^(?:from|import)\s+(\S+)', re.MULTILINE)
    relations = []
    src = Path(src_dir)

    for f_py in sorted(src.glob("**/*.py")):
        if f_py.name.startswith("_") or f_py.name.startswith("test"):
            continue
        content = f_py.read_text(encoding="utf-8")
        imports = import_pattern.findall(content)
        for imp in imports:
            imp_clean = imp.split(".")[0]
            # 只记录项目内部导入（不是标准库/第三方）
            if imp_clean in ["os", "sys", "re", "json", "logging", "datetime",
                              "typing", "pathlib", "collections", "functools",
                              "fastapi", "uvicorn", "pytest", "sqlalchemy",
                              "pydantic", "flask", "django", "asyncio"]:
                continue
            rel = str(f_py.relative_to(src.parent)).replace("\\", "/")
            relations.append({
                "from": rel,
                "to": f"{imp_clean}",
                "type": "depends_on",
            })
    return relations


def main():
    src_dir = sys.argv[1] if len(sys.argv) > 1 else "src"
    graph_path = sys.argv[2] if len(sys.argv) > 2 else "docs/project-graph.yaml"

    graph_file = Path(graph_path)
    if graph_file.exists():
        existing = yaml.safe_load(graph_file.read_text(encoding="utf-8")) or {}
    else:
        existing = {}

    new_structure = build_structure(src_dir)
    # 保留已有的 stability 和 description
    old_structure = existing.get("structure", {})
    for k, v in new_structure.items():
        if k not in old_structure:
            old_structure[k] = v
        else:
            old_structure[k].update(
                {kk: vv for kk, vv in v.items()
                 if kk not in old_structure[k]}
            )

    new_relations = build_relations(src_dir)
    old_relations = existing.get("relations", [])
    seen = {(r["from"], r["to"]) for r in old_relations}
    for r in new_relations:
        if (r["from"], r["to"]) not in seen:
            old_relations.append(r)
            seen.add((r["from"], r["to"]))

    existing["structure"] = old_structure
    existing["relations"] = old_relations
    existing.setdefault("evolution", [])

    graph_file.write_text(yaml.dump(existing, allow_unicode=True, sort_keys=False, default_flow_style=False),
                          encoding="utf-8")
    print(f"✅ project-graph 已同步: {len(old_structure)} 结构 / {len(old_relations)} 关系 / {len(existing['evolution'])} 演变")


if __name__ == "__main__":
    main()
