# VS Code Extension for Remark.js Preview

## Overview

I've created a VS Code extension that provides **live preview for your Remark.js presentations** with a split-view editor! This extension is specifically designed to work with your existing Backslide/CaptionPoint workflow.

## What It Does

- **Split-View Editing**: Markdown editor on the left, live Remark.js presentation preview on the right
- **Auto-Compilation**: Automatically compiles your `template/style.scss` file
- **Live Updates**: Preview updates in real-time as you type
- **Template Integration**: Uses your existing `template/` directory structure
- **File Watching**: Detects changes to template files and refreshes the preview
- **Easy Access**: Press `Cmd+Shift+V` (Mac) or `Ctrl+Shift+V` (Windows/Linux) to open preview

## Quick Start

### 1. Install Dependencies

```bash
cd vscode-extension
npm install
```

### 2. Compile the Extension

```bash
npm run compile
```

### 3. Launch for Testing

```bash
code vscode-extension
```

Then press `F5` in VS Code to launch the Extension Development Host.

### 4. Try It Out

In the new window that opens:

1. Open this project folder (captionpoint-plays)
2. Open any `.md` file (e.g., `starter/presentation.md`)
3. Press `Cmd+Shift+V` or click the preview icon in the editor title bar
4. Watch your Remark.js presentation appear on the right!

## File Structure

```
vscode-extension/
├── src/
│   ├── extension.ts           # Main extension entry point
│   │                          # - Registers commands
│   │                          # - Sets up event listeners
│   │                          # - Manages lifecycle
│   │
│   └── previewProvider.ts     # Preview implementation
│                              # - Compiles SCSS to CSS
│                              # - Renders Remark.js presentations
│                              # - Watches for file changes
│                              # - Updates preview in real-time
│
├── .vscode/
│   ├── launch.json           # Debug configuration
│   └── tasks.json            # Build tasks
│
├── package.json              # Extension manifest & dependencies
├── tsconfig.json            # TypeScript configuration
├── .eslintrc.json           # Code quality rules
├── .vscodeignore            # Files to exclude when packaging
├── .gitignore               # Git ignore rules
├── README.md                # Full documentation
└── SETUP.md                 # Quick setup guide
```

## How It Works

### 1. Extension Activation
When you open a markdown file, the extension activates and registers two commands:
- `remarkPreview.openPreview` - Opens preview in current editor
- `remarkPreview.openPreviewToSide` - Opens preview beside editor (default)

### 2. SCSS Compilation
The extension automatically:
- Finds your `template/style.scss` file
- Compiles it to CSS using the Sass library
- Injects the compiled CSS into the preview
- Watches for changes and recompiles automatically

### 3. Preview Generation
The extension:
- Reads your markdown file content
- Loads your `template/index.html` template
- Injects the compiled CSS and markdown content
- Embeds the `remark.min.js` library
- Renders everything in a VS Code webview panel

### 4. Live Updates
The extension watches for:
- Changes to your markdown file (updates preview immediately)
- Changes to template files (recompiles and updates preview)
- Active editor changes (switches preview to match)

## Key Features Explained

### SCSS Compilation
The extension uses the modern `sass` package to compile your SCSS:
```typescript
const result = sass.compile(scssPath, {
  loadPaths: [path.join(workspaceRoot, 'template')],
  style: 'compressed'
});
```

This means you maintain **one source of truth** for your styles - no need to keep separate CSS files!

### Template Processing
The extension uses Mustache variable replacement (same as Backslide):
- `{{title}}` - Extracted from markdown frontmatter
- `{{{style}}}` - Compiled CSS from style.scss
- `{{{source}}}` - Your markdown content as a JavaScript string

### File Watching
The extension automatically watches for changes to:
- `template/**/*.scss` - SCSS stylesheets
- `template/**/*.css` - CSS stylesheets
- `template/**/*.html` - HTML templates
- `template/**/*.js` - JavaScript files

## Commands Available

| Command | Description | Shortcut |
|---------|-------------|----------|
| Remark: Open Remark.js Preview | Opens preview in current editor | - |
| Remark: Open Remark.js Preview to the Side | Opens preview beside editor | `Cmd+Shift+V` (Mac)<br>`Ctrl+Shift+V` (Win/Linux) |

## Configuration Requirements

Your workspace should have this structure:

```
captionpoint-plays/
├── template/
│   ├── index.html         # Required: Remark.js HTML template
│   ├── style.scss         # Required: Presentation styles
│   └── remark.min.js      # Optional: Falls back to CDN if missing
│
├── your-presentation.md   # Your markdown files
└── vscode-extension/      # The extension
```

## Troubleshooting

### Preview doesn't appear
- Check that you have a `template/` directory in your workspace root
- Verify `template/style.scss` exists and is valid SCSS
- Open VS Code Developer Tools (Help → Toggle Developer Tools) for error messages

### SCSS compilation errors
- Check your SCSS syntax
- Look for error notifications in VS Code
- Check the Debug Console for detailed messages

### Remark.js not loading
- Ensure `template/remark.min.js` exists
- If missing, the extension will try to use the CDN version
- Check your internet connection if using CDN

## Next Steps

### For Regular Use

1. **Install the extension**:
   ```bash
   cd vscode-extension
   npm install
   npm run compile
   ```

2. **Use it**:
   - Open any `.md` file
   - Press `Cmd+Shift+V` (Mac) or `Ctrl+Shift+V` (Win/Linux)
   - Edit and watch the preview update!

### For Distribution

1. **Package the extension**:
   ```bash
   npm install -g @vscode/vsce
   cd vscode-extension
   vsce package
   ```

2. **Install the `.vsix` file**:
   - Open VS Code
   - Go to Extensions (`Cmd+Shift+X`)
   - Click `...` menu → "Install from VSIX..."
   - Select the generated `.vsix` file

3. **Share it**:
   - Share the `.vsix` file with your team
   - Or publish to the VS Code Marketplace

## Development Tips

### While Developing

```bash
cd vscode-extension
npm run watch  # Auto-recompile on changes
```

Then press `F5` to launch, and `Cmd+R` / `Ctrl+R` to reload after changes.

### Adding Features

Key files to modify:
- `src/extension.ts` - Add new commands or event listeners
- `src/previewProvider.ts` - Modify preview rendering or compilation
- `package.json` - Add new commands, keybindings, or settings

## Technical Details

### Dependencies

- **vscode**: VS Code extension API
- **sass**: Modern Sass compiler (Dart Sass)
- **typescript**: Type safety and modern JavaScript features

### TypeScript Configuration

The extension uses:
- ES2020 target for modern JavaScript features
- CommonJS modules for VS Code compatibility
- Strict type checking for safety
- Source maps for debugging

### Build Process

1. TypeScript files in `src/` are compiled to JavaScript
2. Output goes to `out/` directory
3. VS Code loads `out/extension.js` as the entry point

## Benefits Over Other Approaches

### vs. Using `bs serve`
- No need to run separate server
- Integrated directly in VS Code
- Side-by-side editing without switching windows
- Faster iteration cycle

### vs. Generic Markdown Preview
- Shows actual Remark.js presentation (not just rendered markdown)
- Uses your custom templates and styles
- Slide separators render correctly
- Presenter notes are handled properly

### vs. Reveal.js Extensions
- Built specifically for Remark.js
- Matches your existing Backslide workflow
- No configuration needed (uses existing template)
- Theater captioning-specific features supported

## Future Enhancement Ideas

If you want to extend this later, consider:

1. **Settings panel** - Configure ratio, theme, etc.
2. **Multiple templates** - Switch between different template styles
3. **Export command** - Export to HTML/PDF from within VS Code
4. **Slide navigation** - Jump to specific slides
5. **Presenter notes view** - Show notes in separate panel
6. **Live preview server** - Share preview URL for remote viewing

## Support

For issues or questions:

1. Check the README.md in the `vscode-extension/` directory
2. Look at SETUP.md for installation troubleshooting
3. Check VS Code Developer Tools console for errors
4. Review the TypeScript source code (it's well-commented!)

## License

MIT - Same as the parent CaptionPoint project

---

**Congratulations!** You now have a fully functional VS Code extension for previewing Remark.js presentations! 🎉
