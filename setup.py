#!/usr/bin/env python3
"""
Setup script for RAG Chatbot Application
Helps with initial configuration and environment setup
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header():
    """Print setup script header"""
    print("=" * 60)
    print("🤖 RAG Chatbot Application Setup")
    print("=" * 60)
    print("This script will help you set up the RAG chatbot application.")
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("🔍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def create_env_file():
    """Create .env file from template"""
    print("\n📝 Creating environment configuration...")
    
    env_example_path = Path(".env.example")
    env_path = Path(".env")
    
    if env_path.exists():
        overwrite = input("⚠️  .env file already exists. Overwrite? (y/N): ")
        if overwrite.lower() != 'y':
            print("   Skipping .env file creation.")
            return True
    
    if not env_example_path.exists():
        print("❌ .env.example file not found!")
        return False
    
    # Read example and create .env
    with open(env_example_path, 'r') as f:
        content = f.read()
    
    with open(env_path, 'w') as f:
        f.write(content)
    
    print("✅ Created .env file from template")
    print("   Please edit .env file with your actual credentials!")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies!")
        return False

def check_snowflake_setup():
    """Check Snowflake setup requirements"""
    print("\n❄️  Snowflake Setup Requirements:")
    print("   1. Snowflake account with Cortex Search enabled")
    print("   2. Warehouse with appropriate compute resources")
    print("   3. User with necessary permissions")
    print("   4. Run the SQL script: config/snowflake_setup.sql")
    print("   5. Update YOUR_WAREHOUSE placeholder in the SQL script")
    
    return True

def check_mistral_setup():
    """Check Mistral API setup requirements"""
    print("\n🧠 Mistral API Setup Requirements:")
    print("   1. Sign up for Mistral API access")
    print("   2. Get your API key")
    print("   3. Add API key to .env file")
    print("   4. Ensure sufficient API quota")
    
    return True

def display_next_steps():
    """Display next steps for user"""
    print("\n🎉 Setup completed!")
    print("\n📋 Next Steps:")
    print("   1. Edit .env file with your credentials:")
    print("      - Snowflake account details")
    print("      - Mistral API key")
    print("\n   2. Set up Snowflake database:")
    print("      - Connect to your Snowflake account")
    print("      - Run config/snowflake_setup.sql")
    print("      - Update YOUR_WAREHOUSE placeholder")
    print("\n   3. Run the application:")
    print("      streamlit run app.py")
    print("\n   4. Access the app at:")
    print("      http://localhost:8501")
    print("\n📖 For detailed instructions, see README.md")

def main():
    """Main setup function"""
    print_header()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed during dependency installation!")
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        print("\n❌ Setup failed during .env file creation!")
        sys.exit(1)
    
    # Check Snowflake requirements
    check_snowflake_setup()
    
    # Check Mistral requirements
    check_mistral_setup()
    
    # Display next steps
    display_next_steps()

if __name__ == "__main__":
    main() 