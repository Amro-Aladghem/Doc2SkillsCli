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
    
    #(Changing here) delete docker usage
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
        
        # Use installed ChromeDriver in Docker, fallback to webdriver_manager for local development
        chromedriver_path = "/usr/local/bin/chromedriver"
        if os.path.exists(chromedriver_path):
            # Running in Docker - use installed ChromeDriver
            service = Service(chromedriver_path)
            print(f"[*] Using ChromeDriver from: {chromedriver_path}")
        else:
            # Local development - use webdriver_manager
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                print("[*] Using ChromeDriver from webdriver_manager")
            except ImportError:
                raise RuntimeError(
                    "ChromeDriver not found. Either run in Docker or install webdriver-manager: "
                    "pip install webdriver-manager"
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
    
    def expand_navigation(self) -> None:
        """
        Heuristic auto-expansion of navigation menus
        Shared function for discovering all documentation pages
        
        NOTE: Currently disabled for faster processing.
        Uncomment the code below to enable deep navigation scanning.
        """
        # COMMENTED OUT: Heuristic expansion disabled for performance
        # Uncomment below to enable deep navigation scanning
        
        # print("[*] Running Heuristic Expansion (Deep Scan)...")
        #
        # for level in range(self.config.max_expansion_levels):
        #     potential_toggles = self.driver.find_elements(By.CSS_SELECTOR, "div, span, button, svg, i")
        #     clicked_any = False
        #
        #     for element in potential_toggles:
        #         try:
        #             aria_state = element.get_attribute("aria-expanded")
        #             class_name = element.get_attribute("class") or ""
        #
        #             # Check if element should be expanded
        #             should_click = (
        #                 (aria_state == "false") or
        #                 any(marker in class_name.lower() for marker in self.config.expansion_markers)
        #             )
        #
        #             # Skip already expanded elements
        #             if aria_state == "true":
        #                 continue
        #
        #             if should_click and element.is_displayed():
        #                 self.driver.execute_script("arguments[0].click();", element)
        #                 clicked_any = True
        #         except Exception:
        #             continue
        #
        #     if not clicked_any:
        #         break
        #
        #     print(f"    [+] Level {level + 1} expanded.")
        #     time.sleep(self.config.expansion_wait_time)
        
        pass  # Expansion disabled
    
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

