"""
File management utilities
Shared functions for file operations
"""
import os
from typing import Optional
from urllib.parse import urlparse
from ..config import ConverterConfig
from pathlib import Path

#(Changing here)  the files must not generated like this , it must be from config URI .
class FileManager:
    """Manages file operations for saving converted documentation"""
    
    def __init__(self, config: ConverterConfig):
        self.config = config
        
    def extract_library_name(self, url: str) -> str:
        """
        Extract library/package name from URL for metadata
        Returns capitalized library name (e.g., 'React', 'I18next')
        """
        domain = self.extract_domain_from_url(url)
        # Capitalize first letter of each word
        return domain.replace('_', ' ').title().replace(' ', '')
    

    
    def save_markdown_file(self, directory: str, filename: str, content: str) -> str:
        """
        Save markdown content to a file
        Returns the full path of the saved file
        """
        # check and get the file full path for saving 
        filepath = self.prepare_output_file_path(directory,filename)
                
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
    
    def prepare_output_file_path(self,directory:str,filename:str)->str:
        """
        Returns the full path and check
        """
        path = Path(directory).expanduser().resolve()

        if path.exists() and path.is_file():
            raise ValueError("Output path must be a directory.")
        
        path.mkdir(parents=True, exist_ok=True)

        file_path = path / f"{filename}.md"
        return str(file_path)

