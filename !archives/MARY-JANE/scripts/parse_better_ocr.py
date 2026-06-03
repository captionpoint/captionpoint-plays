#!/usr/bin/env python3
"""
Parse MJ-better-OCR.md and generate MARY-JANE-working.md
in CaptionPoint format.

Extracts character dialogue, strips stage directions,
preserves dialogue text exactly as-is from the source.
"""

import re
from collections import Counter

INPUT = '/Users/macnab/CaptionPoint/captionpoint-plays/MJ-better-OCR.md'
OUTPUT = '/Users/macnab/CaptionPoint/captionpoint-plays/MARY-JANE-working.md'

# Character names (including OCR error variants)
CHAR_NAMES = [
    'MARY JANE', 'RUTHIE', 'SHERRY', 'BRIANNE',
    'DR. TOROS', 'AMELIA', 'CHAYA', 'KAT', 'TENKEI',
    'TENKE!', 'TENKEl',
]

# OCR name normalization
NAME_MAP = {
    'TENKE!': 'TENKEI',
    'TENKEl': 'TENKEI',
}

# Escape names for regex, sort longest-first so "MARY JANE" matches before substrings
escaped = sorted([re.escape(n) for n in CHAR_NAMES], key=len, reverse=True)

# Character speaking pattern: word boundary + NAME + period + whitespace
# This only matches speaking indicators (CHARACTER.), not character refs in stage directions
CHAR_RE = re.compile(r'\b(' + '|'.join(escaped) + r')\.\s+')

# Scene header pattern - matches "Scene One: ..." up to the next ( or end of text
SCENE_RE = re.compile(r'Scene\s+(?:One|Two|Three|Four)\s*:[^(\n]*', re.IGNORECASE)

# Stage direction pattern - balanced parentheses
STAGE_DIR_RE = re.compile(r'\([^)]*\)')


def strip_stage_directions(text):
    """Remove all (parenthetical) stage directions."""
    result = STAGE_DIR_RE.sub('', text)
    # Remove any remaining unbalanced parens (OCR artifacts)
    result = result.replace('(', '').replace(')', '')
    return result


def clean_dialogue(text):
    """Clean up whitespace artifacts from stage direction removal."""
    # Collapse multiple spaces to single space
    text = re.sub(r'  +', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text


def main():
    with open(INPUT, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Build full text, filtering scene headers and structural elements
    parts = []
    for line in lines:
        line = line.strip()

        # Skip blank lines
        if not line:
            continue

        # Skip "END"
        if line == 'END':
            continue

        # Remove scene headers (may be standalone or embedded in text)
        line = SCENE_RE.sub('', line).strip()

        # Skip if nothing remains
        if not line:
            continue

        parts.append(line)

    full_text = ' '.join(parts)

    # Find all character speaking instances
    matches = list(CHAR_RE.finditer(full_text))

    if not matches:
        print("ERROR: No character dialogue found!")
        return

    # Extract dialogue blocks
    blocks = []
    for i, m in enumerate(matches):
        name = NAME_MAP.get(m.group(1), m.group(1))
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)

        # Get raw dialogue (may contain stage directions)
        raw_dialogue = full_text[start:end]

        # Strip stage directions
        dialogue = strip_stage_directions(raw_dialogue)

        # Clean up whitespace
        dialogue = clean_dialogue(dialogue)

        # Skip empty blocks (character had only stage directions, no speech)
        if dialogue:
            blocks.append((name, dialogue))

    # Deduplicate consecutive identical blocks (handles OCR page duplicates)
    deduped = []
    for b in blocks:
        if not deduped or b != deduped[-1]:
            deduped.append(b)

    # Write output in CaptionPoint format
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        for name, dialogue in deduped:
            f.write(f'---\n\n## {name}:\n{dialogue}\n\n')

    # Print statistics
    counts = Counter(n for n, _ in deduped)
    print(f"Generated {len(deduped)} dialogue blocks")
    print(f"Output: {OUTPUT}")
    print()
    for name in sorted(counts):
        print(f"  {name}: {counts[name]}")


if __name__ == '__main__':
    main()
