#!/bin/bash
# =============================================================================
# ABENA IHR — DigitalOcean Build + Deploy Script
# DK Technologies, Inc.
#
# Run this ON your DigitalOcean server (Ubuntu 22.04 LTS recommended)
# SSH in first: ssh root@YOUR_DO_IP
#
# This is the FASTEST path to a live testnet — skip Windows build entirely.
# Edit code on Windows (Cursor), push to GitHub, pull and build on DO server.
# =============================================================================
set -e   # Exit on any error

REPO_URL="https://github.com/janicemvk/abena-ihr-backup"
ABENA_DIR="/opt/abena/abena-ihr"
BINARY_DIR="/opt/abena/bin"
DATA_DIR="/var/lib/abena"
LOG_DIR="/var/log/abena"
SERVICE_USER="abena"

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║       ABENA IHR — DigitalOcean Build & Deploy        ║"
echo "║              DK Technologies, Inc.                   ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# =============================================================================
# PHASE 1: System Dependencies
# =============================================================================
echo "► Phase 1: Installing system dependencies..."

apt-get update -qq
apt-get install -y \
    build-essential \
    pkg-config \
    libssl-dev \
    clang \
    libclang-dev \
    cmake \
    protobuf-compiler \
    git \
    curl \
    wget \
    nginx \
    certbot \
    python3-certbot-nginx \
    jq \
    htop

# Verify OpenSSL (this is what was failing on Windows)
echo "  ✓ OpenSSL: $(pkg-config --modversion openssl)"
echo "  ✓ OpenSSL libs: $(pkg-config --libs openssl)"

# =============================================================================
# PHASE 2: Rust Toolchain
# =============================================================================
echo ""
echo "► Phase 2: Setting up Rust toolchain..."

if ! command -v rustup &>/dev/null; then
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
fi

source "$HOME/.cargo/env"

# Pin to exact version required by polkadot-sdk stable2409
rustup install 1.81.0
rustup default 1.81.0
rustup target add wasm32-unknown-unknown
rustup component add rust-src rustfmt clippy

echo "  ✓ Rust: $(rustc --version)"
echo "  ✓ Cargo: $(cargo --version)"
echo "  ✓ WASM target: installed"

# =============================================================================
# PHASE 3: Clone / Update Repo
# =============================================================================
echo ""
echo "► Phase 3: Getting ABENA IHR source code..."

mkdir -p /opt/abena
if [ -d "$ABENA_DIR" ]; then
    echo "  Repo exists — pulling latest..."
    cd "$ABENA_DIR"
    git pull origin main
else
    echo "  Cloning from GitHub..."
    git clone "$REPO_URL" "$ABENA_DIR"
    cd "$ABENA_DIR"
fi

echo "  ✓ Repo at: $ABENA_DIR"
echo "  ✓ Branch: $(git branch --show-current)"
echo "  ✓ Commit: $(git log --oneline -1)"

# =============================================================================
# PHASE 4: Fix Known Substrate Dependency Issues
# =============================================================================
echo ""
echo "► Phase 4: Fixing known Substrate dependency issues..."

# Fix 1: Enum index bug — ensure single parity-scale-codec version
echo "  Updating parity-scale-codec..."
cargo update -p parity-scale-codec 2>/dev/null || true

# Fix 2: Verify no duplicate codec versions
CODEC_DUPES=$(cargo tree -d -p parity-scale-codec 2>/dev/null | grep -c "parity-scale-codec" || echo "0")
if [ "$CODEC_DUPES" -gt "1" ]; then
    echo "  ⚠ Multiple parity-scale-codec versions detected — check workspace Cargo.toml"
else
    echo "  ✓ parity-scale-codec: no duplicates"
fi

# Fix 3: Ensure .cargo/config.toml has correct OpenSSL env vars
mkdir -p .cargo
cat > .cargo/config.toml << 'CARGO_CONFIG'
[build]

[target.wasm32-unknown-unknown]
rustflags = ["-C", "target-feature=+bulk-memory"]

[target.x86_64-unknown-linux-gnu]
rustflags = ["-C", "link-arg=-Wl,-z,stack-size=33554432"]

[net]
retry = 3
CARGO_CONFIG

echo "  ✓ .cargo/config.toml written"

# =============================================================================
# PHASE 5: Build
# =============================================================================
echo ""
echo "► Phase 5: Building abena-node..."
echo "  First build: 20-40 minutes. Grab a coffee."
echo "  Incremental builds: 2-5 minutes."
echo ""

# Capture build output + show live
RUST_LOG=warn \
PKG_CONFIG_PATH=/usr/lib/x86_64-linux-gnu/pkgconfig \
cargo build -p abena-node --release 2>&1 | tee /tmp/abena-build-$(date +%Y%m%d-%H%M%S).log

BUILD_EXIT=$?

if [ $BUILD_EXIT -ne 0 ]; then
    echo ""
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║                  BUILD FAILED                        ║"
    echo "╚══════════════════════════════════════════════════════╝"
    echo "Check the log above for the error."
    echo "Common fixes:"
    echo "  OpenSSL: sudo apt-get install -y libssl-dev pkg-config"
    echo "  WASM:    rustup target add wasm32-unknown-unknown"
    echo "  Rust ver: rustup default 1.81.0"
    exit 1
fi

echo ""
echo "  ✓ Build successful!"

# =============================================================================
# PHASE 6: Install Binary
# =============================================================================
echo ""
echo "► Phase 6: Installing binary..."

mkdir -p "$BINARY_DIR"
cp target/release/abena-node "$BINARY_DIR/abena-node"
chmod +x "$BINARY_DIR/abena-node"

echo "  ✓ Binary: $BINARY_DIR/abena-node"
echo "  ✓ Version: $($BINARY_DIR/abena-node --version)"

# =============================================================================
# PHASE 7: System User + Directories
# =============================================================================
echo ""
echo "► Phase 7: Setting up system user and directories..."

if ! id "$SERVICE_USER" &>/dev/null; then
    useradd --system --no-create-home --shell /bin/false "$SERVICE_USER"
    echo "  ✓ Created system user: $SERVICE_USER"
fi

mkdir -p "$DATA_DIR" "$LOG_DIR"
chown -R "$SERVICE_USER:$SERVICE_USER" "$DATA_DIR" "$LOG_DIR"
echo "  ✓ Data dir: $DATA_DIR"
echo "  ✓ Log dir:  $LOG_DIR"

# =============================================================================
# PHASE 8: Systemd Service
# =============================================================================
echo ""
echo "► Phase 8: Writing systemd service..."

cat > /etc/systemd/system/abena-node.service << SYSTEMD
[Unit]
Description=ABENA IHR Blockchain Node — DK Technologies, Inc.
Documentation=https://github.com/janicemvk/abena-ihr-backup
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${SERVICE_USER}
Group=${SERVICE_USER}
ExecStart=${BINARY_DIR}/abena-node \\
    --base-path ${DATA_DIR} \\
    --chain abena-testnet \\
    --validator \\
    --name "ABENA-Testnet-Node-1" \\
    --port 30333 \\
    --rpc-port 9933 \\
    --ws-port 9944 \\
    --rpc-cors all \\
    --rpc-methods Unsafe \\
    --log info
Restart=always
RestartSec=10
KillSignal=SIGINT
SyslogIdentifier=abena-node
StandardOutput=journal
StandardError=journal

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=${DATA_DIR} ${LOG_DIR}

[Install]
WantedBy=multi-user.target
SYSTEMD

systemctl daemon-reload
systemctl enable abena-node
echo "  ✓ Service file: /etc/systemd/system/abena-node.service"
echo "  ✓ Service enabled on boot"

# =============================================================================
# PHASE 9: Nginx Reverse Proxy (wss://testnet.abenihr.com)
# =============================================================================
echo ""
echo "► Phase 9: Configuring nginx reverse proxy..."

cat > /etc/nginx/sites-available/abena-testnet << 'NGINX'
# ABENA IHR Testnet — WebSocket reverse proxy
# Polkadot.js Apps connects to wss://testnet.abenihr.com
# nginx forwards WebSocket traffic to abena-node on port 9944

map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}

server {
    listen 80;
    server_name testnet.abenihr.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name testnet.abenihr.com;

    # SSL — certbot fills these in after: certbot --nginx -d testnet.abenihr.com
    # ssl_certificate     /etc/letsencrypt/live/testnet.abenihr.com/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/testnet.abenihr.com/privkey.pem;

    # WebSocket upgrade for Polkadot.js Apps
    location / {
        proxy_pass         http://127.0.0.1:9944;
        proxy_http_version 1.1;
        proxy_set_header   Upgrade    $http_upgrade;
        proxy_set_header   Connection $connection_upgrade;
        proxy_set_header   Host       $host;
        proxy_set_header   X-Real-IP  $remote_addr;

        # Keep long-lived WebSocket connections alive
        proxy_read_timeout  3600s;
        proxy_send_timeout  3600s;
        keepalive_timeout   3600s;

        # Buffer settings for large Substrate responses
        proxy_buffer_size          128k;
        proxy_buffers              4 256k;
        proxy_busy_buffers_size    256k;
    }
}
NGINX

ln -sf /etc/nginx/sites-available/abena-testnet /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
echo "  ✓ Nginx config: /etc/nginx/sites-available/abena-testnet"

# =============================================================================
# PHASE 10: SSL Certificate (Let's Encrypt)
# =============================================================================
echo ""
echo "► Phase 10: SSL certificate..."
echo "  Run this manually after DNS is pointed to this server:"
echo ""
echo "  certbot --nginx -d testnet.abenihr.com"
echo ""
echo "  Auto-renewal is set up by certbot automatically."

# =============================================================================
# PHASE 11: Start the Node
# =============================================================================
echo ""
echo "► Phase 11: Starting ABENA node..."

systemctl start abena-node
sleep 3

if systemctl is-active --quiet abena-node; then
    echo "  ✓ abena-node is running!"
else
    echo "  ⚠ Service may not have started. Check: journalctl -u abena-node -n 50"
fi

# =============================================================================
# PHASE 12: Insert Session Keys (validator setup)
# =============================================================================
echo ""
echo "► Phase 12: Session key insertion (MANUAL STEP REQUIRED)..."
echo ""
echo "  After node starts and syncs, insert your validator keys:"
echo ""
echo "  # Generate keys first:"
echo "  $BINARY_DIR/abena-node key generate --scheme sr25519"
echo "  $BINARY_DIR/abena-node key generate --scheme ed25519"
echo ""
echo "  # Insert Aura key:"
cat << 'KEY_CMD'
  curl -sS -H "Content-Type: application/json" \
    --data '{
      "jsonrpc":"2.0","id":1,
      "method":"author_insertKey",
      "params":["aura","YOUR_SECRET_SEED//aura","YOUR_SR25519_PUBLIC_KEY"]
    }' http://localhost:9933

  # Insert Grandpa key:
  curl -sS -H "Content-Type: application/json" \
    --data '{
      "jsonrpc":"2.0","id":1,
      "method":"author_insertKey",
      "params":["gran","YOUR_SECRET_SEED//grandpa","YOUR_ED25519_PUBLIC_KEY"]
    }' http://localhost:9933
KEY_CMD
echo ""
echo "  After inserting keys: systemctl restart abena-node"

# =============================================================================
# PHASE 13: Verify ABENA Coin is live
# =============================================================================
echo ""
echo "► Phase 13: Verifying ABENA Coin..."
echo ""
echo "  Waiting for node to initialize (10s)..."
sleep 10

# Check chain head
HEAD=$(curl -sS -H "Content-Type: application/json" \
    --data '{"jsonrpc":"2.0","id":1,"method":"chain_getHeader","params":[]}' \
    http://localhost:9933 2>/dev/null || echo '{"result":null}')

echo "  Chain head: $(echo $HEAD | jq -r '.result.number // "node not ready yet"')"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              ABENA IHR TESTNET IS LIVE                      ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  Node:    systemctl status abena-node                        ║"
echo "║  Logs:    journalctl -u abena-node -f                        ║"
echo "║  RPC:     http://localhost:9933  ws://localhost:9944 (local) ║"
echo "║  Public:  wss://testnet.abenihr.com (after SSL)              ║"
echo "║                                                              ║"
echo "║  Connect Polkadot.js Apps:                                   ║"
echo "║  https://polkadot.js.org/apps                                ║"
echo "║  → Switch → Custom → wss://testnet.abenihr.com               ║"
echo "║                                                              ║"
echo "║  Verify ABENA Coin:                                          ║"
echo "║  Chain State → balances → totalIssuance                     ║"
echo "║  Should show: 1,000,000,000,000,000,000,000 planck           ║"
echo "║             = 1,000,000,000 ABENA (1 billion)                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
