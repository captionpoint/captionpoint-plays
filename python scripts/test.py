import re

# Read in the file
with open('COLONUS-scratch.md', 'r') as file:
    text = file.read()

# Add two new lines before and after slide breaks
text = re.sub(r'---', r'\n\n---\n\n', text)

# Add a period at the end of lines that don't end with punctuation
text = re.sub(r'(?<!\?|\!|\.)\n', r'.\n', text)

# Add a space after periods if the next character is a letter
text = re.sub(r'\.(?=[a-zA-Z])', r'. ', text)

# Add a new line after each line of dialogue
text = re.sub(r'([a-zA-Z])\n([a-zA-Z])', r'\1 \n\2', text)

# Capitalize character names and add slide breaks
names = ['OEDIPUS', 'THESEUS', 'ANTIGONE', 'ISMENE', 'THE FRIEND', 'CHORAGOS', 'EVANGELIST', 'CREON', 'POLYNIECES', 'POLYNEiCES', 'CHORUS', 'SOLOISTS']
for name in names:
    text = re.sub(fr'(?<=\n){name}(?!\S)', fr'## {name}:\n---\n', text)

# Save the output
with open('output.md', 'w') as file:
    file.write(text)
