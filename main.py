from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.models.crawler_models import CrawlRequest, CrawlResponse, CrawlConfig
from app.services.crawler_service import CrawlerService


# Global service instance
crawler_service = CrawlerService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("Crawler service starting up...")
    yield
    # Shutdown
    print("Crawler service shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Web Crawler Service",
    description="A modular web crawler microservice with configurable extraction rules",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Web Crawler Service",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "crawl": "/crawl",
            "validate": "/validate",
            "engines": "/engines"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "crawler-service",
        "version": "1.0.0"
    }


@app.post("/crawl", response_model=CrawlResponse)
async def crawl_website(request: CrawlRequest):
    """
    Crawl a website based on the provided configuration
    
    Args:
        request: Crawl request containing configuration
        
    Returns:
        CrawlResponse: Result of the crawl operation
        
    Raises:
        HTTPException: If the request is invalid
    """
    try:
        # Validate configuration
        validation_result = crawler_service.validate_config(request.config)
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400, 
                detail={
                    "message": "Invalid configuration",
                    "errors": validation_result["errors"]
                }
            )
        
        # Execute crawl
        result = await crawler_service.crawl(request.config)
        
        return CrawlResponse(result=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/validate")
async def validate_config(config: CrawlConfig):
    """
    Validate a crawl configuration without executing it
    
    Args:
        config: Configuration to validate
        
    Returns:
        Validation result
    """
    try:
        result = crawler_service.validate_config(config)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")


@app.get("/engines")
async def get_supported_engines():
    """
    Get list of supported crawler engines
    
    Returns:
        List of supported engines
    """
    try:
        engines = crawler_service.get_supported_engines()
        return {
            "engines": engines,
            "default": "selenium"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting engines: {str(e)}")


if __name__ == "__main__":
    import os
    
    # Check if running in debug mode
    debug_mode = os.getenv("DEBUG", "false").lower() == "true"
    
    if debug_mode:
        # Debug mode - single worker, no reload
        print("🐛 Starting in DEBUG mode...")
        uvicorn.run(
            app,  # Pass app object directly for debugging
            host="0.0.0.0",
            port=8000,
            debug=True,
            reload=False  # Disable reload for debugging
        )
    else:
        # Normal mode
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True
        )
