#!/usr/bin/env python3
"""
Debug tool to inspect PDF content and diagnose extraction issues
"""

import sys
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    print("Error: pdfplumber not installed")
    sys.exit(1)


def debug_pdf(pdf_path):
    """Show detailed PDF information"""
    path = Path(pdf_path)

    if not path.exists():
        print(f"❌ File not found: {pdf_path}")
        return

    print(f"📄 Analyzing PDF: {path.name}")
    print("=" * 70)

    try:
        with pdfplumber.open(path) as pdf:
            print(f"\n📊 PDF Statistics:")
            print(f"  Total pages: {len(pdf.pages)}")

            if pdf.metadata:
                print(f"\n📋 Metadata:")
                for key, value in pdf.metadata.items():
                    if value:
                        print(f"  {key}: {value}")

            # Analyze first few pages
            print(f"\n📖 Content Analysis:")

            for page_num in range(min(3, len(pdf.pages))):
                page = pdf.pages[page_num]
                print(f"\n  Page {page_num + 1}:")
                print(f"    Size: {page.width} x {page.height}")

                # Try to extract text
                text = page.extract_text()

                if text:
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    print(f"    Lines extracted: {len(lines)}")

                    # Show first few lines
                    print(f"    First lines:")
                    for i, line in enumerate(lines[:10]):
                        print(f"      {i+1}. {line[:80]}{'...' if len(line) > 80 else ''}")

                    if len(lines) > 10:
                        print(f"      ... ({len(lines) - 10} more lines)")
                else:
                    print(f"    ⚠️  No text extracted!")

                    # Check if it's an image-based PDF
                    if page.images:
                        print(f"    📷 Found {len(page.images)} images")
                        print(f"    💡 This might be a scanned/image-based PDF")
                        print(f"       Consider using OCR software first")

                # Check for text objects at a lower level
                chars = page.chars
                if chars:
                    print(f"    Characters found: {len(chars)}")
                else:
                    print(f"    ⚠️  No character data found")

            # Overall assessment
            print(f"\n🔍 Assessment:")

            # Check if any page has text
            has_text = False
            for page in pdf.pages:
                if page.extract_text():
                    has_text = True
                    break

            if has_text:
                print(f"  ✅ PDF contains extractable text")
                print(f"  👍 Should work with pdf_to_captionpoint.py")
            else:
                print(f"  ❌ PDF appears to be image-based (no extractable text)")
                print(f"  💡 Solutions:")
                print(f"     1. Use OCR software to convert to text-based PDF")
                print(f"     2. Copy-paste text from PDF viewer into a text file")
                print(f"     3. Request a text-based version of the script")

    except Exception as e:
        print(f"\n❌ Error analyzing PDF: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python debug_pdf.py your-file.pdf")
        sys.exit(1)

    debug_pdf(sys.argv[1])
