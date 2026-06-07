"""agent-compass 审计脚本 — 命名一致性 + 交叉引用检查 + 骨架残留 + 图格式

用法: python scripts/audit.py docs/
输出: 四维审计报告（markdown）
"""
import os, re, sys
from pathlib import Path


def check_naming(docs_dir: str) -> list[dict]:
    """维度 1: 文件名是否符合 L{Level}_{CAT}{NN}_{Slug}_{Title}.md"""
    pattern = r'^L[1-4]_[A-P]\d{2}_[a-z0-9-]+_.+\.md$'
    findings = []
    for f in Path(docs_dir).glob("*.md"):
        if not f.name.startswith("L"):
            continue
        if not re.match(pattern, f.name):
            findings.append({"file": f.name, "issue": "命名不符合规范", "severity": "FAIL"})
    return findings


def check_broken_links(docs_dir: str) -> list[dict]:
    """维度 2: 交叉引用断链"""
    findings = []
    for f in Path(docs_dir).glob("*.md"):
        content = f.read_text(encoding="utf-8")
        refs = re.findall(r'\(([^)]+\.md)\)', content)
        for ref in refs:
            target = (f.parent / ref.split("#")[0]).resolve()
            if not target.exists():
                findings.append({
                    "file": f.name,
                    "issue": f"引用不存在: {ref}",
                    "severity": "FAIL"
                })
    return findings


def check_skeleton(docs_dir: str) -> list[dict]:
    """维度 3: 骨架残留 — TODO:/FIXME:/TBD:"""
    findings = []
    for f in Path(docs_dir).glob("*.md"):
        content = f.read_text(encoding="utf-8")
        for marker in ["TODO:", "TODO ", "FIXME:", "FIXME ", "TBD:", "TBD "]:
            if marker in content:
                findings.append({
                    "file": f.name,
                    "issue": f"含 {marker.strip()}",
                    "severity": "WARN"
                })
                break
    return findings


def check_graph_schema(docs_dir: str) -> list[dict]:
    """维度 4: project-graph.yaml 格式校验"""
    graph_path = Path(docs_dir) / "project-graph.yaml"
    findings = []

    if not graph_path.exists():
        findings.append({
            "file": "project-graph.yaml",
            "issue": "文件不存在",
            "severity": "FAIL"
        })
        return findings

    try:
        import yaml
    except ImportError:
        findings.append({
            "file": "project-graph.yaml",
            "issue": "PyYAML 未安装，无法校验格式",
            "severity": "WARN"
        })
        return findings

    try:
        doc = yaml.safe_load(graph_path.read_text(encoding="utf-8"))
    except Exception as e:
        findings.append({
            "file": "project-graph.yaml",
            "issue": f"YAML 解析失败: {e}",
            "severity": "FAIL"
        })
        return findings

    if doc is None:
        findings.append({
            "file": "project-graph.yaml",
            "issue": "文件为空或全为注释",
            "severity": "FAIL"
        })
        return findings

    # 检查 top-level 键
    valid_top_keys = {"structure", "relations", "evolution"}
    actual_keys = set(doc.keys())
    extra_keys = actual_keys - valid_top_keys
    if extra_keys:
        findings.append({
            "file": "project-graph.yaml",
            "issue": f"top-level 含非标准键: {extra_keys}（标准: structure/relations/evolution）",
            "severity": "FAIL"
        })

    # 检查 structure
    structure = doc.get("structure")
    if structure is None:
        findings.append({
            "file": "project-graph.yaml",
            "issue": "structure 字段为空（应为 {}）",
            "severity": "FAIL"
        })
    elif isinstance(structure, dict):
        for path, meta in structure.items():
            if not isinstance(meta, dict):
                findings.append({
                    "file": "project-graph.yaml",
                    "issue": f"structure.{path} 不是字典",
                    "severity": "FAIL"
                })
                continue
            if "type" not in meta:
                findings.append({
                    "file": "project-graph.yaml",
                    "issue": f"structure.{path} 缺 type 字段",
                    "severity": "FAIL"
                })
            if "description" not in meta and "children" not in meta:
                findings.append({
                    "file": "project-graph.yaml",
                    "issue": f"structure.{path} 既无 description 也无 children",
                    "severity": "WARN"
                })

    # 检查 relations
    relations = doc.get("relations")
    if relations is None:
        findings.append({
            "file": "project-graph.yaml",
            "issue": "relations 字段为空（应为 []）",
            "severity": "WARN"
        })
    elif isinstance(relations, list):
        valid_types = {"depends_on", "references", "indexes", "extends", "demonstrates", "tests"}
        for i, rel in enumerate(relations):
            if not isinstance(rel, dict):
                findings.append({
                    "file": "project-graph.yaml",
                    "issue": f"relations[{i}] 不是字典",
                    "severity": "FAIL"
                })
                continue
            for field in ["from", "to", "type"]:
                if field not in rel:
                    findings.append({
                        "file": "project-graph.yaml",
                        "issue": f"relations[{i}] 缺 {field} 字段",
                        "severity": "FAIL"
                    })
            if rel.get("type") and rel["type"] not in valid_types:
                findings.append({
                    "file": "project-graph.yaml",
                    "issue": f"relations[{i}].type='{rel['type']}' 不在标准值中 ({valid_types})",
                    "severity": "WARN"
                })
            # 检查 to 字段是否为非标准结构（如 list 而非 string）
            to_val = rel.get("to")
            if isinstance(to_val, list):
                findings.append({
                    "file": "project-graph.yaml",
                    "issue": f"relations[{i}].to 是列表（应为字符串），标准格式不支持 to: [...]",
                    "severity": "FAIL"
                })

    return findings


def main():
    docs_dir = sys.argv[1] if len(sys.argv) > 1 else "docs"
    results = []

    for check, name in [
        (check_naming, "命名一致性"),
        (check_broken_links, "交叉引用完整性"),
        (check_skeleton, "骨架残留"),
        (check_graph_schema, "项目图格式"),
    ]:
        findings = check(docs_dir)
        has_fail = any(item["severity"] == "FAIL" for item in findings)
        status = "PASS" if not findings else "FAIL" if has_fail else "WARN"
        results.append((name, status, findings))

    print("# 审计报告\n")
    print(f"审计范围: {docs_dir}/")
    for name, status, findings in results:
        print(f"## [{status}] {name}")
        if findings:
            for f_item in findings:
                print(f"- [{f_item['severity']}] {f_item['file']}: {f_item['issue']}")
        else:
            print("无问题")
        print()

    total_fail = sum(1 for _, s, _ in results if s == "FAIL")
    total_warn = sum(1 for _, s, _ in results if s == "WARN")
    print(f"---\nFAIL {total_fail}  WARN {total_warn}")
    exit(1 if total_fail else 0)


if __name__ == "__main__":
    main()
