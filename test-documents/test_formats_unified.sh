#!/bin/bash

# MinerU Unified Format Comparison Test
# Tests all supported formats and compares parsing results
# Place test files as: input/sample.{format}

set -e

API_URL="http://localhost:8000"
INPUT_DIR="./input"
OUTPUT_DIR="./output"
REPORT_FILE="./format_comparison_report.md"

# Image/PDF formats (officially supported by MinerU)
CORE_FORMATS=("pdf" "png" "jpg" "jpeg" "jp2" "webp" "gif" "bmp")

# Office/Document formats (for future converter integration)
OFFICE_FORMATS=("docx" "doc" "pptx" "ppt" "xlsx" "xls")

# Text formats
TEXT_FORMATS=("txt" "md" "markdown" "csv" "rtf")

# Combine all formats
FORMATS=("${CORE_FORMATS[@]}" "${OFFICE_FORMATS[@]}" "${TEXT_FORMATS[@]}")

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Test tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}MinerU Format Comparison Test${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Check API availability
echo -e "${YELLOW}Checking MinerU API...${NC}"
if ! curl -s -f "$API_URL/docs" > /dev/null 2>&1; then
    echo -e "${RED}❌ MinerU API is not running at $API_URL${NC}"
    echo "Please start: uv run mineru-api"
    exit 1
fi
echo -e "${GREEN}✅ API is running${NC}"
echo ""

# Get API version
API_VERSION=$(curl -s "$API_URL/openapi.json" | python -m json.tool 2>/dev/null | grep -A1 '"info"' | grep '"version"' | cut -d'"' -f4 || echo "unknown")
echo -e "${CYAN}API Version: $API_VERSION${NC}"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Initialize report
cat > "$REPORT_FILE" << EOF
# MinerU Format Comparison Report

**Test Date:** $(date '+%Y-%m-%d %H:%M:%S')
**API Endpoint:** $API_URL
**API Version:** $API_VERSION

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
1. **Markdown Content** (\`md_content\`) - Extracted text in markdown format
2. **Content List** (\`content_list\`) - Structured content list
3. **Middle JSON** (\`middle_json\`) - Intermediate processing results
4. **Model Output** (\`model_output\`) - Raw model output
5. **Images** (\`images\`) - Extracted images from document

### Test Method
Each format is tested by:
1. Uploading \`input/sample.{format}\` file to API
2. Requesting all output types (\`return_md=true\`, \`return_images=true\`, etc.)
3. Validating API response (HTTP 200, valid JSON)
4. Checking presence of each output type
5. Extracting sample content for comparison

---

## Test Results

EOF

# Function to test a format
test_format() {
    local format=$1
    local file="$INPUT_DIR/sample.$format"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Testing: sample.$format${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    if [ ! -f "$file" ]; then
        echo -e "${YELLOW}⚠️  File not found: $file${NC}"
        echo -e "${YELLOW}   Skipping $format format${NC}"
        echo ""

        cat >> "$REPORT_FILE" << EOF
### ⚠️ $format (SKIPPED)

**Status:** SKIPPED
**Reason:** File not found (\`$file\`)

---

EOF
        return
    fi

    # Verify it's actually the right file type
    local file_type=$(file -b "$file" 2>/dev/null || echo "unknown")
    echo -e "${CYAN}File type: $file_type${NC}"

    # Use temporary output path first (will rename later with status)
    local output_name="sample_$format"
    local temp_output_path="$OUTPUT_DIR/${output_name}_PROCESSING"
    mkdir -p "$temp_output_path"
    local output_path="$temp_output_path"  # Will be updated after status is determined

    # Call API (disable set -e temporarily to capture errors)
    echo -e "${CYAN}Calling MinerU API...${NC}"
    local start_time=$(date +%s)

    set +e  # Don't exit on error - capture unsupported format errors
    local http_code=$(curl -X POST "$API_URL/file_parse" \
        -F "files=@$file" \
        -F "return_md=true" \
        -F "return_middle_json=true" \
        -F "return_model_output=true" \
        -F "return_content_list=true" \
        -F "return_images=true" \
        -o "$output_path/response.json" \
        -w "%{http_code}" \
        -s 2>&1)
    set -e  # Re-enable exit on error

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    echo -e "${CYAN}HTTP Status: $http_code (${duration}s)${NC}"

    # Analyze response
    local status="FAILED"
    local has_md="❌"
    local has_content_list="❌"
    local has_middle_json="❌"
    local has_model_output="❌"
    local has_images="❌"
    local error_msg=""
    local md_preview=""
    local char_count=0

    if [ "$http_code" = "200" ]; then
        # Validate JSON
        if python -m json.tool "$output_path/response.json" > /dev/null 2>&1; then
            # Check for error in response
            if grep -q '"error"' "$output_path/response.json" 2>/dev/null; then
                error_msg=$(python3 -c "
import json
try:
    with open('$output_path/response.json', 'r') as f:
        data = json.load(f)
        print(data.get('error', 'Unknown error'))
except: pass
" 2>/dev/null)
                echo -e "${RED}❌ API returned error: $error_msg${NC}"

                # Mark as unsupported if it's a file type error
                if echo "$error_msg" | grep -iq "unsupported\|not supported"; then
                    status="UNSUPPORTED"
                fi
            else
                # Check each output type
                if grep -q '"md_content"' "$output_path/response.json" 2>/dev/null; then
                    has_md="✅"
                fi

                if grep -q '"content_list"' "$output_path/response.json" 2>/dev/null; then
                    has_content_list="✅"
                fi

                if grep -q '"middle_json"' "$output_path/response.json" 2>/dev/null; then
                    has_middle_json="✅"
                fi

                if grep -q '"model_output"' "$output_path/response.json" 2>/dev/null; then
                    has_model_output="✅"
                fi

                if grep -q '"images"' "$output_path/response.json" 2>/dev/null; then
                    has_images="✅"
                fi

                # Extract content preview
                local extract_result=$(python3 -c "
import json
import sys
try:
    with open('$output_path/response.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    results = data.get('results', {})
    for key, value in results.items():
        md_content = value.get('md_content', '')
        if md_content:
            char_count = len(md_content)
            preview = md_content[:150].replace('\n', ' ').strip()
            print(f'{char_count}|||{preview}')
            sys.exit(0)
    print('0|||No content extracted')
except Exception as e:
    print(f'0|||Error: {e}')
" 2>/dev/null)

                char_count=$(echo "$extract_result" | cut -d'|' -f1)
                md_preview=$(echo "$extract_result" | cut -d'|' -f4-)

                if [ "$has_md" = "✅" ] && [ "$char_count" -gt 0 ]; then
                    status="PASSED"
                    PASSED_TESTS=$((PASSED_TESTS + 1))
                else
                    status="PARTIAL"
                fi
            fi
        else
            error_msg="Invalid JSON response"
            echo -e "${RED}❌ Invalid JSON response${NC}"
        fi
    else
        error_msg="HTTP $http_code"
        echo -e "${RED}❌ HTTP Error: $http_code${NC}"
    fi

    if [ "$status" != "PASSED" ]; then
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi

    # Display results
    echo ""
    echo -e "${CYAN}Results:${NC}"
    echo -e "  Markdown:     $has_md"
    echo -e "  Content List: $has_content_list"
    echo -e "  Middle JSON:  $has_middle_json"
    echo -e "  Model Output: $has_model_output"
    echo -e "  Images:       $has_images"

    if [ -n "$error_msg" ]; then
        echo -e "${RED}  Error: $error_msg${NC}"
    fi

    if [ "$char_count" -gt 0 ]; then
        echo -e "${CYAN}  Extracted: $char_count characters${NC}"
        echo -e "${CYAN}  Preview: $md_preview...${NC}"
    fi

    echo ""

    if [ "$status" = "PASSED" ]; then
        echo -e "${GREEN}✅ Test PASSED${NC}"
    elif [ "$status" = "PARTIAL" ]; then
        echo -e "${YELLOW}⚠️  Test PARTIAL${NC}"
    elif [ "$status" = "UNSUPPORTED" ]; then
        echo -e "${YELLOW}⚠️  UNSUPPORTED FORMAT (needs converter)${NC}"
    else
        echo -e "${RED}❌ Test FAILED${NC}"
    fi
    echo ""

    # Rename output directory to include status
    local final_output_path="$OUTPUT_DIR/${output_name}_${status}"
    if [ -d "$temp_output_path" ]; then
        # Remove old directory if exists
        rm -rf "$final_output_path" 2>/dev/null || true
        mv "$temp_output_path" "$final_output_path"
        output_path="$final_output_path"
        echo -e "${CYAN}📁 Output saved to: ${output_name}_${status}/${NC}"
        echo ""
    fi

    # Write to report
    cat >> "$REPORT_FILE" << EOF
### $format Format

**File:** \`sample.$format\`
**Status:** $status
**Processing Time:** ${duration}s
**HTTP Status:** $http_code
**File Type:** \`$file_type\`

#### Outputs

| Output Type | Present | Details |
|-------------|---------|---------|
| Markdown Content | $has_md | $char_count characters |
| Content List | $has_content_list | - |
| Middle JSON | $has_middle_json | - |
| Model Output | $has_model_output | - |
| Images | $has_images | - |

EOF

    if [ -n "$error_msg" ]; then
        cat >> "$REPORT_FILE" << EOF
**Error:** \`$error_msg\`

EOF
    fi

    if [ "$char_count" -gt 0 ]; then
        cat >> "$REPORT_FILE" << EOF
**Content Preview:**
\`\`\`
$md_preview...
\`\`\`

EOF
    fi

    cat >> "$REPORT_FILE" << EOF
**Response File:** \`$output_path/response.json\`

---

EOF
}

# Test all formats
echo -e "${YELLOW}=====================================${NC}"
echo -e "${YELLOW}Testing All Formats${NC}"
echo -e "${YELLOW}=====================================${NC}"
echo ""

for format in "${FORMATS[@]}"; do
    test_format "$format"
done

# Summary
SUCCESS_RATE=0
if [ $TOTAL_TESTS -gt 0 ]; then
    SUCCESS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
fi

cat >> "$REPORT_FILE" << EOF

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | $TOTAL_TESTS |
| Passed | $PASSED_TESTS |
| Failed | $FAILED_TESTS |
| Success Rate | ${SUCCESS_RATE}% |

## Comparison Insights

EOF

# Add comparison section if multiple formats were tested
if [ $PASSED_TESTS -gt 1 ]; then
    cat >> "$REPORT_FILE" << EOF
### Format Performance

To compare how different formats perform with the same content:
1. Check the "Extracted characters" count for each format
2. Compare the content preview to see if text extraction is consistent
3. Review processing time differences between formats

### Recommendations

- **Best for text extraction:** Compare formats with highest character counts
- **Fastest processing:** Check formats with lowest processing times
- **Most complete output:** Formats with all output types (✅) present

EOF
fi

cat >> "$REPORT_FILE" << EOF

## Notes

- Place test files as \`input/sample.{format}\` (e.g., \`input/sample.pdf\`)
- All files should ideally contain the same content for fair comparison
- Missing formats will be skipped automatically
- **UNSUPPORTED** formats require a converter to be integrated in the future
- Core formats (PDF, images) are natively supported by MinerU
- Office formats (DOCX, PPTX, XLSX) and text formats need pre-conversion to PDF/image

EOF

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}Testing Complete${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""
echo -e "${CYAN}Summary:${NC}"
echo -e "  Total Tests:  $TOTAL_TESTS"
echo -e "  Passed:       ${GREEN}$PASSED_TESTS${NC}"
echo -e "  Failed:       ${RED}$FAILED_TESTS${NC}"
echo -e "  Success Rate: ${SUCCESS_RATE}%"
echo ""
echo -e "${YELLOW}📁 Output: $OUTPUT_DIR${NC}"
echo -e "${YELLOW}📊 Report: $REPORT_FILE${NC}"
echo ""
echo -e "${CYAN}View report:${NC}"
echo -e "  cat $REPORT_FILE"
echo ""
echo -e "${GREEN}To test additional formats:${NC}"
echo -e "  1. Add files to input/ as: ${YELLOW}sample.{pdf,png,jpg,etc}${NC}"
echo -e "  2. Run: ${YELLOW}./test_formats_unified.sh${NC}"
