# Installing Rust on Windows

## Option 1: Using rustup-init.exe (Recommended for Windows)

### Step 1: Download rustup-init

1. Go to https://rustup.rs/
2. Download `rustup-init.exe` (or click the Windows installer link)
3. Run the installer

### Step 2: Run the Installer

1. Double-click `rustup-init.exe`
2. Follow the prompts (default options are usually fine)
3. When prompted, press `1` to proceed with default installation
4. Wait for installation to complete

### Step 3: Restart Your Terminal

**Important**: Close and reopen your terminal (Git Bash, PowerShell, or Command Prompt) after installation.

### Step 4: Verify Installation

```bash
rustc --version
rustup --version
cargo --version
```

You should see version numbers for all three commands.

### Step 5: Add WebAssembly Target

```bash
rustup target add wasm32-unknown-unknown
```

## Option 2: Using Git Bash or WSL

If you're using Git Bash or WSL (Windows Subsystem for Linux), you can use the Linux installation method:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

Then restart your terminal and run:
```bash
source $HOME/.cargo/env
rustup target add wasm32-unknown-unknown
```

## Option 3: Manual PATH Setup (If Rust is installed but not found)

If Rust is installed but `rustup` command is not found:

1. Find where Rust was installed (usually `C:\Users\YourUsername\.cargo\bin`)
2. Add it to your PATH:
   - Open System Properties → Environment Variables
   - Edit the "Path" variable
   - Add: `C:\Users\YourUsername\.cargo\bin`
   - Click OK on all dialogs
3. Restart your terminal

## Troubleshooting

### If you're using Git Bash:

Git Bash might not pick up Windows PATH variables. Try:

```bash
# Check if cargo exists
which cargo

# If not found, add to PATH in Git Bash
export PATH="$HOME/.cargo/bin:$PATH"

# Or add to your ~/.bashrc for permanent fix
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Verify Installation

After installation, verify everything works:

```bash
# Check Rust version
rustc --version

# Check Cargo version  
cargo --version

# Check rustup version
rustup --version

# Add WebAssembly target
rustup target add wasm32-unknown-unknown

# Verify target was added
rustup target list --installed
```

You should see `wasm32-unknown-unknown` in the list.

## Next Steps

Once Rust is installed:

```bash
cd "C:\Users\Jan Marie\Abena Blockchain"
cargo build --release
```

