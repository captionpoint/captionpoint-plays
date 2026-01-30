#!/usr/bin/env python3
"""
Compare source OCR text with cleaned output to find missing dialogue sections.
"""

import sys
import re


def extract_dialogue_from_source(filename):
    """Extract dialogue snippets from source file."""
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()

    # Find character names followed by dialogue
    pattern = r'(MARY JANE|RUTHIE|BRIANNE|SHERRY|DR\. TOROS|AMELIA|CHAYA|KAT|TENKEI)\.\s+([^.]{20,80})'
    matches = re.findall(pattern, text, re.IGNORECASE)

    return matches


def check_in_cleaned_file(cleaned_file, dialogue_snippet):
    """Check if dialogue snippet exists in cleaned file."""
    with open(cleaned_file, 'r', encoding='utf-8') as f:
        cleaned_text = f.read()

    # Clean up the snippet for comparison (remove special chars, lowercase)
    clean_snippet = re.sub(r'[^\w\s]', '', dialogue_snippet).lower()
    clean_file = re.sub(r'[^\w\s]', '', cleaned_text).lower()

    return clean_snippet in clean_file


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 find_missing_dialogue.py source.txt cleaned.txt")
        sys.exit(1)

    source_file = sys.argv[1]
    cleaned_file = sys.argv[2]

    print(f"📄 Comparing {source_file} with {cleaned_file}...")
    print("="*70)

    # Extract all dialogue from source
    dialogue_samples = extract_dialogue_from_source(source_file)

    print(f"Found {len(dialogue_samples)} dialogue snippets in source\n")

    # Check which ones are missing
    missing = []
    for character, dialogue in dialogue_samples:
        if not check_in_cleaned_file(cleaned_file, dialogue):
            missing.append((character, dialogue))

    if missing:
        print(f"⚠️  Found {len(missing)} potentially missing dialogue sections:\n")
        for i, (char, dialogue) in enumerate(missing[:20], 1):  # Show first 20
            print(f"{i}. {char}: {dialogue[:60]}...")

        if len(missing) > 20:
            print(f"\n...and {len(missing) - 20} more")
    else:
        print("✅ All dialogue snippets found in cleaned file!")

    print("\n" + "="*70)
    print(f"Missing: {len(missing)} / {len(dialogue_samples)} snippets")


if __name__ == '__main__':
    main()
