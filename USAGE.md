# Web Crawler Service - Usage Guide

## Overview

This is a modular web crawler microservice built with FastAPI that can extract data from websites based on configurable JSON configurations. It supports two crawler engines (Selenium and BeautifulSoup) and is designed to handle list-based crawling with pagination.

## Features

✅ **Modular Architecture**: Easy to extend with new crawler engines  
✅ **Two Crawler Engines**: Selenium (for JavaScript-heavy sites) and BeautifulSoup (for static content)  
✅ **List Item Crawling**: Can navigate through list pages and extract details from individual items  
✅ **Pagination Support**: Automatically handles pagination with configurable limits  
✅ **Configurable Extraction**: Define custom selectors and extraction rules via JSON  
✅ **RESTful API**: Easy integration with other services  
✅ **Context Management**: Pass and receive context data with requests  
✅ **Error Handling**: Comprehensive error reporting  

## Quick Start

### 1. Start the Service

```bash
# Activate virtual environment
.venv\Scripts\activate

# Start the service
uvicorn main:app --reload --port 8000
```

The service will be available at `http://localhost:8000`

### 2. API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

### 3. Health Check

```bash
curl http://localhost:8000/health
```

## API Endpoints

### `POST /crawl`
Execute a crawl operation with the provided configuration.

### `POST /validate`
Validate a crawl configuration without executing it.

### `GET /engines`
Get list of supported crawler engines.

### `GET /health`
Health check endpoint.

## Configuration Format

### Basic Structure

```json
{
  "start_url": "https://example.com",
  "engine": "selenium" | "beautifulsoup",
  "navigation": { ... },      // Optional: for list crawling
  "extractors": [ ... ],      // Required: data extraction rules
  "pagination": { ... },      // Optional: pagination config
  "wait_config": { ... },     // Optional: timing configuration
  "context": { ... }          // Optional: additional context
}
```

### Single Page Crawling

For extracting data from a single page:

```json
{
  "start_url": "https://example.com/article",
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
        "multiple": true
      }
    }
  ]
}
```

### List-Based Crawling

For crawling lists of items and extracting details from each:

```json
{
  "start_url": "https://example.com/products",
  "engine": "selenium",
  "navigation": {
    "list_items_selector": ".product-card",
    "detail_link_selector": "a",
    "detail_link_attribute": "href"
  },
  "extractors": [
    {
      "field_name": "name",
      "selector_config": {
        "selector": "h1.product-name",
        "attribute": "text"
      }
    },
    {
      "field_name": "price",
      "selector_config": {
        "selector": ".price",
        "attribute": "text"
      }
    }
  ],
  "pagination": {
    "enabled": true,
    "next_page_selector": ".pagination .next",
    "next_page_attribute": "href",
    "max_pages": 5
  }
}
```

## Configuration Reference

### `navigation` (Optional)
For list-based crawling:
- `list_items_selector`: CSS selector for list items
- `detail_link_selector`: CSS selector for link within list item (optional)
- `detail_link_attribute`: Attribute containing the link (default: "href")

### `extractors` (Required)
Array of extraction rules:
- `field_name`: Name for the extracted field
- `selector_config.selector`: CSS selector for the element
- `selector_config.attribute`: Attribute to extract ("text", "href", "src", etc.)
- `selector_config.multiple`: Extract multiple elements (default: false)

### `pagination` (Optional)
For handling pagination:
- `enabled`: Enable pagination (default: false)
- `next_page_selector`: CSS selector for next page link
- `next_page_attribute`: Attribute containing next page URL (default: "href")
- `max_pages`: Maximum pages to crawl (optional)

### `wait_config` (Optional)
Timing configuration:
- `page_load_timeout`: Page load timeout in seconds (default: 10)
- `element_wait_timeout`: Element wait timeout in seconds (default: 5)
- `delay_between_requests`: Delay between requests in seconds (default: 1.0)

## Engine Comparison

### Selenium
- **Best for**: JavaScript-heavy sites, SPAs, dynamic content
- **Pros**: Full browser simulation, handles JavaScript
- **Cons**: Slower, more resource-intensive
- **Use when**: Site requires JavaScript execution

### BeautifulSoup
- **Best for**: Static HTML content, faster crawling
- **Pros**: Fast, lightweight, efficient
- **Cons**: Cannot handle JavaScript
- **Use when**: Site content is available in initial HTML

## Client Usage

### Python Client

```python
import requests

# Basic crawl request
config = {
    "start_url": "https://example.com",
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

response = requests.post(
    "http://localhost:8000/crawl",
    json={"config": config}
)

result = response.json()
print(result["result"]["data"])
```

### Handling Pagination

When pagination is enabled, the service returns `next_page_url` in the response. Your client can use this to continue crawling:

```python
def crawl_all_pages(base_config):
    all_data = []
    config = base_config.copy()
    
    while True:
        response = requests.post(
            "http://localhost:8000/crawl",
            json={"config": config}
        )
        
        result = response.json()["result"]
        all_data.extend(result["data"])
        
        if result["next_page_url"]:
            config["start_url"] = result["next_page_url"]
        else:
            break
    
    return all_data
```

## Error Handling

The service provides comprehensive error information:

```json
{
  "result": {
    "success": false,
    "data": [],
    "errors": [
      "Error extracting from https://example.com/item1: Timeout",
      "Element not found: .price"
    ],
    "total_items": 0
  }
}
```

## Examples

See the `examples/` directory for complete configuration examples:
- `ecommerce_config.json`: E-commerce product listing
- `events_config.json`: Event listing with details
- `single_page_config.json`: Single page article extraction

## Deployment

### Docker

```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Manual Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Best Practices

1. **Start Simple**: Begin with BeautifulSoup for static content
2. **Use Selenium Sparingly**: Only when JavaScript execution is required
3. **Set Appropriate Delays**: Avoid being blocked by setting reasonable delays
4. **Handle Errors**: Always check the `success` field and `errors` array
5. **Test Configurations**: Use the `/validate` endpoint before crawling
6. **Respect Robots.txt**: Always check and respect website crawling policies
7. **Monitor Performance**: Use appropriate timeouts and limits

## Extending the Service

To add a new crawler engine:

1. Create a new crawler class inheriting from `BaseCrawler`
2. Implement all abstract methods
3. Add the new engine to `CrawlerEngine` enum
4. Update `CrawlerFactory` to handle the new engine

## Troubleshooting

### Common Issues

**Service won't start**
- Check that all dependencies are installed
- Verify Python version (3.11+ recommended)

**Selenium not working**
- Ensure Chrome is installed
- Check that chromedriver is accessible

**Extraction returns empty results**
- Verify selectors are correct
- Check if site requires JavaScript (use Selenium)
- Confirm site structure matches configuration

**Getting blocked**
- Increase `delay_between_requests`
- Check User-Agent settings
- Verify robots.txt compliance
