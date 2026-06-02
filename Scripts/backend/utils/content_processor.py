"""
Content processing utilities
Shared functions for HTML parsing and markdown conversion
"""
import re
from typing import List, Optional, Tuple
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from ..config import ConverterConfig


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
    
    #here we must start using AI (Changing here) 
    def extract_description(self, html_content: str, page_title: str = "",
                          library_name: str = "", max_lines: int = 2) -> str:
        """
        Extract description with priority:
        1. Meta tags (most accurate)
        2. First meaningful paragraphs
        3. Dynamic fallback based on title and library
        
        Args:
            html_content: HTML content to extract from
            page_title: Page title for fallback description
            library_name: Library name for fallback description
            max_lines: Maximum number of paragraph lines to extract
            
        Returns:
            Description string
        """
        soup = self.parse_html(html_content)
        
        # Priority 1: Try to get description from Meta Tags (most accurate)
        meta_desc = soup.find('meta', attrs={'name': 'description'}) or \
                    soup.find('meta', attrs={'property': 'og:description'})
        
        if meta_desc and meta_desc.get('content'):
            desc = meta_desc['content'].strip()
            # Limit length if needed
            return (desc[:297] + "...") if len(desc) > 300 else desc
        
        # Priority 2: Extract from first meaningful paragraphs
        # Clean soup from code blocks and navigation
        temp_soup = self.parse_html(html_content)
        for code_tag in temp_soup(['code', 'pre', 'script', 'style', 'nav', 'header', 'footer']):
            code_tag.decompose()
        
        # Find main content area
        main_area = temp_soup.find(['main', 'article']) or temp_soup.body
        
        paragraphs = []
        if main_area:
            # Find first meaningful paragraphs (not code snippets or very short text)
            for p in main_area.find_all('p'):
                text = p.get_text(strip=True)
                # Skip code-like content, very short text, or navigation
                if (len(text) > 40 and
                    not text.startswith(('{', 'import', 'npm', 'const', 'function', 'class')) and
                    not any(skip in text.lower() for skip in ['menu', 'navigation', 'skip to', 'table of contents'])):
                    paragraphs.append(text)
                    if len(paragraphs) >= max_lines:
                        break
        
        if paragraphs:
            description = ' '.join(paragraphs)
            return (description[:297] + "...") if len(description) > 300 else description
        
        # Priority 3: Dynamic fallback description
        if page_title and library_name:
            return f"This skill provides comprehensive documentation for {page_title} in {library_name}. Use it when you need information related to {page_title.lower()}."
        elif library_name:
            return f"Comprehensive documentation and technical reference for {library_name}."
        else:
            return "Comprehensive documentation and technical reference for this skill."
    
    def extract_links_from_navigation(self, soup: BeautifulSoup, base_url: str) -> List[dict]:
        """
        Extract all links from navigation structure
        Returns list of dicts with 'url' and 'title' keys
        """
        from urllib.parse import urljoin
        
        links = []
        processed_urls = set()
        
        # Find all list items that might contain documentation links
        all_lis = soup.find_all('li')
        
        for li in all_lis:
            link_tag = li.find('a', href=True)
            if not link_tag:
                continue
            
            url = urljoin(base_url, link_tag['href'])
            title = link_tag.get_text(strip=True)
            
            # Skip invalid or duplicate links
            if not title or len(title) < 2 or url in processed_urls:
                continue
            
            processed_urls.add(url)
            links.append({
                'url': url,
                'title': title
            })
        
        return links
    
    def format_markdown_document(self, title: str, library: str, source_url: str,
                                description: str, content: str) -> str:
        """
        Format the final markdown document following Bob AI's SKILL.md format
        
        Args:
            title: Page title
            library: Library/package name
            source_url: Source URL of the page
            description: Brief description (2 lines)
            content: Main markdown content
            
        Returns:
            Formatted markdown following Bob AI skill format
        """
        # Create skill name with library
        skill_name = f"{title} - {library}"
        
        # Format YAML frontmatter following Bob AI's skill format
        header = f"""---
name: {title}
description: {description}
library: {library}
source: {source_url}
---

"""
        
        # Combine header with content (instructions section)
        return f"{header}# {title}\n\n{content}"

