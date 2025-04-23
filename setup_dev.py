#!/usr/bin/env python3
"""
Development setup script for Knowledge Storage MCP.

This script helps set up the development environment by:
1. Creating a virtual environment if it doesn't exist
2. Installing dependencies
3. Setting up pre-commit hooks
4. Creating a .env file with development configuration
"""

import os
import subprocess
import sys
import venv
from pathlib import Path

def check_python_version():
    """Check that Python version is at least 3.10."""
    if sys.version_info < (3, 10):
        print("Error: Python 3.10 or higher is required.")
        sys.exit(1)

def create_venv():
    """Create a virtual environment if it doesn't exist."""
    venv_path = Path(".venv")
    if not venv_path.exists():
        print("Creating virtual environment...")
        venv.create(".venv", with_pip=True)
        return True
    return False

def get_venv_python():
    """Get the path to the Python executable in the virtual environment."""
    if os.name == "nt":  # Windows
        return Path(".venv") / "Scripts" / "python.exe"
    return Path(".venv") / "bin" / "python"

def install_dependencies(python_exec):
    """Install dependencies using pip."""
    print("Installing dependencies...")
    subprocess.run([python_exec, "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.run([python_exec, "-m", "pip", "install", "-r", "requirements.txt"])
    subprocess.run([python_exec, "-m", "pip", "install", "-r", "requirements-dev.txt"])

def setup_precommit(python_exec):
    """Set up pre-commit hooks."""
    print("Setting up pre-commit hooks...")
    subprocess.run([python_exec, "-m", "pip", "install", "pre-commit"])
    subprocess.run(["pre-commit", "install"])

def create_env_file():
    """Create a .env file with development configuration if it doesn't exist."""
    env_path = Path(".env")
    if not env_path.exists():
        print("Creating .env file with development configuration...")
        with open(env_path, "w") as f:
            f.write("""# Development environment configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
MCP_HOST=0.0.0.0
MCP_PORT=8000
LOG_LEVEL=DEBUG
""")

def main():
    """Main function."""
    check_python_version()
    created_new_venv = create_venv()
    python_exec = get_venv_python()
    
    if created_new_venv:
        install_dependencies(python_exec)
        setup_precommit(python_exec)
    
    create_env_file()
    
    print("\nDevelopment environment setup complete!")
    print("\nTo activate the virtual environment:")
    if os.name == "nt":  # Windows
        print("    .venv\\Scripts\\activate")
    else:
        print("    source .venv/bin/activate")
    
    print("\nTo start the Neo4j database:")
    print("    docker-compose up -d neo4j")
    
    print("\nTo run the server:")
    print("    python -m knowledge_storage_mcp.server")

if __name__ == "__main__":
    main()
