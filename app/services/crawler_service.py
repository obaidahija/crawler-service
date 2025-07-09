import asyncio
from typing import Dict, Any
from app.models.crawler_models import CrawlConfig, CrawlResult
from app.crawlers.crawler_factory import CrawlerFactory


class CrawlerService:
    """Service class for handling crawl operations"""
    
    async def crawl(self, config: CrawlConfig) -> CrawlResult:
        """
        Execute a crawl operation based on the provided configuration
        
        Args:
            config: Crawl configuration
            
        Returns:
            CrawlResult: Result of the crawl operation
        """
        crawler = None
        
        try:
            # Create crawler instance
            crawler = CrawlerFactory.create_crawler(config)
            
            # Execute crawl
            result = await crawler.crawl()
            
            return result
            
        except Exception as e:
            # Return error result
            return CrawlResult(
                success=False,
                data=[],
                errors=[f"Crawl service error: {str(e)}"],
                context=config.context
            )
        
        finally:
            # Always cleanup resources
            if crawler:
                await crawler.cleanup()
    
    def validate_config(self, config: CrawlConfig) -> Dict[str, Any]:
        """
        Validate crawl configuration
        
        Args:
            config: Configuration to validate
            
        Returns:
            Dict containing validation result
        """
        errors = []
        warnings = []
        
        # Check required fields
        if not config.start_url:
            errors.append("start_url is required")
        
        if not config.extractors:
            errors.append("At least one extractor is required")
        
        # Validate extractors
        for i, extractor in enumerate(config.extractors):
            if not extractor.field_name:
                errors.append(f"Extractor {i}: field_name is required")
            
            if not extractor.selector_config.selector:
                errors.append(f"Extractor {i}: selector is required")
        
        # Validate navigation config
        if config.navigation:
            if not config.navigation.list_items_selector:
                errors.append("Navigation config: list_items_selector is required")
        
        # Validate pagination config
        if config.pagination and config.pagination.enabled:
            if not config.pagination.next_page_selector:
                errors.append("Pagination config: next_page_selector is required when pagination is enabled")
            
            if config.pagination.max_pages is not None and config.pagination.max_pages <= 0:
                errors.append("Pagination config: max_pages must be greater than 0")
        
        # Warnings
        if config.engine.value == "selenium" and config.wait_config.delay_between_requests < 1.0:
            warnings.append("Consider increasing delay_between_requests for Selenium to avoid being blocked")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def get_supported_engines(self) -> list:
        """Get list of supported crawler engines"""
        return CrawlerFactory.get_supported_engines()
