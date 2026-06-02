"""
Doc2Skills Backend - Documentation to Markdown Converter
Converts HTML documentation to structured markdown skill files
"""
from .config import ConverterConfig
from .converter import (
    DocumentationConverter,
    convert_full_documentation,
    convert_single_page
)

__version__ = "1.0.0"
__all__ = [
    'ConverterConfig',
    'DocumentationConverter',
    'convert_full_documentation',
    'convert_single_page'
]

