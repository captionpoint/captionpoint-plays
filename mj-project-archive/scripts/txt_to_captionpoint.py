#!/usr/bin/env python3
"""
Convert OCR'd text file to CaptionPoint markdown format.
Simpler than PDF parser - works with plain text files.
"""

import re
import sys
import argparse


def is_character_name(line):
    """Check if line looks like a character name."""
    # Character names are typically ALL CAPS followed by period
    # Examples: MARY JANE. RUTHIE. DR. TOROS.
    line = line.strip()
    if not line:
        return False

    # Must end with period
    if not line.endswith('.'):
        return False

    # Remove the period and check if mostly uppercase
    name = line[:-1].strip()

    # Must have at least 2 letters
    letters = [c for c in name if c.isalpha()]
    if len(letters) < 2:
        return False

    # Must be at least 70% uppercase letters
    uppercase = [c for c in letters if c.isupper()]
    if len(uppercase) / len(letters) >= 0.7:
        return True

    return False


def is_stage_direction(line):
    """Check if line is a stage direction (in parentheses)."""
    line = line.strip()
    return line.startswith('(') and line.endswith(')')


def is_scene_header(line):
    """Check if line is a scene header or title."""
    line = line.strip().upper()
    keywords = ['SCENE', 'ACT', 'PART ONE', 'PART TWO', 'PROLOGUE', 'EPILOGUE']
    return any(keyword in line for keyword in keywords)


def is_page_number(line):
    """Check if line is just a page number."""
    line = line.strip()
    return line.isdigit() or (len(line) <= 3 and any(c.isdigit() for c in line))


def clean_character_name(line):
    """Extract clean character name from line."""
    # Remove period and extra whitespace
    name = line.strip().rstrip('.')
    # Convert to title case-ish (keep first letter of each word caps)
    words = name.split()
    # Keep names like "MARY JANE" but format as "MARY-JANE"
    return '-'.join(words)


def process_text_file(input_file, output_file, start_line=0):
    """Process text file and convert to CaptionPoint markdown."""

    print(f"\n📄 Processing: {input_file}")
    print(f"💾 Output to: {output_file}")
    print("\n" + "="*70)
    print("Instructions:")
    print("  - Character names will be auto-detected (ALL CAPS.)")
    print("  - Stage directions in (parentheses) will be highlighted")
    print("  - Press ENTER to accept, or edit the line")
    print("  - Type 'skip' to skip a section")
    print("  - Type 'quit' to save and exit")
    print("="*70 + "\n")

    # Read input file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"❌ Error: File '{input_file}' not found")
        return False

    # Open output file for writing
    output_lines = []
    current_character = None
    current_dialogue = []

    # Skip to start line if resuming
    for i, line in enumerate(lines[start_line:], start=start_line):
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Skip page numbers
        if is_page_number(line):
            continue

        # Check for character name
        if is_character_name(line):
            # Save previous character's dialogue if any
            if current_character and current_dialogue:
                output_lines.append(f"## {current_character}:")
                output_lines.append(' '.join(current_dialogue))
                output_lines.append("\n---\n")
                current_dialogue = []

            # Set new character
            current_character = clean_character_name(line)
            print(f"\n✨ Character: {current_character}")
            continue

        # Skip stage directions
        if is_stage_direction(line):
            print(f"  ⏩ Stage direction: {line[:50]}...")
            continue

        # Skip scene headers
        if is_scene_header(line):
            print(f"  📍 Scene: {line}")
            # Add scene separator
            if output_lines:
                output_lines.append("\n---\n")
            continue

        # Regular dialogue line
        if current_character:
            # Show the line
            print(f"  💬 {line[:70]}...")
            current_dialogue.append(line)

    # Save last character's dialogue
    if current_character and current_dialogue:
        output_lines.append(f"## {current_character}:")
        output_lines.append(' '.join(current_dialogue))
        output_lines.append("\n---\n")

    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))

    print("\n" + "="*70)
    print(f"✅ Processing complete!")
    print(f"📊 Wrote {len(output_lines)} lines to {output_file}")
    print("="*70)

    return True


def main():
    parser = argparse.ArgumentParser(
        description='Convert OCR\'d text to CaptionPoint markdown'
    )
    parser.add_argument('input', help='Input text file')
    parser.add_argument('output', help='Output markdown file')
    parser.add_argument('--start', type=int, default=0,
                       help='Start processing from line N')

    args = parser.parse_args()

    success = process_text_file(args.input, args.output, args.start)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
