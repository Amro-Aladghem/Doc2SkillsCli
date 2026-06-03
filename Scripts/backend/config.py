"""
Configuration module for Doc2Skills converter
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ConverterConfig:
    """Configuration for the documentation converter"""
    
    
    # Browser settings
    headless: bool = True
    window_size: str = "1920,1080"
    page_load_timeout: int = 30
    
    # Extraction settings
    output_base_dir: str = ".bob/skills"
    
    # HTML cleanup tags
    cleanup_tags: tuple = ('nav', 'footer', 'script', 'style', 'header', 'aside')
    
    api_key = ""
    
    # Chrome driver settings
    chrome_driver_path: Optional[str] = None
    
    def get_output_dir(self, domain: str) -> str:
        """Get the output directory for a specific domain"""
        return os.path.join(self.output_base_dir, domain)
    
    def ensure_output_dir(self, domain: str) -> str:
        """Create and return the output directory"""
        output_dir = self.get_output_dir(domain)
        os.makedirs(output_dir, exist_ok=True)
        return output_dir

