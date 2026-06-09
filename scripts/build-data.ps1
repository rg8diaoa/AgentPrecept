# build-data.ps1 — 构建前从根目录复制数据文件到 agentprecept/（wheel 打包用）
# 用法: powershell scripts/build-data.ps1
# 产物不进 git，构建后自然丢弃

$ErrorActionPreference = "Stop"
$src = $PSScriptRoot | Split-Path -Parent
$dst = Join-Path $src "agentprecept"

Write-Host "[build-data] copying data files to $dst ..."

Copy-Item (Join-Path $src "AGENTS.md") $dst/ -Force
Copy-Item (Join-Path $src "SKILL.md") $dst/ -Force
Copy-Item (Join-Path $src "README.md") $dst/ -Force
Copy-Item (Join-Path $src "pyproject.toml") $dst/ -Force

$dirs = @("templates", "methodology", "skills", "scripts", "examples", "reference")
foreach ($d in $dirs) {
    $from = Join-Path $src $d
    $to = Join-Path $dst $d
    if (Test-Path $to) { Remove-Item -Recurse $to -Force }
    Copy-Item -Recurse $from $to
}

Write-Host "[build-data] done."
