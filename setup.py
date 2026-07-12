# setup.py - One-time setup script
import os
import sys
import subprocess

def install_dependencies():
    print("📦 Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("✅ Dependencies installed!")

def create_env_file():
    if not os.path.exists('.env'):
        print("📝 Creating .env file...")
        with open('.env', 'w') as f:
            f.write("""# ===== API CONFIGURATION =====
# Choose which API to use: 'huggingface' or 'gemini'
USE_API=huggingface

# Hugging Face API (100% FREE - Get from https://huggingface.co/settings/tokens)
HF_API_KEY=your_huggingface_token_here
HF_MODEL=microsoft/DialoGPT-medium

# Gemini API (Free Tier - 60 requests/min)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_API_BASE=https://generativelanguage.googleapis.com/v1beta
GEMINI_MODEL=gemini-2.0-flash

# OpenWeather API (Free for weather)
OPENWEATHER_API_KEY=your_openweather_key_here
""")
        print("✅ .env file created!")
        print("\n⚠️ Please edit .env file and add your API keys.")
    else:
        print("✅ .env file already exists.")

def main():
    print("🚀 Setting up MediGuide...")
    print("-" * 40)
    
    install_dependencies()
    create_env_file()
    
    print("-" * 40)
    print("✅ Setup complete!")
    print("\n📝 Next steps:")
    print("1. Get your FREE API key from: https://huggingface.co/settings/tokens")
    print("2. Add the key to .env file")
    print("3. Run: python gui.py")

if __name__ == "__main__":
    main()