# Remark.js Preview for VS Code

A VS Code extension for live previewing [Remark.js](https://remarkjs.com) presentations with split-view editing. Built specifically for the CaptionPoint theater captioning workflow.

## Features

- **Split-view editing**: Edit markdown on the left, see live Remark.js presentation on the right
- **Live reload**: Preview updates automatically as you type
- **SCSS compilation**: Automatically compiles your `template/style.scss` file
- **Template integration**: Uses your existing `template/` directory structure
- **File watching**: Detects changes to template files and updates preview
- **Keyboard shortcut**: Press `Cmd+Shift+V` (Mac) or `Ctrl+Shift+V` (Windows/Linux) to open preview

## Installation

### Option 1: Install from Source (Recommended for development)

1. Navigate to the extension directory:
   ```bash
   cd vscode-extension
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Compile the extension:
   ```bash
   npm run compile
   ```

4. Open this directory in VS Code:
   ```bash
   code .
   ```

5. Press `F5` to launch a new VS Code window with the extension loaded

### Option 2: Package and Install

1. Install `vsce` (VS Code Extension Manager):
   ```bash
   npm install -g @vscode/vsce
   ```

2. Package the extension:
   ```bash
   cd vscode-extension
   vsce package
   ```

3. Install the `.vsix` file in VS Code:
   - Open VS Code
   - Go to Extensions view (`Cmd+Shift+X` or `Ctrl+Shift+X`)
   - Click the `...` menu at the top
   - Select "Install from VSIX..."
   - Choose the generated `.vsix` file

## Usage

### Opening a Preview

1. Open any markdown (`.md`) file in your workspace
2. Use one of these methods to open the preview:
   - **Keyboard shortcut**: `Cmd+Shift+V` (Mac) or `Ctrl+Shift+V` (Windows/Linux)
   - **Command Palette**: `Cmd+Shift+P` → Type "Remark: Open Preview to the Side"
   - **Editor title bar**: Click the preview icon (when editing a markdown file)

### Working with the Preview

- The preview automatically updates as you type
- Changes to `template/style.scss` are automatically compiled and applied
- Changes to `template/index.html` refresh the preview
- Use standard Remark.js syntax in your markdown files

## Requirements

Your workspace should have the following structure:

```
your-project/
├── template/
│   ├── index.html
│   ├── style.scss
│   └── remark.min.js
├── your-presentation.md
└── vscode-extension/
    └── (extension files)
```

### Template Files

- **template/index.html**: Remark.js HTML template (supports Mustache syntax)
- **template/style.scss**: Stylesheet for your presentations
- **template/remark.min.js**: Remark.js library (optional, falls back to CDN)

## Markdown Syntax

Write your presentations using standard Remark.js markdown syntax:

```markdown
title: My Presentation
class: center, middle

# My First Slide

---

# Second Slide

- Bullet point 1
- Bullet point 2

---

# Code Example

```javascript
function hello() {
  console.log('Hello, Remark!');
}
```
\`\`\`
```

### Slide Separators

- `---` creates a new slide
- `--` creates incremental content (appears on click)

### Presenter Notes

```markdown
???
These are presenter notes that won't appear on the slide
```

## Configuration

The extension uses your existing `template/` directory structure. No additional configuration needed!

### Supported Template Variables

In your `template/index.html`, use these Mustache variables:

- `{{title}}`: Extracted from markdown frontmatter
- `{{{style}}}`: Compiled CSS from `style.scss`
- `{{{source}}}`: Your markdown content

## Keyboard Shortcuts

| Command | Mac | Windows/Linux |
|---------|-----|---------------|
| Open Preview to Side | `Cmd+Shift+V` | `Ctrl+Shift+V` |

## Commands

Available commands in the Command Palette (`Cmd+Shift+P`):

- **Remark: Open Remark.js Preview** - Opens preview in current editor
- **Remark: Open Remark.js Preview to the Side** - Opens preview beside editor

## Troubleshooting

### Preview not updating

- Make sure you have a `template/` directory in your workspace root
- Check that `template/style.scss` exists and is valid SCSS
- Look for error messages in the VS Code Developer Tools (Help → Toggle Developer Tools)

### SCSS compilation errors

- Verify your `style.scss` syntax is valid
- Error messages will appear as VS Code notifications
- Check the Developer Console for detailed error messages

### Remark.js not loading

- Ensure `template/remark.min.js` exists in your template directory
- If missing, the extension will attempt to load from CDN
- Download Remark.js from [remarkjs.com](https://remarkjs.com)

## Development

### Building

```bash
npm run compile
```

### Watching for changes

```bash
npm run watch
```

### Testing

Press `F5` in VS Code to launch the Extension Development Host

## License

MIT

## Credits

Built for CaptionPoint theater captioning presentations using:
- [Remark.js](https://remarkjs.com) - Markdown-based presentation framework
- [Backslide](https://github.com/sinedied/backslide) - CLI tool for Remark.js presentations
- [Sass](https://sass-lang.com) - CSS preprocessing
