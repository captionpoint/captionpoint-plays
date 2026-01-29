#!/usr/bin/env python3
"""
Final comprehensive dialogue comparison report.
Extracts and compares all character dialogue between OCR and caption files.
"""

import re
from pathlib import Path
from difflib import SequenceMatcher
from collections import defaultdict

def extract_ocr_dialogue(file_path):
    """
    Extract character dialogue from OCR source.
    Character dialogue follows pattern: CHARACTER NAME. dialogue text
    Stage directions are in parentheses and should be excluded.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove line numbers
    content = re.sub(r'^\s*\d+→', '', content, flags=re.MULTILINE)

    dialogue_list = []

    # Find all character dialogue
    # Pattern: Word boundary, UPPERCASE NAME (potentially multi-word), period, space, then dialogue
    # Must not be inside parentheses (stage direction)

    # First, remove all stage directions to avoid false matches
    # Stage directions are in parentheses, potentially multi-line
    cleaned = re.sub(r'\([^)]*\)', ' ', content)

    # Now find CHARACTER. dialogue patterns
    pattern = r'\b([A-Z][A-Z\s&\.]+?)\.\s+([^.!?]+[.!?])'

    matches = re.finditer(pattern, cleaned)

    for match in matches:
        char_name = match.group(1).strip()
        dialogue_text = match.group(2).strip()

        # Filter out false positives
        # Skip if "name" contains common stage direction words
        skip_words = ['SHERRY prepares', 'MARY JANE exits', 'enters', 'Offstage',
                      'Brief pause', 'Pause', 'Long pause', 'They', 'She', 'He']
        if any(word in char_name or word in dialogue_text[:30] for word in skip_words):
            continue

        # Skip if name is likely a scene header
        if char_name.startswith('Scene') or 'Scene' in char_name:
            continue

        # Skip if name contains stage direction indicators
        if any(word in char_name for word in ['exits', 'enters', 'appears', 'prepares', 'turns']):
            continue

        # Character names should be relatively short (under 30 chars usually)
        if len(char_name) > 30:
            continue

        # Skip very short dialogue (likely extraction error)
        if len(dialogue_text) < 5:
            continue

        dialogue_list.append({
            'character': char_name,
            'text': dialogue_text.strip()
        })

    # Additional pass: Look for longer dialogue blocks
    # Pattern: CHARACTER. followed by longer text before next CHARACTER.
    pattern2 = r'\b([A-Z][A-Z\s]+?)\.\s+([^(]+?)(?=\s+[A-Z][A-Z\s]+?\.|Scene\s|$)'

    matches2 = re.finditer(pattern2, cleaned, re.DOTALL)

    seen = set()
    dialogue_list2 = []

    for match in matches2:
        char_name = match.group(1).strip()
        dialogue_text = match.group(2).strip()

        # Same filters as above
        if any(word in char_name for word in ['enters', 'exits', 'prepares', 'appears', 'turns', 'Scene']):
            continue

        if len(char_name) > 25:
            continue

        # Clean up dialogue text
        dialogue_text = ' '.join(dialogue_text.split())

        if len(dialogue_text) < 10:
            continue

        # Avoid duplicates
        key = (char_name, dialogue_text[:100])
        if key in seen:
            continue
        seen.add(key)

        dialogue_list2.append({
            'character': char_name,
            'text': dialogue_text.strip()
        })

    # Combine and deduplicate
    all_dialogue = dialogue_list + dialogue_list2
    unique_dialogue = []
    seen_texts = set()

    for entry in all_dialogue:
        text_key = (entry['character'], entry['text'][:150])
        if text_key not in seen_texts:
            seen_texts.add(text_key)
            unique_dialogue.append(entry)

    return sorted(unique_dialogue, key=lambda x: all_dialogue.index(next(d for d in all_dialogue if d['character'] == x['character'] and d['text'] == x['text'])))

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

            # Collect dialogue from following lines
            dialogue_lines = []
            i += 1

            while i < len(lines):
                next_line = lines[i].strip()

                # Stop at separator or next character
                if next_line in ['---', '--'] or next_line.startswith('## '):
                    break

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
    text = ' '.join(text.split())
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    text = text.replace('…', '...')
    return text.strip().lower()

def main():
    ocr_file = Path('/Users/macnab/CaptionPoint/captionpoint-plays/MJ-better-OCR.md')
    caption_file = Path('/Users/macnab/CaptionPoint/captionpoint-plays/MARY-JANE-working.md')

    print("=" * 80)
    print("MARY JANE SCRIPT DIALOGUE VERIFICATION REPORT")
    print("=" * 80)
    print()
    print(f"OCR Source: {ocr_file.name}")
    print(f"Caption File: {caption_file.name}")
    print()

    ocr_dialogue = extract_ocr_dialogue(ocr_file)
    caption_dialogue = extract_caption_dialogue(caption_file)

    print(f"OCR dialogue entries extracted: {len(ocr_dialogue)}")
    print(f"Caption dialogue entries extracted: {len(caption_dialogue)}")
    print()

    # Normalize all texts
    ocr_norm = [normalize_text(d['text']) for d in ocr_dialogue]
    cap_norm = [normalize_text(d['text']) for d in caption_dialogue]

    # Create set for faster lookup
    cap_norm_set = set(cap_norm)

    # Check each OCR entry
    exact_matches = 0
    partial_matches = 0
    missing = []

    for i, ocr_entry in enumerate(ocr_dialogue):
        ocr_text_norm = ocr_norm[i]

        # Check for exact match
        if ocr_text_norm in cap_norm_set:
            exact_matches += 1
            continue

        # Check for partial match (OCR text is substring of caption text or vice versa)
        found = False
        for cap_text in cap_norm:
            if ocr_text_norm in cap_text or cap_text in ocr_text_norm:
                if len(ocr_text_norm) > 20 or len(cap_text) > 20:  # Avoid matching very short phrases
                    partial_matches += 1
                    found = True
                    break

        if not found:
            # Check similarity with best match
            best_ratio = 0
            best_match = None
            for j, cap_text in enumerate(cap_norm):
                ratio = SequenceMatcher(None, ocr_text_norm, cap_text).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = caption_dialogue[j]

            if best_ratio >= 0.65:  # 65% similarity threshold
                partial_matches += 1
            else:
                missing.append({
                    'ocr': ocr_entry,
                    'best_match': best_match,
                    'similarity': best_ratio
                })

    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print()
    print(f"Exact matches: {exact_matches}")
    print(f"Partial matches (variations, truncations): {partial_matches}")
    print(f"Potentially missing: {len(missing)}")
    print()

    if len(missing) > 0:
        print("=" * 80)
        print("POTENTIALLY MISSING DIALOGUE (showing first 15)")
        print("=" * 80)
        print()
        for i, entry in enumerate(missing[:15], 1):
            print(f"{i}. CHARACTER: {entry['ocr']['character']}")
            print(f"   OCR TEXT: {entry['ocr']['text'][:150]}")
            if entry['best_match']:
                print(f"   BEST MATCH ({entry['similarity']:.1%}): {entry['best_match']['character']}")
                print(f"   CAPTION TEXT: {entry['best_match']['text'][:150]}")
            print()

    print("=" * 80)
    print("OVERALL ASSESSMENT")
    print("=" * 80)
    print()

    total_matched = exact_matches + partial_matches
    match_rate = (total_matched / len(ocr_dialogue) * 100) if ocr_dialogue else 0

    print(f"Match rate: {match_rate:.1f}% ({total_matched}/{len(ocr_dialogue)})")
    print()

    if match_rate >= 98:
        print("✓ EXCELLENT: Dialogue appears complete and accurate")
    elif match_rate >= 95:
        print("✓ VERY GOOD: Minor discrepancies, mostly complete")
    elif match_rate >= 90:
        print("⚠ GOOD: Some dialogue may be missing or modified")
    elif match_rate >= 80:
        print("⚠ FAIR: Significant portions may be missing")
    else:
        print("✗ POOR: Many dialogue entries appear to be missing")

    print()

if __name__ == '__main__':
    main()
