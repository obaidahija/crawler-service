import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup, Tag
import time

from app.crawlers.base_crawler import BaseCrawler
from app.models.crawler_models import CrawlConfig, CrawlResult, SelectorConfig


class BeautifulSoupCrawler(BaseCrawler):
    """BeautifulSoup-based crawler implementation"""
    
    def __init__(self, config: CrawlConfig):
        super().__init__(config)
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            timeout = aiohttp.ClientTimeout(total=self.config.wait_config.page_load_timeout)
            self.session = aiohttp.ClientSession(headers=headers, timeout=timeout)
        return self.session
    
    async def crawl(self) -> CrawlResult:
        """Main crawl method"""
        result = CrawlResult(
            success=False,
            data=[],
            context=self.config.context.copy()
        )
        
        try:
            current_url = self.config.start_url
            page_count = 0
            max_pages = self.config.pagination.max_pages if self.config.pagination else 1
            
            while current_url and (max_pages is None or page_count < max_pages):
                print(f"Crawling page {page_count + 1}: {current_url}")
                
                if self.config.navigation:
                    # List-based crawling
                    list_items = await self.get_list_items(current_url)
                    print(f"Found {len(list_items)} items on page")
                    
                    for item_url in list_items:
                        try:
                            item_data = await self.extract_data_from_page(item_url)
                            if item_data:
                                result.data.append(item_data)
                        except Exception as e:
                            result.errors.append(f"Error extracting from {item_url}: {str(e)}")
                        
                        # Delay between requests
                        await asyncio.sleep(self.config.wait_config.delay_between_requests)
                else:
                    # Single page crawling
                    page_data = await self.extract_data_from_page(current_url)
                    if page_data:
                        result.data.append(page_data)
                
                # Check for next page
                if self.config.pagination and self.config.pagination.enabled:
                    next_url = await self.get_next_page_url(current_url)
                    if next_url and next_url != current_url:
                        result.next_page_url = next_url
                        current_url = next_url
                        page_count += 1
                    else:
                        break
                else:
                    break
            
            result.total_items = len(result.data)
            result.success = True
            
        except Exception as e:
            result.errors.append(f"Crawl failed: {str(e)}")
        
        return result
    
    async def extract_data_from_page(self, url: str) -> Dict[str, Any]:
        """Extract data from a single page using configured extractors"""
        data = {}
        
        try:
            soup = await self._get_soup(url)
            
            for extractor in self.config.extractors:
                try:
                    value = await self._extract_field(soup, extractor.selector_config)
                    if value is not None:
                        data[extractor.field_name] = value
                except Exception as e:
                    print(f"Error extracting field {extractor.field_name}: {str(e)}")
                    continue
            
        except Exception as e:
            print(f"Error loading page {url}: {str(e)}")
        
        return data
    
    async def get_list_items(self, url: str) -> List[str]:
        """Get list of URLs for detail pages"""
        if not self.config.navigation:
            return []
        
        urls = []
        
        try:
            soup = await self._get_soup(url)
            
            # Find all list items
            list_elements = soup.select(self.config.navigation.list_items_selector)
            
            for element in list_elements:
                try:
                    if self.config.navigation.detail_link_selector:
                        # Find link within the list item
                        link_element = element.select_one(self.config.navigation.detail_link_selector)
                    else:
                        # Use the list item itself as the link
                        link_element = element
                    
                    if link_element:
                        link_url = link_element.get(self.config.navigation.detail_link_attribute)
                        if link_url:
                            # Convert relative URLs to absolute
                            absolute_url = urljoin(url, link_url)
                            urls.append(absolute_url)
                            
                except Exception as e:
                    print(f"Error processing list item: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Error getting list items from {url}: {str(e)}")
        
        return urls
    
    async def get_next_page_url(self, current_url: str) -> Optional[str]:
        """Get the URL of the next page for pagination"""
        if not self.config.pagination or not self.config.pagination.enabled:
            return None
        
        try:
            soup = await self._get_soup(current_url)
            next_link = soup.select_one(self.config.pagination.next_page_selector)
            
            if next_link:
                next_url = next_link.get(self.config.pagination.next_page_attribute)
                if next_url:
                    return urljoin(current_url, next_url)
                    
        except Exception as e:
            print(f"Error getting next page URL: {str(e)}")
        
        return None
    
    async def _get_soup(self, url: str) -> BeautifulSoup:
        """Get BeautifulSoup object for URL"""
        session = await self._get_session()
        
        async with session.get(url) as response:
            if response.status == 200:
                html = await response.text()
                return BeautifulSoup(html, 'lxml')
            else:
                raise Exception(f"HTTP {response.status} for {url}")
    
    async def _extract_field(self, soup: BeautifulSoup, selector_config: SelectorConfig) -> Any:
        """Extract a field value using the selector configuration"""
        try:
            if selector_config.multiple:
                elements = soup.select(selector_config.selector)
                values = []
                for element in elements:
                    value = self._get_element_value(element, selector_config.attribute)
                    if value:
                        values.append(value)
                return values
            else:
                element = soup.select_one(selector_config.selector)
                if element:
                    return self._get_element_value(element, selector_config.attribute)
                    
        except Exception as e:
            print(f"Error extracting with selector {selector_config.selector}: {str(e)}")
            return None
    
    def _get_element_value(self, element: Tag, attribute: Optional[str]) -> str:
        """Get value from element based on attribute"""
        if attribute is None or attribute == "text":
            return element.get_text(strip=True)
        elif attribute == "html":
            return str(element)
        else:
            return element.get(attribute, "")
    
    async def cleanup(self):
        """Cleanup session resources"""
        if self.session:
            await self.session.close()
            self.session = None
