# Windows Build Fix Guide

## Issues Found

1. **OpenSSL Build Error**: Git's Perl is missing required modules (`Locale::Maketext::Simple`)
2. **protoc Missing**: Protocol Buffers compiler is required for `litep2p` dependency

## Solutions

### Option 1: Install Strawberry Perl (Recommended)

Strawberry Perl includes all modules needed for OpenSSL builds:

1. Download from: https://strawberryperl.com/
2. Install to default location: `C:\Strawberry`
3. Add to PATH: `C:\Strawberry\perl\bin`
4. Restart terminal/PowerShell

### Option 2: Install Protocol Buffers

1. Download protoc from: https://github.com/protocolbuffers/protobuf/releases
2. Download `protoc-XX.X-win64.zip` (latest version)
3. Extract to `C:\protoc`
4. Add `C:\protoc\bin` to PATH
5. Verify: `protoc --version`

### Option 3: Use Pre-built OpenSSL (Alternative)

If you have OpenSSL installed:
1. Set `OPENSSL_DIR` environment variable
2. Set `OPENSSL_NO_VENDOR=1`
3. Ensure OpenSSL includes `include` and `lib` directories

## Quick Fix Commands

After installing dependencies:

```powershell
# Set environment variables
$env:PATH = "C:\Strawberry\perl\bin;C:\protoc\bin;$env:PATH"

# Build
cd "C:\Users\Jan Marie\Abena Blockchain"
cargo build --release
```

## Alternative: Use vcpkg (Advanced)

If you have Visual Studio:
```powershell
vcpkg install openssl:x64-windows
vcpkg integrate install
```

Then set:
```powershell
$env:OPENSSL_DIR = "C:\vcpkg\installed\x64-windows"
$env:OPENSSL_NO_VENDOR = "1"
```

