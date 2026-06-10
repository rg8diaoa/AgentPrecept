# agentprecept 初始化脚本 (Windows PowerShell)
# 用法:
#   首次安装: .\init.ps1 C:\path\to\your-project
#   版本升级: .\init.ps1 C:\path\to\your-project -Update
#   默认目标: .\init.ps1 (当前目录)

param([string]$Project = ".", [switch]$Update)

Write-Host "agentprecept 初始化 → $Project"
if ($Update) { Write-Host "模式: 升级 — 框架文件将被覆盖，用户数据跳过" }

# --- AGENTS.md（框架文件，-Update 时覆盖）---
if (Test-Path "$Project\AGENTS.md") {
    if ($Update) {
        Copy-Item "AGENTS.md" "$Project/"
        Write-Host "[UPDATED] AGENTS.md — 已更新到最新版本"
    } else {
        Write-Host "[SKIP] AGENTS.md — 已存在（用 -Update 覆盖）"
    }
} else {
    Copy-Item "AGENTS.md" "$Project/"
    Write-Host "[OK] AGENTS.md — 已创建"
}

New-Item -ItemType Directory -Force -Path "$Project\docs" | Out-Null

# --- 用户数据（docs/ 下全部，永不覆盖）---
$files = @{
    "INDEX.md" = "templates\INDEX.md"
    "L1_A02_naming-convention_命名规范.md" = "templates\L1_A02_naming-convention_命名规范.md"
    "L1_B01_glossary_术语表.md" = "templates\L1_B01_glossary_术语表.md"
    "HANDOFF.md" = "templates\HANDOFF.md"
    "MEMORY.md" = "templates\MEMORY.md"
    "project-graph.yaml" = "templates\project-graph.yaml"
    "L4_O01_design-rationale_设计依据.md" = "templates\L4_O01_design-rationale_设计依据.md"
}

foreach ($name in $files.Keys) {
    $dest = "$Project\docs\$name"
    if (Test-Path $dest) {
        Write-Host "[SKIP] $name — 已存在（用户数据，不覆盖）"
    } else {
        Copy-Item $files[$name] $dest
        Write-Host "[OK] $name — 已创建"
    }
}

Write-Host ""
Write-Host "一等公民文档（5/5）:"
Write-Host "   $Project\docs\INDEX.md              — 文档目录"
Write-Host "   $Project\docs\L1_A02_*.md           — 命名规范"
Write-Host "   $Project\docs\L1_B01_*.md           — 术语表"
Write-Host "   $Project\docs\HANDOFF.md            — 会话交接"
Write-Host "   $Project\docs\MEMORY.md             — 持久记忆（自动生长）"
Write-Host ""
Write-Host "核心支撑:"
Write-Host "   $Project\AGENTS.md                  — Agent 入口"
Write-Host "   $Project\docs\project-graph.yaml    — 项目图"
Write-Host "   $Project\docs\L4_O01_*.md           — 设计依据"
Write-Host ""
Write-Host ""
Write-Host "可选: 初始化 git 仓库？(y/n)"
$gitAnswer = Read-Host
if ($gitAnswer -eq 'y') {
    git init $Project 2>$null
    Write-Host "   git init done"
}
Write-Host ""
Write-Host "下一步: 1) 运行 agentprecept setup 获取 MCP 配置"
Write-Host "      2) 将 MCP 配置加入 Claude Code(.mcp.json) 或 CodeWhale(~/.deepseek/mcp.json)"
Write-Host "      3) 重启 Agent, MCP tools 自动可用"
Write-Host "      4) 或: 复制 examples\first-run.md 中的 prompt 发给 Agent 自动初始化 project-graph"
