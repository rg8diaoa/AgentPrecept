"""ripple_check — 涟漪分析：给定变更文件，输出项目图中的影响范围

用法:
  python scripts/ripple_check.py file1.py file2.py
  python scripts/ripple_check.py --diff HEAD~1         # 从 git diff 获取变更文件
  python scripts/ripple_check.py --all                   # 全量分析所有 relations

输出:
  [DIRECT]  直接依赖: relations 中 to 字段匹配变更文件的条目
  [INDIRECT] 间接依赖: DIRECT 条目的 from 文件（它们也受影响）
  [SAME_PKG] 同一包内: 与变更文件同目录的其他文件
"""
import sys
import json
from pathlib import Path
from collections import defaultdict

GRAPH_PATH = Path("docs/project-graph.yaml")


def load_graph():
    if not GRAPH_PATH.exists():
        return None
    import yaml
    return yaml.safe_load(GRAPH_PATH.read_text(encoding="utf-8")) or {}


def get_changed_files():
    """获取变更文件列表"""
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--diff" in sys.argv:
        import subprocess as sp
        idx = sys.argv.index("--diff")
        rev = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "HEAD~1"
        result = sp.run(["git", "diff", "--name-only", rev, "HEAD"],
                        capture_output=True, text=True, timeout=10)
        return [f.strip() for f in result.stdout.split("\n") if f.strip()]
    if "--all" in sys.argv:
        graph = load_graph()
        if graph:
            return list(graph.get("structure", {}).keys())
        return []
    return args


def analyze(changed_files, graph):
    """分析涟漪范围"""
    relations = graph.get("relations", [])
    structure = graph.get("structure", {})

    # [DIRECT] 直接依赖: relation.to 匹配变更文件
    direct = []
    for rel in relations:
        to_val = rel.get("to", "")
        for cf in changed_files:
            if cf and to_val.startswith(cf.rstrip("/")):
                direct.append(rel)
                break

    # 受影响模块: relation.from 匹配变更文件的那些 relation 的 to
    affected = set()
    for rel in relations:
        from_val = rel.get("from", "")
        for cf in changed_files:
            if cf and from_val.startswith(cf.rstrip("/")):
                if rel.get("to"):
                    affected.add(rel["to"])

    # [INDIRECT] 间接: 直接依赖的 from 文件
    indirect = set()
    for rel in direct:
        if rel.get("from"):
            f = rel["from"]
            if f not in [c.rstrip("/") for c in changed_files]:
                indirect.add(f)

    # 也加入 affected
    indirect |= affected

    # [SAME_PKG] 同一包内: 与变更文件同目录下的其他文件
    same_pkg = set()
    for cf in changed_files:
        pkg_path = "/".join(cf.split("/")[:-1]) if "/" in cf else ""
        if pkg_path:
            for sp in structure:
                if sp.startswith(pkg_path) and sp != cf and not sp.endswith("/"):
                    fname = sp.split("/")[-1]
                    if "." in fname:
                        same_pkg.add(sp)

    return {
        "direct_count": len(direct),
        "direct": direct,
        "indirect": sorted(indirect),
        "same_pkg": sorted(same_pkg),
    }


def main():
    json_mode = "--json" in sys.argv
    graph = load_graph()
    if not graph:
        print("project-graph.yaml not found")
        sys.exit(1)

    changed = get_changed_files()
    if not changed:
        print("no changed files")
        sys.exit(0)

    result = analyze(changed, graph)

    if json_mode:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    print(f"# 涟漪分析: {len(changed)} changed file(s)")
    print()

    if result["direct"]:
        print("## [DIRECT] 直接依赖")
        for rel in result["direct"]:
            print(f"  {rel['from']} -> {rel['to']} ({rel['type']})")
        print()

    if result["indirect"]:
        print("## [INDIRECT] 间接影响")
        for f in result["indirect"]:
            print(f"  {f}")
        print()

    if result["same_pkg"]:
        print("## [SAME_PKG] 同一包内")
        for f in result["same_pkg"]:
            print(f"  {f}")
        print()

    direct_n = result["direct_count"]
    indirect_n = len(result["indirect"])
    same_n = len(result["same_pkg"])
    total = direct_n + indirect_n + same_n
    print(f"---\n总计: [DIRECT]{direct_n} [INDIRECT]{indirect_n} [SAME_PKG]{same_n} = {total} affected")


if __name__ == "__main__":
    main()