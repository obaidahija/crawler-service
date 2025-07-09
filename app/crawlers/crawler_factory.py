from typing import List
from app.crawlers.base_crawler import BaseCrawler
from app.crawlers.selenium_crawler import SeleniumCrawler
from app.crawlers.beautifulsoup_crawler import BeautifulSoupCrawler
from app.models.crawler_models import CrawlConfig, CrawlerEngine


class CrawlerFactory:
    """Factory class for creating crawler instances"""
    
    @staticmethod
    def create_crawler(config: CrawlConfig) -> BaseCrawler:
        """
        Create a crawler instance based on the configuration
        
        Args:
            config: Crawl configuration
            
        Returns:
            BaseCrawler: Crawler instance
            
        Raises:
            ValueError: If crawler engine is not supported
        """
        if config.engine == CrawlerEngine.SELENIUM:
            return SeleniumCrawler(config)
        elif config.engine == CrawlerEngine.BEAUTIFULSOUP:
            return BeautifulSoupCrawler(config)
        else:
            raise ValueError(f"Unsupported crawler engine: {config.engine}")
    
    @staticmethod
    def get_supported_engines() -> List[str]:
        """Get list of supported crawler engines"""
        return [engine.value for engine in CrawlerEngine]
