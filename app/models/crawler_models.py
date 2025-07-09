from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum


class CrawlerEngine(str, Enum):
    SELENIUM = "selenium"
    BEAUTIFULSOUP = "beautifulsoup"


class SelectorConfig(BaseModel):
    selector: str = Field(..., description="CSS selector or XPath")
    attribute: Optional[str] = Field(None, description="Attribute to extract (text, href, src, etc.)")
    multiple: bool = Field(False, description="Whether to extract multiple elements")


class ExtractorConfig(BaseModel):
    field_name: str = Field(..., description="Name of the field in output")
    selector_config: SelectorConfig = Field(..., description="Selector configuration")
    post_process: Optional[str] = Field(None, description="Post-processing function name")


class NavigationConfig(BaseModel):
    list_items_selector: str = Field(..., description="Selector for list items")
    detail_link_selector: Optional[str] = Field(None, description="Selector for detail page link within list item")
    detail_link_attribute: str = Field("href", description="Attribute containing the detail link")


class PaginationConfig(BaseModel):
    enabled: bool = Field(False, description="Whether pagination is enabled")
    next_page_selector: Optional[str] = Field(None, description="Selector for next page link")
    next_page_attribute: str = Field("href", description="Attribute containing next page link")
    max_pages: Optional[int] = Field(None, description="Maximum number of pages to crawl")


class WaitConfig(BaseModel):
    page_load_timeout: int = Field(10, description="Page load timeout in seconds")
    element_wait_timeout: int = Field(5, description="Element wait timeout in seconds")
    delay_between_requests: float = Field(1.0, description="Delay between requests in seconds")


class CrawlConfig(BaseModel):
    start_url: str = Field(..., description="Starting URL to crawl")
    engine: CrawlerEngine = Field(CrawlerEngine.SELENIUM, description="Crawler engine to use")
    navigation: Optional[NavigationConfig] = Field(None, description="Navigation configuration for list crawling")
    extractors: List[ExtractorConfig] = Field(..., description="List of field extractors")
    pagination: Optional[PaginationConfig] = Field(None, description="Pagination configuration")
    wait_config: WaitConfig = Field(default_factory=WaitConfig, description="Wait and timeout configuration")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context data")


class CrawlResult(BaseModel):
    success: bool = Field(..., description="Whether the crawl was successful")
    data: List[Dict[str, Any]] = Field(default_factory=list, description="Extracted data")
    next_page_url: Optional[str] = Field(None, description="URL of next page if pagination is enabled")
    total_items: int = Field(0, description="Total number of items extracted")
    context: Dict[str, Any] = Field(default_factory=dict, description="Updated context data")
    errors: List[str] = Field(default_factory=list, description="List of errors encountered")


class CrawlRequest(BaseModel):
    config: CrawlConfig = Field(..., description="Crawl configuration")


class CrawlResponse(BaseModel):
    result: CrawlResult = Field(..., description="Crawl result")
