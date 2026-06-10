#!/bin/bash
# agentprecept 初始化脚本
# 用法:
#   首次安装: bash init.sh /path/to/your-project
#   版本升级: bash init.sh --update /path/to/your-project
#   默认目标: bash init.sh

UPDATE=false
if [ "$1" = "--update" ]; then
    UPDATE=true
    shift
fi
PROJECT="${1:-.}"

echo "agentprecept 初始化 → $PROJECT"
if [ "$UPDATE" = true ]; then echo "模式: 升级 — 框架文件将被覆盖，用户数据跳过"; fi

# --- AGENTS.md（框架文件，--update 时覆盖）---
if [ -f "$PROJECT/AGENTS.md" ]; then
    if [ "$UPDATE" = true ]; then
        cp AGENTS.md "$PROJECT/"
        echo "[UPDATED] AGENTS.md — 已更新到最新版本"
    else
        echo "[SKIP] AGENTS.md — 已存在（用 --update 覆盖）"
    fi
else
    cp AGENTS.md "$PROJECT/"
    echo "[OK] AGENTS.md — 已创建"
fi

mkdir -p "$PROJECT/docs"

# --- 用户数据（docs/ 下全部，永不覆盖）---
copy_if_missing() {
    local name="$1"
    local src="$2"
    local dest="$PROJECT/docs/$name"
    if [ -f "$dest" ]; then
        echo "[SKIP] $name — 已存在（用户数据，不覆盖）"
    else
        cp "$src" "$dest"
        echo "[OK] $name — 已创建"
    fi
}

copy_if_missing "INDEX.md" "templates/INDEX.md"
copy_if_missing "L1_A02_naming-convention_命名规范.md" "templates/L1_A02_naming-convention_命名规范.md"
copy_if_missing "L1_B01_glossary_术语表.md" "templates/L1_B01_glossary_术语表.md"
copy_if_missing "HANDOFF.md" "templates/HANDOFF.md"
copy_if_missing "MEMORY.md" "templates/MEMORY.md"
copy_if_missing "project-graph.yaml" "templates/project-graph.yaml"
copy_if_missing "L4_O01_design-rationale_设计依据.md" "templates/L4_O01_design-rationale_设计依据.md"

echo ""
echo "一等公民文档（5/5）:"
echo "   $PROJECT/docs/INDEX.md              — 文档目录"
echo "   $PROJECT/docs/L1_A02_*.md           — 命名规范"
echo "   $PROJECT/docs/L1_B01_*.md           — 术语表"
echo "   $PROJECT/docs/HANDOFF.md            — 会话交接"
echo "   $PROJECT/docs/MEMORY.md             — 持久记忆（自动生长）"
echo ""
echo "核心支撑:"
echo "   $PROJECT/AGENTS.md                  — Agent 入口"
echo "   $PROJECT/docs/project-graph.yaml    — 项目图"
echo "   $PROJECT/docs/L4_O01_*.md           — 设计依据"
echo ""
echo ""
echo -n "可选: 初始化 git 仓库？(y/n) "
read -r git_answer
if [ "$git_answer" = "y" ]; then
    git init "$PROJECT" 2>/dev/null
    echo "   git init done"
fi
echo ""
echo "下一步: 1) 运行 agentprecept setup 获取 MCP 配置"
echo "      2) 将 MCP 配置加入 Claude Code(.mcp.json) 或 CodeWhale(~/.deepseek/mcp.json)"
echo "      3) 重启 Agent, MCP tools 自动可用"
echo "      4) 或: 复制 examples/first-run.md 中的 prompt 发给 Agent 自动初始化 project-graph"
