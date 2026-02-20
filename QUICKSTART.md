# ABENA Blockchain Quick Start

## Minimal Setup (Just the Essentials)

### 1. Install Rust & WebAssembly Target

**For Windows (Recommended):**
1. Download `rustup-init.exe` from https://rustup.rs/
2. Run the installer and follow the prompts
3. **Restart your terminal** after installation
4. Verify installation:
   ```bash
   rustc --version
   rustup --version
   ```
5. Add WebAssembly target:
   ```bash
   rustup target add wasm32-unknown-unknown
   ```

**For Git Bash/WSL (Alternative):**
```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Restart terminal, then:
source $HOME/.cargo/env

# Add WebAssembly target
rustup target add wasm32-unknown-unknown
```

**⚠️ If you get "rustup: command not found"**, see `INSTALL_RUST_WINDOWS.md` for detailed Windows installation instructions.

### 2. Build the Project

```bash
cd "C:\Users\Jan Marie\Abena Blockchain"
cargo build --release
```

**⚠️ First build takes 30-60 minutes** - grab a coffee! ☕

### 3. Run the Node

```bash
# Development mode (single node, fresh state each time)
./target/release/abena-node --dev
```

### 4. Connect Polkadot.js Apps

1. Open https://polkadot.js.org/apps/
2. Click the network selector (top left)
3. Select "Local Node" or add `ws://127.0.0.1:9944`
4. Start interacting with your ABENA blockchain!

## What You Have

✅ **Patient Health Records Pallet** - Quantum-resistant encrypted health data  
✅ **ABENA Coin Pallet** - Native token for gamification  
✅ **Quantum Computing Pallet** - Integration points for quantum computing results  

## Common Commands

```bash
# Run tests
cargo test

# Run specific pallet tests
cargo test -p pallet-patient-health-records

# Clean build (if having issues)
cargo clean && cargo build --release

# Check node help
./target/release/abena-node --help
```

## Need Help?

See `SETUP.md` for detailed setup instructions and troubleshooting.

