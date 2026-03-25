# Full sequence: populate patches/sc-network, fix paths, enum fix, cargo update, build.
# Run from workspace root:  powershell -ExecutionPolicy Bypass -File .\scripts\setup-and-build.ps1
# Requires: git, Python 3 (optional but recommended), Rust toolchain, network for clone.

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$patchDir = Join-Path $Root "patches\sc-network"
$tmpSdk = Join-Path $Root ".temp-polkadot-sdk"

if (Test-Path "/root/patches/sc-network") {
    Write-Host "Copying from /root/patches/sc-network..."
    New-Item -ItemType Directory -Force -Path (Join-Path $Root "patches") | Out-Null
    if (Test-Path $patchDir) { Remove-Item -Recurse -Force $patchDir }
    Copy-Item -Recurse "/root/patches/sc-network" $patchDir
} else {
    Write-Host "Cloning polkadot-sdk (polkadot-stable2409)..."
    if (Test-Path $tmpSdk) { Remove-Item -Recurse -Force $tmpSdk }
    git clone --depth 1 --branch "polkadot-stable2409" `
        "https://github.com/paritytech/polkadot-sdk.git" $tmpSdk
    New-Item -ItemType Directory -Force -Path (Join-Path $Root "patches") | Out-Null
    if (Test-Path $patchDir) { Remove-Item -Recurse -Force $patchDir }
    $src = Join-Path $tmpSdk "substrate\client\network"
    Copy-Item -Recurse $src $patchDir
    Remove-Item -Recurse -Force $tmpSdk
}

$fixPaths = Join-Path $Root "scripts\fix-patch-paths.sh"
if (Test-Path $fixPaths) {
    $bash = @(
        "${env:ProgramFiles}\Git\bin\bash.exe",
        "${env:ProgramFiles(x86)}\Git\bin\bash.exe",
        "bash"
    ) | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
    if ($bash) {
        & $bash -lc "cd '$($Root -replace '\\','/')' && ./scripts/fix-patch-paths.sh"
    } else {
        Write-Warning "Git Bash not found; run scripts/fix-patch-paths.sh manually (WSL or Linux server)."
    }
}

$py = Get-Command python3 -ErrorAction SilentlyContinue
if (-not $py) { $py = Get-Command python -ErrorAction SilentlyContinue }
if ($py) {
    & $py.Path (Join-Path $Root "scripts\apply-sc-network-enum-fix.py")
} else {
    Write-Warning "Python not found; run scripts/apply-sc-network-enum-fix.py after setup."
}

Write-Host "cargo update -p sc-network-types"
cargo update -p sc-network-types

Write-Host "cargo build --release -p abena-node"
cargo build --release -p abena-node
