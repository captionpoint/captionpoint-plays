# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CaptionPoint is a specialized tool for creating live theater captioning presentations. It's a fork of [Backslide](https://github.com/sinedied/backslide) that generates HTML presentations using [Remark.js](https://remarkjs.com) from Markdown files, with specific features for theater captioning workflows.

**Key Characteristics:**
- Theater caption files are Markdown documents that become slide-based presentations
- Each slide represents a caption screen shown during live theater performances
- Character dialogue is color-coded for accessibility
- Template-based styling system for consistent theater branding

## Development Commands

### Core CLI Commands (bs)

```bash
# Start development server with live preview (port 4100)
npm start
# or manually:
node ./bin/bs serve [directory]

# Export markdown files to self-contained HTML
node ./bin/bs export [files]
# Default output: dist/
# Options: --strip-notes, --handouts, --no-inline, --web

# Export to PDF (requires decktape: npm i -g decktape)
node ./bin/bs pdf [files]
# Default output: pdf/

# Initialize new presentation with template
node ./bin/bs init
# Creates template/ directory and presentation.md

# Linting
npm run lint        # Check code style with xo
npm run lint:fix    # Auto-fix linting issues
```

### VSCode Extension Development

The `vscode-extension/` directory contains a VSCode extension for live Remark.js preview:

```bash
cd vscode-extension

# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Watch mode for development
npm run watch

# Package as .vsix file
vsce package

# Test in VSCode: Press F5 to launch Extension Development Host
```

## Architecture

### CLI Tool Architecture (backslide.js)

The main CLI is implemented as a single-file Node.js class (`BackslideCli`) with these core methods:

1. **`serve(dir, port, open)`** - Development server with live reload
   - Uses BrowserSync for hot reloading
   - Watches `.md`, template files, and compiles SCSS on the fly
   - Serves from `.tmp/`, `template/`, and source directory

2. **`export(output, files, stripNotes, stripFragments, fixRelativePaths, inline, website)`** - HTML export
   - Compiles SCSS → CSS
   - Processes Mustache templates (`template/index.html`)
   - Inlines resources (CSS, images, scripts) by default
   - Handles relative path resolution for images

3. **`pdf(output, files, wait, handouts, verbose, options)`** - PDF export
   - Requires external `decktape` CLI tool
   - First exports to HTML in `.tmp/pdf/`
   - Then converts HTML to PDF using Decktape

4. **`init(fromTemplateDir, force)`** - Project initialization
   - Copies `starter/template/` → `template/`
   - Creates sample `presentation.md`

**Key Internal Methods:**
- `_sass()` - Compiles `template/style.scss` using node-sass
- `_inline()` - Inlines external resources using web-resource-inliner
- `_getTitle()` - Extracts title from markdown frontmatter (`title: ...`)
- `_makePathRelativeTo()` - Rewrites relative URLs to absolute file:// paths

### VSCode Extension Architecture

**Entry Point:** `vscode-extension/src/extension.ts`
- Registers commands: `remarkPreview.openPreview` and `remarkPreview.openPreviewToSide`
- Listens to editor and document changes

**Core Provider:** `vscode-extension/src/previewProvider.ts`
- `showPreview()` - Creates webview panel with Remark.js presentation
- `updatePreview()` - Regenerates HTML on document changes
- `compileScss()` - Compiles SCSS using Dart Sass (not node-sass)
- `generatePreviewHtml()` - Processes template with Mustache variables
- `setupTemplateWatcher()` - Watches `template/**/*` for changes

**Template Processing:**
```
template/index.html (Mustache template)
  {{title}}    → Extracted from markdown frontmatter
  {{{style}}}  → <style>compiled CSS from style.scss</style>
  {{{source}}} → source: "raw markdown content"
```

### Template System

The `template/` directory is the presentation engine:

**Required Files:**
- `index.html` - Mustache template with Remark.js initialization
- `style.scss` - Sass stylesheet (compiles to CSS)
- `remark.min.js` - Remark.js library (optional, falls back to CDN)
- `font/` - Custom fonts (League Gothic, Source Sans Pro)

**Template Variables (Mustache):**
- `{{title}}` - From `title: ...` in markdown frontmatter
- `{{{source}}}` - Markdown content as JavaScript string
- `{{{style}}}` - Compiled CSS wrapped in `<style>` tags

### Theater Caption File Structure

Caption markdown files follow this pattern:

```markdown
class: center, middle, smaller
BEGIN SETTINGS
---

title: PLAY TITLE
author: Author Name

[//]: # (Color-coded character assignments)
plum-purple: character-one
stiletto-red: character-two
st-tropaz-blue: character-three
...

layout: true
---
name: title
class: center, middle
---
name: music
class: center, middle
&#9834; &#9834;
---
name: song
class: song
---

class: center, middle, smaller
END SETTINGS
---
---

[Caption slides begin here]

## CHARACTER-NAME:
Dialogue text here.

---

template: music
(Song title or description)

---
```

**Remark.js Slide Syntax:**
- `---` = New slide
- `--` = Incremental content (click to reveal)
- `???` = Presenter notes (followed by content)
- `template: name` = Apply named template
- `class: className` = Apply CSS classes
- `## CHARACTER:` = H2 headers are character names (color-coded)

## Workflow Patterns

### Creating New Caption Files

1. Copy from `theater-templates/BOILERPLATE-*.md` or `BOILERPLATE.md`
2. Update title and character color mappings in settings section
3. Add caption slides with character dialogue
4. Use `bs serve` to preview live
5. Export with `bs export filename.md`

### Theater-Specific Templates

The `theater-templates/` directory contains boilerplates for specific theaters:
- `BOILERPLATE-Court-Theatre-center.md` - Center-aligned captions
- `BOILERPLATE-Court-Theatre-left.md` - Left-aligned captions
- `BOILERPLATE-Northlight-Theatre.md` - Northlight branding
- Each has pre-configured character colors and styling

### Script Formatting Toolkit

The `caption_toolkit.py` provides a unified pipeline for converting raw play scripts to CaptionPoint format. It consolidates and generalizes the functionality from various play-specific scripts.

#### Toolkit Commands

```bash
# Auto-detect characters in a script
python caption_toolkit.py detect script.md

# Stage 1: Clean - Remove stage directions, page numbers, act markers
python caption_toolkit.py clean script.md script-clean.md

# Stage 2: Format - Convert to CaptionPoint markdown
python caption_toolkit.py format script-clean.md script-formatted.md --characters "HAMLET,OPHELIA"

# Stage 3: Chunk - Break long dialogues into slides
python caption_toolkit.py chunk script-formatted.md script-final.md --max-chars 150

# Full pipeline - Run all stages at once
python caption_toolkit.py full script.md script-final.md --characters "HAMLET,OPHELIA" --verify
```

#### Processing Stages

1. **Clean Stage**: Removes artifacts from raw scripts
   - Parenthetical stage directions `(He exits)`
   - Page numbers (standalone digits)
   - ACT/SCENE markers
   - Options: `--keep-parens`, `--keep-pages`, `--keep-acts`

2. **Format Stage**: Converts to CaptionPoint markdown
   - Transforms `CHARACTER.` or `CHARACTER:` to `## CHARACTER:`
   - Splits lines with multiple speakers
   - Joins continuation lines
   - Auto-detects characters if not specified

3. **Chunk Stage**: Breaks long dialogues into slides
   - Splits at sentence boundaries
   - Default max 150 characters per slide
   - Preserves character headers on continuation slides

#### Legacy Scripts

These play-specific scripts are still available but `caption_toolkit.py` is preferred:
- `chunk_dialogue.py` - Line-based chunking (for specific character lists)
- `format_gaslight.py` - Gaslight-specific formatting
- `chunk_gaslight.py` - Character-based chunking
- `format_play_script.py` - Generic formatter with song detection
- `format_fair_lady.py` - My Fair Lady specific (handles songs)

## File Organization

```
captionpoint-plays/
├── template/              # Active presentation template
│   ├── index.html        # Remark.js template
│   ├── style.scss        # Theater caption styles
│   ├── remark.min.js     # Remark.js library
│   └── font/             # Custom fonts
├── theater-templates/     # Theater-specific boilerplates
├── !archives/            # Completed caption files
├── dist/                 # Exported HTML presentations
├── .tmp/                 # Temporary build files (gitignored)
├── vscode-extension/     # VSCode preview extension
├── backslide.js          # Main CLI implementation
├── chunk_dialogue.py     # Dialogue splitting utility
├── BOILERPLATE.md        # Generic caption template
└── PLAY-worksheet.md     # Template for new captions
```

## Key Styling Concepts

### Character Color Coding

Characters are assigned colors in the markdown frontmatter:
```markdown
plum-purple: hamlet
stiletto-red: ophelia
```

These map to CSS classes in `template/style.scss` and the boilerplate's embedded styles:
```scss
h2.hamlet { color: #862d86; }  // Maps to plum-purple
```

The boilerplate includes 20+ predefined color options for multi-character plays.

### Caption Display Classes

- `class: center, middle` - Centered slides (titles, scene breaks)
- `class: song` - Song lyrics styling
- `class: noise` - Sound effects
- `class: aside` - Stage directions
- `class: overlap` - Overlapping dialogue
- `class: smaller` - Reduced font size

### Font Size Control

Default: `$font-size: 5.3em` in `style.scss` for theater visibility
Character names: `$font-size-char: 70%` of main size

## Important Notes

- **Active directory is workspace root**, not subdirectories. The `bs` commands expect to run from the repository root where `template/` exists.
- **SCSS compilation** uses node-sass in CLI, but Dart Sass in VSCode extension
- **HTML exports are self-contained** - all resources inlined by default
- **Archived captions** go in `!archives/` directory
- **The template directory must exist** before running serve/export commands (use `bs init` if missing)
- **PDF export requires Decktape** installed globally: `npm i -g decktape`

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
**Smart dialogue chunker** for breaking long character monologues into readable slides. Automatically detects long paragraphs (>150 characters) and splits them into sentence-based chunks.

Features:
- Detects any character name in caps (## CHARACTER:)
- Identifies long paragraphs that need splitting
- Splits by sentences while preserving quoted dialogue
- Creates multiple slides per character when needed
- Preserves short dialogues and non-dialogue slides unchanged

Usage:
```bash
python3 chunk_dialogue.py input.md output.md 2  # 2 = max sentences per slide
python3 chunk_dialogue.py input.md output.md 3  # 3 = max sentences per slide
```

**Recommended**: Use 2-3 sentences per chunk for theater captioning. This creates more slides but improves on-screen readability during live performances.

Example results:
- Input: 874 slides → Output: 1,021 slides (2 sentences/chunk)
- Input: 874 slides → Output: 959 slides (3 sentences/chunk)

Use this after converting from PDF or when working with scripts that have long paragraph-style dialogue.

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

4. **Chunk long dialogues** (recommended for readability):
   ```bash
   python chunk_dialogue.py raw-output.md chunked-output.md 2
   ```
   - Use `2` for shorter, more readable chunks (recommended for captioning)
   - Use `3` for slightly longer chunks if screen real estate is limited
   - This splits long paragraph-style dialogue into sentence-based chunks
   - Creates more slides but dramatically improves readability during performances

5. **Preview and refine**:
   ```bash
   bs serve
   ```

6. **Deactivate when done**:
   ```bash
   deactivate
   ```

See [PDF_WORKFLOW.md](PDF_WORKFLOW.md) for detailed instructions and troubleshooting.

## Chunking Long Dialogues

When working with scripts that have long monologues or paragraph-style dialogue, use the chunking script to break them into readable slides.

### When to Chunk
- After importing from PDF/OCR (dialogue often comes in as long paragraphs)
- When individual dialogue slides have >150 characters
- When you need better on-screen readability for live performances
- When actors deliver long monologues that need pacing breaks

### Chunking Workflow
1. **Check if chunking is needed**:
   ```bash
   # Count slides before
   grep -c "^---$" input.md
   ```

2. **Run chunking script**:
   ```bash
   python3 scripts/chunk_dialogue.py input.md output.md 2
   ```

3. **Verify results**:
   ```bash
   # Count slides after
   grep -c "^---$" output.md

   # Preview in browser
   bs serve
   ```

4. **Adjust chunk size if needed**:
   - Too many slides? Use `3` sentences per chunk
   - Slides still too long? Use `1` sentence per chunk
   - Just right? Keep `2` sentences per chunk (recommended)

### Chunking Parameters
- **2 sentences** (recommended): Best balance of readability and slide count
- **3 sentences**: Good for screens with more space
- **1 sentence**: Maximum readability, creates most slides

### Example Results
The MARY JANE script chunking:
- **Before**: 874 slides, some with 400+ character paragraphs
- **After (2 sentences)**: 1,021 slides, max ~200 characters per slide
- **Result**: 147 new slides created, much more readable during performance

## Development Notes

- **Node Version**: Requires Node.js >= 10.0.0
- **Python Version**: Python 3.x required for PDF parsing tools
- **Linting**: Uses XO with Prettier formatting
- **Testing**: `npm test` runs XO linter
- **Deployment**: Uses gh-pages for static site deployment

When creating new play scripts, start from `BOILERPLATE.md` or use theater-specific templates from `theater-templates/` directory.
