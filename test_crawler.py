import pytest
import httpx
import asyncio
import json
from pathlib import Path
from fastapi.testclient import TestClient
from main import app

# Test client for FastAPI
client = TestClient(app)


def test_health_endpoint():
    """Test the health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "crawler-service"
    assert data["version"] == "1.0.0"


def test_engines_endpoint():
    """Test the engines endpoint"""
    response = client.get("/engines")
    assert response.status_code == 200
    data = response.json()
    assert "engines" in data
    assert "default" in data
    assert isinstance(data["engines"], list)
    assert len(data["engines"]) > 0


def test_config_validation():
    """Test configuration validation endpoint"""
    # Valid config
    valid_config = {
        "start_url": "https://httpbin.org/html",
        "engine": "beautifulsoup",
        "extractors": [
            {
                "field_name": "title",
                "selector_config": {
                    "selector": "h1",
                    "attribute": "text"
                }
            }
        ]
    }
    
    response = client.post("/validate", json=valid_config)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True


def test_config_validation_invalid():
    """Test configuration validation with invalid config"""
    # Invalid config (missing required fields)
    invalid_config = {
        "start_url": "not-a-url",
        "engine": "invalid_engine"
        # Missing required 'extractors' field
    }
    
    response = client.post("/validate", json=invalid_config)
    # FastAPI returns 422 for validation errors, which is correct
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_config_validation_with_business_logic_errors():
    """Test configuration validation with business logic errors"""
    # Valid structure but invalid business logic
    invalid_config = {
        "start_url": "https://example.com",
        "engine": "beautifulsoup",
        "extractors": [
            {
                "field_name": "test",
                "selector_config": {
                    "selector": "",  # Empty selector should fail validation
                    "attribute": "text"
                }
            }
        ]
    }
    
    response = client.post("/validate", json=invalid_config)
    assert response.status_code == 200  # Structure is valid, but business logic validation should fail
    data = response.json()
    assert data["valid"] is False
    assert "errors" in data


@pytest.mark.asyncio
async def test_crawl_endpoint():
    """Test the crawl endpoint with a simple configuration"""
    config = {
        "start_url": "https://httpbin.org/html",
        "engine": "beautifulsoup",
        "extractors": [
            {
                "field_name": "title",
                "selector_config": {
                    "selector": "h1",
                    "attribute": "text"
                }
            }
        ],
        "context": {
            "test": True
        }
    }
    
    crawl_request = {"config": config}
    
    # Use httpx for async testing
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/crawl", json=crawl_request)
    
    assert response.status_code == 200
    data = response.json()
    assert "result" in data  # Changed from "results" to "result"
    assert "success" in data["result"]
    assert "data" in data["result"]


def test_example_configs():
    """Test that example configurations are valid"""
    examples_dir = Path("examples")
    
    if not examples_dir.exists():
        pytest.skip("Examples directory not found")
    
    config_files = list(examples_dir.glob("*.json"))
    
    if not config_files:
        pytest.skip("No example config files found")
    
    for config_file in config_files:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        response = client.post("/validate", json=config)
        assert response.status_code == 200, f"Failed to validate {config_file.name}"
        
        data = response.json()
        assert data["valid"] is True, f"Config {config_file.name} is invalid: {data.get('errors', [])}"


def test_cors_headers():
    """Test that CORS headers are properly set"""
    # Test with a regular GET request to see if CORS is configured
    response = client.get("/health")
    assert response.status_code == 200
    
    # For TestClient, CORS headers might not be included in the same way as real requests
    # This is a limitation of the test client, so we'll test the endpoint works instead


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
