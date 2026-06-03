#!/usr/bin/env python3
"""
Chunk Long Dialogue Script
---------------------------
Breaks long character dialogues into smaller, more readable slides for theater captioning.

This script:
1. Identifies character dialogue slides (## CHARACTER:)
2. Detects long paragraphs (>150 characters)
3. Splits them into sentences
4. Creates multiple slides with max N sentences each

Usage:
    python chunk_dialogue.py input.md output.md [max_sentences_per_chunk]

Example:
    python chunk_dialogue.py MARY-JANE.md MARY-JANE-chunked.md 2

    This will split long dialogues into chunks of 2 sentences each.
"""
import re
import sys

def split_into_sentences(text):
    """
    Split text into sentences, preserving quoted dialogue.

    Uses regex to split on sentence-ending punctuation (. ! ?)
    followed by a space and a capital letter or quote mark.
    This keeps quoted dialogue together as much as possible.

    Args:
        text: String of dialogue text

    Returns:
        List of sentence strings
    """
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z"\'])', text)
    return [s.strip() for s in sentences if s.strip()]

def chunk_long_dialogues(input_file, output_file, max_sentences=3):
    """
    Process a markdown script and chunk long character dialogues.

    Args:
        input_file: Path to input markdown file
        output_file: Path to output markdown file
        max_sentences: Maximum sentences per dialogue chunk (default: 3)

    Returns:
        Tuple of (original_slide_count, new_slide_count)

    How it works:
    1. Splits markdown by slide separator (---\n\n)
    2. For each slide with character dialogue (## CHARACTER:):
       - Checks if any line exceeds 150 characters
       - If yes: splits into sentences and creates multiple slides
       - If no: keeps slide as-is
    3. Preserves non-dialogue slides unchanged
    """
    with open(input_file, 'r') as f:
        content = f.read()

    # Split the content into slides using the standard separator
    slides = re.split(r'---\n\n', content)
    new_slides = []

    for slide in slides:
        lines = slide.strip().split('\n')

        # Skip empty slides
        if not lines or all(not line.strip() for line in lines):
            continue

        # Check if this is a character's dialogue
        # Pattern matches: ## CHARACTER NAME: (any caps, spaces, dots)
        character_match = re.match(r'## ([A-Z\s\.]+):', lines[0])

        if character_match:
            character = character_match.group(1)
            dialogue_lines = lines[1:]

            # Check if this is a long paragraph that needs splitting
            # Threshold: any line longer than 150 characters
            needs_chunking = False
            for line in dialogue_lines:
                # Skip stage directions (text in parentheses)
                if line.strip().startswith('(') and line.strip().endswith(')'):
                    continue
                # If any line is very long, we need to chunk it
                if len(line) > 150:
                    needs_chunking = True
                    break

            if needs_chunking:
                # Combine all dialogue into one text block (excluding stage directions)
                dialogue_text = ' '.join([
                    line for line in dialogue_lines
                    if line.strip() and not (line.strip().startswith('(') and line.strip().endswith(')'))
                ])

                # Split into sentences
                sentences = split_into_sentences(dialogue_text)

                # Create chunks of max_sentences each
                # This will create multiple slides for the same character
                for i in range(0, len(sentences), max_sentences):
                    chunk_sentences = sentences[i:i+max_sentences]
                    chunk_text = ' '.join(chunk_sentences)
                    new_slides.append(f"## {character}:\n{chunk_text}")
            else:
                # Keep short dialogues as-is
                new_slides.append('\n'.join(lines))
        else:
            # Not a character dialogue (title, settings, etc.), keep as-is
            new_slides.append('\n'.join(lines))

    # Join the slides back together
    new_content = '\n\n---\n\n'.join(new_slides)

    with open(output_file, 'w') as f:
        f.write(new_content)

    return len(slides), len(new_slides)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py input_file output_file [max_sentences_per_chunk]")
        print("  max_sentences_per_chunk: Number of sentences per slide (default: 3)")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    max_sentences = int(sys.argv[3]) if len(sys.argv) > 3 else 3

    original, new = chunk_long_dialogues(input_file, output_file, max_sentences)
    print(f"Processed {original} slides into {new} slides with max {max_sentences} sentences per dialogue chunk.")
