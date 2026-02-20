# ABENA Blockchain Setup Guide

## Prerequisites

### 1. Install Rust

If you haven't installed Rust yet, run:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

After installation, restart your terminal or run:
```bash
source $HOME/.cargo/env
```

### 2. Add WebAssembly Target

Substrate requires the WebAssembly compilation target:

```bash
rustup target add wasm32-unknown-unknown
```

### 3. Install Required Tools

Install additional Rust tools needed for Substrate development:

```bash
# Install Rust nightly (some Substrate features require it)
rustup toolchain install nightly

# Install required components
rustup component add rust-src --toolchain nightly
rustup target add wasm32-unknown-unknown --toolchain nightly

# Install cargo-contract for smart contracts (optional, for future use)
# cargo install --force --locked cargo-contract
```

### 4. Install Additional Dependencies

#### For Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install -y git clang curl libssl-dev llvm libudev-dev
```

#### For macOS:
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install openssl
```

#### For Windows:
Install the following:
- [Git for Windows](https://git-scm.com/download/win)
- [LLVM](https://github.com/llvm/llvm-project/releases)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022)

## Building the ABENA Blockchain

### First Build

Navigate to the project directory and build the project:

```bash
cd "C:\Users\Jan Marie\Abena Blockchain"
cargo build --release
```

**Note**: The first build will take a long time (30-60 minutes) as it compiles all Substrate dependencies. Subsequent builds will be much faster.

### Development Build (Faster, with Debug Info)

For development, use a debug build which is faster to compile:

```bash
cargo build
```

## Running the Node

### Development Mode (Single Node)

Run a development node with a fresh chain state:

```bash
# Using release build (recommended for performance)
./target/release/abena-node --dev

# Or using debug build (faster compilation, slower runtime)
./target/debug/abena-node --dev
```

### Local Testnet (Multiple Nodes)

To run a local testnet with multiple nodes:

**Terminal 1:**
```bash
./target/release/abena-node --chain local --alice --port 30333 --ws-port 9944
```

**Terminal 2:**
```bash
./target/release/abena-node --chain local --bob --port 30334 --ws-port 9945 --bootnodes /ip4/127.0.0.1/tcp/30333/p2p/12D3KooWEyoppNCUx8Yx66oV9fJnriXwCcXwDDUA2kj6vnc6iDEp
```

## Testing

Run tests for all pallets:

```bash
# Run all tests
cargo test

# Run tests for a specific pallet
cargo test -p pallet-patient-health-records
cargo test -p pallet-abena-coin
cargo test -p pallet-quantum-computing

# Run tests with output
cargo test -- --nocapture
```

## Benchmarking

To benchmark the runtime pallets:

```bash
cargo build --release --features runtime-benchmarks
./target/release/abena-node benchmark --chain dev --pallet "*" --extrinsic "*" --steps 20 --repeat 10
```

## Troubleshooting

### Build Errors

If you encounter build errors:

1. **Update Rust:**
   ```bash
   rustup update
   ```

2. **Clean and rebuild:**
   ```bash
   cargo clean
   cargo build --release
   ```

3. **Check Rust version:**
   ```bash
   rustc --version
   ```
   Should be rustc 1.70.0 or newer.

### Missing Dependencies

If you get linker errors, ensure all system dependencies are installed (see step 4 above).

### Windows-Specific Issues

On Windows, you may need to:
- Use PowerShell or Git Bash instead of Command Prompt
- Ensure LLVM is in your PATH
- Install Visual Studio Build Tools with C++ workload

## Next Steps

1. **Connect to Polkadot.js Apps**: 
   - Open https://polkadot.js.org/apps/
   - Go to Settings > Developer
   - Add your local node endpoint: `ws://127.0.0.1:9944`
   - Click "Save & Reload"

2. **Interact with Your Chain**:
   - Use Polkadot.js Apps to interact with your custom pallets
   - Submit extrinsics for health records, ABENA Coin, and quantum computing jobs

3. **Development**:
   - Modify pallet logic in `pallets/` directories
   - Add new features and test them
   - Run benchmarks to optimize weights

## Important Notes

- **DO NOT** install the substrate-node-template as we've already created a custom node structure
- The first build will download and compile all Substrate dependencies (this is normal and takes time)
- Always use `--release` flag for production builds
- Development builds (`cargo build`) are faster to compile but slower at runtime

