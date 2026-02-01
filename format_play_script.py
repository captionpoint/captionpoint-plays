import re
import sys
import os

def is_line_song(text):
    # Heuristic: A line is part of a song if it is predominantly uppercase.
    clean = re.sub(r'[^a-zA-Z]', '', text)
    if not clean:
        return False
    
    upper_count = sum(1 for c in clean if c.isupper())
    ratio = upper_count / len(clean)
    
    return ratio > 0.85

def format_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    final_slides = []
    
    # Parser State
    current_speaker = None
    buffer = []
    
    # Regex for Speaker Headers
    # Matches "NAME:" or "## NAME:"
    # Also handles "PICKERING." (found in source)
    # We want to capture the name part.
    header_pattern = re.compile(r"^(?:##\s*)?([A-Z0-9 \.\-&,]+)[:\.]$")
    
    # Title handling
    iterator = iter(lines)
    
    # Capture Title Slide
    title_slide = []
    try:
        first_line = next(iterator)
        if "class: title" in first_line:
            title_slide.append(first_line.strip())
            while True:
                line = next(iterator)
                if line.strip() == "---":
                    break
                title_slide.append(line.strip())
            # Add formatted title slide
            final_slides.append("\n".join(title_slide))
        else:
            # If no title template found immediately, rewind (conceptually) or just process
            # But the file shows it has it.
            pass
    except StopIteration:
        pass

    # Find where we left off (skip title section)
    start_idx = 0
    if final_slides:
        for i, line in enumerate(lines):
            if line.strip() == "---":
                start_idx = i + 1
                break
    
    # Process the stream
    for i in range(start_idx, len(lines)):
        original_line = lines[i]
        s_line = original_line.strip()
        
        if not s_line:
            continue
        if s_line == "---":
            continue
            
        # Check for Header
        # Rule: Must be at start of line (no leading whitespace) to be a header candidate
        # AND match pattern
        # AND not be too long
        
        is_indented = original_line[0].isspace()
        
        match = header_pattern.match(s_line)
        if match and not is_indented:
            name_part = match.group(1).strip()
            
            # Length check (lyrics like "THE RAIN IN SPAIN STAYS MAINLY IN THE PLAIN." are long)
            if len(name_part) < 40:
                # Flush current buffer
                if buffer:
                    flush_slides(final_slides, current_speaker, buffer)
                    buffer = []
                
                current_speaker = name_part
                continue
        
        # Add to buffer
        buffer.append(s_line)

    # Flush last
    if buffer:
        flush_slides(final_slides, current_speaker, buffer)

    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n\n---\n\n".join(final_slides))
        f.write("\n")

def flush_slides(slides_list, speaker, content_lines):
    # Process content lines to identify song/speech blocks and chunk them.
    current_mode_is_song = False
    chunk_buffer = []
    
    for line in content_lines:
        is_song = is_line_song(line)
        
        if not chunk_buffer:
            current_mode_is_song = is_song
            chunk_buffer.append(line)
            continue
            
        if is_song == current_mode_is_song:
            chunk_buffer.append(line)
        else:
            # Mode changed. Flush current chunk.
            create_slides_from_chunk(slides_list, speaker, chunk_buffer, current_mode_is_song)
            chunk_buffer = [line]
            current_mode_is_song = is_song
            
    if chunk_buffer:
        create_slides_from_chunk(slides_list, speaker, chunk_buffer, current_mode_is_song)

def create_slides_from_chunk(slides_list, speaker, lines, is_song):
    # Sub-chunk based on length
    max_chars = 250
    current_slide_lines = []
    current_char_count = 0
    
    first_slide_in_group = True
    
    for line in lines:
        if current_slide_lines and (current_char_count + len(line) > max_chars or len(current_slide_lines) >= 4):
            add_single_slide(slides_list, speaker, current_slide_lines, is_song, first_slide_in_group)
            current_slide_lines = []
            current_char_count = 0
            first_slide_in_group = False 
            
        current_slide_lines.append(line)
        current_char_count += len(line)
        
    if current_slide_lines:
        add_single_slide(slides_list, speaker, current_slide_lines, is_song, first_slide_in_group)

def add_single_slide(slides_list, speaker, lines, is_song, include_header):
    slide_parts = []
    
    if is_song:
        slide_parts.append("class: song")
        
    if include_header and speaker:
        slide_parts.append(f"## {speaker}:")
        
    if is_song:
        slide_parts.append("\n\n".join(lines))
    else:
        slide_parts.extend(lines)
    
    slides_list.append("\n".join(slide_parts))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python format_play_script.py <input_file> <output_file>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
        
    print(f"Formatting '{input_file}' to '{output_file}'...")
    format_file(input_file, output_file)
    print("Done.")
