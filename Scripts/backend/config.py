"""
Configuration module for Doc2Skills converter
"""
import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
from platformdirs import user_config_dir


@dataclass
class ConverterConfig:
    """Configuration for the documentation converter"""
    
    
    # Browser settings
    headless: bool = True
    window_size: str = "1920,1080"
    page_load_timeout: int = 30
    
    # Extraction settings
    output_base_dir: str = ""
    
    # HTML cleanup tags
    cleanup_tags: tuple = ('nav', 'footer', 'script', 'style', 'header', 'aside')
    
    default_api_key = ""
    default_max_content_size = 3500
    default_model="gemma-4-31b-it"

    config_dir = Path(user_config_dir("DocToSkill"))
    config_file_path = config_dir / "config.json"
    
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

