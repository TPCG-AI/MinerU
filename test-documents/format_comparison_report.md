# MinerU Format Comparison Report

**Test Date:** 2025-10-20 11:56:21
**API Endpoint:** http://localhost:8000
**API Version:** 

## Test Configuration

### Tested Input Formats

#### Core Formats (MinerU Native Support)
- PDF
- Images: PNG, JPEG, JPG, JP2, WEBP, GIF, BMP

#### Office Document Formats (Requires Converter)
- Word: DOCX, DOC
- PowerPoint: PPTX, PPT
- Excel: XLSX, XLS

#### Text Formats (Requires Converter)
- Plain Text: TXT, MD, CSV, RTF

### Output Types Tested
1. **Markdown Content** (`md_content`) - Extracted text in markdown format
2. **Content List** (`content_list`) - Structured content list
3. **Middle JSON** (`middle_json`) - Intermediate processing results
4. **Model Output** (`model_output`) - Raw model output
5. **Images** (`images`) - Extracted images from document

### Test Method
Each format is tested by:
1. Uploading `input/sample.{format}` file to API
2. Requesting all output types (`return_md=true`, `return_images=true`, etc.)
3. Validating API response (HTTP 200, valid JSON)
4. Checking presence of each output type
5. Extracting sample content for comparison

---

## Test Results

### pdf Format

**File:** `sample.pdf`
**Status:** PARTIAL
**Processing Time:** 28s
**HTTP Status:** 200
**File Type:** `PDF document, version 1.4, 3 page(s)`

#### Outputs

| Output Type | Present | Details |
|-------------|---------|---------|
| Markdown Content | ✅ |  characters |
| Content List | ✅ | - |
| Middle JSON | ✅ | - |
| Model Output | ✅ | - |
| Images | ✅ | - |

**Response File:** `./output/sample_pdf_PARTIAL/response.json`

---

### png Format

**File:** `sample.png`
**Status:** PARTIAL
**Processing Time:** 19s
**HTTP Status:** 200
**File Type:** `PNG image data, 642 x 816, 8-bit/color RGBA, non-interlaced`

#### Outputs

| Output Type | Present | Details |
|-------------|---------|---------|
| Markdown Content | ✅ |  characters |
| Content List | ✅ | - |
| Middle JSON | ✅ | - |
| Model Output | ✅ | - |
| Images | ✅ | - |

**Response File:** `./output/sample_png_PARTIAL/response.json`

---

### jpg Format

**File:** `sample.jpg`
**Status:** PARTIAL
**Processing Time:** 18s
**HTTP Status:** 200
**File Type:** `JPEG image data, JFIF standard 1.01, resolution (DPI), density 96x96, segment length 16, baseline, precision 8, 683x816, components 3`

#### Outputs

| Output Type | Present | Details |
|-------------|---------|---------|
| Markdown Content | ✅ |  characters |
| Content List | ✅ | - |
| Middle JSON | ✅ | - |
| Model Output | ✅ | - |
| Images | ✅ | - |

**Response File:** `./output/sample_jpg_PARTIAL/response.json`

---

### ⚠️ jpeg (SKIPPED)

**Status:** SKIPPED
**Reason:** File not found (`./input/sample.jpeg`)

---

### ⚠️ jp2 (SKIPPED)

**Status:** SKIPPED
**Reason:** File not found (`./input/sample.jp2`)

---

### ⚠️ webp (SKIPPED)

**Status:** SKIPPED
**Reason:** File not found (`./input/sample.webp`)

---

### gif Format

**File:** `sample.gif`
**Status:** PARTIAL
**Processing Time:** 20s
**HTTP Status:** 200
**File Type:** `GIF image data, version 89a, 683 x 816`

#### Outputs

| Output Type | Present | Details |
|-------------|---------|---------|
| Markdown Content | ✅ |  characters |
| Content List | ✅ | - |
| Middle JSON | ✅ | - |
| Model Output | ✅ | - |
| Images | ✅ | - |

**Response File:** `./output/sample_gif_PARTIAL/response.json`

---

### ⚠️ bmp (SKIPPED)

**Status:** SKIPPED
**Reason:** File not found (`./input/sample.bmp`)

---

### docx Format

**File:** `sample.docx`
**Status:** FAILED
**Processing Time:** 0s
**HTTP Status:** 400
**File Type:** `Microsoft Word 2007+`

#### Outputs

| Output Type | Present | Details |
|-------------|---------|---------|
| Markdown Content | ❌ | 0 characters |
| Content List | ❌ | - |
| Middle JSON | ❌ | - |
| Model Output | ❌ | - |
| Images | ❌ | - |

**Error:** `HTTP 400`

**Response File:** `./output/sample_docx_FAILED/response.json`

---

### ⚠️ doc (SKIPPED)

**Status:** SKIPPED
**Reason:** File not found (`./input/sample.doc`)

---

### pptx Format

**File:** `sample.pptx`
**Status:** FAILED
**Processing Time:** 1s
**HTTP Status:** 400
**File Type:** `Microsoft PowerPoint 2007+`

#### Outputs

| Output Type | Present | Details |
|-------------|---------|---------|
| Markdown Content | ❌ | 0 characters |
| Content List | ❌ | - |
| Middle JSON | ❌ | - |
| Model Output | ❌ | - |
| Images | ❌ | - |

**Error:** `HTTP 400`

**Response File:** `./output/sample_pptx_FAILED/response.json`

---

### ⚠️ ppt (SKIPPED)

**Status:** SKIPPED
**Reason:** File not found (`./input/sample.ppt`)

---

### xlsx Format

**File:** `sample.xlsx`
**Status:** FAILED
**Processing Time:** 1s
**HTTP Status:** 400
**File Type:** `Microsoft Excel 2007+`

#### Outputs

| Output Type | Present | Details |
|-------------|---------|---------|
| Markdown Content | ❌ | 0 characters |
| Content List | ❌ | - |
| Middle JSON | ❌ | - |
| Model Output | ❌ | - |
| Images | ❌ | - |

**Error:** `HTTP 400`

**Response File:** `./output/sample_xlsx_FAILED/response.json`

---

### ⚠️ xls (SKIPPED)

**Status:** SKIPPED
**Reason:** File not found (`./input/sample.xls`)

---

### txt Format

**File:** `sample.txt`
**Status:** FAILED
**Processing Time:** 0s
**HTTP Status:** 400
**File Type:** `ASCII text, with CRLF line terminators`

#### Outputs

| Output Type | Present | Details |
|-------------|---------|---------|
| Markdown Content | ❌ | 0 characters |
| Content List | ❌ | - |
| Middle JSON | ❌ | - |
| Model Output | ❌ | - |
| Images | ❌ | - |

**Error:** `HTTP 400`

**Response File:** `./output/sample_txt_FAILED/response.json`

---

### md Format

**File:** `sample.md`
**Status:** FAILED
**Processing Time:** 0s
**HTTP Status:** 400
**File Type:** `ASCII text, with CRLF line terminators`

#### Outputs

| Output Type | Present | Details |
|-------------|---------|---------|
| Markdown Content | ❌ | 0 characters |
| Content List | ❌ | - |
| Middle JSON | ❌ | - |
| Model Output | ❌ | - |
| Images | ❌ | - |

**Error:** `HTTP 400`

**Response File:** `./output/sample_md_FAILED/response.json`

---

### ⚠️ markdown (SKIPPED)

**Status:** SKIPPED
**Reason:** File not found (`./input/sample.markdown`)

---

### ⚠️ csv (SKIPPED)

**Status:** SKIPPED
**Reason:** File not found (`./input/sample.csv`)

---

### ⚠️ rtf (SKIPPED)

**Status:** SKIPPED
**Reason:** File not found (`./input/sample.rtf`)

---


## Summary

| Metric | Value |
|--------|-------|
| Total Tests | 19 |
| Passed | 0 |
| Failed | 9 |
| Success Rate | 0% |

## Comparison Insights


## Notes

- Place test files as `input/sample.{format}` (e.g., `input/sample.pdf`)
- All files should ideally contain the same content for fair comparison
- Missing formats will be skipped automatically
- **UNSUPPORTED** formats require a converter to be integrated in the future
- Core formats (PDF, images) are natively supported by MinerU
- Office formats (DOCX, PPTX, XLSX) and text formats need pre-conversion to PDF/image

