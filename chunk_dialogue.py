import re
import sys

def chunk_long_dialogues(input_file, output_file, max_lines=4):
    with open(input_file, 'r') as f:
        content = f.read()
    
    # Split the content into slides
    slides = re.split(r'---\n\n', content)
    new_slides = []
    
    for slide in slides:
        lines = slide.strip().split('\n')
        
        # Skip empty slides
        if not lines or all(not line.strip() for line in lines):
            continue
        
        # Check if this is a character's dialogue
        character_match = re.match(r'## (REN|FALLON|TED|OLIVIA|MARILYN):', lines[0])
        
        if character_match and len(lines) > max_lines + 1:
            # This is a long dialogue that needs chunking
            character = character_match.group(1)
            dialogue_lines = lines[1:]
            
            # Process chunks of dialogue
            current_chunk = [lines[0]]  # Start with character name
            current_line_count = 0
            
            for line in dialogue_lines:
                # Handle stage directions separately
                is_stage_direction = line.strip().startswith('(') and line.strip().endswith(')')
                
                # If adding this line would exceed our limit, create a new chunk
                if current_line_count >= max_lines and not is_stage_direction:
                    new_slides.append('\n'.join(current_chunk))
                    current_chunk = [f"## {character}:"]
                    current_line_count = 0
                
                current_chunk.append(line)
                if line.strip() and not is_stage_direction:
                    current_line_count += 1
            
            # Add the last chunk
            if current_chunk:
                new_slides.append('\n'.join(current_chunk))
        else:
            # Keep small dialogues as is
            new_slides.append('\n'.join(lines))
    
    # Join the slides back together
    new_content = '\n\n---\n\n'.join(new_slides)
    
    with open(output_file, 'w') as f:
        f.write(new_content)
    
    return len(slides), len(new_slides)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py input_file output_file [max_lines_per_chunk]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    max_lines = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    
    original, new = chunk_long_dialogues(input_file, output_file, max_lines)
    print(f"Processed {original} slides into {new} slides with max {max_lines} lines per dialogue chunk.")