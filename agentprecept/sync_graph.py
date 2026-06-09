"""从代码自动同步 project-graph.yaml 的结构层和关系层

用法: python -m agentprecept.sync_graph src/ docs/project-graph.yaml

用 tree 生成结构层（不覆盖 stability 和 description），
多维度扫描生成关系层（全量替换 relations）：
  - depends_on: Python/JS import（符号级，多语言）
  - maps_to:    ORM model → DB table
  - exposes:    模块 → API 端点 / 页面挂载
  - routes:     页面 → 页面导航
  - calls:      函数 → 外部服务

输出: 类型统计 + 框架推断 + 盲区检测报告
不覆盖 evolution 层和人类手动修改的条目。
"""
import json, os, re, sys, yaml
from collections import Counter
from pathlib import Path

# 标准库 + 常见第三方库首段（排除，不记录）
STDLIB_ROOTS = {
    "os", "sys", "re", "json", "logging", "datetime",
    "typing", "pathlib", "collections", "functools",
    "dataclasses", "enum", "abc", "contextlib", "itertools",
    "math", "random", "hashlib", "uuid", "io", "time",
    "threading", "subprocess", "shutil", "tempfile", "atexit",
    "copy", "textwrap", "argparse", "traceback", "warnings",
    "unittest", "doctest", "pdb",
    "fastapi", "uvicorn", "pytest", "sqlalchemy",
    "pydantic", "flask", "django", "asyncio", "peewee",
}

EXTERNAL_PATTERNS = [
    (r'OpenAI\(', "openai:chat.completions"),
    (r'Fernet\(', "cryptography:fernet"),
    (r'requests\.(get|post|put|delete|patch)\s*\(', None),
    (r'boto3\.client\s*\(\s*["\'](\w+)["\']', None),
    (r'httpx\.(get|post|put|delete)\s*\(', None),
]

# 框架推断：import 首段 → (框架名, 类别)
FRAMEWORK_SIGNATURES = {
    "fastapi": ("FastAPI", "API"),
    "flask": ("Flask", "API"),
    "django": ("Django", "Full-stack"),
    "flet": ("Flet", "前端"),
    "streamlit": ("Streamlit", "前端"),
    "gradio": ("Gradio", "前端"),
    "sqlalchemy": ("SQLAlchemy", "ORM"),
    "peewee": ("Peewee", "ORM"),
    "tortoise": ("Tortoise ORM", "ORM"),
    "pydantic": ("Pydantic", "数据校验"),
    "celery": ("Celery", "任务队列"),
    "openai": ("OpenAI SDK", "外部服务"),
    "langchain": ("LangChain", "AI"),
}

# 文件扩展名 → 语言名
EXT_TO_LANG = {
    ".py": "Python", ".pyi": "Python",
    ".ts": "TypeScript", ".tsx": "TypeScript",
    ".js": "JavaScript", ".jsx": "JavaScript",
    ".go": "Go", ".rs": "Rust",
    ".vue": "Vue", ".svelte": "Svelte",
    ".java": "Java", ".kt": "Kotlin",
    ".rb": "Ruby", ".php": "PHP",
    ".c": "C", ".cpp": "C++", ".h": "C/C++",
    ".swift": "Swift", ".m": "Objective-C",
}
# 语言 → 是否有通用扫描器
LANG_HAS_SCANNER = {
    "Python": True, "TypeScript": False, "JavaScript": False,
    "Go": False, "Rust": False, "Vue": False, "Svelte": False,
    "Java": False, "Kotlin": False, "Ruby": False, "PHP": False,
    "C": False, "C++": False, "Swift": False, "Objective-C": False,
}


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
                "stability": "stable",
                "children": children,
            }
    return structure


def _prep(content: str) -> str:
    content = re.sub(r'\\\s*\n\s*', ' ', content)
    content = re.sub(r'\(\s*\n\s*', '(', content)
    content = re.sub(r'\n\s*\)', ')', content)
    return content


def build_python_relations(src_dir: str) -> list:
    """Python import（符号级）"""
    from_import_re = re.compile(r'^from\s+(\S+)\s+import\s+(.+?)$', re.MULTILINE)
    import_re = re.compile(r'^import\s+(.+?)$', re.MULTILINE)
    src = Path(src_dir)
    relations = []
    seen = set()
    for f_py in sorted(src.glob("**/*.py")):
        if f_py.name.startswith("_") or f_py.name.startswith("test"):
            continue
        content = _prep(f_py.read_text(encoding="utf-8"))
        rel = str(f_py.relative_to(src.parent)).replace("\\", "/")
        for m in from_import_re.finditer(content):
            module = m.group(1)
            root = module.split(".")[0]
            if root in STDLIB_ROOTS:
                continue
            for sym in m.group(2).split(","):
                sym = sym.strip()
                if not sym or sym == "*":
                    continue
                key = (rel, f"{module}.{sym}", "depends_on")
                if key not in seen:
                    seen.add(key)
                    relations.append({"from": rel, "to": f"{module}.{sym}", "type": "depends_on"})
        for m in import_re.finditer(content):
            for module in m.group(1).split(","):
                module = module.strip()
                if not module:
                    continue
                root = module.split(".")[0]
                if root in STDLIB_ROOTS:
                    continue
                key = (rel, module, "depends_on")
                if key not in seen:
                    seen.add(key)
                    relations.append({"from": rel, "to": module, "type": "depends_on"})
    return relations


def build_js_relations(src_dir: str) -> list:
    """ES import / require（模块级，不深入符号）"""
    es_re = re.compile(r'(?:import\s+.+?\s+from\s+["\']([^"\']+)["\']|require\s*\(\s*["\']([^"\']+)["\']\s*\))')
    src = Path(src_dir)
    relations = []
    seen = set()
    for ext in ("*.ts", "*.tsx", "*.js", "*.jsx", "*.mjs", "*.cjs"):
        for f in sorted(src.glob(f"**/{ext}")):
            if f.name.startswith("_") or f.name.startswith("test") or "node_modules" in str(f):
                continue
            content = f.read_text(encoding="utf-8", errors="ignore")
            rel = str(f.relative_to(src.parent)).replace("\\", "/")
            for m in es_re.finditer(content):
                target = m.group(1) or m.group(2)
                if not target or target.startswith(".") or target.startswith("/"):
                    continue  # 相对路径跳过（需解析路径，暂不做）
                # 只记录外部包引用（非相对路径）
                key = (rel, target, "depends_on")
                if key not in seen:
                    seen.add(key)
                    relations.append({"from": rel, "to": target, "type": "depends_on"})
    return relations


def build_db_relations(src_dir: str) -> list:
    """ORM model → DB table"""
    model_re = re.compile(r'^class\s+(\w+)\s*\(\s*(?:\w+\.)?(?:Model|BaseModel)\s*\)\s*:', re.MULTILINE)
    table_re = re.compile(r"(?:table_name|__tablename__)\s*=\s*['\"](\w+)['\"]")
    fk_re = re.compile(r'(?:ForeignKeyField|ForeignKey)\s*\(\s*[\'"]?(\w+)\.(\w+)[\'"]?')
    src = Path(src_dir)
    relations = []
    seen = set()
    for f_py in sorted(src.glob("**/*.py")):
        if f_py.name.startswith("_") or f_py.name.startswith("test"):
            continue
        content = f_py.read_text(encoding="utf-8")
        rel = str(f_py.relative_to(src.parent)).replace("\\", "/")
        for m in model_re.finditer(content):
            model_name = m.group(1)
            if model_name in ("Model", "BaseModel"):
                continue
            tail = content[m.end():m.end() + 2000]
            table_match = table_re.search(tail)
            table_name = table_match.group(1) if table_match else model_name.lower() + "s"
            key = (f"{rel}:{model_name}", table_name, "maps_to")
            if key not in seen:
                seen.add(key)
                relations.append({"from": f"{rel}:{model_name}", "to": table_name, "type": "maps_to"})
            for fk in fk_re.finditer(tail):
                ref_model = fk.group(1)
                key = (f"{rel}:{model_name}", f"{rel}:{ref_model}", "maps_to")
                if key not in seen:
                    seen.add(key)
                    relations.append({"from": f"{rel}:{model_name}", "to": f"{rel}:{ref_model}", "type": "maps_to"})
    return relations


def build_api_relations(src_dir: str) -> list:
    """API 端点 / 页面挂载"""
    fastapi_re = re.compile(r'@\w+\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']')
    flet_re = re.compile(r'(?:page|self)\.(?:add|controls\.append)\s*\(\s*(\w+)')
    view_re = re.compile(r'(?:page\.go|view\.push)\s*\(\s*["\']([^"\']+)["\']')
    src = Path(src_dir)
    relations = []
    seen = set()
    for f_py in sorted(src.glob("**/*.py")):
        if f_py.name.startswith("_") or f_py.name.startswith("test"):
            continue
        content = f_py.read_text(encoding="utf-8")
        rel = str(f_py.relative_to(src.parent)).replace("\\", "/")
        for m in fastapi_re.finditer(content):
            method, path = m.group(1).upper(), m.group(2)
            key = (rel, f"{method} {path}", "exposes")
            if key not in seen:
                seen.add(key)
                relations.append({"from": rel, "to": f"{method} {path}", "type": "exposes"})
        for m in flet_re.finditer(content):
            widget = m.group(1)
            key = (rel, f"widget:{widget}", "mounts")
            if key not in seen:
                seen.add(key)
                relations.append({"from": rel, "to": f"widget:{widget}", "type": "mounts"})
        for m in view_re.finditer(content):
            route = m.group(1)
            key = (rel, route, "routes")
            if key not in seen:
                seen.add(key)
                relations.append({"from": rel, "to": route, "type": "routes"})
    return relations


def build_frontend_relations(src_dir: str) -> list:
    """前端导航"""
    nav_re = re.compile(r'NavigationBarDestination\s*\([^)]*?label\s*=\s*["\']([^"\']+)["\']', re.DOTALL)
    route_re = re.compile(r'if\s+.*?(?:index|e\.control\.selected_index)\s*==\s*(\d+)\s*:')
    src = Path(src_dir)
    relations = []
    seen = set()
    nav_labels = []
    for f_py in sorted(src.glob("**/*.py")):
        if f_py.name.startswith("_") or f_py.name.startswith("test"):
            continue
        content = f_py.read_text(encoding="utf-8")
        rel = str(f_py.relative_to(src.parent)).replace("\\", "/")
        for m in nav_re.finditer(content):
            nav_labels.append((rel, m.group(1)))
        for m in route_re.finditer(content):
            idx = int(m.group(1))
            if idx < len(nav_labels):
                nav_rel, label = nav_labels[idx]
                key = (nav_rel, label, "routes")
                if key not in seen:
                    seen.add(key)
                    relations.append({"from": nav_rel, "to": label, "type": "routes"})
    return relations


def build_external_relations(src_dir: str) -> list:
    """外部服务调用"""
    func_re = re.compile(r'^def\s+(\w+)\s*\(', re.MULTILINE)
    src = Path(src_dir)
    relations = []
    seen = set()
    for f_py in sorted(src.glob("**/*.py")):
        if f_py.name.startswith("_") or f_py.name.startswith("test"):
            continue
        content = f_py.read_text(encoding="utf-8")
        rel = str(f_py.relative_to(src.parent)).replace("\\", "/")
        for func_m in func_re.finditer(content):
            func_name = func_m.group(1)
            tail = content[func_m.end():func_m.end() + 3000]
            for pat, static_to in EXTERNAL_PATTERNS:
                for call_m in re.finditer(pat, tail):
                    to_val = static_to or call_m.group(0).split("(")[0].strip()
                    key = (f"{rel}:{func_name}", to_val, "calls")
                    if key not in seen:
                        seen.add(key)
                        relations.append({"from": f"{rel}:{func_name}", "to": to_val, "type": "calls"})
    return relations


# ── 语言检测 & 框架推断 ──

def detect_languages(root_dir: str) -> dict[str, int]:
    """扫描项目根目录下所有源文件，统计各语言文件数"""
    root = Path(root_dir)
    lang_counts = Counter()
    for f in root.rglob("*"):
        if f.is_dir():
            continue
        if any(p.startswith(".") for p in f.parts):
            continue
        if any(p in ("node_modules", "dist", "build", "__pycache__", ".git") for p in f.parts):
            continue
        lang = EXT_TO_LANG.get(f.suffix.lower())
        if lang:
            lang_counts[lang] += 1
    return dict(lang_counts)


def infer_frameworks(all_relations: list) -> dict[str, set]:
    """从 depends_on 关系中推断使用的框架"""
    frameworks = {}
    seen_packages = set()
    for r in all_relations:
        if r["type"] == "depends_on":
            root = r["to"].split(".")[0]
            if root in seen_packages:
                continue
            seen_packages.add(root)
            if root in FRAMEWORK_SIGNATURES:
                name, cat = FRAMEWORK_SIGNATURES[root]
                frameworks.setdefault(cat, set()).add(name)
    return frameworks


# ── 主入口 ──

def main():
    src_dir = sys.argv[1] if len(sys.argv) > 1 else "src"
    graph_path = sys.argv[2] if len(sys.argv) > 2 else "docs/project-graph.yaml"
    root_dir = str(Path(src_dir).parent)

    graph_file = Path(graph_path)
    if graph_file.exists():
        existing = yaml.safe_load(graph_file.read_text(encoding="utf-8")) or {}
    else:
        existing = {}

    new_structure = build_structure(src_dir)
    old_structure = existing.get("structure") or {}
    for k, v in new_structure.items():
        if k not in old_structure:
            old_structure[k] = v
        else:
            old_structure[k].update({kk: vv for kk, vv in v.items() if kk not in old_structure[k]})

    all_relations = []
    all_relations.extend(build_python_relations(src_dir))
    all_relations.extend(build_js_relations(src_dir))
    all_relations.extend(build_db_relations(src_dir))
    all_relations.extend(build_api_relations(src_dir))
    all_relations.extend(build_frontend_relations(src_dir))
    all_relations.extend(build_external_relations(src_dir))

    existing["relations"] = all_relations
    existing["structure"] = old_structure
    existing.setdefault("evolution", [])

    graph_file.write_text(
        yaml.dump(existing, allow_unicode=True, sort_keys=False, default_flow_style=False),
        encoding="utf-8")

    # ── 类型统计 ──
    type_counts = Counter(r["type"] for r in all_relations)
    print(f"[OK] project-graph synced: {len(old_structure)} structure / {len(all_relations)} relations / {len(existing['evolution'])} evolution")

    has_output = any(type_counts.get(t, 0) > 0 for t in ("maps_to", "exposes", "mounts", "routes", "calls"))
    if has_output:
        print()
        print("  ═══════════════════════════════════════")
        print("   类型统计")
        print("  ─────────────────────────────────────")
        for t, c in sorted(type_counts.items()):
            print(f"    {t:<14} {c:>4} 条")
        print("  ═══════════════════════════════════════")

    # ── 框架推断 ──
    frameworks = infer_frameworks(all_relations)
    langs = detect_languages(root_dir)
    relevant_langs = {k: v for k, v in langs.items() if v > 0}
    py_frameworks = frameworks

    if py_frameworks or len(relevant_langs) > 1:
        print()
        print("  ═══════════════════════════════════════")
        print("   框架推断")
        print("  ─────────────────────────────────────")
        if "Python" in relevant_langs:
            print(f"    Python ({langs['Python']} 文件)")
            for cat, names in sorted(py_frameworks.items()):
                print(f"      {cat}: {', '.join(sorted(names))}")
        for lang, count in sorted(relevant_langs.items()):
            if lang == "Python":
                continue
            print(f"    {lang} ({count} 文件)")
        print("  ═══════════════════════════════════════")

    # ── 盲区检测 ──
    blind_langs = {lang: count for lang, count in relevant_langs.items()
                   if not LANG_HAS_SCANNER.get(lang, False)}
    if blind_langs:
        print()
        print("  ═══════════════════════════════════════")
        print("   盲区检测")
        print("  ─────────────────────────────────────")
        for lang, count in sorted(blind_langs.items()):
            print(f"    {lang} ({count} 文件)  — 暂无扫描器 → 需手动维护 relations")
        print("  ═══════════════════════════════════════")
        print()
        print("  💡 建议:")
        print("     1. 手动在 project-graph.yaml 中补充未扫描语言的 relations")
        print("     2. 运行 agentprecept audit 检查文档完整性")
        if any(t not in type_counts or type_counts[t] == 0 for t in ("maps_to", "routes", "calls")):
            print("     3. 检查是否有 ORM/API/前端 关系未被 scan 覆盖")


if __name__ == "__main__":
    main()
