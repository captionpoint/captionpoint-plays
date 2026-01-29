# PDF to CaptionPoint Workflow

This document explains how to convert PDF theater scripts into CaptionPoint markdown format.

## Setup (One-time)

### Quick Setup (Recommended)
Run the setup script to create a virtual environment and install dependencies:

```bash
./setup.sh
```

This creates a `venv/` folder with isolated Python dependencies.

### Manual Setup
If you prefer to set up manually:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Using the Virtual Environment

**Activate before use:**
```bash
source venv/bin/activate
```

Your prompt will show `(venv)` when active.

**Deactivate when done:**
```bash
deactivate
```

## Checking Your PDF First (Recommended)

Before parsing, check if your PDF has extractable text:

```bash
./debug-pdf your-script.pdf
```

This shows:
- Whether text can be extracted
- First few lines from each page
- If it's an image-based PDF that needs OCR

**If the PDF is image-based:** Use OCR software (like Adobe Acrobat) to convert it to a text-based PDF first.

## Basic Usage

### Option 1: Using the Wrapper Script (Easiest)

```bash
./parse-pdf script.pdf output.md
```

The `parse-pdf` wrapper automatically activates the virtual environment for you.

### Option 2: Manual Activation

```bash
# Activate virtual environment
source venv/bin/activate

# Convert a PDF script to markdown
python pdf_to_captionpoint.py script.pdf output.md

# When done
deactivate
```

## Interactive Workflow

The tool will show you each line of text from the PDF and ask you to classify it:

### Example Session

```
========================================
  >>> HAMLET
  After:  To be or not to be...
  💡 Likely: CHARACTER NAME

  Options:
    [c] Character name    [d] Dialogue
    [s] Skip (stage dir)  [n] New slide separator
    [q] Save and quit     [a] Auto-mode (bulk skip)
    [m] Merge with previous line
  Choice: c
  Character name [HAMLET]: ⏎
```

### Commands

- **`c`** - Mark as character name (starts new slide with `## CHARACTER:`)
- **`d`** - Mark as dialogue (adds to current character's slide)
- **`s`** - Skip this line (stage directions, page numbers, etc.)
- **`n`** - Force a new slide separator
- **`m`** - Merge with previous line (useful for dialogue split across lines)
- **`a`** - Auto-skip mode: automatically skip lines until next likely character name
- **`q`** - Save progress and quit (resume later with `--resume`)

### Smart Detection

The tool provides suggestions based on patterns:

- **Character Names**: All caps text (e.g., `HAMLET`, `OPHELIA:`)
- **Stage Directions**: Text in parentheses `(exits)`, brackets `[lights fade]`, or action keywords
- **Page Numbers**: Digits, roman numerals, "Page X" format

You can accept or override suggestions for full control.

## Resuming Work

If you quit partway through (press `q`), resume where you left off:

```bash
python3 pdf_to_captionpoint.py script.pdf output.md --resume
```

Progress is saved in `output.md.progress.json`.

## Tips for Efficiency

### 1. Use Auto-Skip Mode
When you hit long stage directions or scene descriptions:
- Press `a` to enter auto-skip mode
- Everything is skipped until the next character name
- Saves time on title pages, act breaks, etc.

### 2. Merge Split Lines
If dialogue is split across lines:
```
HAMLET
To be or not
to be...
```
- Mark first line as character (`c`)
- Mark second as dialogue (`d`)
- Mark third with merge (`m`) - it joins with previous line

### 3. Save Often
Press `q` every few pages to save progress. Better safe than sorry!

## Post-Processing

After conversion, you'll likely want to:

1. **Add the boilerplate** - Copy settings from `BOILERPLATE.md`:
   - Color assignments
   - Template names
   - Font configuration

2. **Assign character colors** - Edit the settings section:
   ```markdown
   plum-purple: hamlet
   stiletto-red: ophelia
   st-tropaz-blue: claudius
   ```

3. **Add special slides** - Insert as needed:
   - Music/sound effects: `template: music`
   - Songs: `template: song`
   - Titles: `template: title`

4. **Run chunking** (if needed) - Break up long monologues:
   ```bash
   python3 chunk_dialogue.py output.md output-chunked.md 4
   ```

5. **Preview and refine**:
   ```bash
   bs serve
   # Open in browser and review
   ```

## Example Output

The tool produces clean markdown like:

```markdown
## HAMLET:
To be or not to be, that is the question.

---

## OPHELIA:
My lord, I have remembrances of yours.

---

## HAMLET:
I never gave you aught.
```

Then you add the boilerplate and color assignments to complete the CaptionPoint format.

## Troubleshooting

### "pdfplumber not installed"
Run: `./setup.sh` to set up the virtual environment

### Empty output file created (MJ.md is empty)
Your PDF likely has no extractable text. Run:
```bash
./debug-pdf your-file.pdf
```

Common causes:
- **Scanned/image-based PDF**: The PDF is pictures of pages, not actual text
  - Solution: Use OCR software (Adobe Acrobat, online OCR tools)
- **Protected PDF**: The PDF has copy protection
  - Solution: Try a different PDF viewer or remove protection
- **Corrupted PDF**: The file may be damaged
  - Solution: Try re-downloading or use a different source

### PDF extraction looks garbled
Some PDFs have complex layouts or scanned images. Try:
1. Use a different PDF source (text-based PDFs work best)
2. Use OCR software first if the PDF is scanned images
3. Consider copy-pasting text from a preview tool

### Character names not detected
The tool detects all-caps text as character names. If your PDF uses different formatting:
- Manually mark them with `c` when prompted
- The tool learns your character list and shows it at the end

### Progress file corrupted
Delete `output.md.progress.json` and start over

## Statistics

At the end, you'll see:
```
📊 PROCESSING COMPLETE
========================================
  Total slides:       142
  Characters found:   8
  Lines processed:    1,234
  Lines skipped:      456

  Characters: HAMLET, OPHELIA, CLAUDIUS, GERTRUDE, ...
========================================
```

Use this to verify you captured all characters.
