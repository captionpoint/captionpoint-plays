#!/usr/bin/env python3
"""
Detailed dialogue comparison between OCR source and caption-ready script.
Extracts dialogue from OCR format (CHARACTER. dialogue) and compares to
markdown format (## CHARACTER:\ndialogue).
"""

import re
from pathlib import Path
from difflib import SequenceMatcher

def extract_ocr_dialogue(file_path):
    """Extract character dialogue from OCR source file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove line numbers (format: "     1→")
    content = re.sub(r'^\s*\d+→', '', content, flags=re.MULTILINE)

    dialogue_list = []

    # Split by character name pattern: UPPERCASE NAME followed by period
    # Character names are in format: "CHARACTER NAME. dialogue text"
    # Stage directions in parentheses should be ignored

    # Find all instances of CHARACTER. dialogue
    # Pattern: UPPERCASE NAME (one or more words) followed by period, then dialogue
    pattern = r'\b([A-Z][A-Z\s\.]+?)\.\s+([^(]+?)(?=\s+[A-Z][A-Z\s\.]+?\.|$|\(|\n\nScene)'

    matches = re.finditer(pattern, content, re.DOTALL)

    for match in matches:
        char_name = match.group(1).strip()
        dialogue_text = match.group(2).strip()

        # Skip if character name looks like a scene header
        if char_name.startswith('Scene'):
            continue

        # Skip very short "names" (likely not real character names)
        if len(char_name) < 2:
            continue

        # Clean up the dialogue - remove stage directions in parentheses
        dialogue_text = re.sub(r'\([^)]*\)', '', dialogue_text)
        dialogue_text = ' '.join(dialogue_text.split())

        # Skip if no actual dialogue text
        if not dialogue_text or len(dialogue_text) < 2:
            continue

        dialogue_list.append({
            'character': char_name,
            'text': dialogue_text
        })

    return dialogue_list

def extract_caption_dialogue(file_path):
    """Extract character dialogue from caption-ready markdown file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    dialogue_list = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # Look for character header: ## CHARACTER:
        if line.startswith('## ') and line.endswith(':'):
            char_name = line[3:-1].strip()

            # Collect dialogue from following lines until separator or next character
            dialogue_lines = []
            i += 1

            while i < len(lines):
                next_line = lines[i].strip()

                # Stop at separator or next character
                if next_line in ['---', '--'] or next_line.startswith('## '):
                    break

                # Skip empty lines
                if next_line:
                    dialogue_lines.append(next_line)

                i += 1

            if dialogue_lines:
                dialogue_text = ' '.join(dialogue_lines)
                dialogue_list.append({
                    'character': char_name,
                    'text': dialogue_text
                })
        else:
            i += 1

    return dialogue_list

def normalize_text(text):
    """Normalize text for comparison."""
    # Normalize whitespace
    text = ' '.join(text.split())
    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    # Normalize ellipsis
    text = text.replace('…', '...').replace('....', '...')
    # Remove trailing punctuation variations
    return text.strip()

def similarity_ratio(a, b):
    """Calculate similarity ratio between two strings."""
    return SequenceMatcher(None, a, b).ratio()

def main():
    ocr_file = Path('/Users/macnab/CaptionPoint/captionpoint-plays/MJ-better-OCR.md')
    caption_file = Path('/Users/macnab/CaptionPoint/captionpoint-plays/MARY-JANE-working.md')

    print("=" * 80)
    print("MARY JANE DIALOGUE COMPARISON REPORT")
    print("=" * 80)
    print()

    print("Extracting dialogue from OCR source file...")
    ocr_dialogue = extract_ocr_dialogue(ocr_file)
    print(f"Found {len(ocr_dialogue)} dialogue entries in OCR file")
    print()

    print("Extracting dialogue from caption-ready file...")
    caption_dialogue = extract_caption_dialogue(caption_file)
    print(f"Found {len(caption_dialogue)} dialogue entries in caption file")
    print()

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()

    # Show first 10 from each for comparison
    print("First 10 dialogue entries from OCR file:")
    print("-" * 80)
    for i, entry in enumerate(ocr_dialogue[:10], 1):
        text_preview = entry['text'][:100] + "..." if len(entry['text']) > 100 else entry['text']
        print(f"{i}. {entry['character']}: {text_preview}")
    print()

    print("First 10 dialogue entries from caption file:")
    print("-" * 80)
    for i, entry in enumerate(caption_dialogue[:10], 1):
        text_preview = entry['text'][:100] + "..." if len(entry['text']) > 100 else entry['text']
        print(f"{i}. {entry['character']}: {text_preview}")
    print()

    # Try to match OCR entries to caption entries
    print("=" * 80)
    print("MATCHING ANALYSIS")
    print("=" * 80)
    print()

    ocr_normalized = [normalize_text(d['text']) for d in ocr_dialogue]
    caption_normalized = [normalize_text(d['text']) for d in caption_dialogue]

    missing_count = 0
    partial_match_count = 0
    full_match_count = 0

    for i, ocr_entry in enumerate(ocr_dialogue):
        ocr_text = ocr_normalized[i]
        char_name = ocr_entry['character']

        # Look for exact match
        if ocr_text in caption_normalized:
            full_match_count += 1
            continue

        # Look for partial match (dialogue contained within caption dialogue)
        found_partial = False
        best_match_ratio = 0
        best_match_idx = -1

        for j, caption_text in enumerate(caption_normalized):
            if ocr_text in caption_text or caption_text in ocr_text:
                partial_match_count += 1
                found_partial = True
                break

            # Check similarity
            ratio = similarity_ratio(ocr_text, caption_text)
            if ratio > best_match_ratio:
                best_match_ratio = ratio
                best_match_idx = j

        if not found_partial:
            # Check if reasonably similar (>70% match)
            if best_match_ratio >= 0.7:
                partial_match_count += 1
            else:
                missing_count += 1
                if missing_count <= 20:  # Show first 20 missing
                    print(f"POSSIBLY MISSING (#{i+1}):")
                    print(f"  Character: {char_name}")
                    print(f"  OCR Text: {ocr_text[:200]}")
                    if best_match_idx >= 0:
                        print(f"  Best match ({best_match_ratio:.1%} similar):")
                        print(f"    {caption_dialogue[best_match_idx]['character']}: {caption_normalized[best_match_idx][:200]}")
                    print()

    print("=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    print()
    print(f"Total OCR dialogue entries: {len(ocr_dialogue)}")
    print(f"Total caption dialogue entries: {len(caption_dialogue)}")
    print()
    print(f"Full matches: {full_match_count}")
    print(f"Partial matches: {partial_match_count}")
    print(f"Possibly missing: {missing_count}")
    print()

    if missing_count == 0 and full_match_count + partial_match_count == len(ocr_dialogue):
        print("✓ ALL DIALOGUE APPEARS TO BE PRESENT!")
    else:
        print(f"⚠ {missing_count} dialogue entries may be missing or significantly different")
    print()

if __name__ == '__main__':
    main()
