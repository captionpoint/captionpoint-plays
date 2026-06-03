#!/usr/bin/env python3
"""
Break up long dialogue lines in CaptionPoint format.
Splits at sentence boundaries and creates new slides when needed.
"""

import re

# Maximum characters per slide before we split
MAX_CHARS = 150

def split_into_sentences(text):
    """Split text into sentences, keeping punctuation attached."""
    # Split on sentence-ending punctuation followed by space
    # But be careful with abbreviations, quotes, etc.
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z"\'])', text)
    return [s.strip() for s in sentences if s.strip()]

def chunk_dialogue(dialogue, max_chars=MAX_CHARS):
    """Break dialogue into chunks that fit within max_chars."""
    sentences = split_into_sentences(dialogue)

    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        sentence_len = len(sentence)

        # If single sentence is too long, we have to include it as-is
        if sentence_len > max_chars and not current_chunk:
            chunks.append(sentence)
            continue

        # If adding this sentence would exceed limit, start new chunk
        if current_length + sentence_len + 1 > max_chars and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
            current_length = sentence_len
        else:
            current_chunk.append(sentence)
            current_length += sentence_len + (1 if current_chunk else 0)

    # Don't forget the last chunk
    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

def process_file(input_file, output_file, max_chars=MAX_CHARS):
    """Process the formatted script and break up long dialogues."""
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into slides (separator is ---)
    parts = re.split(r'\n---\n', content)

    new_parts = []

    for part in parts:
        part = part.strip()
        if not part:
            continue

        lines = part.split('\n')

        # Check if this is a character dialogue block
        if lines and lines[0].startswith('## '):
            character_line = lines[0]
            dialogue = ' '.join(lines[1:]) if len(lines) > 1 else ''

            if len(dialogue) > max_chars:
                # Need to chunk this dialogue
                chunks = chunk_dialogue(dialogue, max_chars)
                for chunk in chunks:
                    new_parts.append(f"{character_line}\n{chunk}")
            else:
                # Keep as-is
                new_parts.append(part)
        else:
            # Not a dialogue block, keep as-is
            new_parts.append(part)

    # Join with separators and blank lines for readability
    output = '\n---\n\n'.join(new_parts)
    output += '\n---\n'

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output)

    print(f"Processed {len(parts)} slides into {len(new_parts)} slides")
    print(f"(max {max_chars} chars per dialogue)")

if __name__ == '__main__':
    import sys

    input_file = sys.argv[1] if len(sys.argv) > 1 else 'GASLIGHT-formatted.md'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'GASLIGHT-chunked.md'
    max_chars = int(sys.argv[3]) if len(sys.argv) > 3 else MAX_CHARS

    process_file(input_file, output_file, max_chars)
