from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.models.crawler_models import CrawlConfig, CrawlResult


class BaseCrawler(ABC):
    """Base class for all crawler implementations"""
    
    def __init__(self, config: CrawlConfig):
        self.config = config
    
    @abstractmethod
    async def crawl(self) -> CrawlResult:
        """
        Main crawl method that should be implemented by each crawler
        
        Returns:
            CrawlResult: The result of the crawl operation
        """
        pass
    
    @abstractmethod
    async def extract_data_from_page(self, url: str) -> Dict[str, Any]:
        """
        Extract data from a single page
        
        Args:
            url: URL of the page to extract data from
            
        Returns:
            Dict containing extracted data
        """
        pass
    
    @abstractmethod
    async def get_list_items(self, url: str) -> List[str]:
        """
        Get list of URLs for detail pages
        
        Args:
            url: URL of the page containing the list
            
        Returns:
            List of URLs for detail pages
        """
        pass
    
    @abstractmethod
    async def get_next_page_url(self, current_url: str) -> Optional[str]:
        """
        Get the URL of the next page for pagination
        
        Args:
            current_url: Current page URL
            
        Returns:
            URL of next page or None if no next page
        """
        pass
    
    @abstractmethod
    async def cleanup(self):
        """
        Cleanup resources (close browser, etc.)
        """
        pass
