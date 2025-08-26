#!/usr/bin/env python3
"""
Main Application Entry Point
Lumber Estimator API Server
"""

import uvicorn
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.api.main import app

if __name__ == "__main__":
    print("🚀 Starting Lumber Estimator API Server...")
    print("📖 API Documentation: http://localhost:8003/docs")
    print("🔧 Health Check: http://localhost:8003/health")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8003,  # Use port 8003 as documented in README
        reload=False,  # Disable reload to avoid warning
        log_level="info"
    )

