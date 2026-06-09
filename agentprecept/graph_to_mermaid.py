"""project-graph.yaml → Mermaid 可视化

用法: python scripts/graph-to-mermaid.py docs/project-graph.yaml

输出可直接嵌入 .md 的 Mermaid 代码块。
GitHub/VS Code 自动渲染。
"""
import sys, yaml
from pathlib import Path


def color_for_stability(stability: str) -> str:
    colors = {
        "critical": "#ff6b6b",  # 红
        "stable": "#4ecdc4",     # 青
        "volatile": "#999",      # 灰
    }
    return colors.get(stability, "#eee")


def main():
    graph_path = sys.argv[1] if len(sys.argv) > 1 else "docs/project-graph.yaml"
    doc = yaml.safe_load(Path(graph_path).read_text(encoding="utf-8")) or {}

    structure = doc.get("structure", {})
    relations = doc.get("relations", [])
    evolution = doc.get("evolution", [])

    print("```mermaid")
    print("graph TD")

    # 节点
    node_ids = {}
    idx = 0
    for path, meta in structure.items():
        nid = f"N{idx}"
        node_ids[path] = nid
        stability = meta.get("stability", "stable")
        label = path.replace("/", "/<br/>")
        print(f'    {nid}["{label}"]')
        print(f'    style {nid} fill:{color_for_stability(stability)}')
        idx += 1

    # 边
    for rel in relations:
        src = rel.get("from", "").replace("\\", "/")
        dst = rel.get("to", "").replace("\\", "/")
        rtype = rel.get("type", "depends_on")
        # 找最佳匹配节点
        src_nid = None
        dst_nid = None
        for path, nid in node_ids.items():
            if path in src:
                src_nid = nid
            if path in dst:
                dst_nid = nid
        if src_nid and dst_nid:
            arrow = "-->|tests|" if rtype == "tests" else "-->"
            print(f"    {src_nid} {arrow} {dst_nid}")

    # 图例
    print("    subgraph Legend")
    print('        L1["critical"]:::critical')
    print('        L2["stable"]:::stable')
    print('        L3["volatile"]:::volatile')
    print("    end")
    print("    classDef critical fill:#ff6b6b")
    print("    classDef stable fill:#4ecdc4")
    print("    classDef volatile fill:#999")
    print("```")

    if evolution:
        print(f"\n> {len(evolution)} 条设计决策。详见 L4_O01。")


if __name__ == "__main__":
    main()
