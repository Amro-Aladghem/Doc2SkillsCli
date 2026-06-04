"""
Content processing utilities
Shared functions for HTML parsing and markdown conversion
"""
import re
from typing import List, Optional, Tuple
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from ..config import ConverterConfig
from .ai_skill_data_generator import AISkillDataGen
from ..models import SkillData


class ContentProcessor:
    """Handles HTML parsing and markdown conversion"""
    
    def __init__(self, config: ConverterConfig):
        self.config = config
    
    def parse_html(self, html_content: str) -> BeautifulSoup:
        """Parse HTML content into BeautifulSoup object"""
        return BeautifulSoup(html_content, 'html.parser')
    
    def cleanup_html(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Remove unwanted HTML elements (nav, footer, scripts, etc.)"""
        for tag in soup(self.config.cleanup_tags):
            tag.decompose()
        return soup
    
    def convert_to_markdown(self, html_content: str) -> str:
        """Convert HTML to markdown format"""
        soup = self.parse_html(html_content)
        soup = self.cleanup_html(soup)
        return md(str(soup), heading_style="ATX")
    
    def sanitize_filename(self, name: str, max_length: int = 100) -> str:
        """
        Convert a string into a safe filename with length limit
        
        Args:
            name: Original name to sanitize
            max_length: Maximum length for the filename (default: 100)
            
        Returns:
            Sanitized filename with length limit
        """
        # Remove special characters and replace spaces with underscores
        safe_name = re.sub(r'[^\w\s-]', '', name).strip()
        safe_name = safe_name.replace(" ", "_")
        
        # Truncate if too long, keeping the most important part (beginning)
        if len(safe_name) > max_length:
            safe_name = safe_name[:max_length].rstrip('_')
        
        return safe_name
    
    @staticmethod
    def get_skill_metedata_with_ai(doc_content_md:str) ->  SkillData:
        data = AISkillDataGen().get_gen_data(doc_content_md)
        return data

    def format_markdown_document(self,skill_data:SkillData, content: str) -> str:
        """
        Format the final markdown document following 
        
        Args:
            title: Page title
            description: Brief description (2 lines)
            content: Main markdown content
            
        Returns:
            Formatted markdown skill 
        """
        
        # Format YAML frontmatter skill format
        header = f"""---
            title: {skill_data.title}
            description: {skill_data.description}
---
"""
        
        # Combine header with content (instructions section)
        return f"{header}# \n\n{content}"

