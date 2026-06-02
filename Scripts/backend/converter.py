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
    
    def _clean_github_title(self, title: str, url: str) -> str:
        """
        Clean GitHub page titles to extract just the repo name
        
        GitHub titles follow the pattern: "GitHub - owner/repo: description"
        This extracts just "owner/repo" for cleaner filenames
        
        Args:
            title: Original page title
            url: Page URL to check if it's from GitHub
            
        Returns:
            Cleaned title (repo name for GitHub, original for others)
        """
        from urllib.parse import urlparse
        
        # Check if this is a GitHub URL
        parsed = urlparse(url)
        if 'github.com' not in parsed.netloc.lower():
            return title
        
        # GitHub title pattern: "GitHub - owner/repo: description · GitHub"
        # Extract just "owner/repo"
        if ':' in title:
            # Split at the first colon
            before_colon = title.split(':', 1)[0].strip()
            
            # Remove "GitHub - " prefix if present
            if before_colon.startswith('GitHub - '):
                repo_name = before_colon.replace('GitHub - ', '', 1).strip()
                return repo_name
        
        # If pattern doesn't match, return original title
        return title
    
    def convert_full_documentation(self, doc_url: str, output_dir: Optional[str] = None, max_pages: Optional[int] = None) -> Dict[str, any]:
        """
        Convert entire documentation site to markdown files
        
        Args:
            doc_url: Base URL of the documentation
            output_dir: Optional custom output directory name
            max_pages: Optional maximum number of pages to process (useful for API limits)
            
        Returns:
            Dictionary with conversion results and statistics
        """
        results = {
            'success': False,
            'total_pages': 0,
            'successful': 0,
            'failed': 0,
            'output_directory': '',
            'pages': []
        }
        
        try:
            # Setup output directory
            output_path = self.file_manager.get_output_directory(doc_url, output_dir)
            results['output_directory'] = output_path
            
            print(f"[*] Starting Full Documentation Conversion")
            print(f"[*] Source: {doc_url}")
            print(f"[*] Output: {output_path}")
            
            with self.browser_manager as browser:
                # Load the main documentation page
                browser.load_page(doc_url)
                
                # Expand all navigation menus to discover all pages
                # COMMENTED OUT: Heuristic expansion disabled for faster processing
                # browser.expand_navigation()
                
                # Extract all documentation links
                html_content = browser.get_page_source()
                soup = self.content_processor.parse_html(html_content)
                links = self.content_processor.extract_links_from_navigation(soup, doc_url)
                
                # Apply max_pages limit if specified
                if max_pages is not None and len(links) > max_pages:
                    print(f"[*] Found {len(links)} documentation pages, limiting to {max_pages} pages")
                    links = links[:max_pages]
                else:
                    print(f"[*] Found {len(links)} documentation pages")
                
                results['total_pages'] = len(links)
                
                # Process pages in parallel batches for maximum speed
                batch_size = 1
                print(f"[*] Processing in parallel batches of {batch_size} pages")
                
                for batch_start in range(0, len(links), batch_size):
                    batch_end = min(batch_start + batch_size, len(links))
                    batch = links[batch_start:batch_end]
                    
                    print(f"[*] Processing batch {batch_start//batch_size + 1} ({batch_start + 1}-{batch_end} of {len(links)}) in parallel...")
                    
                    # Process batch in parallel using ThreadPoolExecutor
                    batch_results = self._process_batch_parallel(
                        batch=batch,
                        output_dir=output_path,
                        batch_start=batch_start,
                        total_pages=len(links)
                    )
                    
                    # Collect results
                    for page_result in batch_results:
                        results['pages'].append(page_result)
                        if page_result['success']:
                            results['successful'] += 1
                        else:
                            results['failed'] += 1
                    
                    print(f"    [+] Batch complete: {len([r for r in batch_results if r['success']])}/{len(batch_results)} successful")
                    
                    # Brief pause between batches
                    if batch_end < len(links):
                        time.sleep(1)
            
            results['success'] = True
            print(f"\n[✓] Full Documentation Conversion Complete!")
            print(f"[✓] Successfully converted: {results['successful']}/{results['total_pages']} pages")
            print(f"[✓] Output directory: {output_path}")
            
        except Exception as e:
            print(f"\n[✗] Conversion failed: {str(e)}")
            results['error'] = str(e)
        
        return results
    
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
            output_path = self.file_manager.get_output_directory(page_url, output_dir)
            result['output_directory'] = output_path
            
            print(f"[*] Starting Single Page Conversion")
            print(f"[*] Source: {page_url}")
            print(f"[*] Output: {output_path}")
            
            with self.browser_manager as browser:
                page_result = self._process_single_page(
                    browser=browser,
                    url=page_url,
                    title=custom_title,
                    output_dir=output_path,
                    extract_title=custom_title is None
                )
                
                result.update(page_result)
            
            if result['success']:
                print(f"\n[✓] Single Page Conversion Complete!")
                print(f"[✓] Output file: {result['output_file']}")
            
        except Exception as e:
            print(f"\n[✗] Conversion failed: {str(e)}")
            result['error'] = str(e)
        
        return result
    
    def _process_batch_parallel(self, batch: List[dict], output_dir: str,
                               batch_start: int, total_pages: int) -> List[Dict[str, any]]:
        """
        Process a batch of pages in parallel using multiple browser instances
        
        Args:
            batch: List of link dictionaries with 'url' and 'title'
            output_dir: Output directory path
            batch_start: Starting index for this batch
            total_pages: Total number of pages being processed
            
        Returns:
            List of result dictionaries for each page
        """
        def process_page_worker(link_info: dict, idx: int) -> Dict[str, any]:
            """Worker function to process a single page with its own browser"""
            # Create a new browser instance for this thread
            browser_manager = BrowserManager(self.config)
            
            try:
                with browser_manager as browser:
                    return self._process_single_page(
                        browser=browser,
                        url=link_info['url'],
                        title=link_info['title'],
                        output_dir=output_dir,
                        page_num=idx,
                        total_pages=total_pages
                    )
            except Exception as e:
                return {
                    'success': False,
                    'url': link_info['url'],
                    'title': link_info['title'],
                    'output_file': '',
                    'error': str(e)
                }
        
        # Process batch in parallel using ThreadPoolExecutor
        results = []
        with ThreadPoolExecutor(max_workers=len(batch)) as executor:
            # Submit all tasks
            futures = []
            for i, link_info in enumerate(batch):
                idx = batch_start + i + 1
                future = executor.submit(process_page_worker, link_info, idx)
                futures.append(future)
            
            # Collect results as they complete
            for future in futures:
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({
                        'success': False,
                        'url': 'unknown',
                        'title': 'unknown',
                        'output_file': '',
                        'error': str(e)
                    })
        
        return results
    
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
            
            # Extract title if needed
            if extract_title:
                soup = self.content_processor.parse_html(html_content)
                title_tag = soup.find('title') or soup.find('h1')
                if title_tag:
                    result['title'] = title_tag.get_text(strip=True)
                    # Clean GitHub titles to extract just the repo name
                    result['title'] = self._clean_github_title(result['title'], url)
            
            # Extract library name from URL
            library_name = self.file_manager.extract_library_name(url)
            
            # Extract description with page title and library context
            description = self.content_processor.extract_description(
                html_content=html_content,
                page_title=result['title'],
                library_name=library_name,
                max_lines=2
            )
            
            # Convert to markdown
            markdown_content = self.content_processor.convert_to_markdown(html_content)
            
            # Format the document with metadata
            formatted_content = self.content_processor.format_markdown_document(
                title=result['title'],
                library=library_name,
                source_url=url,
                description=description,
                content=markdown_content
            )
            
            # Save to file
            safe_filename = self.content_processor.sanitize_filename(result['title'])
            output_file = self.file_manager.save_markdown_file(
                output_dir,
                safe_filename,
                formatted_content
            )
            
            result['output_file'] = output_file
            result['success'] = True
            
        except Exception as e:
            print(f"    [✗] Failed: {str(e)}")
            result['error'] = str(e)
        
        return result


# Convenience functions for direct usage
def convert_full_documentation(doc_url: str, config: Optional[ConverterConfig] = None,
                               output_dir: Optional[str] = None) -> Dict[str, any]:
    """
    Convert entire documentation site to markdown files
    
    Args:
        doc_url: Base URL of the documentation
        config: Optional ConverterConfig instance
        output_dir: Optional custom output directory name
        
    Returns:
        Dictionary with conversion results
    """
    converter = DocumentationConverter(config)
    return converter.convert_full_documentation(doc_url, output_dir)


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

