#!/bin/bash

# Document to PDF Converter
# Wrapper script for easy conversion

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONVERTER="$SCRIPT_DIR/src/document_converter.py"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}Document to PDF Converter${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi

# Check dependencies
echo -e "${YELLOW}Checking dependencies...${NC}"

# Check LibreOffice
if command -v libreoffice &> /dev/null || command -v soffice &> /dev/null; then
    echo -e "${GREEN}✅ LibreOffice found${NC}"
else
    echo -e "${YELLOW}⚠️  LibreOffice not found - Office format conversion unavailable${NC}"
    echo -e "${YELLOW}   Install: sudo apt install libreoffice (Linux)${NC}"
    echo -e "${YELLOW}   Install: brew install libreoffice (Mac)${NC}"
    echo -e "${YELLOW}   Install: Download from https://www.libreoffice.org/ (Windows)${NC}"
fi

# Check reportlab
if python3 -c "import reportlab" 2>/dev/null; then
    echo -e "${GREEN}✅ reportlab found${NC}"
else
    echo -e "${YELLOW}⚠️  reportlab not found - Text format conversion unavailable${NC}"
    echo -e "${YELLOW}   Install: pip install reportlab${NC}"
fi

echo ""

# Run converter
python3 "$CONVERTER" "$@"
