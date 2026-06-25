"""
Docker build and test script
Usage: python docker_build.py
"""

import subprocess
import sys
import time

def run_command(cmd, description):
    """Run a shell command and print output"""
    print(f"\n📦 {description}...")
    print("-" * 70)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("🐳 EV BATTERY HEALTH PREDICTION - DOCKER BUILD & TEST")
    print("="*70)
    
    # Build Docker image
    build_cmd = "docker build -t ev-battery-prediction:latest ."
    if not run_command(build_cmd, "Building Docker image"):
        print("\n❌ Docker build failed!")
        print("Make sure Docker is installed and running.")
        return
    
    print("\n✅ Docker image built successfully!")
    
    # Show image info
    print("\n📋 Docker Image Information")
    print("-" * 70)
    subprocess.run("docker images | grep ev-battery-prediction", shell=True)
    
    print("\n" + "="*70)
    print("🚀 NEXT STEPS:")
    print("="*70)
    print("""
To run the Docker container:

  # Run in background
  docker run -d \\
    --name ev-battery-api \\
    -p 8000:8000 \\
    ev-battery-prediction:latest

  # View logs
  docker logs -f ev-battery-api

  # Stop container
  docker stop ev-battery-api

  # Test API
  curl http://localhost:8000/docs

For deployment:

  # Tag for registry (e.g., Docker Hub)
  docker tag ev-battery-prediction:latest your-registry/ev-battery-prediction:latest

  # Push to registry
  docker push your-registry/ev-battery-prediction:latest
    """)
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
