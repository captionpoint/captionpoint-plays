# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CaptionPoint is a live theater captioning system built as a fork of [Backslide](https://github.com/sinedied/backslide). It creates real-time caption presentations for live theater performances using Remark.js and Markdown files.

The system converts Markdown scripts into HTML slide presentations with theater-specific features:
- Color-coded character names
- Song lyrics and sound effects formatting
- Custom aspect ratios for different display configurations
- Live preview and editing via VSCode extension

## Repository Structure

- **Root directory**: Contains play scripts as `.md` files (e.g., `JOURNEY-ON-backup.md`)
- **`!archives/`**: Archived/completed play scripts
- **`template/`**: Core presentation template files
  - `index.html` - Remark.js HTML template (supports Mustache variables)
  - `style.scss` - Main stylesheet for presentations
  - `remark.min.js` - Remark.js library
  - `font/` - Custom fonts
- **`theater-templates/`**: Theater-specific boilerplate templates (Court Theatre, Latte Da, Northlight, etc.)
- **`vscode-extension/`**: VSCode extension for live preview
  - `src/extension.ts` - Extension entry point
  - `src/previewProvider.ts` - Preview rendering logic
- **`starter/`**: Template starter files for new presentations
- **`dist/`**: Exported HTML presentations
- **`backslide.js`**: Main CLI tool implementation

## Common Commands

### Development Workflow

```bash
# Initialize template directory (required before first use)
npm run init

# Start live development server with auto-reload
bs serve
# Or specify a directory
bs serve example

# Start dev server on custom port
bs serve -p 8080

# Start dev server without opening browser
bs serve --skip-open
```

### Exporting Presentations

```bash
# Export all .md files to self-contained HTML
bs export

# Export specific file
bs export PLAY-NAME.md

# Export to custom output directory
bs export -o output/

# Export as website (copies assets, doesn't inline)
bs export --web PLAY-NAME.md

# Strip presenter notes from export
bs export --strip-notes

# Strip slide fragments for handouts
bs export --handouts
```

### PDF Export

```bash
# Export all .md files to PDF (requires decktape)
bs pdf

# Export specific file to PDF
bs pdf PLAY-NAME.md

# Export with custom settings
bs pdf -o output/ -w 2000

# Strip fragments for handout PDFs
bs pdf --handouts
```

### VSCode Extension

```bash
# Install dependencies and compile extension
cd vscode-extension
npm install
npm run compile

# Package extension for installation
npm install -g @vscode/vsce
vsce package

# Install the packaged extension
code --install-extension remark-preview-0.1.0.vsix --force

# Development: watch for changes
npm run watch
```

In VSCode:
- **Cmd+Shift+V** (Mac) or **Ctrl+Shift+V** (Windows/Linux) - Open preview beside editor
- Command Palette: "Remark: Open Preview to the Side"

## Theater Captioning Workflow

### Script Format

Theater scripts use Remark.js markdown with special conventions:

1. **YAML Frontmatter** (optional) - Configure aspect ratio and font size:
```markdown
---
title: Play Title
author: Author Name
ratio: 16:9
fontSize: 4rem
---
```

2. **Settings Section** - Define character color mappings at the start:
```markdown
class: center, middle, smaller
BEGIN SETTINGS
---

title: PLAY TITLE
author: Author Name

plum-purple: character-one
stiletto-red: character-two
st-tropaz-blue: character-three
...

END SETTINGS
```

3. **Slide Separators**:
   - `---` creates a new slide
   - `--` creates incremental content

4. **Character Dialogue** - Use H2 with character name and color class:
```markdown
## CHARACTER-ONE:
This is the dialogue text.
```

5. **Special Slide Types**:
   - Music: `template: music` or use `&#9834; &#9834;`
   - Songs: `template: song`
   - Sound effects: `template: noise`
   - Titles: `template: title`
   - Asides: `template: aside`
   - Overlapping dialogue: `template: overlap`

### Character Color Coding

Available colors (defined in `BOILERPLATE.md`):
- plum-purple, stiletto-red, st-tropaz-blue, orange-zest, lavender-purple
- green-goblin, shocking-pink, brown-clay, pelorous-aqua, magenta
- dark-violet, gold, dodger-blue, cornflower-blue, cyan
- lime-green, coral, hot-pink, orange, tomato, lime

Colors are mapped to character names in the settings section, then applied automatically when using the character name as an H2 heading.

### Aspect Ratio Configuration

YAML frontmatter supports custom aspect ratios for different theater displays:

- **58:9** (ultra-wide): Use `fontSize: 3rem` - `3.5rem`
- **29:9** (wide): Use `fontSize: 3.5rem` - `4rem`
- **16:9** (standard): Use `fontSize: 4rem` - `5rem`
- **4:3** (classic): Use `fontSize: 5rem` - `6rem`

## Architecture

### Template System

The template system uses Mustache variable replacement:

1. **Variables in `template/index.html`**:
   - `{{title}}` - Extracted from markdown frontmatter
   - `{{{style}}}` - Compiled CSS from `style.scss`
   - `{{{source}}}` - Raw markdown content (escaped)

2. **SCSS Compilation**:
   - `template/style.scss` is compiled to CSS at build/serve time
   - Uses Sass with compressed output
   - Supports imports and SCSS features

3. **Remark.js Configuration**:
   - Ratio can be set via YAML frontmatter or in template
   - Custom CSS classes for theater-specific styling
   - Support for presenter notes (lines starting with `???`)

### VSCode Extension Architecture

The extension provides split-view editing with live updates:

1. **Preview Provider** (`previewProvider.ts`):
   - Compiles SCSS to CSS
   - Processes Mustache template variables
   - Generates complete HTML for webview
   - Watches template files for changes
   - Parses YAML frontmatter for configuration

2. **File Watching**:
   - Markdown changes trigger instant preview updates
   - Template file changes recompile and refresh
   - Pattern: `template/**/*.{scss,css,html,js}`

3. **SCSS Compilation**:
   - Uses Dart Sass (modern, maintained)
   - Compiles on-demand with caching
   - Errors shown as VSCode notifications

## Python Helper Scripts

### `pdf_to_captionpoint.py`
**Interactive PDF-to-markdown converter** for theater scripts. Extracts character names and dialogue while filtering out stage directions, page numbers, and other content.

Features:
- Interactive line-by-line classification (character/dialogue/skip)
- Smart detection of character names (all caps), stage directions, page numbers
- Auto-skip mode for bulk filtering of stage directions
- Resume capability - save progress and continue later
- Statistics tracking (characters found, lines processed)

Basic usage:
```bash
./parse-pdf script.pdf output.md              # Using wrapper script
./parse-pdf script.pdf output.md --resume     # Resume saved progress
```

### `debug_pdf.py`
**PDF inspection tool** to check if a PDF has extractable text before parsing.

Usage:
```bash
./debug-pdf script.pdf    # Shows PDF statistics and first few lines
```

Use this first to verify your PDF isn't image-based (scanned). Image-based PDFs need OCR before parsing.

### `txt_to_clean_dialogue.py`
**OCR text cleaner** for converting OCR'd script text files into clean, readable dialogue format.

Features:
- Skips front matter (copyright, cast list) - starts from "PART ONE"
- Removes stage directions (content in parentheses)
- Removes scene headers
- Fixes common OCR errors (e.g., "1ARY JANE" → "MARY JANE", "trafﬁc" → "traffic")
- Formats character dialogue into separate paragraphs
- Provides statistics (blocks created, errors fixed, character counts)

Usage:
```bash
python3 txt_to_clean_dialogue.py input.txt output.txt
```

This is useful when you have an OCR'd text export from a PDF and want to clean it up before converting to CaptionPoint format.

See [PDF_WORKFLOW.md](PDF_WORKFLOW.md) for detailed workflow and tips.

### `chunk_dialogue.py`
Splits long character dialogues across multiple slides (max 4 lines per slide). Useful for post-processing scripts with lengthy monologues.

Usage:
```bash
python3 chunk_dialogue.py input.md output.md 4  # 4 = max lines per slide
```

## Theater-Specific Templates

The `theater-templates/` directory contains boilerplate files customized for different theaters:
- Court Theatre (centered and left-aligned variants)
- Latte Da Theater
- Northlight Theatre

These templates have pre-configured styling and branding for each venue.

## Key Technical Details

### Backslide CLI (`backslide.js`)

- Built on Node.js with browser-sync for live reload
- Uses `node-sass` for SCSS compilation in CLI tool
- Uses `web-resource-inliner` to inline external resources in exports
- Template directory must exist before running (use `npm run init`)

### File Exports

- **HTML Export**: Self-contained single file with all resources inlined (including images as data URIs)
- **Web Export**: Multi-file output with asset folders preserved
- **PDF Export**: Requires `decktape` installed globally (`npm install -g decktape`)

### Security Considerations

- VSCode extension webview has scripts enabled (required for Remark.js)
- Local resources restricted to workspace and extension directories
- No external network requests except CDN fallback for remark.js

## PDF to CaptionPoint Workflow

### Setup
Run the setup script to create a virtual environment:
```bash
./setup.sh
```

Or manually:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Converting PDF Scripts
1. **Activate virtual environment**:
   ```bash
   source venv/bin/activate
   ```

2. **Parse PDF** - Interactive extraction of character dialogue:
   ```bash
   python pdf_to_captionpoint.py script.pdf raw-output.md
   ```
   - Press `c` for character names, `d` for dialogue, `s` to skip
   - Press `a` for auto-skip mode (skips until next character)
   - Press `q` to save progress, resume with `--resume`

3. **Add boilerplate** - Copy settings from `BOILERPLATE.md` or theater-specific template
   - Configure character color assignments
   - Add title/author YAML frontmatter
   - Set aspect ratio and font size

4. **Chunk long dialogues** (optional):
   ```bash
   python chunk_dialogue.py raw-output.md final-output.md 4
   ```

5. **Preview and refine**:
   ```bash
   bs serve
   ```

6. **Deactivate when done**:
   ```bash
   deactivate
   ```

See [PDF_WORKFLOW.md](PDF_WORKFLOW.md) for detailed instructions and troubleshooting.

## Development Notes

- **Node Version**: Requires Node.js >= 10.0.0
- **Python Version**: Python 3.x required for PDF parsing tools
- **Linting**: Uses XO with Prettier formatting
- **Testing**: `npm test` runs XO linter
- **Deployment**: Uses gh-pages for static site deployment

When creating new play scripts, start from `BOILERPLATE.md` or use theater-specific templates from `theater-templates/` directory.
