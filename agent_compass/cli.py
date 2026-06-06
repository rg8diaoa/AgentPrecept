"""agent-compass CLI — 项目初始化 / 同步 / 审计 / 诊断"""

import sys
import subprocess
from pathlib import Path

SCRIPTS = Path(__file__).parent.parent / "scripts"


def cmd_init(project: str = "."):
    """复制核心文件到目标项目"""
    project = Path(project)
    project.mkdir(parents=True, exist_ok=True)
    docs = project / "docs"
    docs.mkdir(exist_ok=True)

    root = Path(__file__).parent.parent
    (root / "AGENTS.md").replace(project / "AGENTS.md")
    (root / "templates" / "project-graph.yaml").replace(docs / "project-graph.yaml")
    (root / "templates" / "HANDOFF.md").replace(docs / "HANDOFF.md")
    (root / "templates" / "L4_O01_design-rationale_设计依据.md").replace(
        docs / "L4_O01_design-rationale_设计依据.md"
    )

    print(f"[OK] agent-compass 初始化完成 -> {project}")
    print(f"   已复制: AGENTS.md / project-graph.yaml / HANDOFF.md / L4_O01")
    print(f"   下一步: 复制 examples/first-run.md 中的 prompt 发给 Agent")


def cmd_sync(src: str = "src", graph: str = "docs/project-graph.yaml"):
    """从代码自动同步 project-graph"""
    subprocess.run([sys.executable, str(SCRIPTS / "sync-graph.py"), src, graph])


def cmd_audit(docs: str = "docs"):
    """快速审计（命名/断链/骨架）"""
    subprocess.run([sys.executable, str(SCRIPTS / "basic-audit.py"), docs])


def cmd_doctor():
    """诊断：检查项目缺少哪些 agent-compass 文件"""
    root = Path.cwd()
    checks = {
        "AGENTS.md": root / "AGENTS.md",
        "docs/project-graph.yaml": root / "docs" / "project-graph.yaml",
        "docs/HANDOFF.md": root / "docs" / "HANDOFF.md",
        "docs/L4_O01": root / "docs" / "L4_O01_design-rationale_设计依据.md",
    }

    ok = 0
    for name, path in checks.items():
        status = "OK" if path.exists() else "MISSING"
        if path.exists():
            ok += 1
        print(f"  {status}  {name}")
    print(f"\n{ok}/{len(checks)} 项通过")

    if ok < len(checks):
        print("运行 agent-compass init 修复缺失文件")


COMMANDS = {
    "init": cmd_init,
    "sync": cmd_sync,
    "audit": cmd_audit,
    "doctor": cmd_doctor,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print("agent-compass — Agent 开发完整循环方法论")
        print(f"用法: agent-compass {{{'|'.join(COMMANDS)}}}")
        return

    cmd = COMMANDS[sys.argv[1]]
    cmd(*sys.argv[2:])
