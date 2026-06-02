"""
File management utilities
Shared functions for file operations
"""
import os
from typing import Optional
from urllib.parse import urlparse
from ..config import ConverterConfig

#(Changing here)  the files must not generated like this , it must be from config URI .
class FileManager:
    """Manages file operations for saving converted documentation"""
    
    def __init__(self, config: ConverterConfig):
        self.config = config
    
    def extract_domain_from_url(self, url: str) -> str:
        """Extract domain name from URL for directory naming"""
        parsed = urlparse(url)
        # Try to get the main domain (e.g., 'i18next' from 'www.i18next.com')
        domain_parts = parsed.netloc.split('.')
        
        # Handle different domain formats
        if len(domain_parts) >= 2:
            # If it's like www.example.com, take 'example'
            # If it's like example.com, take 'example'
            return domain_parts[-2] if domain_parts[0] == 'www' else domain_parts[0]
        
        return parsed.netloc.replace('.', '_')
    
    def extract_library_name(self, url: str) -> str:
        """
        Extract library/package name from URL for metadata
        Returns capitalized library name (e.g., 'React', 'I18next')
        """
        domain = self.extract_domain_from_url(url)
        # Capitalize first letter of each word
        return domain.replace('_', ' ').title().replace(' ', '')
    
    def ensure_directory(self, path: str) -> str:
        """Create directory if it doesn't exist and return the path"""
        os.makedirs(path, exist_ok=True)
        return path
    
    def save_markdown_file(self, directory: str, filename: str, content: str) -> str:
        """
        Save markdown content to a file
        Returns the full path of the saved file
        """
        # Ensure the filename has .md extension
        if not filename.endswith('.md'):
            filename = f"{filename}.md"
        
        filepath = os.path.join(directory, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
    
    def get_output_directory(self, base_url: str, custom_dir: Optional[str] = None) -> str:
        """
        Get the output directory for a documentation source
        If custom_dir is provided, use it; otherwise, extract from URL
        """
        if custom_dir:
            output_dir = os.path.join(self.config.output_base_dir, custom_dir)
        else:
            domain = self.extract_domain_from_url(base_url)
            output_dir = self.config.get_output_dir(domain)
        
        return self.ensure_directory(output_dir)
