"""
File management utilities
Shared functions for file operations
"""
import os
from typing import Optional
from urllib.parse import urlparse
from ..config import ConverterConfig
from pathlib import Path
from platformdirs import user_config_dir
import json
from ..models.Config import Config

#(Changing here)  the files must not generated like this , it must be from config URI .
class FileManager:
    """Manages files operations """
    
    def __init__(self, config: Optional[ConverterConfig] = None):
        self.config = config or ConverterConfig()
        
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
    
    def prepare_default_configfile(self)->bool:
        config = {
            "api_key": ConverterConfig.default_api_key,
            "model": ConverterConfig.default_model,
            "max_content_size": ConverterConfig.default_max_content_size
        }

        config_dir = Path(user_config_dir("DocToSkill"))

        config_dir.mkdir(parents=True, exist_ok=True)

        config_file = config_dir / "config.json"

        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

        return True
    
    def update_file_api_key(self,api_key:str):
        with open(self.config.config_file_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        config["api_key"] = api_key

        with open(self.config.config_file_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

    def load_config(self)-> Config:
        with open(self.config.config_file_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        return Config(**config)
    
    def config_file_exist(self) -> bool:
        path = Path(self.config.config_file_path)
        return path.exists() and path.is_file()

        

    
    



