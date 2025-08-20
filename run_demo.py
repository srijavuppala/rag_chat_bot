#!/usr/bin/env python3
"""
Quick demo runner for the RAG Chatbot
This script helps you test the system without full setup
"""
import sys
import os
import subprocess
import importlib.util

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'pandas', 'numpy', 'sentence_transformers', 
        'transformers', 'torch', 'streamlit'
    ]
    
    missing_packages = []
    for package in required_packages:
        spec = importlib.util.find_spec(package)
        if spec is None:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install them using:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All required packages are installed!")
    return True

def run_offline_demo():
    """Run the offline demo"""
    print("🚀 Starting offline RAG demo...")
    try:
        from demo_offline import main
        main()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed.")
    except Exception as e:
        print(f"❌ Demo failed: {e}")

def run_streamlit_app():
    """Run the Streamlit web app"""
    print("🚀 Starting Streamlit web app...")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Streamlit app: {e}")
    except FileNotFoundError:
        print("❌ Streamlit not found. Please install it: pip install streamlit")

def main():
    """Main function"""
    print("🎓 RAG Chatbot Demo Runner")
    print("=" * 40)
    
    if not check_dependencies():
        print("\n💡 You can still try the offline demo with limited functionality.")
        choice = input("Continue anyway? (y/N): ").strip().lower()
        if choice != 'y':
            return
    
    print("\nChoose an option:")
    print("1. Run offline demo (no database required)")
    print("2. Run Streamlit web app (requires database setup)")
    print("3. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            run_offline_demo()
            break
        elif choice == '2':
            run_streamlit_app()
            break
        elif choice == '3':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()