# MinerU Format Testing Suite

Comprehensive testing framework for validating MinerU's document parsing capabilities across multiple file formats.

## Overview

This test suite validates MinerU's ability to parse and extract content from various document formats, including:
- **Core formats** (natively supported)
- **Office documents** (requires converter integration)
- **Text formats** (requires converter integration)

## Directory Structure

```
test-documents/
├── input/                          # Test files location
│   ├── sample.pdf                 # Place test files here
│   ├── sample.png                 # with consistent naming
│   ├── sample.docx                # sample.{format}
│   └── ...
├── output/                        # Test results
│   └── sample_{format}/          # Per-format outputs
│       └── response.json         # API response
├── test_formats_unified.sh       # Main test script
├── format_comparison_report.md   # Generated test report
└── README.md                     # This file
```

## Tested Formats

### Core Formats (Native MinerU Support)
✅ **Fully Supported**
- `pdf` - PDF documents
- `png` - PNG images
- `jpg`, `jpeg` - JPEG images
- `jp2` - JPEG 2000 images
- `webp` - WebP images
- `gif` - GIF images
- `bmp` - Bitmap images

### Office Document Formats
⚠️ **Requires Converter Integration**
- `docx`, `doc` - Microsoft Word documents
- `pptx`, `ppt` - Microsoft PowerPoint presentations
- `xlsx`, `xls` - Microsoft Excel spreadsheets

### Text Formats
⚠️ **Requires Converter Integration**
- `txt` - Plain text files
- `md`, `markdown` - Markdown files
- `csv` - CSV files
- `rtf` - Rich Text Format files

## Test Outputs Validated

For each format, the test validates:

1. **Markdown Content** (`md_content`) - Extracted text in markdown format
2. **Content List** (`content_list`) - Structured content list with bounding boxes
3. **Middle JSON** (`middle_json`) - Intermediate processing results
4. **Model Output** (`model_output`) - Raw model detection output
5. **Images** (`images`) - Extracted images from document

## Usage

### Prerequisites

1. **Start MinerU API server:**
   ```bash
   cd /path/to/MinerU
   uv run mineru-api
   ```
   The API should be running on `http://localhost:8000`

2. **Prepare test files:**
   Place test files in the `input/` directory with consistent naming:
   ```bash
   cd test-documents/input
   # Add your test files
   cp /path/to/document.pdf sample.pdf
   cp /path/to/document.docx sample.docx
   # etc.
   ```

   **Important:** For meaningful comparison, all files should contain the same content in different formats.

### Running Tests

```bash
cd test-documents
./test_formats_unified.sh
```

### Viewing Results

**Console Output:**
- Real-time test progress
- Pass/fail status for each format
- Summary statistics

**Test Report:**
```bash
cat format_comparison_report.md
```

The report includes:
- Test configuration and metadata
- Per-format results with:
  - HTTP status codes
  - Processing time
  - Output type validation
  - Content preview
  - Error messages (if any)
- Comparison insights
- Summary statistics

**Raw API Responses:**
```bash
# View specific format response
cat output/sample_pdf/response.json | python -m json.tool

# View extracted markdown
cat output/sample_pdf/response.json | python -c "import json,sys; data=json.load(sys.stdin); print(data['results'][list(data['results'].keys())[0]]['md_content'])"
```

## Test Results Interpretation

### Status Types

- **✅ PASSED**: Format is supported, content extracted successfully
- **⚠️ PARTIAL**: API responded but some outputs missing
- **⚠️ UNSUPPORTED**: Format not supported (needs converter)
- **❌ FAILED**: API error or invalid response
- **⚠️ SKIPPED**: Test file not found

### Success Criteria

A test **PASSES** when:
1. HTTP 200 response
2. Valid JSON response
3. Markdown content present
4. Character count > 0

## Format Comparison Workflow

To compare how different formats perform with identical content:

1. **Prepare source document:**
   - Create a document with representative content (text, tables, images)
   - Use English text for consistency

2. **Convert to all formats:**
   ```bash
   # Example using LibreOffice for conversions
   libreoffice --headless --convert-to pdf sample.docx
   libreoffice --headless --convert-to png sample.docx
   # etc.
   ```

3. **Run tests:**
   ```bash
   ./test_formats_unified.sh
   ```

4. **Analyze results:**
   - Compare character counts across formats
   - Review content preview for consistency
   - Check processing times
   - Identify unsupported formats

## Future Enhancements

### Planned Features

1. **Document Converter Integration**
   - Convert office formats (DOCX, PPTX, XLSX) to PDF
   - Convert text formats to PDF/images
   - Enable testing of all format types

2. **Advanced Validation**
   - Compare extracted content similarity
   - Validate table extraction accuracy
   - Image extraction quality metrics

3. **Performance Benchmarking**
   - Processing time analysis
   - Memory usage tracking
   - Throughput testing

4. **Automated Test Data Generation**
   - Generate test documents programmatically
   - Create documents with known content for validation
   - Multi-language support testing

## Troubleshooting

### API Not Running
```
❌ MinerU API is not running at http://localhost:8000
```
**Solution:** Start the API server with `uv run mineru-api`

### Unsupported Format Errors
```
Error: Unsupported file type: docx
```
**Expected Behavior:** Office and text formats are not yet supported. Converter integration is planned.

### Empty Character Count
If markdown content is present but character count shows 0, check the response structure:
```bash
cat output/sample_pdf/response.json | python -m json.tool | grep -A5 md_content
```

## Contributing

To add support for new formats:

1. Update `FORMATS` array in `test_formats_unified.sh`
2. Add format to appropriate category (CORE_FORMATS, OFFICE_FORMATS, TEXT_FORMATS)
3. Update this README
4. Run tests to validate

## License

Part of the MinerU project. See main project LICENSE for details.

## Contact

For issues or questions, refer to the main MinerU project repository.
