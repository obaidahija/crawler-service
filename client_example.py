import requests
import json
from typing import Dict, Any


class CrawlerClient:
    """Client for interacting with the crawler service"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
    
    def health_check(self) -> Dict[str, Any]:
        """Check if the service is healthy"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def get_supported_engines(self) -> Dict[str, Any]:
        """Get list of supported crawler engines"""
        response = requests.get(f"{self.base_url}/engines")
        response.raise_for_status()
        return response.json()
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a crawl configuration"""
        response = requests.post(f"{self.base_url}/validate", json=config)
        response.raise_for_status()
        return response.json()
    
    def crawl(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a crawl operation"""
        payload = {"config": config}
        response = requests.post(f"{self.base_url}/crawl", json=payload)
        response.raise_for_status()
        return response.json()
    
    def crawl_from_file(self, config_file: str) -> Dict[str, Any]:
        """Execute a crawl operation from a configuration file"""
        with open(config_file, 'r') as f:
            config = json.load(f)
        return self.crawl(config)


# Example usage
if __name__ == "__main__":
    client = CrawlerClient()
    
    try:
        # Check service health
        health = client.health_check()
        print("Service is healthy:", health)
        
        # Get supported engines
        engines = client.get_supported_engines()
        print("Supported engines:", engines)
        
        # Example configuration for a hypothetical website
        example_config = {
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
                "test": "example"
            }
        }
        
        # Validate configuration
        validation = client.validate_config(example_config)
        print("Validation result:", validation)
        
        if validation["valid"]:
            # Execute crawl
            result = client.crawl(example_config)
            print("Crawl result:", json.dumps(result, indent=2))
        else:
            print("Configuration is invalid:", validation["errors"])
            
    except requests.exceptions.ConnectionError:
        print("Could not connect to crawler service. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"Error: {str(e)}")
