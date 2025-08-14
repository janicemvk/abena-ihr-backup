#!/usr/bin/env python3
"""
Unified Startup Script for Abena Predictive Analytics Engine
All systems consolidated through Abena SDK services
"""

import sys
import subprocess
import webbrowser
import time
import asyncio
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'httpx', 'pandas', 'numpy', 'asyncio'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies():
    """Install missing dependencies"""
    print("📦 Installing required dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--upgrade"
        ])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def run_engine_test():
    """Run the unified predictive analytics engine test"""
    print("🧪 Testing Unified Predictive Analytics Engine...")
    
    engine_path = Path("application-services/predictive-analytics-engine/test_engine.py")
    
    if not engine_path.exists():
        print("❌ Engine test file not found.")
        return False
    
    try:
        subprocess.run([sys.executable, str(engine_path)])
        return True
    except Exception as e:
        print(f"❌ Error running engine test: {e}")
        return False

def run_web_interface():
    """Launch web interface (if available)"""
    print("🌐 Checking for web interface...")
    
    # Check if Streamlit is available
    try:
        import streamlit
        streamlit_path = Path("application-services/predictive-analytics-engine/streamlit_app.py")
        
        if streamlit_path.exists():
            print("🚀 Starting Web Interface...")
            print("🔗 URL: http://localhost:8501")
            print("⏹️  Press Ctrl+C to stop the server")
            
            process = subprocess.Popen([
                sys.executable, "-m", "streamlit", "run", str(streamlit_path),
                "--server.address", "localhost",
                "--server.port", "8501",
                "--browser.gatherUsageStats", "false"
            ])
            
            time.sleep(3)
            webbrowser.open("http://localhost:8501")
            process.wait()
        else:
            print("ℹ️  Web interface not available. Run engine tests instead.")
            return False
            
    except ImportError:
        print("ℹ️  Streamlit not available. Install with: pip install streamlit")
        return False

def check_abena_services():
    """Check Abena service connectivity"""
    print("🔍 Checking Abena service connectivity...")
    
    try:
        import httpx
        import asyncio
        
        async def test_services():
            config = {
                'auth_service_url': 'http://localhost:3001',
                'data_service_url': 'http://localhost:8001',
                'privacy_service_url': 'http://localhost:8002',
                'blockchain_service_url': 'http://localhost:8003'
            }
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                for service_name, url in config.items():
                    try:
                        response = await client.get(f"{url}/health")
                        if response.status_code == 200:
                            print(f"✅ {service_name}: Connected")
                        else:
                            print(f"⚠️  {service_name}: Status {response.status_code}")
                    except Exception as e:
                        print(f"❌ {service_name}: Not available ({e})")
        
        asyncio.run(test_services())
        
    except ImportError:
        print("⚠️  httpx not available. Install with: pip install httpx")
    except Exception as e:
        print(f"❌ Error checking services: {e}")

def show_menu():
    """Display the unified menu"""
    print("🧬 Abena Predictive Analytics Engine (Unified)")
    print("=" * 55)
    print("1. 🧪 Test Engine (Abena SDK)")
    print("2. 🌐 Launch Web Interface")
    print("3. 🔍 Check Abena Services")
    print("4. 📦 Install Dependencies")
    print("5. 📚 Show Documentation")
    print("6. ❌ Exit")
    print("=" * 55)

def show_documentation():
    """Show documentation and usage information"""
    print("📚 Abena Predictive Analytics Engine Documentation")
    print("=" * 55)
    
    readme_path = Path("application-services/predictive-analytics-engine/README.md")
    if readme_path.exists():
        print("📖 Full documentation available in:")
        print(f"   {readme_path}")
        print("\n🚀 Quick Start:")
        print("   1. Set environment variables (optional):")
        print("      export AUTH_SERVICE_URL=http://localhost:3001")
        print("      export DATA_SERVICE_URL=http://localhost:8001")
        print("      export PRIVACY_SERVICE_URL=http://localhost:8002")
        print("      export BLOCKCHAIN_SERVICE_URL=http://localhost:8003")
        print("   2. Run engine test: python start_app.py")
        print("   3. Select option 1 to test the engine")
    else:
        print("📖 Documentation not found.")
    
    print("\n🔧 Key Features:")
    print("   • Unified Abena SDK integration")
    print("   • Privacy-compliant data processing")
    print("   • Blockchain audit trail")
    print("   • Real-time predictions")
    print("   • Population health analytics")

def main():
    """Main application entry point"""
    while True:
        show_menu()
        
        try:
            choice = input("\nSelect an option (1-6): ").strip()
            
            if choice == "1":
                run_engine_test()
            elif choice == "2":
                run_web_interface()
            elif choice == "3":
                check_abena_services()
            elif choice == "4":
                install_dependencies()
            elif choice == "5":
                show_documentation()
            elif choice == "6":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid option. Please select 1-6.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    print("🚀 Starting Abena Predictive Analytics Engine (Unified)")
    print("🔗 All systems consolidated through Abena SDK")
    print()
    
    # Check dependencies first
    missing = check_dependencies()
    if missing:
        print(f"⚠️  Missing packages: {missing}")
        print("💡 Installing dependencies...")
        install_dependencies()
    
    main() 