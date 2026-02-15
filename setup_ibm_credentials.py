"""
IBM Quantum Credentials Setup Helper
This script helps you configure your IBM Quantum credentials for ABENA
"""

import sys
import io
import os
import json
from pathlib import Path

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    from qiskit_ibm_runtime import QiskitRuntimeService
except ImportError:
    print("❌ Error: qiskit-ibm-runtime not installed!")
    print("   Install it with: pip install qiskit-ibm-runtime")
    sys.exit(1)

def check_existing_credentials():
    """Check if credentials already exist"""
    print("\n" + "="*70)
    print("📋 CHECKING EXISTING CREDENTIALS")
    print("="*70)
    
    qiskit_dir = Path.home() / ".qiskit"
    config_file = qiskit_dir / "qiskit-ibm.json"
    
    if config_file.exists():
        print(f"✅ Found credentials file: {config_file}")
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            print("\n📝 Current configuration:")
            for key, value in config.items():
                if 'token' in value:
                    token_preview = value['token'][:10] + "..." + value['token'][-5:]
                    print(f"   {key}:")
                    print(f"      Channel: {value.get('channel', 'N/A')}")
                    print(f"      Token: {token_preview}")
                    print(f"      URL: {value.get('url', 'N/A')}")
            
            return config
        except Exception as e:
            print(f"⚠️  Error reading config: {e}")
            return None
    else:
        print(f"❌ No credentials file found at: {config_file}")
        return None

def test_connection(token=None):
    """Test connection to IBM Quantum"""
    print("\n" + "="*70)
    print("🔌 TESTING CONNECTION TO IBM QUANTUM")
    print("="*70)
    
    try:
        # Modern qiskit-ibm-runtime accepts only these channels:
        # - 'ibm_quantum'
        # - 'ibm_cloud'
        # (Older docs referenced 'ibm_quantum_platform', but recent runtimes reject it.)
        channels_to_try = ['ibm_quantum', 'ibm_cloud']

        last_err = None
        service = None
        for channel in channels_to_try:
            try:
                print(f"   Trying channel: {channel}")
                if token:
                    service = QiskitRuntimeService(channel=channel, token=token)
                else:
                    service = QiskitRuntimeService(channel=channel)
                break
            except Exception as e:
                print(f"   ⚠️  Channel {channel} failed: {e}")
                last_err = e
                service = None

        if service is None:
            raise last_err or Exception("Failed to initialize IBM Runtime service")
        
        print("✅ Connection successful!")
        
        # List available backends
        print("\n🖥️  Available quantum backends:")
        backends = service.backends()
        for backend in backends[:5]:  # Show first 5
            status = backend.status()
            print(f"   • {backend.name}")
            print(f"     Qubits: {backend.num_qubits}")
            print(f"     Status: {status.status_msg}")
            print(f"     Pending jobs: {status.pending_jobs}")
        
        if len(backends) > 5:
            print(f"   ... and {len(backends) - 5} more backends")
        
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Possible issues:")
        print("   1. Invalid or expired API token")
        print("   2. Network connectivity issues")
        print("   3. IBM Quantum service temporarily unavailable")
        return False

def save_credentials(token, channel=None):
    """Save credentials to Qiskit config file"""
    print("\n" + "="*70)
    print("💾 SAVING CREDENTIALS")
    print("="*70)
    
    try:
        # Prefer modern channel names.
        channels_to_try = [channel] if channel else ['ibm_quantum', 'ibm_cloud']
        last_err = None
        for ch in channels_to_try:
            if not ch:
                continue
            try:
                QiskitRuntimeService.save_account(channel=ch, token=token, overwrite=True)
                last_err = None
                break
            except Exception as e:
                last_err = e
                continue
        if last_err:
            raise last_err
        print(f"✅ Credentials saved successfully!")
        print(f"   Location: {Path.home() / '.qiskit' / 'qiskit-ibm.json'}")
        return True
    except Exception as e:
        print(f"❌ Failed to save credentials: {e}")
        return False

def get_token_instructions():
    """Display instructions for getting an IBM Quantum API token"""
    print("\n" + "="*70)
    print("📖 HOW TO GET YOUR IBM QUANTUM API TOKEN")
    print("="*70)
    print("""
1. 🌐 Go to IBM Quantum Platform:
   https://quantum.ibm.com/

2. 👤 Sign in or create a free account:
   - Click "Sign in" or "Get started"
   - Use your IBM ID or create a new account

3. 🔑 Get your API token:
   - After logging in, click on your profile icon (top right)
   - Select "My account" or "Account settings"
   - Navigate to "API token" section
   - Click "Generate token" if you don't have one
   - Copy the token (you'll only see it once!)

4. 💾 Save the token securely:
   - You can use this script to save it
   - Or set environment variable: QISKIT_IBM_TOKEN=your_token_here

5. ✅ Test your connection:
   - Run this script with --test flag
   - Or run: python setup_ibm_credentials.py --test

📚 More info: https://docs.quantum.ibm.com/start/install
    """)

def main():
    print("="*70)
    print("🔧 IBM QUANTUM CREDENTIALS SETUP HELPER")
    print("="*70)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--test':
            # Test existing credentials
            config = check_existing_credentials()
            if config:
                test_connection()
            else:
                print("\n❌ No credentials found. Please save credentials first.")
                get_token_instructions()
            return
        elif sys.argv[1] == '--help' or sys.argv[1] == '-h':
            print("""
Usage:
  python setup_ibm_credentials.py              # Interactive setup
  python setup_ibm_credentials.py --test       # Test existing credentials
  python setup_ibm_credentials.py --help       # Show this help
  python setup_ibm_credentials.py --token TOKEN # Save token directly
            """)
            return
        elif sys.argv[1] == '--token' and len(sys.argv) > 2:
            # Save token directly
            token = sys.argv[2]
            if save_credentials(token):
                test_connection(token)
            return
    
    # Interactive mode
    config = check_existing_credentials()
    
    if config:
        print("\n" + "="*70)
        print("🧪 TESTING EXISTING CREDENTIALS")
        print("="*70)
        if test_connection():
            print("\n✅ Your credentials are working correctly!")
            print("   You can now run: python abena_quantum_hardware_test.py")
            return
        else:
            print("\n⚠️  Existing credentials are not working.")
            print("   You may need to update your API token.")
    
    # Get new token
    print("\n" + "="*70)
    print("🔑 ENTER YOUR IBM QUANTUM API TOKEN")
    print("="*70)
    get_token_instructions()
    
    print("\n" + "-"*70)
    token = input("\nEnter your IBM Quantum API token (or press Enter to skip): ").strip()
    
    if not token:
        print("\n⚠️  No token entered. Exiting.")
        print("   Run this script again when you have your token.")
        return
    
    # Save credentials
    if save_credentials(token):
        # Test connection
        if test_connection(token):
            print("\n" + "="*70)
            print("🎉 SUCCESS! CREDENTIALS CONFIGURED")
            print("="*70)
            print("\n✅ You can now run the hardware test:")
            print("   python abena_quantum_hardware_test.py")
        else:
            print("\n⚠️  Credentials saved but connection test failed.")
            print("   Please verify your token is correct.")

if __name__ == "__main__":
    main()





