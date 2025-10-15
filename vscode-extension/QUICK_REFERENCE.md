# Remark.js Preview - Quick Reference

## Installation (First Time Only)

```bash
cd vscode-extension
npm install
npm run compile
```

## Development Workflow

```bash
# Start watching for changes (automatic recompilation)
npm run watch

# Open in VS Code
code .

# Press F5 to launch Extension Development Host
```

## Using the Extension

| Action | Shortcut (Mac) | Shortcut (Win/Linux) |
|--------|----------------|----------------------|
| Open preview to side | `Cmd+Shift+V` | `Ctrl+Shift+V` |
| Reload extension | `Cmd+R` | `Ctrl+R` |

## Commands

Open Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`) and type:

- `Remark: Open Remark.js Preview`
- `Remark: Open Remark.js Preview to the Side`

## File Structure

```
your-project/
├── template/
│   ├── index.html         # Required
│   ├── style.scss         # Required
│   └── remark.min.js      # Optional
│
├── your-slides.md         # Your presentations
│
└── vscode-extension/
    ├── src/
    │   ├── extension.ts        # Entry point
    │   └── previewProvider.ts  # Main logic
    └── package.json
```

## Remark.js Markdown Syntax

### Slide Separator
```markdown
---
```

### Incremental Content
```markdown
--
```

### Presenter Notes
```markdown
???
These notes won't show on slides
```

### Frontmatter
```markdown
title: My Presentation
class: center, middle
layout: true
```

### Classes
```markdown
class: impact

# This slide has the 'impact' class
```

### Inline Classes
```markdown
This is .red[red text] and this is .big[big text]
```

### Two Columns
```markdown
.col-6[
  Left column content
]
.col-6[
  Right column content
]
```

## Troubleshooting

### Preview doesn't show
```bash
# Check template exists
ls -la template/

# Should see:
# - index.html
# - style.scss
# - remark.min.js (optional)
```

### SCSS errors
1. Check syntax in `template/style.scss`
2. Look for error notification in VS Code
3. Check Debug Console (Help → Toggle Developer Tools)

### Extension not loading
1. Ensure you compiled: `npm run compile`
2. Check `out/` directory exists
3. Press `Cmd+R` / `Ctrl+R` to reload

### Changes not appearing
1. Check you're editing the right file
2. Ensure preview is focused on same file
3. Try closing and reopening preview

## Keyboard Shortcuts

### In Extension Development Host

| Action | Mac | Windows/Linux |
|--------|-----|---------------|
| Open preview | `Cmd+Shift+V` | `Ctrl+Shift+V` |
| Command palette | `Cmd+Shift+P` | `Ctrl+Shift+P` |
| Reload window | `Cmd+R` | `Ctrl+R` |
| Developer tools | `Cmd+Option+I` | `Ctrl+Shift+I` |

### In Remark Presentation

| Action | Key |
|--------|-----|
| Next slide | `→` or `Page Down` or `Space` |
| Previous slide | `←` or `Page Up` |
| First slide | `Home` |
| Last slide | `End` |
| Presenter mode | `P` |
| Clone presentation | `C` |
| Help | `H` or `?` |

## npm Scripts

```bash
# Compile TypeScript once
npm run compile

# Watch for changes and auto-compile
npm run watch

# Run linter
npm run lint

# Package extension (requires @vscode/vsce)
npm run vscode:prepublish
```

## Package Extension for Distribution

```bash
# Install packaging tool
npm install -g @vscode/vsce

# Package
cd vscode-extension
vsce package

# Creates: remark-preview-0.1.0.vsix
```

## Install Packaged Extension

1. Open VS Code
2. Extensions view (`Cmd+Shift+X` / `Ctrl+Shift+X`)
3. Click `...` menu → "Install from VSIX..."
4. Select `.vsix` file

## Debugging

### View Console Output

1. In Extension Development Host
2. Help → Toggle Developer Tools
3. Console tab shows errors and logs

### Set Breakpoints

1. Open `src/extension.ts` or `src/previewProvider.ts`
2. Click in gutter to set breakpoint
3. Press `F5` to start debugging
4. Trigger the code path

## Common Tasks

### Change keyboard shortcut

Edit `package.json`:
```json
"keybindings": [
  {
    "command": "remarkPreview.openPreviewToSide",
    "key": "ctrl+shift+v",
    "mac": "cmd+shift+v"  // Change this
  }
]
```

### Change preview position

In extension, change `ViewColumn`:
```typescript
const column = vscode.ViewColumn.Beside; // or Two, Three, etc.
```

### Add configuration options

1. Add to `package.json`:
```json
"configuration": {
  "properties": {
    "remarkPreview.ratio": {
      "type": "string",
      "default": "16:9",
      "description": "Aspect ratio"
    }
  }
}
```

2. Use in code:
```typescript
const ratio = vscode.workspace.getConfiguration('remarkPreview').get('ratio');
```

## File Locations

| File | Purpose |
|------|---------|
| `src/extension.ts` | Extension entry point, commands |
| `src/previewProvider.ts` | Preview logic, SCSS compilation |
| `package.json` | Extension manifest, dependencies |
| `tsconfig.json` | TypeScript settings |
| `.vscode/launch.json` | Debug configuration |
| `.vscode/tasks.json` | Build tasks |

## VS Code Extension API

### Key APIs Used

```typescript
// Create webview panel
vscode.window.createWebviewPanel(...)

// Register command
vscode.commands.registerCommand(...)

// Watch files
vscode.workspace.createFileSystemWatcher(...)

// Listen to editor changes
vscode.window.onDidChangeActiveTextEditor(...)

// Listen to document changes
vscode.workspace.onDidChangeTextDocument(...)
```

## Resources

- [VS Code Extension API](https://code.visualstudio.com/api)
- [Remark.js Documentation](https://github.com/gnab/remark/wiki)
- [Sass Documentation](https://sass-lang.com/documentation)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)

## Quick Tips

1. **Auto-compile**: Run `npm run watch` before development
2. **Reload fast**: `Cmd+R` / `Ctrl+R` in Extension Development Host
3. **Check console**: Developer Tools Console shows all errors
4. **Test with examples**: Use `starter/presentation.md` for testing
5. **Keep it simple**: Start with basic features, add complexity later

## Getting Help

1. Check `README.md` for full documentation
2. Check `SETUP.md` for installation issues
3. Check `ARCHITECTURE.md` to understand internals
4. Check `VSCODE_EXTENSION_GUIDE.md` for overview
5. Check VS Code Extension samples on GitHub
