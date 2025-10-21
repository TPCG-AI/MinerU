# Document to PDF Converter

Converts various document formats to PDF for MinerU processing.

## Overview

MinerU natively supports PDF and image formats. This converter enables support for:
- **Office Documents**: DOCX, DOC, PPTX, PPT, XLSX, XLS
- **Text Formats**: TXT, MD, CSV, RTF

## Features

- ✅ Batch conversion of multiple files
- ✅ Automatic format detection
- ✅ LibreOffice integration for Office formats
- ✅ ReportLab for text-to-PDF conversion
- ✅ Detailed logging and error handling
- ✅ CLI and Python API

## Installation

### Prerequisites

**1. LibreOffice (for Office documents)**

Linux:
```bash
sudo apt install libreoffice
```

macOS:
```bash
brew install libreoffice
```

Windows:
Download and install from [libreoffice.org](https://www.libreoffice.org/)

**2. Python Dependencies**

```bash
pip install reportlab
```

## Usage

### Command Line Interface

**Convert a single file:**
```bash
cd converter
./convert.sh input.docx -o output/
```

**Convert all files in a directory:**
```bash
./convert.sh ../test-documents/input/ -o output/
```

**With verbose output:**
```bash
./convert.sh input.docx -o output/ -v
```

### Python API

```python
from pathlib import Path
from src.document_converter import DocumentConverter

# Initialize converter
converter = DocumentConverter()

# Convert single file
input_path = Path("document.docx")
output_dir = Path("output")
pdf_path = converter.convert(input_path, output_dir)

if pdf_path:
    print(f"Converted: {pdf_path}")

# Batch conversion
files = [Path("file1.docx"), Path("file2.pptx"), Path("file3.txt")]
results = converter.batch_convert(files, output_dir)

for input_file, output_file in results.items():
    if output_file:
        print(f"✅ {input_file.name} -> {output_file.name}")
    else:
        print(f"❌ {input_file.name} failed")
```

## Supported Formats

### Office Formats (via LibreOffice)

| Format | Extension | Status |
|--------|-----------|--------|
| Word | .docx, .doc | ✅ |
| PowerPoint | .pptx, .ppt | ✅ |
| Excel | .xlsx, .xls | ✅ |

### Text Formats (via ReportLab)

| Format | Extension | Status |
|--------|-----------|--------|
| Plain Text | .txt | ✅ |
| Markdown | .md, .markdown | ✅ |
| CSV | .csv | ✅ |
| Rich Text | .rtf | ✅ |

### No Conversion Needed

| Format | Extension | Note |
|--------|-----------|------|
| PDF | .pdf | Already supported by MinerU |
| Images | .png, .jpg, .jpeg, .jp2, .webp, .gif, .bmp | Already supported by MinerU |

## Integration with Test Suite

The converter is designed to integrate seamlessly with the MinerU test suite:

```bash
# 1. Convert test files
cd converter
./convert.sh ../test-documents/input/ -o ../test-documents/input/

# 2. Run MinerU tests
cd ../test-documents
./test_formats_unified.sh
```

## Architecture

```
converter/
├── src/
│   └── document_converter.py   # Main converter class
├── tests/
│   └── test_converter.py       # Unit tests
├── output/                      # Converted PDFs
├── convert.sh                   # CLI wrapper script
└── README.md                    # This file
```

### Class: DocumentConverter

**Methods:**
- `is_supported(file_path)` - Check if format is supported
- `needs_conversion(file_path)` - Check if file needs conversion
- `convert(input_path, output_dir)` - Convert single file to PDF
- `batch_convert(input_files, output_dir)` - Convert multiple files

**Conversion Methods:**
- `_convert_with_libreoffice()` - For Office documents
- `_convert_text_to_pdf()` - For text files

## Output

Converted PDFs are saved with the same base name as the input file:

```
input/document.docx  →  output/document.pdf
input/slides.pptx    →  output/slides.pdf
input/notes.txt      →  output/notes.pdf
```

## Logging

The converter provides detailed logging:

```
2025-10-20 10:00:00 - INFO - Found LibreOffice at: libreoffice
2025-10-20 10:00:01 - INFO - Converting with LibreOffice: document.docx
2025-10-20 10:00:03 - INFO - Successfully converted: document.docx -> document.pdf
2025-10-20 10:00:03 - INFO - Batch conversion complete: 5/5 successful
```

## Error Handling

Common errors and solutions:

### LibreOffice Not Found
```
WARNING - LibreOffice not found - Office format conversion unavailable
```
**Solution:** Install LibreOffice (see Installation section)

### ReportLab Not Installed
```
ERROR - reportlab not installed - text conversion unavailable
Install with: pip install reportlab
```
**Solution:** `pip install reportlab`

### Conversion Timeout
```
ERROR - Conversion timeout for: large_file.docx
```
**Solution:** File may be too large or corrupted. Try splitting or repairing the file.

### Permission Denied
```
ERROR - Output directory not writable
```
**Solution:** Check directory permissions or specify a different output directory

## Performance

Typical conversion times:

| Format | File Size | Time |
|--------|-----------|------|
| DOCX | 1 MB | 2-3s |
| PPTX | 5 MB | 5-10s |
| XLSX | 2 MB | 3-5s |
| TXT | 100 KB | <1s |

## Limitations

1. **Complex Formatting**: Some advanced formatting may not convert perfectly
2. **Macros**: VBA macros in Office files are not preserved
3. **Large Files**: Very large files (>50 MB) may timeout
4. **Fonts**: Custom fonts may be substituted if not available
5. **Text Conversion**: Text files use monospace font (Courier)

## Future Enhancements

- [ ] Support for HTML to PDF conversion
- [ ] Image-based PDF creation from images
- [ ] Configurable PDF settings (compression, quality)
- [ ] Parallel batch conversion for faster processing
- [ ] Progress bars for long conversions
- [ ] OCR integration for scanned documents
- [ ] Format validation before conversion

## Testing

Run unit tests:

```bash
cd converter
python -m pytest tests/
```

Manual testing:

```bash
# Test Office format
./convert.sh tests/sample.docx -o output/

# Test text format
./convert.sh tests/sample.txt -o output/

# Test batch conversion
./convert.sh tests/ -o output/
```

## Contributing

To add support for new formats:

1. Add extension to appropriate format set in `DocumentConverter`
2. Implement conversion method
3. Add to `conversion_methods` mapping
4. Update README and tests

## License

Part of the MinerU project. See main project LICENSE for details.
