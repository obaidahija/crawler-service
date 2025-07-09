import asyncio
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from app.crawlers.base_crawler import BaseCrawler
from app.models.crawler_models import CrawlConfig, CrawlResult, SelectorConfig


class SeleniumCrawler(BaseCrawler):
    """Selenium-based crawler implementation"""
    
    def __init__(self, config: CrawlConfig):
        super().__init__(config)
        self.driver = None
        self._setup_driver()
    
    def _setup_driver(self):
        """Setup Chrome WebDriver with options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.set_page_load_timeout(self.config.wait_config.page_load_timeout)
    
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
                
                # Navigate to page
                self.driver.get(current_url)
                await asyncio.sleep(self.config.wait_config.delay_between_requests)
                
                if self.config.pagination and self.config.pagination.enabled:
                    next_url = await self.get_next_page_url(current_url)
                    if next_url and next_url != current_url:
                        result.next_page_url = next_url
 
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
                else:
                    # Single page crawling
                    page_data = await self.extract_data_from_page(current_url)
                    if page_data:
                        result.data.append(page_data)
                

                
                # Check for next page
                if self.config.pagination and self.config.pagination.enabled:
                    if result.next_page_url and result.next_page_url != current_url:
                        current_url = result.next_page_url
                        page_count += 1
                    else:
                        result.next_page_url = None
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
        
        # Navigate to the page if not already there
        if self.driver.current_url != url:
            self.driver.get(url)
            await asyncio.sleep(self.config.wait_config.delay_between_requests)
        
        for extractor in self.config.extractors:
            try:
                value = await self._extract_field(extractor.selector_config)
                if value is not None:
                    data[extractor.field_name] = value
            except Exception as e:
                print(f"Error extracting field {extractor.field_name}: {str(e)}")
                continue
        
        return data
    
    async def get_list_items(self, url: str) -> List[str]:
        """Get list of URLs for detail pages"""
        if not self.config.navigation:
            return []
        
        # Navigate to page if not already there
        if self.driver.current_url != url:
            self.driver.get(url)
            await asyncio.sleep(self.config.wait_config.delay_between_requests)
        
        urls = []
        
        try:
            # Wait for list items to load
            wait = WebDriverWait(self.driver, self.config.wait_config.element_wait_timeout)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.config.navigation.list_items_selector)))
            
            # Find all list items
            list_elements = self.driver.find_elements(By.CSS_SELECTOR, self.config.navigation.list_items_selector)
            
            for element in list_elements:
                try:
                    if self.config.navigation.detail_link_selector:
                        # Find link within the list item
                        link_element = element.find_element(By.CSS_SELECTOR, self.config.navigation.detail_link_selector)
                    else:
                        # Use the list item itself as the link
                        link_element = element
                    
                    link_url = link_element.get_attribute(self.config.navigation.detail_link_attribute)
                    if link_url:
                        # Convert relative URLs to absolute
                        absolute_url = urljoin(url, link_url)
                        urls.append(absolute_url)
                        
                except NoSuchElementException:
                    continue
                    
        except TimeoutException:
            print(f"Timeout waiting for list items: {self.config.navigation.list_items_selector}")
        
        return urls
    
    async def get_next_page_url(self, current_url: str) -> Optional[str]:
        """Get the URL of the next page for pagination"""
        if not self.config.pagination or not self.config.pagination.enabled:
            return None
        
        try:
            next_link = self.driver.find_element(By.CSS_SELECTOR, self.config.pagination.next_page_selector)
            next_url = next_link.get_attribute(self.config.pagination.next_page_attribute)
            
            if next_url:
                return urljoin(current_url, next_url)
                
        except NoSuchElementException:
            print("Next page link not found")
        
        return None
    
    async def _extract_field(self, selector_config: SelectorConfig) -> Any:
        """Extract a field value using the selector configuration"""
        try:
            if selector_config.multiple:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector_config.selector)
                values = []
                for element in elements:
                    value = self._get_element_value(element, selector_config.attribute)
                    if value:
                        values.append(value)
                return values
            else:
                element = self.driver.find_element(By.CSS_SELECTOR, selector_config.selector)
                return self._get_element_value(element, selector_config.attribute)
                
        except NoSuchElementException:
            return None
    
    def _get_element_value(self, element, attribute: Optional[str]) -> str:
        """Get value from element based on attribute"""
        if attribute is None or attribute == "text":
            return element.text.strip()
        elif attribute == "html":
            return element.get_attribute("innerHTML")
        else:
            return element.get_attribute(attribute)
    
    async def cleanup(self):
        """Cleanup WebDriver resources"""
        if self.driver:
            self.driver.quit()
            self.driver = None
