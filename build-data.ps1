# build-data.ps1 — 构建前复制数据文件到 agentprecept/（wheel 打包用）
param()
$ErrorActionPreference = "Stop"
$src = $PSScriptRoot
$dst = Join-Path $src "agentprecept"

Write-Host "[build-data] copying to $dst ..."

foreach ($f in "AGENTS.md","SKILL.md","README.md","pyproject.toml") {
    Copy-Item (Join-Path $src $f) $dst -Force
}

foreach ($d in "templates","methodology","skills","scripts","examples","reference") {
    $from = Join-Path $src $d
    $to   = Join-Path $dst $d
    if (Test-Path $to) { Remove-Item -Recurse -Force $to }
    New-Item -ItemType Directory -Path $to -Force | Out-Null
    Copy-Item "$from\*" $to -Recurse -Force
}

Write-Host "[build-data] done."
