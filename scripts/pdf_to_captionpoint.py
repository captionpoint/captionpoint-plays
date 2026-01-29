#!/usr/bin/env python3
"""
Interactive PDF to CaptionPoint Markdown Converter

Extracts text from PDF theater scripts and converts to CaptionPoint markdown format.
Provides interactive classification of character names and dialogue.

Usage:
    python3 pdf_to_captionpoint.py input.pdf output.md
    python3 pdf_to_captionpoint.py input.pdf output.md --resume
"""

import re
import sys
import argparse
import json
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    print("Error: pdfplumber not installed. Install with:")
    print("  pip3 install pdfplumber")
    sys.exit(1)


class CaptionPointParser:
    def __init__(self, pdf_path, output_path, resume=False):
        self.pdf_path = Path(pdf_path)
        self.output_path = Path(output_path)
        self.progress_path = Path(f"{output_path}.progress.json")
        self.resume = resume

        # Statistics
        self.stats = {
            'characters': set(),
            'slides': 0,
            'lines_processed': 0,
            'lines_skipped': 0
        }

        # Output buffer
        self.slides = []
        self.current_slide = []

        # Progress tracking
        self.current_page = 0
        self.current_line_idx = 0

        # Load progress if resuming
        if resume and self.progress_path.exists():
            self._load_progress()

    def _save_progress(self):
        """Save current progress to resume later"""
        progress = {
            'current_page': self.current_page,
            'current_line_idx': self.current_line_idx,
            'slides': self.slides,
            'stats': {
                'characters': list(self.stats['characters']),
                'slides': self.stats['slides'],
                'lines_processed': self.stats['lines_processed'],
                'lines_skipped': self.stats['lines_skipped']
            }
        }
        with open(self.progress_path, 'w') as f:
            json.dump(progress, f, indent=2)

    def _load_progress(self):
        """Load saved progress"""
        with open(self.progress_path, 'r') as f:
            progress = json.load(f)
        self.current_page = progress.get('current_page', 0)
        self.current_line_idx = progress.get('current_line_idx', 0)
        self.slides = progress.get('slides', [])
        stats = progress.get('stats', {})
        self.stats = {
            'characters': set(stats.get('characters', [])),
            'slides': stats.get('slides', 0),
            'lines_processed': stats.get('lines_processed', 0),
            'lines_skipped': stats.get('lines_skipped', 0)
        }
        print(f"📂 Resuming from page {self.current_page}, line {self.current_line_idx}")

    def _is_likely_page_number(self, text):
        """Detect if text is likely a page number"""
        text = text.strip()
        # Just digits
        if text.isdigit():
            return True
        # Roman numerals
        if re.match(r'^[ivxlcdm]+$', text.lower()):
            return True
        # Page X of Y
        if re.match(r'page\s+\d+', text.lower()):
            return True
        return False

    def _is_likely_stage_direction(self, text):
        """Detect if text is likely a stage direction"""
        text = text.strip()

        # Parentheses or brackets
        if (text.startswith('(') and text.endswith(')')) or \
           (text.startswith('[') and text.endswith(']')):
            return True

        # Common stage direction patterns (all caps actions)
        stage_keywords = [
            'EXIT', 'ENTER', 'LIGHTS', 'CURTAIN', 'SCENE', 'ACT',
            'BLACKOUT', 'FADE', 'MUSIC', 'SOUND', 'PAUSE', 'BEAT'
        ]
        upper_text = text.upper()
        if any(keyword in upper_text for keyword in stage_keywords):
            return True

        return False

    def _is_likely_character_name(self, text):
        """Detect if text is likely a character name"""
        text = text.strip()

        # All caps (with optional colon)
        if text.isupper() and len(text) > 1:
            # Remove colon if present
            name = text.rstrip(':').strip()
            # Not too long (character names are usually short)
            if 2 <= len(name) <= 30 and ' ' not in name or name.count(' ') <= 2:
                return True

        return False

    def _normalize_character_name(self, name):
        """Normalize character name to CaptionPoint format"""
        # Remove colon, strip, convert to title case with hyphens
        name = name.rstrip(':').strip()
        # Keep it uppercase but clean
        name = re.sub(r'\s+', '-', name)
        return name

    def _classify_line(self, text, context_before=None, context_after=None):
        """
        Interactively classify a line of text
        Returns: ('character', name), ('dialogue', text), ('skip', None), or ('new_slide', None)
        """
        text = text.strip()
        if not text:
            return ('skip', None)

        # Auto-skip obvious cases
        if self._is_likely_page_number(text):
            return ('skip', None)

        # Show context
        print("\n" + "="*70)
        if context_before:
            print(f"  Before: {context_before[:60]}...")
        print(f"  >>> {text}")
        if context_after:
            print(f"  After:  {context_after[:60]}...")

        # Provide smart suggestions
        suggestions = []
        if self._is_likely_character_name(text):
            suggestions.append("Likely: CHARACTER NAME")
        if self._is_likely_stage_direction(text):
            suggestions.append("Likely: STAGE DIRECTION (skip)")

        if suggestions:
            print(f"  💡 {' | '.join(suggestions)}")

        # Get user input
        print("\n  Options:")
        print("    [c] Character name    [d] Dialogue")
        print("    [s] Skip (stage dir)  [n] New slide separator")
        print("    [q] Save and quit     [a] Auto-mode (bulk skip)")
        print("    [m] Merge with previous line")

        while True:
            choice = input("  Choice: ").lower().strip()

            if choice == 'q':
                self._save_progress()
                print("\n💾 Progress saved. Run with --resume to continue.")
                sys.exit(0)

            elif choice == 'c':
                # Character name
                normalized = self._normalize_character_name(text)
                confirm = input(f"  Character name [{normalized}]: ").strip()
                name = confirm if confirm else normalized
                self.stats['characters'].add(name)
                return ('character', name)

            elif choice == 'd':
                # Dialogue
                return ('dialogue', text)

            elif choice == 's':
                # Skip
                return ('skip', None)

            elif choice == 'n':
                # New slide
                return ('new_slide', None)

            elif choice == 'm':
                # Merge with previous
                return ('merge', text)

            elif choice == 'a':
                # Auto-mode: skip everything until next likely character
                return ('auto_skip', None)

            else:
                print("  ❌ Invalid choice. Try again.")

    def _add_slide(self):
        """Add current slide to output and start new slide"""
        if self.current_slide:
            self.slides.append('\n'.join(self.current_slide))
            self.stats['slides'] += 1
            self.current_slide = []

    def process_pdf(self):
        """Main processing loop"""
        print(f"📖 Opening PDF: {self.pdf_path}")

        with pdfplumber.open(self.pdf_path) as pdf:
            print(f"📄 Found {len(pdf.pages)} pages")

            # Quick check if PDF has extractable text
            has_text = False
            for page in pdf.pages[:3]:  # Check first 3 pages
                if page.extract_text():
                    has_text = True
                    break

            if not has_text:
                print("\n❌ ERROR: No extractable text found in PDF!")
                print("This appears to be an image-based (scanned) PDF.\n")
                print("💡 Solutions:")
                print("   1. Run OCR on the PDF first")
                print("   2. Use './debug-pdf filename.pdf' for more details")
                print("   3. Copy-paste text manually from PDF viewer\n")
                return

            print("✅ PDF contains extractable text\n")

            auto_skip_mode = False

            for page_num, page in enumerate(pdf.pages):
                # Skip already processed pages
                if page_num < self.current_page:
                    continue

                self.current_page = page_num
                print(f"\n{'='*70}")
                print(f"📃 Page {page_num + 1} of {len(pdf.pages)}")
                print(f"{'='*70}")

                # Extract text
                text = page.extract_text()
                if not text:
                    print(f"⚠️  Page {page_num + 1} has no extractable text, skipping...")
                    continue

                # Split into lines
                lines = [line.strip() for line in text.split('\n') if line.strip()]

                if not lines:
                    print(f"⚠️  Page {page_num + 1} is empty after cleaning, skipping...")
                    continue

                print(f"Found {len(lines)} lines on page {page_num + 1}")

                for line_idx, line in enumerate(lines):
                    # Skip already processed lines
                    if page_num == self.current_page and line_idx < self.current_line_idx:
                        continue

                    self.current_line_idx = line_idx
                    self.stats['lines_processed'] += 1

                    # Get context
                    context_before = lines[line_idx - 1] if line_idx > 0 else None
                    context_after = lines[line_idx + 1] if line_idx < len(lines) - 1 else None

                    # Auto-skip mode: skip until we find likely character name
                    if auto_skip_mode:
                        if self._is_likely_character_name(line):
                            auto_skip_mode = False
                            print(f"\n🎯 Auto-skip ended, found character: {line}")
                        else:
                            self.stats['lines_skipped'] += 1
                            continue

                    # Classify the line
                    line_type, content = self._classify_line(line, context_before, context_after)

                    if line_type == 'character':
                        # Start new slide with character
                        self._add_slide()
                        self.current_slide.append(f"## {content}:")

                    elif line_type == 'dialogue':
                        # Add dialogue to current slide
                        self.current_slide.append(content)

                    elif line_type == 'new_slide':
                        # Force new slide
                        self._add_slide()

                    elif line_type == 'merge':
                        # Merge with previous line
                        if self.current_slide:
                            self.current_slide[-1] += ' ' + content

                    elif line_type == 'auto_skip':
                        # Enter auto-skip mode
                        auto_skip_mode = True
                        self.stats['lines_skipped'] += 1
                        print("\n⚡ Auto-skip mode activated")

                    elif line_type == 'skip':
                        self.stats['lines_skipped'] += 1

                # Reset line index for next page
                self.current_line_idx = 0

        # Add final slide
        self._add_slide()

        # Save output
        self._save_output()

        # Show statistics
        self._show_stats()

    def _save_output(self):
        """Save the final markdown output"""
        # Join all slides with separator
        output = '\n\n---\n\n'.join(self.slides)

        # Write to file
        with open(self.output_path, 'w') as f:
            f.write(output)

        print(f"\n✅ Saved to: {self.output_path}")

        # Remove progress file
        if self.progress_path.exists():
            self.progress_path.unlink()

    def _show_stats(self):
        """Display processing statistics"""
        print("\n" + "="*70)
        print("📊 PROCESSING COMPLETE")
        print("="*70)
        print(f"  Total slides:       {self.stats['slides']}")
        print(f"  Characters found:   {len(self.stats['characters'])}")
        print(f"  Lines processed:    {self.stats['lines_processed']}")
        print(f"  Lines skipped:      {self.stats['lines_skipped']}")
        print(f"\n  Characters: {', '.join(sorted(self.stats['characters']))}")
        print("="*70)


def main():
    parser = argparse.ArgumentParser(
        description='Convert PDF theater scripts to CaptionPoint markdown format'
    )
    parser.add_argument('input', help='Input PDF file')
    parser.add_argument('output', help='Output markdown file')
    parser.add_argument('--resume', action='store_true',
                        help='Resume from saved progress')

    args = parser.parse_args()

    # Validate input file
    if not Path(args.input).exists():
        print(f"❌ Error: Input file not found: {args.input}")
        sys.exit(1)

    # Create parser and process
    converter = CaptionPointParser(args.input, args.output, resume=args.resume)

    try:
        converter.process_pdf()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        converter._save_progress()
        print("💾 Progress saved. Run with --resume to continue.")
        sys.exit(0)


if __name__ == '__main__':
    main()
