#!/usr/bin/env python3
"""
Document to PDF Converter
Converts various document formats to PDF for MinerU processing
"""

import os
import sys
from pathlib import Path
from typing import Optional, List
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DocumentConverter:
    """
    Converts various document formats to PDF

    Supported formats:
    - Office: DOCX, DOC, PPTX, PPT, XLSX, XLS
    - Text: TXT, MD, CSV, RTF
    - Images: Already supported by MinerU (PNG, JPG, etc.)
    """

    OFFICE_FORMATS = {'.docx', '.doc', '.pptx', '.ppt', '.xlsx', '.xls'}
    TEXT_FORMATS = {'.txt', '.md', '.markdown', '.csv', '.rtf'}
    IMAGE_FORMATS = {'.png', '.jpg', '.jpeg', '.jp2', '.webp', '.gif', '.bmp'}
    PDF_FORMAT = {'.pdf'}

    def __init__(self):
        self.libreoffice_path = self._find_libreoffice()
        self.conversion_methods = {
            **{fmt: self._convert_with_libreoffice for fmt in self.OFFICE_FORMATS},
            **{fmt: self._convert_text_to_pdf for fmt in self.TEXT_FORMATS},
        }

    def _find_libreoffice(self) -> Optional[str]:
        """Find LibreOffice installation"""
        common_paths = [
            'libreoffice',
            'soffice',
            '/usr/bin/libreoffice',
            '/usr/local/bin/libreoffice',
            'C:\\Program Files\\LibreOffice\\program\\soffice.exe',
            'C:\\Program Files (x86)\\LibreOffice\\program\\soffice.exe',
        ]

        for path in common_paths:
            try:
                import subprocess
                result = subprocess.run(
                    [path, '--version'],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    logger.info(f"Found LibreOffice at: {path}")
                    return path
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue

        logger.warning("LibreOffice not found - Office format conversion unavailable")
        return None

    def is_supported(self, file_path: Path) -> bool:
        """Check if file format is supported for conversion"""
        ext = file_path.suffix.lower()
        return ext in (self.OFFICE_FORMATS | self.TEXT_FORMATS)

    def needs_conversion(self, file_path: Path) -> bool:
        """Check if file needs conversion to PDF"""
        ext = file_path.suffix.lower()
        # Images and PDFs don't need conversion
        return ext not in (self.IMAGE_FORMATS | self.PDF_FORMAT)

    def convert(self, input_path: Path, output_dir: Path) -> Optional[Path]:
        """
        Convert document to PDF

        Args:
            input_path: Path to input document
            output_dir: Directory to save converted PDF

        Returns:
            Path to converted PDF, or None if conversion failed
        """
        if not input_path.exists():
            logger.error(f"Input file not found: {input_path}")
            return None

        ext = input_path.suffix.lower()

        # No conversion needed
        if ext in self.PDF_FORMAT:
            logger.info(f"File is already PDF: {input_path}")
            return input_path

        if ext in self.IMAGE_FORMATS:
            logger.info(f"Image file (no conversion needed): {input_path}")
            return input_path

        # Check if we can convert this format
        if ext not in self.conversion_methods:
            logger.error(f"Unsupported format: {ext}")
            return None

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Get conversion method
        convert_func = self.conversion_methods[ext]

        try:
            output_path = convert_func(input_path, output_dir)
            if output_path and output_path.exists():
                logger.info(f"Successfully converted: {input_path} -> {output_path}")
                return output_path
            else:
                logger.error(f"Conversion failed: {input_path}")
                return None
        except Exception as e:
            logger.error(f"Error converting {input_path}: {e}")
            return None

    def _convert_with_libreoffice(self, input_path: Path, output_dir: Path) -> Optional[Path]:
        """Convert office documents using LibreOffice"""
        if not self.libreoffice_path:
            logger.error("LibreOffice not available for conversion")
            return None

        import subprocess

        try:
            logger.info(f"Converting with LibreOffice: {input_path}")

            # Run LibreOffice conversion
            result = subprocess.run(
                [
                    self.libreoffice_path,
                    '--headless',
                    '--convert-to', 'pdf',
                    '--outdir', str(output_dir),
                    str(input_path)
                ],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                logger.error(f"LibreOffice conversion failed: {result.stderr}")
                return None

            # Find the output PDF
            output_path = output_dir / f"{input_path.stem}.pdf"

            if output_path.exists():
                return output_path
            else:
                logger.error(f"Output PDF not found: {output_path}")
                return None

        except subprocess.TimeoutExpired:
            logger.error(f"Conversion timeout for: {input_path}")
            return None
        except Exception as e:
            logger.error(f"LibreOffice conversion error: {e}")
            return None

    def _convert_text_to_pdf(self, input_path: Path, output_dir: Path) -> Optional[Path]:
        """Convert text files to PDF using reportlab"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import inch
        except ImportError:
            logger.error("reportlab not installed - text conversion unavailable")
            logger.error("Install with: pip install reportlab")
            return None

        try:
            logger.info(f"Converting text to PDF: {input_path}")

            # Read text content
            with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Create PDF
            output_path = output_dir / f"{input_path.stem}.pdf"
            c = canvas.Canvas(str(output_path), pagesize=letter)
            width, height = letter

            # Add title
            c.setFont("Helvetica-Bold", 14)
            c.drawString(1*inch, height - 1*inch, f"Converted: {input_path.name}")

            # Add content
            c.setFont("Courier", 10)
            y = height - 1.5*inch

            for line in content.split('\n'):
                if y < 1*inch:  # New page if needed
                    c.showPage()
                    c.setFont("Courier", 10)
                    y = height - 1*inch

                # Truncate long lines
                if len(line) > 100:
                    line = line[:100] + "..."

                c.drawString(0.75*inch, y, line)
                y -= 0.15*inch

            c.save()
            logger.info(f"Text converted to PDF: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Text to PDF conversion error: {e}")
            return None

    def batch_convert(self, input_files: List[Path], output_dir: Path) -> dict:
        """
        Convert multiple files to PDF

        Args:
            input_files: List of input file paths
            output_dir: Directory to save converted PDFs

        Returns:
            Dictionary mapping input paths to output paths (or None if failed)
        """
        results = {}

        for input_path in input_files:
            output_path = self.convert(input_path, output_dir)
            results[input_path] = output_path

        # Summary
        successful = sum(1 for v in results.values() if v is not None)
        logger.info(f"Batch conversion complete: {successful}/{len(input_files)} successful")

        return results


def main():
    """CLI interface for document converter"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Convert documents to PDF for MinerU processing'
    )
    parser.add_argument(
        'input',
        type=str,
        help='Input file or directory'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='./output',
        help='Output directory (default: ./output)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    converter = DocumentConverter()

    input_path = Path(args.input)
    output_dir = Path(args.output)

    if not input_path.exists():
        logger.error(f"Input not found: {input_path}")
        sys.exit(1)

    if input_path.is_file():
        # Single file
        result = converter.convert(input_path, output_dir)
        if result:
            print(f"✅ Converted: {result}")
            sys.exit(0)
        else:
            print(f"❌ Conversion failed")
            sys.exit(1)

    elif input_path.is_dir():
        # Directory - convert all supported files
        files = [
            f for f in input_path.iterdir()
            if f.is_file() and converter.is_supported(f)
        ]

        if not files:
            logger.warning(f"No supported files found in: {input_path}")
            sys.exit(0)

        print(f"Found {len(files)} files to convert")
        results = converter.batch_convert(files, output_dir)

        # Print results
        print("\nConversion Results:")
        for input_file, output_file in results.items():
            status = "✅" if output_file else "❌"
            print(f"  {status} {input_file.name}")

        successful = sum(1 for v in results.values() if v is not None)
        print(f"\nTotal: {successful}/{len(results)} successful")

        sys.exit(0 if successful == len(results) else 1)

    else:
        logger.error(f"Invalid input: {input_path}")
        sys.exit(1)


if __name__ == '__main__':
    main()
