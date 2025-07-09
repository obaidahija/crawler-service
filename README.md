# Web Crawler Service

A modular web crawler microservice built with FastAPI that can extract data from websites based on configurable JSON configurations.

## Features

- Modular crawler engine (supports Selenium and BeautifulSoup)
- Configurable extraction rules via JSON
- List item crawling with detail page navigation
- Pagination support
- RESTful API with FastAPI
- Extensible architecture for adding new crawler engines

## Setup

1. Create virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the service:
```bash
uvicorn main:app --reload --port 8000
```

## API Endpoints

- `POST /crawl` - Start a crawl job with configuration
- `POST /validate` - Validate a crawl configuration
- `GET /engines` - Get supported crawler engines
- `GET /health` - Health check endpoint

## Configuration Format

See `examples/` directory for sample configurations.

## Quick Example - FVRL Events

Here's a complete example of crawling Fraser Valley Regional Library events:

```python
import requests
import json

# Load FVRL events configuration
with open("examples/fvrl_events_config.json", 'r') as f:
    config = json.load(f)

# Crawl events
response = requests.post(
    "http://localhost:8000/crawl",
    json={"config": config}
)

result = response.json()["result"]
print(f"Found {result['total_items']} events")

# Show sample event
if result["data"]:
    event = result["data"][0]
    print(f"Event: {event['title']}")
    print(f"Date: {event['date_time']}")
    print(f"Location: {event['location']}")
```

To run the complete FVRL example:
```bash
python fvrl_complete_example.py
```
