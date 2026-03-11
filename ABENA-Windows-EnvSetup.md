# ABENA Windows Environment Setup

This guide helps you set up the ABENA blockchain development environment on Windows, including Rust, targets, and environment variables.

---

## Step 6: Setting Environment Variables

Environment variables like `RUST_LOG` and `RUST_BACKTRACE` are useful for debugging. You have three options:

### Option A: Set per terminal session

In PowerShell, before each build/run:

```powershell
$env:RUST_LOG = "info"
$env:RUST_BACKTRACE = "1"
cargo run -p abena-node -- --dev --tmp
```

**Pros:** No global changes  
**Cons:** Must run every time you open a new terminal

---

### Option B: Set in VS Code/Cursor task or launch config

Already done in `.vscode/tasks.json` and `.vscode/launch.json`. The Run tasks use `$env:RUST_LOG='info'` automatically.

**Pros:** Works when using Tasks (Ctrl+Shift+P → Run Task)  
**Cons:** Only applies when running through VS Code tasks, not a raw terminal

---

### Option C: Add to PowerShell profile (recommended)

Load variables automatically every time you open a terminal. No Admin rights required.

1. **Open your PowerShell profile** (create if it doesn't exist):
   ```powershell
   if (!(Test-Path $PROFILE)) { New-Item -Path $PROFILE -ItemType File -Force }
   notepad $PROFILE
   ```

2. **Add these lines** at the end:
   ```powershell
   # ABENA blockchain development
   $env:RUST_LOG = "info"
   $env:RUST_BACKTRACE = "1"
   Write-Host "ABENA dev env loaded (RUST_LOG=$env:RUST_LOG)" -ForegroundColor Green
   ```

3. **Save and close.** If you get an execution policy error, run:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

4. **Open a new terminal.** You should see: `ABENA dev env loaded (RUST_LOG=info)`

**Pros:**  
- Loads automatically every terminal  
- Confirmation message so you know it's active  
- No Admin rights  
- Easy to change (`notepad $PROFILE`)

**Cons:** Affects all PowerShell sessions (usually fine)

---

## Verify Your Full Rust Setup

Run this checklist before building. Copy and paste into PowerShell (from your project root):

```powershell
cd "C:\Users\Jan Marie\Abena Blockchain"

Write-Host "`n=== ABENA Rust Setup Check ===" -ForegroundColor Cyan

# 1. Rust version
$rust = rustc --version 2>$null
if ($rust) { Write-Host "[OK] Rust: $rust" -ForegroundColor Green } else { Write-Host "[FAIL] Rust not found" -ForegroundColor Red; exit 1 }

# 2. Cargo
$cargo = cargo --version 2>$null
if ($cargo) { Write-Host "[OK] Cargo: $cargo" -ForegroundColor Green } else { Write-Host "[FAIL] Cargo not found" -ForegroundColor Red }

# 3. wasm32 target (required for Substrate)
$targets = rustup target list --installed 2>$null
if ($targets -match "wasm32-unknown-unknown") {
  Write-Host "[OK] wasm32-unknown-unknown installed" -ForegroundColor Green
} else {
  Write-Host "[MISSING] wasm32-unknown-unknown - installing..." -ForegroundColor Yellow
  rustup target add wasm32-unknown-unknown
  if ($LASTEXITCODE -eq 0) { Write-Host "[OK] wasm32-unknown-unknown installed" -ForegroundColor Green }
}

# 4. Rust nightly (if required by rust-toolchain.toml)
if (Test-Path "rust-toolchain.toml") {
  $toolchain = (Get-Content rust-toolchain.toml | Select-String "channel").ToString() -replace '.*"([^"]+)".*','$1'
  Write-Host "[INFO] rust-toolchain.toml requests: $toolchain" -ForegroundColor Cyan
}

# 5. Project path (space handling)
$pwd = (Get-Location).Path
if ($pwd -match " ") {
  Write-Host "[INFO] Path has spaces - use quotes: cd `"$pwd`"" -ForegroundColor Cyan
}

Write-Host "`n=== Check complete ===" -ForegroundColor Cyan
```

**Expected output:** All `[OK]` lines in green. If `wasm32-unknown-unknown` is missing, the script will add it.

---

## Quick Start After Setup

1. Open a terminal in the project root  
2. Run the **Verify Your Full Rust Setup** checklist above  
3. Build: `cargo build -p abena-node --release`  
4. Run dev node: `cargo run -p abena-node -- --dev --tmp`  
   Or use VS Code: **Ctrl+Shift+P** → **Tasks: Run Task** → **Run ABENA Node (Dev)**
