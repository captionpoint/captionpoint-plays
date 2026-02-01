#!/usr/bin/env python3
"""
CaptionPoint Script Formatting Toolkit

A unified toolkit for converting play scripts to CaptionPoint markdown format.
Supports multiple input formats and provides modular processing steps.

Usage:
    python caption_toolkit.py <command> [options] <input_file> <output_file>

Commands:
    clean       Remove stage directions (parenthetical text) from scripts
    format      Convert CHARACTER. dialogue to ## CHARACTER: format
    chunk       Break long dialogues into multiple slides
    full        Run complete pipeline (clean -> format -> chunk)

Examples:
    python caption_toolkit.py clean script.md script-clean.md
    python caption_toolkit.py format script-clean.md script-formatted.md --characters "HAMLET,OPHELIA,CLAUDIUS"
    python caption_toolkit.py chunk script-formatted.md script-final.md --max-chars 150
    python caption_toolkit.py full script.md script-final.md --characters "HAMLET,OPHELIA"
"""

import re
import sys
import argparse
from pathlib import Path


# =============================================================================
# STAGE 1: CLEAN - Remove stage directions and artifacts
# =============================================================================

def remove_stage_directions(text):
    """Remove all parenthetical stage directions from text."""
    # Remove parenthetical content (single-line)
    result = re.sub(r'\([^)]*\)', '', text)

    # Clean up extra whitespace left behind
    result = re.sub(r'  +', ' ', result)  # Multiple spaces to single
    result = re.sub(r'^ +', '', result, flags=re.MULTILINE)  # Leading spaces
    result = re.sub(r' +$', '', result, flags=re.MULTILINE)  # Trailing spaces
    result = re.sub(r'\n{3,}', '\n\n', result)  # Multiple blank lines to double

    return result


def remove_page_numbers(text):
    """Remove standalone page numbers."""
    # Remove lines that are just numbers
    result = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
    return result


def remove_act_markers(text):
    """Remove ACT/SCENE markers and similar structural elements."""
    patterns = [
        r'^ACT\s+(ONE|TWO|THREE|FOUR|FIVE|[IVX]+|\d+)\s*$',
        r'^Scene\s+(One|Two|Three|Four|Five|[IVX]+|\d+)\s*$',
        r'^End of Act\s+.*$',
        r'^INTERMISSION\s*$',
        r'^CURTAIN\s*$',
    ]
    result = text
    for pattern in patterns:
        result = re.sub(pattern, '', result, flags=re.MULTILINE | re.IGNORECASE)
    return result


def clean_script(text, remove_parens=True, remove_pages=True, remove_acts=True):
    """
    Clean a raw script by removing stage directions and artifacts.

    Args:
        text: The raw script text
        remove_parens: Remove parenthetical stage directions
        remove_pages: Remove page numbers
        remove_acts: Remove ACT/SCENE markers

    Returns:
        Cleaned script text
    """
    if remove_parens:
        text = remove_stage_directions(text)
    if remove_pages:
        text = remove_page_numbers(text)
    if remove_acts:
        text = remove_act_markers(text)

    # Final cleanup of excessive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


# =============================================================================
# STAGE 2: FORMAT - Convert to CaptionPoint markdown
# =============================================================================

def detect_characters(text, min_occurrences=3):
    """
    Auto-detect character names from script.
    Looks for patterns like "CHARACTER." or "CHARACTER:" at start of lines.

    Args:
        text: Script text
        min_occurrences: Minimum times a name must appear to be considered a character

    Returns:
        List of detected character names
    """
    # Pattern: Start of line, ALL CAPS words, followed by . or :
    pattern = r'^([A-Z][A-Z\s\-\']+)\s*[.:]'
    matches = re.findall(pattern, text, re.MULTILINE)

    # Count occurrences and filter
    from collections import Counter
    counts = Counter(m.strip() for m in matches)

    # Filter by minimum occurrences and reasonable length
    characters = [
        name for name, count in counts.items()
        if count >= min_occurrences and len(name) < 40
    ]

    return sorted(characters, key=lambda x: -counts[x])


def split_multi_character_lines(text, characters):
    """
    Split lines that have multiple CHARACTER. patterns into separate lines.

    Args:
        text: Script text
        characters: List of character names to look for

    Returns:
        Text with multi-character lines split
    """
    if not characters:
        return text

    lines = text.split('\n')
    result = []

    # Build pattern for splitting
    char_pattern = '|'.join(re.escape(c) for c in characters)
    split_pattern = re.compile(r'(?<=[.!?"\'])\s+(?=(?:' + char_pattern + r')[.:])')

    for line in lines:
        parts = split_pattern.split(line)
        if len(parts) > 1:
            for part in parts:
                part = part.strip()
                if part:
                    result.append(part)
        else:
            result.append(line)

    return '\n'.join(result)


def join_continuation_lines(text, characters):
    """
    Join lines that continue dialogue (don't start with a character name).

    Args:
        text: Script text
        characters: List of character names

    Returns:
        Text with continuation lines joined
    """
    if not characters:
        return text

    lines = text.split('\n')
    result = []

    char_pattern = re.compile(r'^(' + '|'.join(re.escape(c) for c in characters) + r')[.:]')

    for line in lines:
        stripped = line.strip()
        if not stripped:
            result.append('')
            continue

        # If line starts with a character name, it's new dialogue
        if char_pattern.match(stripped):
            result.append(stripped)
        # If line continues previous dialogue
        elif result and result[-1] and not result[-1].startswith('---'):
            result[-1] = result[-1] + ' ' + stripped
        else:
            result.append(stripped)

    return '\n'.join(result)


def convert_to_captionpoint(text, characters):
    """
    Convert CHARACTER. dialogue to ## CHARACTER: format with --- separators.

    Args:
        text: Script text with CHARACTER. format
        characters: List of character names

    Returns:
        CaptionPoint formatted text
    """
    if not characters:
        return text

    lines = text.split('\n')
    result = []

    char_pattern = re.compile(
        r'^(' + '|'.join(re.escape(c) for c in characters) + r')[.:]\s*(.*)'
    )

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        match = char_pattern.match(stripped)
        if match:
            character = match.group(1)
            dialogue = match.group(2)

            # Add separator before each character line (except first)
            if result:
                result.append('---')
                result.append('')

            result.append(f'## {character}:')
            if dialogue:
                result.append(dialogue)
        else:
            # Non-dialogue line - append to previous if exists
            if result and result[-1] and not result[-1].startswith('---') and not result[-1].startswith('##'):
                result[-1] = result[-1] + ' ' + stripped
            else:
                result.append(stripped)

    # Add final separator
    if result:
        result.append('')
        result.append('---')

    return '\n'.join(result)


def format_script(text, characters=None, auto_detect=True):
    """
    Format a cleaned script to CaptionPoint markdown.

    Args:
        text: Cleaned script text
        characters: List of character names (optional)
        auto_detect: Auto-detect characters if none provided

    Returns:
        CaptionPoint formatted text
    """
    if not characters and auto_detect:
        characters = detect_characters(text)
        if characters:
            print(f"Auto-detected characters: {', '.join(characters)}")

    if not characters:
        print("Warning: No characters specified or detected. Output may be incomplete.")
        return text

    # Step 1: Split multi-character lines
    text = split_multi_character_lines(text, characters)

    # Step 2: Join continuation lines
    text = join_continuation_lines(text, characters)

    # Step 3: Convert to CaptionPoint format
    text = convert_to_captionpoint(text, characters)

    return text


# =============================================================================
# STAGE 3: CHUNK - Break long dialogues into slides
# =============================================================================

def split_into_sentences(text):
    """
    Split text into sentences, keeping punctuation attached.

    Args:
        text: Dialogue text

    Returns:
        List of sentences
    """
    # Split on sentence-ending punctuation followed by space and capital
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z"\'])', text)
    return [s.strip() for s in sentences if s.strip()]


def chunk_dialogue(dialogue, max_chars=150):
    """
    Break dialogue into chunks that fit within max_chars.

    Args:
        dialogue: Dialogue text
        max_chars: Maximum characters per chunk

    Returns:
        List of dialogue chunks
    """
    sentences = split_into_sentences(dialogue)

    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        sentence_len = len(sentence)

        # If single sentence is too long, include it as-is
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


def chunk_script(text, max_chars=150):
    """
    Process a formatted script and break up long dialogues.

    Args:
        text: CaptionPoint formatted script
        max_chars: Maximum characters per dialogue slide

    Returns:
        Chunked script text
    """
    # Split into slides
    parts = re.split(r'\n---\n', text)

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

    # Join with separators
    output = '\n---\n\n'.join(new_parts)
    if output:
        output += '\n---\n'

    return output


# =============================================================================
# SONG DETECTION (for musicals)
# =============================================================================

def is_line_song(text, threshold=0.85):
    """
    Detect if a line is likely song lyrics (predominantly uppercase).

    Args:
        text: Line of text
        threshold: Ratio of uppercase letters to consider it a song

    Returns:
        True if line appears to be song lyrics
    """
    clean = re.sub(r'[^a-zA-Z]', '', text)
    if not clean:
        return False

    upper_count = sum(1 for c in clean if c.isupper())
    ratio = upper_count / len(clean)

    return ratio > threshold


# =============================================================================
# FULL PIPELINE
# =============================================================================

def process_script(input_text, characters=None, max_chars=150,
                   remove_parens=True, remove_pages=True, remove_acts=True):
    """
    Run the complete processing pipeline on a script.

    Args:
        input_text: Raw script text
        characters: List of character names (or None for auto-detect)
        max_chars: Maximum characters per dialogue slide
        remove_parens: Remove parenthetical stage directions
        remove_pages: Remove page numbers
        remove_acts: Remove ACT/SCENE markers

    Returns:
        Fully processed CaptionPoint script
    """
    # Stage 1: Clean
    print("Stage 1: Cleaning script...")
    text = clean_script(input_text, remove_parens, remove_pages, remove_acts)

    # Stage 2: Format
    print("Stage 2: Formatting to CaptionPoint...")
    text = format_script(text, characters)

    # Stage 3: Chunk
    print("Stage 3: Chunking long dialogues...")
    text = chunk_script(text, max_chars)

    return text


# =============================================================================
# VERIFICATION
# =============================================================================

def verify_dialogue_preserved(original, processed, characters=None):
    """
    Verify that no dialogue was lost during processing.

    Args:
        original: Original script text
        processed: Processed script text
        characters: List of character names (for targeted checking)

    Returns:
        Tuple of (success, message)
    """
    # Extract dialogue phrases from original
    original_clean = remove_stage_directions(original)

    # Get unique phrases (10+ chars, ending in punctuation)
    phrases = re.findall(r'[A-Za-z][^.!?]{10,}[.!?]', original_clean)
    unique_phrases = set(phrases)

    missing = []
    for phrase in unique_phrases:
        if phrase not in processed:
            missing.append(phrase)

    if missing:
        return False, f"Missing {len(missing)} phrases. First few: {missing[:5]}"
    else:
        return True, f"All {len(unique_phrases)} unique dialogue phrases preserved."


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='CaptionPoint Script Formatting Toolkit',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Clean command
    clean_parser = subparsers.add_parser('clean', help='Remove stage directions')
    clean_parser.add_argument('input', help='Input file')
    clean_parser.add_argument('output', help='Output file')
    clean_parser.add_argument('--keep-parens', action='store_true',
                              help='Keep parenthetical text')
    clean_parser.add_argument('--keep-pages', action='store_true',
                              help='Keep page numbers')
    clean_parser.add_argument('--keep-acts', action='store_true',
                              help='Keep ACT/SCENE markers')

    # Format command
    format_parser = subparsers.add_parser('format', help='Convert to CaptionPoint format')
    format_parser.add_argument('input', help='Input file')
    format_parser.add_argument('output', help='Output file')
    format_parser.add_argument('--characters', '-c',
                               help='Comma-separated list of character names')
    format_parser.add_argument('--no-auto-detect', action='store_true',
                               help='Disable character auto-detection')

    # Chunk command
    chunk_parser = subparsers.add_parser('chunk', help='Break long dialogues into slides')
    chunk_parser.add_argument('input', help='Input file')
    chunk_parser.add_argument('output', help='Output file')
    chunk_parser.add_argument('--max-chars', '-m', type=int, default=150,
                              help='Maximum characters per slide (default: 150)')

    # Full pipeline command
    full_parser = subparsers.add_parser('full', help='Run complete pipeline')
    full_parser.add_argument('input', help='Input file')
    full_parser.add_argument('output', help='Output file')
    full_parser.add_argument('--characters', '-c',
                             help='Comma-separated list of character names')
    full_parser.add_argument('--max-chars', '-m', type=int, default=150,
                             help='Maximum characters per slide (default: 150)')
    full_parser.add_argument('--verify', '-v', action='store_true',
                             help='Verify no dialogue was lost')

    # Detect command
    detect_parser = subparsers.add_parser('detect', help='Auto-detect characters in script')
    detect_parser.add_argument('input', help='Input file')
    detect_parser.add_argument('--min-occurrences', '-m', type=int, default=3,
                               help='Minimum occurrences to be considered a character')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Read input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file '{args.input}' not found.")
        sys.exit(1)

    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Process based on command
    if args.command == 'clean':
        result = clean_script(
            text,
            remove_parens=not args.keep_parens,
            remove_pages=not args.keep_pages,
            remove_acts=not args.keep_acts
        )

    elif args.command == 'format':
        characters = None
        if args.characters:
            characters = [c.strip() for c in args.characters.split(',')]
        result = format_script(text, characters, auto_detect=not args.no_auto_detect)

    elif args.command == 'chunk':
        result = chunk_script(text, args.max_chars)

    elif args.command == 'full':
        characters = None
        if args.characters:
            characters = [c.strip() for c in args.characters.split(',')]
        result = process_script(text, characters, args.max_chars)

        if args.verify:
            success, message = verify_dialogue_preserved(text, result, characters)
            print(f"Verification: {message}")
            if not success:
                print("Warning: Some dialogue may have been lost!")

    elif args.command == 'detect':
        characters = detect_characters(text, args.min_occurrences)
        print("Detected characters:")
        for char in characters:
            count = len(re.findall(re.escape(char) + r'[.:]', text))
            print(f"  {char}: {count} occurrences")
        sys.exit(0)

    # Write output
    if args.command != 'detect':
        output_path = Path(args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"Output written to {args.output}")


if __name__ == '__main__':
    main()
