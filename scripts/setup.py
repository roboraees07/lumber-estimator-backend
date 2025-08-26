#!/usr/bin/env python3
"""
Setup script for Lumber Estimator project
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stder` r}")
        return False

def create_directories():
    """Create necessary project directories"""
    directories = [
        "data",
        "outputs", 
        "logs",
        "temp",
        "samples"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Created directory: {directory}")

def setup_environment():
    """Set up environment file"""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists() and env_example.exists():
        print("📝 Creating .env file from template...")
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("⚠️  Please edit .env file with your actual API keys and configuration")
        return True
    elif env_file.exists():
        print("✅ .env file already exists")
        return True
    else:
        print("❌ env.example file not found")
        return False

def install_dependencies():
    """Install Python dependencies"""
    return run_command("pip install -r requirements.txt", "Installing dependencies")

def run_tests():
    """Run the test suite"""
    return run_command("python -m pytest tests/ -v", "Running tests")

def main():
    """Main setup function"""
    print("🚀 Setting up Lumber Estimator project...")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Create directories
    create_directories()
    
    # Setup environment
    if not setup_environment():
        print("❌ Environment setup failed")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Dependency installation failed")
        sys.exit(1)
    
    # Run tests
    print("\n🧪 Running tests...")
    if not run_tests():
        print("⚠️  Some tests failed, but setup can continue")
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your Gemini API key")
    print("2. Run: python app.py")
    print("3. Open: http://localhost:8003/docs")
    print("\n🔑 Default admin credentials:")
    print("   Username: admin")
    print("   Password: admin123")

if __name__ == "__main__":
    main()




