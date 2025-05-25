import subprocess
import sys
import platform

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else "Not installed"
    except:
        return "Error checking"

def check_package(package_name):
    try:
        module = __import__(package_name)
        version = getattr(module, '__version__', 'unknown')
        return f"{version}"
    except ImportError:
        return "Not installed"

print("=== Windows Development Environment Check ===")
print(f"Platform: {platform.platform()}")
print(f"Python: {sys.version}")
print(f"Virtual Environment: {'Yes' if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else 'No'}")
print()

print("=== External Tools ===")
print(f"Node.js: {run_command('node --version')}")
print(f"npm: {run_command('npm --version')}")
print(f"Git: {run_command('git --version')}")
print(f"AWS CLI: {run_command('aws --version')}")
print(f"SAM CLI: {run_command('sam --version')}")
print()

print("=== Python Packages ===")
packages = [
    'fastapi', 'uvicorn', 'mangum', 'boto3', 
    'pydantic', 'pytest', 'black', 'pylint'
]

for package in packages:
    version = check_package(package)
    print(f"{package}: {version}")

print()
print("=== Check Complete ===")

# Test FastAPI specifically
try:
    from fastapi import FastAPI
    app = FastAPI()
    print("✅ FastAPI can be imported and instantiated successfully!")
except Exception as e:
    print(f"❌ FastAPI test failed: {e}")