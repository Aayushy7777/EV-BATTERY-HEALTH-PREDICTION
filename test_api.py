"""
Test script for the EV Battery Health Prediction API
Usage: python test_api.py
"""

import requests
import json
import time

API_URL = "http://127.0.0.1:8000"

def test_health():
    """Check if the API and model are properly loaded"""
    print("\n🔍 Testing API Health Check...")
    response = requests.get(f"{API_URL}/health")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API is running")
        print(f"   Model loaded: {data['model_loaded']}")
        print(f"   Features loaded: {data['feature_names_loaded']}")
        print(f"   Expected features: {data['expected_features']}")
        return True
    else:
        print(f"❌ API health check failed: {response.status_code}")
        return False

def test_predictions():
    """Test various battery health scenarios"""
    print("\n📊 Testing Model Predictions...")
    
    test_cases = [
        {
            "name": "Healthy Battery (New)",
            "data": {
                "cycle_count": 100,
                "avg_temperature": 25.0,
                "charge_rate": 1.0,
                "discharge_rate": 1.0,
                "depth_of_discharge": 50.0,
                "internal_resistance": 0.01
            }
        },
        {
            "name": "Moderate Battery (Mid-life)",
            "data": {
                "cycle_count": 1000,
                "avg_temperature": 35.0,
                "charge_rate": 2.0,
                "discharge_rate": 2.0,
                "depth_of_discharge": 75.0,
                "internal_resistance": 0.015
            }
        },
        {
            "name": "Degraded Battery (End-of-life)",
            "data": {
                "cycle_count": 3000,
                "avg_temperature": 45.0,
                "charge_rate": 2.5,
                "discharge_rate": 2.5,
                "depth_of_discharge": 90.0,
                "internal_resistance": 0.025
            }
        },
        {
            "name": "Extreme Conditions",
            "data": {
                "cycle_count": 5000,
                "avg_temperature": 50.0,
                "charge_rate": 3.0,
                "discharge_rate": 3.0,
                "depth_of_discharge": 95.0,
                "internal_resistance": 0.035
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   Test {i}: {test_case['name']}")
        print(f"   Input: {json.dumps(test_case['data'], indent=12)}")
        
        response = requests.post(
            f"{API_URL}/predict",
            json=test_case["data"]
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Prediction successful")
            print(f"      SOH: {result['soh']:.2f}%")
            print(f"      Health Status: {result['bucket']}")
        else:
            print(f"   ❌ Prediction failed: {response.status_code}")
            print(f"      Error: {response.text}")
        
        time.sleep(0.1)

def test_root():
    """Test root endpoint"""
    print("\n🏠 Testing Root Endpoint...")
    response = requests.get(API_URL)
    if response.status_code == 200:
        print(f"✅ Root endpoint working")
        print(f"   Response: {response.json()}")
    else:
        print(f"❌ Root endpoint failed")

def main():
    print("=" * 70)
    print("🔬 EV Battery Health Prediction API - Test Suite")
    print("=" * 70)
    
    try:
        # Test root
        test_root()
        
        # Check health
        if not test_health():
            print("\n⚠️  API health check failed. Make sure:")
            print("   1. FastAPI server is running: python -m uvicorn src.serve.app:app --reload")
            print("   2. Training pipeline has been executed")
            return
        
        # Test predictions
        test_predictions()
        
        print("\n" + "=" * 70)
        print("✅ All tests completed!")
        print("=" * 70)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to API at http://127.0.0.1:8000")
        print("   Make sure the FastAPI server is running:")
        print("   python -m uvicorn src.serve.app:app --reload")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
