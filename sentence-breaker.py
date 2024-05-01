import re

# Read in the Markdown file
with open('S-PARADOX-SCRATCH.md', 'r') as file:
    text = file.read()

# Split the text into sentences
sentences = re.split(r'(?<=[.?!])\s', text)

# Initialize a counter to keep track of sentence indices
counter = 0

# Iterate through the sentences and add two returns, "---," and two more returns
for i, sentence in enumerate(sentences):
    if i % 2 == 1:  # Check if it's the second occurrence
        sentences[i] = sentence + '\n\n---\n\n'
        counter += 1

# Join the modified sentences back into a single text
new_text = ' '.join(sentences)

# Write the modified text back to the Markdown file
with open('output.md', 'w') as file:
    file.write(new_text)
