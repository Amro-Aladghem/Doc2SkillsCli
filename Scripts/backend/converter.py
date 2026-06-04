"""
Main converter module with both approaches:
1. Full documentation conversion (all pages)
2. Single page conversion (user-specified URL)

Supports asynchronous processing for improved performance
"""
import time
import asyncio
from typing import Optional, List, Dict
from concurrent.futures import ThreadPoolExecutor
from .config import ConverterConfig
from .utils import BrowserManager, ContentProcessor, FileManager
from ..backend.models import SkillData

#(Changing here)  just keep single converter
class DocumentationConverter:
    """
    Unified converter for documentation to markdown skills
    Supports both full documentation and single page conversion
    """
    
    def __init__(self, config: Optional[ConverterConfig] = None):
        self.config = config or ConverterConfig()
        self.browser_manager = BrowserManager(self.config)
        self.content_processor = ContentProcessor(self.config)
        self.file_manager = FileManager(self.config)
        
    def convert_single_page(self, page_url: str, output_dir: Optional[str] = None, 
                           custom_title: Optional[str] = None) -> Dict[str, any]:
        """
        Convert a single documentation page to markdown
        
        Args:
            page_url: URL of the specific page to convert
            output_dir: Optional custom output directory name
            custom_title: Optional custom title for the page
            
        Returns:
            Dictionary with conversion result
        """
        result = {
            'success': False,
            'url': page_url,
            'title': custom_title or 'Untitled',
            'output_file': '',
            'output_directory': ''
        }
        
        try:
            # Setup output directory
            
            print(f"[*] Starting Single Page Conversion")
            print(f"[*] Source: {page_url}")
            
            with self.browser_manager as browser:
                page_result = self._process_single_page(
                    browser=browser,
                    url=page_url,
                    title=custom_title,
                    output_dir=output_dir,
                    extract_title=custom_title is None
                )
                
                result.update(page_result)
            
            if result['success']:
                print(f"\n[✓] Single Page Conversion Complete!")
            
        except Exception as e:
            print(f"\n[✗] Conversion failed: {str(e)}")
            result['error'] = str(e)
        
        return result
    
    
    def _process_single_page(self, browser: BrowserManager, url: str,
                            title: Optional[str], output_dir: str,
                            page_num: Optional[int] = None,
                            total_pages: Optional[int] = None,
                            extract_title: bool = False) -> Dict[str, any]:
        """
        Internal method to process a single page
        Shared by both conversion approaches
        
        Args:
            browser: BrowserManager instance
            url: Page URL
            title: Page title (or None to extract from page)
            output_dir: Output directory path
            page_num: Current page number (for progress display)
            total_pages: Total number of pages (for progress display)
            extract_title: Whether to extract title from page content
            
        Returns:
            Dictionary with page processing result
        """
        result = {
            'success': False,
            'url': url,
            'title': title or 'Untitled',
            'output_file': ''
        }
        
        try:
            # Display progress
            if page_num and total_pages:
                print(f"[{page_num}/{total_pages}] Processing: {result['title']}")
            else:
                print(f"[*] Processing: {url}")
            
            # Load the page
            browser.load_page(url, wait_time=2.0)
            
            # Get page content
            html_content = browser.get_page_source()

            # Convert to markdown
            markdown_content = self.content_processor.convert_to_markdown(html_content)
            
            skill_data : SkillData = self.content_processor.get_skill_metedata_with_ai(markdown_content)

            # Format the document with metadata
            formatted_content = self.content_processor.format_markdown_document(
                skill_data,
                content=markdown_content
            )
            
            # Save to file
            
            output_file = self.file_manager.save_markdown_file(
                output_dir,
                formatted_content,
                safe_filename=skill_data.file_name,
            )
            
            result['output_file'] = output_file
            result['success'] = True
            
        except Exception as e:
            print(f"    [✗] Failed: {str(e)}")
            result['error'] = str(e)
        
        return result



def convert_single_page(page_url: str, config: Optional[ConverterConfig] = None,
                       output_dir: Optional[str] = None,
                       title: Optional[str] = None) -> Dict[str, any]:
    """
    Convert a single documentation page to markdown
    
    Args:
        page_url: URL of the specific page to convert
        config: Optional ConverterConfig instance
        output_dir: Optional custom output directory name
        title: Optional custom title for the page
        
    Returns:
        Dictionary with conversion result
    """
    converter = DocumentationConverter(config)
    return converter.convert_single_page(page_url, output_dir, title)

