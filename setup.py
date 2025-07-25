#!/usr/bin/env python3
"""
Setup script for Modular Portfolio.
This script handles Git submodule initialization and dependency installation.
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"⚡ {description}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr}")
        return False

def main():
    """Main setup function."""
    print("🔧 Setting up Modular Portfolio...")
    
    # Check if we're in a git repository
    if not os.path.exists('.git'):
        print("❌ Error: Not in a git repository")
        sys.exit(1)
    
    # Initialize and update git submodules
    if not run_command("git submodule init", "Initializing Git submodules"):
        sys.exit(1)
        
    if not run_command("git submodule update", "Updating Git submodules"):
        sys.exit(1)
    
    # Install Python dependencies
    requirements_path = "modular_portfolio/requirements.txt"
    if os.path.exists(requirements_path):
        if not run_command(f"pip install -r {requirements_path}", "Installing Python dependencies"):
            sys.exit(1)
    else:
        print(f"⚠️  Warning: Requirements file not found at {requirements_path}")
    
    print("✅ Setup completed successfully!")
    print("\n🚀 You can now run the application:")
    print("   CLI mode:  python3 modular_portfolio/start.py")
    print("   Web mode:  python3 modular_portfolio/start.py web")
    print("   GUI mode:  python3 modular_portfolio/start.py gui")

if __name__ == "__main__":
    main()
