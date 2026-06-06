"""
Browser utilities for web scraping
Shared functions for both full documentation and single page conversion
"""
import os
import time
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from ..config import ConverterConfig


class BrowserManager:
    """Manages browser instance and operations"""
    
    def __init__(self, config: ConverterConfig):
        self.config = config
        self.driver: Optional[webdriver.Chrome] = None
    
    
    def initialize_driver(self) -> webdriver.Chrome:
        """Initialize and return a Chrome WebDriver instance"""
        chrome_options = Options()
        
        if self.config.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument(f"--window-size={self.config.window_size}")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")


        try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                print("[*] Using ChromeDriver from webdriver_manager")
        except ImportError:
                raise RuntimeError(
                    "ChromeDriver not found. Either install webdriver-manager (pip install webdriver-manager) "
                    "or provide chromedriver in the container at /usr/local/bin/chromedriver"
                )
        
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.set_page_load_timeout(self.config.page_load_timeout)
        
        return self.driver
    
    def load_page(self, url: str, wait_time: Optional[float] = None) -> None:
        """Load a page and wait for it to render"""
        if not self.driver:
            raise RuntimeError("Driver not initialized. Call initialize_driver() first.")
        
        print(f"[*] Loading: {url}")
        self.driver.get(url)
        time.sleep(wait_time or self.config.initial_load_wait)
    
    
    def get_page_source(self) -> str:
        """Get the current page source"""
        if not self.driver:
            raise RuntimeError("Driver not initialized.")
        return self.driver.page_source
    
    def close(self) -> None:
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def __enter__(self):
        """Context manager entry"""
        self.initialize_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

