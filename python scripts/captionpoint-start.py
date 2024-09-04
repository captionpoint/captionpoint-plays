import re
from PyPDF2 import PdfReader


def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


def split_into_slides(text, max_lines=4):
    lines = text.split('\n')
    slides = []
    current_slide = []

    for line in lines:
        if line.strip() == "":
            continue
        current_slide.append(line.strip())
        if len(current_slide) >= max_lines:
            slides.append(current_slide)
            current_slide = []

    if current_slide:
        slides.append(current_slide)

    return slides


def format_as_markdown(slides):
    markdown = ""
    for slide in slides:
        markdown += "\n".join(slide) + "\n\n---\n\n"
    return markdown


def save_to_file(markdown_text, output_file):
    with open(output_file, 'w') as file:
        file.write(markdown_text)


# Path to your PDF file
pdf_path = '/Users/macnab/Downloads/_docs/Ann_PRIME Productions.pdf'

# Extract text from PDF
text = extract_text_from_pdf(pdf_path)

# Split text into slides
slides = split_into_slides(text)

# Format as markdown
markdown_text = format_as_markdown(slides)

# Save markdown to a file
save_to_file(markdown_text, 'output.md')
