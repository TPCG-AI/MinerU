#!/usr/bin/env python3
"""
Example usage of the Document Converter
"""

from pathlib import Path
from src.document_converter import DocumentConverter


def example_single_file():
    """Example: Convert a single file"""
    print("=" * 50)
    print("Example 1: Convert Single File")
    print("=" * 50)

    converter = DocumentConverter()

    # Example file path (adjust as needed)
    input_file = Path("../test-documents/input/sample.docx")
    output_dir = Path("./output")

    if not input_file.exists():
        print(f"⚠️  Sample file not found: {input_file}")
        print("   Create a test file first")
        return

    print(f"Input: {input_file}")
    print(f"Output: {output_dir}")
    print()

    # Convert
    result = converter.convert(input_file, output_dir)

    if result:
        print(f"✅ Success! PDF saved to: {result}")
    else:
        print("❌ Conversion failed")

    print()


def example_batch_conversion():
    """Example: Batch convert multiple files"""
    print("=" * 50)
    print("Example 2: Batch Conversion")
    print("=" * 50)

    converter = DocumentConverter()

    # Example: Convert all supported files in a directory
    input_dir = Path("../test-documents/input")
    output_dir = Path("./output")

    if not input_dir.exists():
        print(f"⚠️  Input directory not found: {input_dir}")
        return

    # Find all supported files
    files = [
        f for f in input_dir.iterdir()
        if f.is_file() and converter.is_supported(f)
    ]

    if not files:
        print(f"⚠️  No supported files found in: {input_dir}")
        return

    print(f"Found {len(files)} file(s) to convert:")
    for f in files:
        print(f"  - {f.name}")
    print()

    # Convert
    results = converter.batch_convert(files, output_dir)

    # Show results
    print("Results:")
    successful = 0
    for input_path, output_path in results.items():
        if output_path:
            print(f"  ✅ {input_path.name} -> {output_path.name}")
            successful += 1
        else:
            print(f"  ❌ {input_path.name} (failed)")

    print()
    print(f"Total: {successful}/{len(files)} successful")
    print()


def example_check_support():
    """Example: Check format support"""
    print("=" * 50)
    print("Example 3: Check Format Support")
    print("=" * 50)

    converter = DocumentConverter()

    test_files = [
        "document.docx",
        "presentation.pptx",
        "spreadsheet.xlsx",
        "notes.txt",
        "readme.md",
        "image.png",
        "document.pdf",
        "unknown.xyz"
    ]

    print("Format Support Check:")
    for filename in test_files:
        path = Path(filename)
        supported = converter.is_supported(path)
        needs_conv = converter.needs_conversion(path)

        status = "✅" if supported else "❌"
        conv_status = "Needs Conversion" if needs_conv else "No Conversion"

        print(f"  {status} {filename:20} - {conv_status}")

    print()


def example_check_dependencies():
    """Example: Check dependencies"""
    print("=" * 50)
    print("Example 4: Check Dependencies")
    print("=" * 50)

    converter = DocumentConverter()

    print("Dependency Status:")

    # Check LibreOffice
    if converter.libreoffice_path:
        print(f"  ✅ LibreOffice: {converter.libreoffice_path}")
    else:
        print("  ❌ LibreOffice: Not found (Office format conversion unavailable)")

    # Check reportlab
    try:
        import reportlab
        print(f"  ✅ reportlab: Installed")
    except ImportError:
        print("  ❌ reportlab: Not installed (Text format conversion unavailable)")

    print()


def main():
    """Run all examples"""
    print()
    print("╔" + "═" * 48 + "╗")
    print("║" + " " * 10 + "Document Converter Examples" + " " * 11 + "║")
    print("╚" + "═" * 48 + "╝")
    print()

    # Check dependencies first
    example_check_dependencies()

    # Check format support
    example_check_support()

    # Single file conversion
    example_single_file()

    # Batch conversion
    example_batch_conversion()

    print("=" * 50)
    print("Examples Complete!")
    print("=" * 50)


if __name__ == '__main__':
    main()
