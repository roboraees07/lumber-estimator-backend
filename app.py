#!/usr/bin/env python3
"""
Main Application Entry Point
Lumber Estimator API Server
"""

import uvicorn
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Load environment variables first
def load_env_file():
    """Load environment variables from .env file"""
    env_file = Path(".env")
    if env_file.exists():
        print("📋 Loading environment from .env file...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print("✅ Environment variables loaded from .env file")
    else:
        print("⚠️ .env file not found")

# Load environment variables
load_env_file()

# Import the FastAPI app
try:
    from src.api.main import app
    print("🏗️ Estimation Engine initialized with database integration")
except ImportError as e:
    print(f"❌ Failed to import application: {e}")
    print("💡 Make sure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

if __name__ == "__main__":
    print("🚀 Starting Lumber Estimator API Server...")
    print("📖 API Documentation: http://localhost:8003/docs")
    print("🔧 Health Check: http://localhost:8003/health")
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8003,  # Use port 8003 as documented in README
            reload=False,  # Disable reload to avoid warning
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        print("💡 Check if port 8003 is available or if there are dependency issues")
        sys.exit(1)

