#!/usr/bin/env python3
"""
Unit tests for document converter
"""

import pytest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.document_converter import DocumentConverter


class TestDocumentConverter:
    """Test cases for DocumentConverter"""

    @pytest.fixture
    def converter(self):
        """Create converter instance"""
        return DocumentConverter()

    def test_initialization(self, converter):
        """Test converter initialization"""
        assert converter is not None
        assert hasattr(converter, 'convert')
        assert hasattr(converter, 'batch_convert')

    def test_is_supported(self, converter):
        """Test format support detection"""
        # Office formats
        assert converter.is_supported(Path("test.docx"))
        assert converter.is_supported(Path("test.pptx"))
        assert converter.is_supported(Path("test.xlsx"))

        # Text formats
        assert converter.is_supported(Path("test.txt"))
        assert converter.is_supported(Path("test.md"))
        assert converter.is_supported(Path("test.csv"))

        # Unsupported
        assert not converter.is_supported(Path("test.pdf"))
        assert not converter.is_supported(Path("test.png"))
        assert not converter.is_supported(Path("test.unknown"))

    def test_needs_conversion(self, converter):
        """Test conversion necessity check"""
        # Needs conversion
        assert converter.needs_conversion(Path("test.docx"))
        assert converter.needs_conversion(Path("test.txt"))

        # No conversion needed
        assert not converter.needs_conversion(Path("test.pdf"))
        assert not converter.needs_conversion(Path("test.png"))
        assert not converter.needs_conversion(Path("test.jpg"))

    def test_office_formats(self, converter):
        """Test Office format recognition"""
        office_files = [
            "doc.docx", "doc.doc",
            "pres.pptx", "pres.ppt",
            "sheet.xlsx", "sheet.xls"
        ]
        for filename in office_files:
            assert Path(filename).suffix.lower() in converter.OFFICE_FORMATS

    def test_text_formats(self, converter):
        """Test text format recognition"""
        text_files = [
            "file.txt", "readme.md", "notes.markdown",
            "data.csv", "doc.rtf"
        ]
        for filename in text_files:
            assert Path(filename).suffix.lower() in converter.TEXT_FORMATS

    def test_image_formats(self, converter):
        """Test image format recognition"""
        image_files = [
            "img.png", "photo.jpg", "pic.jpeg",
            "img.jp2", "img.webp", "img.gif", "img.bmp"
        ]
        for filename in image_files:
            assert Path(filename).suffix.lower() in converter.IMAGE_FORMATS

    def test_conversion_methods_mapping(self, converter):
        """Test that all supported formats have conversion methods"""
        supported_formats = converter.OFFICE_FORMATS | converter.TEXT_FORMATS
        for fmt in supported_formats:
            assert fmt in converter.conversion_methods


def test_import():
    """Test that module can be imported"""
    from src.document_converter import DocumentConverter
    assert DocumentConverter is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
