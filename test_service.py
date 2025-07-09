import asyncio
import json
import requests
from pathlib import Path


async def test_crawler_service():
    """Test the crawler service with example configurations"""
    
    base_url = "http://localhost:8000"
    
    print("Testing Crawler Service...")
    print("=" * 50)
    
    try:
        # Test health endpoint
        print("1. Testing health endpoint...")
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print("❌ Health check failed")
            return
        
        # Test engines endpoint
        print("\n2. Testing engines endpoint...")
        response = requests.get(f"{base_url}/engines")
        if response.status_code == 200:
            print("✅ Engines endpoint working")
            print(f"   Supported engines: {response.json()}")
        else:
            print("❌ Engines endpoint failed")
        
        # Test configuration validation
        print("\n3. Testing configuration validation...")
        
        # Load example config
        config_path = Path("examples/single_page_config.json")
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            response = requests.post(f"{base_url}/validate", json=config)
            if response.status_code == 200:
                validation_result = response.json()
                print("✅ Configuration validation working")
                print(f"   Valid: {validation_result['valid']}")
                if validation_result.get('errors'):
                    print(f"   Errors: {validation_result['errors']}")
                if validation_result.get('warnings'):
                    print(f"   Warnings: {validation_result['warnings']}")
            else:
                print("❌ Configuration validation failed")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text}")
        else:
            print("❌ Example config file not found")
        
        print("\n4. Service is ready for crawling!")
        print(f"   API Documentation: {base_url}/docs")
        print(f"   Example configs available in: examples/")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the service.")
        print("   Make sure the service is running with: uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_crawler_service())
