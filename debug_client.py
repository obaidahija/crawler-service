"""
Debug client to test the crawler service with breakpoints
"""

import requests
import json
import time

def test_with_breakpoints():
    """Test the service - perfect for setting breakpoints in the server"""
    
    print("🧪 Debug Client - Testing Crawler Service")
    print("=" * 50)
    
    # Simple test configuration
    test_config = {
        "start_url": "https://httpbin.org/html",
        "engine": "beautifulsoup",
        "extractors": [
            {
                "field_name": "title",
                "selector_config": {
                    "selector": "h1",
                    "attribute": "text"
                }
            },
            {
                "field_name": "paragraphs",
                "selector_config": {
                    "selector": "p",
                    "attribute": "text",
                    "multiple": True
                }
            }
        ],
        "context": {
            "debug_test": True,
            "test_timestamp": time.time()
        }
    }
    
    try:
        print("🔍 Testing health endpoint...")
        health_response = requests.get("http://localhost:8000/health")
        print(f"✅ Health: {health_response.json()}")
        
        print("\n🔍 Testing validation endpoint...")
        validation_response = requests.post(
            "http://localhost:8000/validate",
            json=test_config
        )
        print(f"✅ Validation: {validation_response.json()}")
        
        print("\n🔍 Testing crawl endpoint...")
        print("⚠️  SET YOUR BREAKPOINTS NOW!")
        print("   - In main.py at the crawl_website function")
        print("   - In crawler_service.py at the crawl method")
        print("   - In the crawler implementations")
        
        input("Press Enter to send crawl request...")
        
        crawl_response = requests.post(
            "http://localhost:8000/crawl",
            json={"config": test_config}
        )
        
        result = crawl_response.json()
        print(f"✅ Crawl result:")
        print(json.dumps(result, indent=2))
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to service!")
        print("   Make sure the debug server is running")
        print("   Run: python debug_server.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_with_breakpoints()
