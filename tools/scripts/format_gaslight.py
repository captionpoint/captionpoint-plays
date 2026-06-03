#!/usr/bin/env python3
"""
Format Gaslight script to CaptionPoint markdown format.
- Splits lines with multiple characters
- Converts CHARACTER. to ## CHARACTER:
- Adds --- slide separators
- Joins continuation lines with their character
"""

import re

# Known character names in the play
CHARACTERS = ['JACK', 'BELLA', 'NANCY', 'ELIZABETH', 'SERGEANT ROUGH']

def split_multi_character_lines(text):
    """Split lines that have multiple CHARACTER. patterns."""
    lines = text.split('\n')
    result = []

    for line in lines:
        # Check if line has multiple character speeches
        # Pattern: end of one speech followed by CHARACTER.
        parts = re.split(r'(?<=[.!?"\'])\s+(?=(?:' + '|'.join(CHARACTERS) + r')\.)', line)

        if len(parts) > 1:
            for part in parts:
                part = part.strip()
                if part:
                    result.append(part)
        else:
            result.append(line)

    return '\n'.join(result)

def join_continuation_lines(text):
    """Join lines that continue dialogue (don't start with a character name)."""
    lines = text.split('\n')
    result = []
    char_pattern = re.compile(r'^(' + '|'.join(CHARACTERS) + r')\.')

    for line in lines:
        stripped = line.strip()
        if not stripped:
            result.append('')
            continue

        # If line starts with a character name, it's a new dialogue
        if char_pattern.match(stripped):
            result.append(stripped)
        # If line starts with lowercase or continues previous dialogue
        elif result and result[-1] and not result[-1].startswith('---'):
            # Join with previous line
            result[-1] = result[-1] + ' ' + stripped
        else:
            result.append(stripped)

    return '\n'.join(result)

def convert_to_captionpoint(text):
    """Convert CHARACTER. dialogue to ## CHARACTER: format with --- separators."""
    lines = text.split('\n')
    result = []
    char_pattern = re.compile(r'^(' + '|'.join(CHARACTERS) + r')\.\s*(.*)')

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        match = char_pattern.match(stripped)
        if match:
            character = match.group(1)
            dialogue = match.group(2)

            # Add separator before each new character line (except first)
            if result:
                result.append('---')
                result.append('')

            result.append(f'## {character}:')
            if dialogue:
                result.append(dialogue)
        else:
            # Non-dialogue line (shouldn't happen after cleanup, but just in case)
            result.append(stripped)

    # Add final separator
    result.append('')
    result.append('---')

    return '\n'.join(result)

def main():
    input_file = 'GASLIGHT-clean.md'
    output_file = 'GASLIGHT-formatted.md'

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Step 1: Split lines with multiple characters
    content = split_multi_character_lines(content)

    # Step 2: Join continuation lines
    content = join_continuation_lines(content)

    # Step 3: Convert to CaptionPoint format
    content = convert_to_captionpoint(content)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Formatted script written to {output_file}")

if __name__ == '__main__':
    main()
