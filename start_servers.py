#!/usr/bin/env python3
"""
Startup script for MCP servers
Launches all MCP servers in the background
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def start_mcp_servers():
    """Start all MCP servers in the background"""
    
    print("🚀 Starting MCP Servers...")
    
    # Get the directory of this script
    script_dir = Path(__file__).parent
    
    # Start Weather MCP Server
    print("🌤️  Starting Weather MCP Server on port 3001...")
    weather_cmd = [sys.executable, str(script_dir / "mcp_servers" / "weather_mcp.py")]
    weather_process = subprocess.Popen(
        weather_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Start Calculator MCP Server
    print("🧮 Starting Calculator MCP Server on port 3002...")
    calculator_cmd = [sys.executable, str(script_dir / "mcp_servers" / "calculator_mcp.py")]
    calculator_process = subprocess.Popen(
        calculator_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait a moment for servers to start
    print("⏳ Waiting for servers to start...")
    time.sleep(3)
    
    # Check if servers are running
    try:
        import requests
        
        # Check Weather MCP
        try:
            response = requests.get("http://localhost:3001/", timeout=5)
            if response.status_code == 200:
                print("✅ Weather MCP Server is running")
            else:
                print(f"⚠️  Weather MCP Server returned status {response.status_code}")
        except requests.RequestException:
            print("❌ Weather MCP Server failed to start")
        
        # Check Calculator MCP
        try:
            response = requests.get("http://localhost:3002/", timeout=5)
            if response.status_code == 200:
                print("✅ Calculator MCP Server is running")
            else:
                print(f"⚠️  Calculator MCP Server returned status {response.status_code}")
        except requests.RequestException:
            print("❌ Calculator MCP Server failed to start")
            
    except ImportError:
        print("⚠️  requests module not available, skipping server checks")
    
    print("\n🎉 MCP Servers started!")
    print("You can now run: python main.py")
    print("\nTo stop the servers, press Ctrl+C")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping MCP Servers...")
        weather_process.terminate()
        calculator_process.terminate()
        print("👋 Servers stopped")

if __name__ == "__main__":
    start_mcp_servers() 