#!/usr/bin/env python3
"""
Compare dialogue between OCR source and caption-ready script.
Extracts only character dialogue from both files and compares them.
"""

import re
from pathlib import Path

def extract_dialogue_from_ocr(file_path):
    """Extract character dialogue from OCR file, ignoring stage directions."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    dialogue = []
    lines = content.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Remove line numbers from OCR (format: "     1→")
        line = re.sub(r'^\s*\d+→', '', line).strip()

        # Skip empty lines, scene headers, and stage directions
        if not line:
            i += 1
            continue
        if line.startswith('Scene ') or line.startswith('('):
            i += 1
            continue

        # Check if line is a character name (all caps, followed by period or just text)
        # Character names in OCR are like "MARY JANE." or just start dialogue
        parts = line.split('.', 1)
        if len(parts) == 2:
            char_name = parts[0].strip()
            # Check if it's all caps (character name)
            if char_name.isupper() and len(char_name.split()) <= 3:
                dialogue_text = parts[1].strip()

                # Continue reading dialogue until we hit another character or stage direction
                full_dialogue = dialogue_text
                i += 1
                while i < len(lines):
                    next_line = lines[i].strip()
                    next_line = re.sub(r'^\s*\d+→', '', next_line).strip()

                    # Stop if empty, new character, stage direction, or scene header
                    if not next_line or next_line.startswith('(') or next_line.startswith('Scene '):
                        break

                    # Check if next line is a new character
                    next_parts = next_line.split('.', 1)
                    if len(next_parts) == 2 and next_parts[0].strip().isupper():
                        break

                    # Otherwise, it's continuation of dialogue
                    full_dialogue += ' ' + next_line
                    i += 1

                dialogue.append({
                    'character': char_name,
                    'text': full_dialogue
                })
                continue

        i += 1

    return dialogue

def extract_dialogue_from_caption(file_path):
    """Extract character dialogue from caption-ready markdown file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    dialogue = []
    lines = content.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Skip empty lines
        if not line:
            i += 1
            continue

        # Check for character name (markdown H2 format: "## CHARACTER:")
        if line.startswith('## ') and line.endswith(':'):
            char_name = line[3:-1].strip()

            # Get the dialogue (next non-empty line)
            i += 1
            dialogue_text = ''
            while i < len(lines):
                next_line = lines[i].strip()

                # Skip separator lines
                if next_line == '---' or next_line == '--':
                    i += 1
                    break

                # Stop at next character
                if next_line.startswith('## '):
                    break

                # Skip empty lines
                if not next_line:
                    i += 1
                    continue

                # Add to dialogue
                if dialogue_text:
                    dialogue_text += ' ' + next_line
                else:
                    dialogue_text = next_line
                i += 1

            dialogue.append({
                'character': char_name,
                'text': dialogue_text
            })
            continue

        i += 1

    return dialogue

def normalize_text(text):
    """Normalize text for comparison."""
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Remove special quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    # Remove ellipsis variations
    text = text.replace('...', '…')
    return text

def compare_dialogues(ocr_dialogue, caption_dialogue):
    """Compare two dialogue lists and find discrepancies."""
    discrepancies = []

    print(f"\nOCR file has {len(ocr_dialogue)} dialogue entries")
    print(f"Caption file has {len(caption_dialogue)} dialogue entries")

    # Compare each entry
    min_len = min(len(ocr_dialogue), len(caption_dialogue))

    for i in range(min_len):
        ocr_entry = ocr_dialogue[i]
        cap_entry = caption_dialogue[i]

        # Check character names
        if ocr_entry['character'].upper() != cap_entry['character'].upper():
            discrepancies.append({
                'type': 'character_mismatch',
                'position': i + 1,
                'ocr_char': ocr_entry['character'],
                'cap_char': cap_entry['character'],
                'ocr_text': ocr_entry['text'][:100],
                'cap_text': cap_entry['text'][:100]
            })
            continue

        # Normalize and compare dialogue text
        ocr_text = normalize_text(ocr_entry['text'])
        cap_text = normalize_text(cap_entry['text'])

        if ocr_text != cap_text:
            # Calculate similarity
            if ocr_text in cap_text or cap_text in ocr_text:
                disc_type = 'partial_match'
            else:
                disc_type = 'text_mismatch'

            discrepancies.append({
                'type': disc_type,
                'position': i + 1,
                'character': ocr_entry['character'],
                'ocr_text': ocr_text,
                'cap_text': cap_text
            })

    # Check for missing entries
    if len(ocr_dialogue) > len(caption_dialogue):
        for i in range(min_len, len(ocr_dialogue)):
            discrepancies.append({
                'type': 'missing_in_caption',
                'position': i + 1,
                'character': ocr_dialogue[i]['character'],
                'text': ocr_dialogue[i]['text'][:200]
            })
    elif len(caption_dialogue) > len(ocr_dialogue):
        for i in range(min_len, len(caption_dialogue)):
            discrepancies.append({
                'type': 'extra_in_caption',
                'position': i + 1,
                'character': caption_dialogue[i]['character'],
                'text': caption_dialogue[i]['text'][:200]
            })

    return discrepancies

def main():
    ocr_file = Path('/Users/macnab/CaptionPoint/captionpoint-plays/MJ-better-OCR.md')
    caption_file = Path('/Users/macnab/CaptionPoint/captionpoint-plays/MARY-JANE-working.md')

    print("Extracting dialogue from OCR file...")
    ocr_dialogue = extract_dialogue_from_ocr(ocr_file)

    print("Extracting dialogue from caption file...")
    caption_dialogue = extract_dialogue_from_caption(caption_file)

    print("\nComparing dialogues...")
    discrepancies = compare_dialogues(ocr_dialogue, caption_dialogue)

    if not discrepancies:
        print("\n✓ ALL DIALOGUE MATCHES PERFECTLY!")
        return

    print(f"\n✗ Found {len(discrepancies)} discrepancies:\n")

    for disc in discrepancies[:50]:  # Show first 50
        print("=" * 80)
        print(f"Position: {disc['position']}")
        print(f"Type: {disc['type']}")

        if disc['type'] == 'character_mismatch':
            print(f"OCR Character: {disc['ocr_char']}")
            print(f"Caption Character: {disc['cap_char']}")
            print(f"OCR Text: {disc['ocr_text']}")
            print(f"Caption Text: {disc['cap_text']}")

        elif disc['type'] in ['text_mismatch', 'partial_match']:
            print(f"Character: {disc['character']}")
            print(f"\nOCR Text:\n{disc['ocr_text'][:300]}")
            print(f"\nCaption Text:\n{disc['cap_text'][:300]}")

        elif disc['type'] == 'missing_in_caption':
            print(f"Character: {disc['character']}")
            print(f"Text: {disc['text']}")
            print("⚠ THIS DIALOGUE IS MISSING FROM CAPTION FILE")

        elif disc['type'] == 'extra_in_caption':
            print(f"Character: {disc['character']}")
            print(f"Text: {disc['text']}")
            print("⚠ THIS DIALOGUE IS EXTRA IN CAPTION FILE")

    if len(discrepancies) > 50:
        print(f"\n... and {len(discrepancies) - 50} more discrepancies")

    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()
