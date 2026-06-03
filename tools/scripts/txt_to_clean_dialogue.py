#!/usr/bin/env python3
"""
Convert OCR'd theater script text to clean, readable dialogue format.

Removes stage directions, scene headers, and front matter.
Formats character dialogue into separate paragraphs.
"""

import re
import sys
import argparse
from collections import defaultdict


class DialogueFormatter:
    """Format OCR'd script text into clean character dialogue."""

    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file

        # Character names (include OCR error variants)
        self.character_names = [
            'MARY JANE', '1ARY JANE', 'l ARY JANE', 'IMARY JANE',  # OCR variants
            'RUTHIE',
            'BRIANNE',
            'SHERRY',
            'DR. TOROS',
            'AMELIA',
            'CHAYA',
            'KAT',
            'TENKEI'
        ]

        # OCR error fixes
        self.ocr_fixes = {
            '1ARY JANE': 'MARY JANE',
            'l ARY JANE': 'MARY JANE',
            'IMARY JANE': 'MARY JANE',
            'trafﬁc': 'traffic',
            'ﬁ': 'fi',
            'ﬂ': 'fl',
            'ﬁnally': 'finally',
            'ﬁrst': 'first',
            'ﬂoor': 'floor',
        }

        # Build character detection pattern
        # Escape periods in names like "DR. TOROS"
        names_escaped = [name.replace('.', r'\.') for name in self.character_names]
        self.char_pattern = re.compile(
            r'\b(' + '|'.join(names_escaped) + r')\.\s+',
            re.IGNORECASE
        )

        # Statistics
        self.stats = {
            'lines_processed': 0,
            'lines_skipped': 0,
            'stage_directions_removed': 0,
            'ocr_errors_fixed': 0,
            'dialogue_blocks': 0,
            'characters_found': defaultdict(int)
        }

    def remove_stage_directions(self, text):
        """Remove content in parentheses (stage directions)."""
        original = text
        # Remove (stage directions)
        text = re.sub(r'\([^)]*\)', '', text)

        if text != original:
            self.stats['stage_directions_removed'] += 1

        return text

    def fix_ocr_errors(self, text):
        """Fix common OCR errors."""
        original = text
        for error, fix in self.ocr_fixes.items():
            text = text.replace(error, fix)

        if text != original:
            self.stats['ocr_errors_fixed'] += 1

        return text

    def is_scene_header(self, line):
        """Check if line is a scene header or structural element."""
        line_upper = line.upper().strip()

        # Scene headers and structural keywords
        keywords = [
            'PART ONE', 'PART TWO',
            'ACT I', 'ACT II', 'ACT III', 'ACT IV', 'ACT V',
            'SCENE ONE', 'SCENE TWO', 'SCENE THREE', 'SCENE FOUR', 'SCENE FIVE',
            'PROLOGUE', 'EPILOGUE',
            'CHARACTERS', 'SETTING', 'TIME',
        ]

        # Check if line starts with or contains these keywords
        for keyword in keywords:
            if keyword in line_upper:
                return True

        # Also check for "Scene X:" pattern
        if re.match(r'Scene\s+\w+:', line, re.IGNORECASE):
            return True

        return False

    def is_page_number(self, line):
        """Check if line is just a page number."""
        line = line.strip()
        # Just digits
        if line.isdigit():
            return True
        # Roman numerals or single characters
        if len(line) <= 3 and not any(c.isalpha() and c not in 'IVXLCDM' for c in line):
            return True
        return False

    def normalize_character_name(self, name):
        """Normalize character name (fix OCR errors, standardize format)."""
        name = name.strip().upper()

        # Apply OCR fixes
        for error, fix in self.ocr_fixes.items():
            if error.upper() in name:
                name = name.replace(error.upper(), fix.upper())

        # Handle "DR. TOROS" variants
        if 'DR' in name and 'TOROS' in name:
            name = 'DR. TOROS'

        return name

    def split_on_characters(self, line):
        """
        Split line on character name patterns.
        Returns list of (character, dialogue) tuples.
        """
        if not line.strip():
            return []

        results = []

        # Find all character name matches
        matches = list(self.char_pattern.finditer(line))

        if not matches:
            return []

        for i, match in enumerate(matches):
            char_name = self.normalize_character_name(match.group(1))

            # Extract dialogue: from end of this match to start of next match (or end of line)
            start_pos = match.end()
            if i + 1 < len(matches):
                end_pos = matches[i + 1].start()
            else:
                end_pos = len(line)

            dialogue = line[start_pos:end_pos].strip()
            results.append((char_name, dialogue))

        return results

    def output_dialogue_block(self, character, dialogue_lines, output_file):
        """Write a character's dialogue block to output file."""
        if not character or not dialogue_lines:
            return

        # Join dialogue lines with spaces
        dialogue_text = ' '.join(dialogue_lines).strip()

        if dialogue_text:
            output_file.write(f"{character}\n")
            output_file.write(f"{dialogue_text}\n")
            output_file.write("\n")  # Blank line separator

            self.stats['dialogue_blocks'] += 1
            self.stats['characters_found'][character] += 1

    def process(self):
        """Main processing method."""
        print(f"\n📄 Processing: {self.input_file}")
        print(f"💾 Output to: {self.output_file}")
        print("\n" + "="*70)

        # Read input file
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"❌ Error: File '{self.input_file}' not found")
            return False

        # Open output file
        with open(self.output_file, 'w', encoding='utf-8') as out_f:
            current_character = None
            current_dialogue = []
            found_part_one = False

            for line_num, line in enumerate(lines, 1):
                self.stats['lines_processed'] += 1

                # Skip until we find "PART ONE"
                if not found_part_one:
                    if 'PART ONE' in line.upper():
                        found_part_one = True
                        print(f"✓ Found 'PART ONE' at line {line_num}, starting processing...")
                    self.stats['lines_skipped'] += 1
                    continue

                # Clean the line
                line = self.remove_stage_directions(line)
                line = self.fix_ocr_errors(line)
                line = line.strip()

                # Skip empty lines
                if not line:
                    continue

                # Skip scene headers
                if self.is_scene_header(line):
                    continue

                # Skip page numbers
                if self.is_page_number(line):
                    continue

                # Check for character names in this line
                splits = self.split_on_characters(line)

                if splits:
                    # Found character(s) in this line
                    for char_name, dialogue_text in splits:
                        # Output previous character's dialogue
                        if current_character and current_dialogue:
                            self.output_dialogue_block(current_character, current_dialogue, out_f)

                        # Start new character
                        current_character = char_name
                        current_dialogue = [dialogue_text] if dialogue_text else []
                else:
                    # Continuation of current character's dialogue
                    if current_character and line:
                        current_dialogue.append(line)

            # Output final character's dialogue
            if current_character and current_dialogue:
                self.output_dialogue_block(current_character, current_dialogue, out_f)

        # Print statistics
        self.print_statistics()

        return True

    def print_statistics(self):
        """Print processing statistics."""
        print("\n" + "="*70)
        print("📊 PROCESSING COMPLETE")
        print("="*70)
        print(f"  Lines processed:         {self.stats['lines_processed']}")
        print(f"  Lines skipped (front):   {self.stats['lines_skipped']}")
        print(f"  Dialogue blocks created: {self.stats['dialogue_blocks']}")
        print(f"  Stage directions removed: {self.stats['stage_directions_removed']}")
        print(f"  OCR errors fixed:        {self.stats['ocr_errors_fixed']}")
        print()
        print("  Characters found:")
        for char, count in sorted(self.stats['characters_found'].items()):
            print(f"    {char}: {count} dialogue blocks")
        print("="*70)


def main():
    parser = argparse.ArgumentParser(
        description='Convert OCR\'d script to clean dialogue format'
    )
    parser.add_argument('input', help='Input text file (OCR\'d script)')
    parser.add_argument('output', help='Output text file (clean dialogue)')

    args = parser.parse_args()

    formatter = DialogueFormatter(args.input, args.output)
    success = formatter.process()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
