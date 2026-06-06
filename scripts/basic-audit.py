"""agent-compass 审计脚本 — 命名一致性 + 交叉引用检查

用法: python scripts/audit.py docs/
输出: 七维审计报告（markdown）
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


def check_glossary(docs_dir: str) -> list[dict]:
    """维度 6: 骨架残留 — TODO:/FIXME:/TBD:（只匹配显式标记，不匹配项目名）"""
    findings = []
    for f in Path(docs_dir).glob("*.md"):
        content = f.read_text(encoding="utf-8")
        # 只匹配显式标记格式: TODO:/TODO /FIXME:/TBD:（排除项目名如 todo-api）
        import_re = __import__("re")
        for marker in ["TODO:", "TODO ", "FIXME:", "FIXME ", "TBD:", "TBD "]:
            if import_re.search(marker, content):
                findings.append({
                    "file": f.name,
                    "issue": f"含 {marker.strip()}",
                    "severity": "WARN"
                })
                break
    return findings


def main():
    docs_dir = sys.argv[1] if len(sys.argv) > 1 else "docs"
    results = []

    for check, name in [
        (check_naming, "命名一致性"),
        (check_broken_links, "交叉引用完整性"),
        (check_glossary, "骨架残留"),
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
