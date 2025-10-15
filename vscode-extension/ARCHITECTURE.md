# Extension Architecture

## Overview

This document explains how the Remark.js Preview extension works internally.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      VS Code Editor                          │
│  ┌─────────────────────┐       ┌─────────────────────────┐  │
│  │                     │       │                         │  │
│  │  Markdown Editor    │       │   Remark.js Preview     │  │
│  │                     │       │     (Webview Panel)     │  │
│  │  presentation.md    │◄─────►│                         │  │
│  │                     │       │   Live Presentation     │  │
│  │  Edit here...       │       │   [Slide 1]             │  │
│  │                     │       │   [Slide 2]             │  │
│  │                     │       │   [Slide 3]             │  │
│  └─────────────────────┘       └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                      ▲
                      │
                      ▼
            ┌─────────────────────┐
            │  Extension Process   │
            │                      │
            │  1. Watch for changes│
            │  2. Compile SCSS     │
            │  3. Generate HTML    │
            │  4. Update webview   │
            └─────────────────────┘
                      ▲
                      │
                      ▼
            ┌─────────────────────┐
            │   Template Files     │
            │                      │
            │  - index.html        │
            │  - style.scss        │
            │  - remark.min.js     │
            └─────────────────────┘
```

## Component Breakdown

### 1. Extension Entry Point (`extension.ts`)

**Purpose**: Initializes the extension and registers commands

**Key Functions**:
- `activate()` - Called when extension loads
  - Creates PreviewProvider instance
  - Registers commands
  - Sets up event listeners
- `deactivate()` - Cleanup when extension unloads

**Event Listeners**:
- `onDidChangeActiveTextEditor` - Switch preview when changing files
- `onDidChangeTextDocument` - Update preview when typing

### 2. Preview Provider (`previewProvider.ts`)

**Purpose**: Core logic for rendering and updating the preview

**Key Methods**:

#### `showPreview(document, sideBySide)`
Opens or reveals the webview panel
- Creates new panel if doesn't exist
- Sets up panel configuration (scripts enabled, local resources)
- Calls `updatePreview()` to render content

#### `updatePreview(document)`
Regenerates and updates the preview HTML
- Compiles SCSS if needed
- Reads markdown content
- Processes template
- Updates webview

#### `compileScss()`
Compiles SCSS to CSS
- Finds `template/style.scss`
- Uses Sass library to compile
- Returns compressed CSS
- Shows errors if compilation fails

#### `generatePreviewHtml(document)`
Creates the final HTML for the webview
- Reads template files
- Extracts title from markdown
- Processes Mustache variables
- Inlines remark.js
- Returns complete HTML

#### `setupTemplateWatcher()`
Watches for template file changes
- Creates FileSystemWatcher for template directory
- Triggers recompilation on changes
- Updates preview automatically

## Data Flow

### Initial Preview Opening

```
User presses Cmd+Shift+V
         │
         ▼
Command: remarkPreview.openPreviewToSide
         │
         ▼
PreviewProvider.showPreview()
         │
         ├─► Create webview panel (if needed)
         │
         └─► updatePreview()
                  │
                  ├─► compileScss()
                  │    │
                  │    └─► Read template/style.scss
                  │         │
                  │         └─► Compile with Sass
                  │
                  ├─► generatePreviewHtml()
                  │    │
                  │    ├─► Read markdown content
                  │    ├─► Read template/index.html
                  │    ├─► Extract title
                  │    ├─► Process Mustache variables
                  │    └─► Inline remark.js
                  │
                  └─► Update webview.html
```

### Live Updates (Typing in Markdown)

```
User types in editor
         │
         ▼
onDidChangeTextDocument event
         │
         ▼
PreviewProvider.updatePreview()
         │
         └─► (Same flow as above, but SCSS cached)
```

### Template Changes

```
User edits template/style.scss
         │
         ▼
FileSystemWatcher detects change
         │
         ▼
PreviewProvider.compileScss()
         │
         └─► Recompile SCSS
                  │
                  └─► updatePreview()
```

## Template Processing

### Input Template (`template/index.html`)

```html
<!DOCTYPE html>
<html>
<head>
  <title>{{title}}</title>
  {{{style}}}
  <script src="remark.min.js"></script>
  <script>
    function create() {
      return remark.create({
        {{{source}}},
        ratio: '16:9'
      });
    }
  </script>
</head>
<body onload="slideshow = create()">
</body>
</html>
```

### Variable Replacement

| Variable | Replaced With | Source |
|----------|--------------|--------|
| `{{title}}` | Presentation title | Extracted from `title:` in markdown frontmatter |
| `{{{style}}}` | `<style>...compiled CSS...</style>` | Compiled from `template/style.scss` |
| `{{{source}}}` | `source: "...markdown content..."` | Raw markdown file content (escaped) |

### Output HTML (Simplified)

```html
<!DOCTYPE html>
<html>
<head>
  <title>My Presentation</title>
  <style>
    /* Compiled CSS from style.scss */
    body { font-family: sans-serif; }
    .remark-slide-content { padding: 2em; }
    /* ... more styles ... */
  </style>
  <script>
    /* remark.min.js content inlined here */
  </script>
  <script>
    function create() {
      return remark.create({
        source: "title: My Presentation\n\n---\n\n# Slide 1\n...",
        ratio: '16:9'
      });
    }
  </script>
</head>
<body onload="slideshow = create()">
</body>
</html>
```

## SCSS Compilation Details

### Process

1. **Find SCSS file**: `template/style.scss`
2. **Configure Sass compiler**:
   ```typescript
   sass.compile(scssPath, {
     loadPaths: [path.join(workspaceRoot, 'template')],
     style: 'compressed'
   })
   ```
3. **Cache result**: Stored in `compiledCss` variable
4. **Inject into template**: Wrapped in `<style>` tags

### Why Sass Instead of node-sass?

- **Modern**: Uses Dart Sass (the reference implementation)
- **Maintained**: node-sass is deprecated
- **Fast**: Compiles quickly for preview updates
- **Compatible**: Works with existing SCSS syntax

## File Watching

### What's Watched

```typescript
const templateGlob = new vscode.RelativePattern(
  workspaceRoot,
  'template/**/*.{scss,css,html,js}'
);
```

Watches for changes to:
- `template/**/*.scss` - Stylesheets
- `template/**/*.css` - CSS files
- `template/**/*.html` - Templates
- `template/**/*.js` - Scripts

### Actions on Change

1. **SCSS files**: Recompile → Update preview
2. **HTML files**: Reload template → Update preview
3. **JS files**: Reload scripts → Update preview

## Security Considerations

### Webview Security

```typescript
{
  enableScripts: true,           // Allow remark.js to run
  retainContextWhenHidden: true, // Keep state when hidden
  localResourceRoots: [          // Only allow these paths
    vscode.Uri.file(workspaceRoot),
    vscode.Uri.file(extensionPath)
  ]
}
```

### Content Security

- Scripts are enabled (required for remark.js)
- Local resources restricted to workspace and extension directories
- No external network requests (except CDN fallback)

## Performance Optimizations

### 1. SCSS Caching
- Compiled CSS cached in memory
- Only recompiled when template changes
- Avoids unnecessary compilation on every keystroke

### 2. Debouncing
- VS Code handles debouncing of document changes
- Only updates after user stops typing

### 3. Selective Updates
- Only updates preview if it's the active document
- Doesn't update hidden previews

## Error Handling

### SCSS Compilation Errors

```typescript
try {
  const result = sass.compile(scssPath, {...});
  return result.css;
} catch (error) {
  vscode.window.showErrorMessage(`SCSS compilation failed: ${error}`);
  return ''; // Return empty CSS, don't crash
}
```

### Missing Template Files

- **index.html missing**: Use default template
- **style.scss missing**: Use empty styles
- **remark.min.js missing**: Attempt CDN fallback

### File System Errors

All file operations wrapped in try-catch blocks with user-friendly error messages.

## Extension Lifecycle

### Activation

```
User opens markdown file
         │
         ▼
Extension activates
         │
         ├─► Create PreviewProvider
         ├─► Register commands
         ├─► Set up file watchers
         └─► Set up event listeners
```

### Runtime

```
Extension running
         │
         ├─► Listen for document changes
         ├─► Listen for editor changes
         ├─► Listen for template changes
         └─► Update previews as needed
```

### Deactivation

```
VS Code closing
         │
         ▼
Extension deactivates
         │
         ├─► Dispose webview panels
         ├─► Dispose file watchers
         └─► Clean up resources
```

## Future Enhancement Possibilities

### 1. Configuration Settings

Add VS Code settings for:
- Ratio (16:9, 4:3, etc.)
- Highlight style
- Default template path

### 2. Multiple Templates

Allow users to switch between different template styles:
```typescript
vscode.workspace.getConfiguration('remarkPreview').get('templatePath')
```

### 3. Export Features

Add commands to export directly from preview:
- Export to HTML
- Export to PDF (using Decktape)
- Export individual slides as images

### 4. Slide Navigation

Add UI controls to:
- Jump to specific slides
- Navigate forward/backward
- Show slide thumbnails

### 5. Presenter Mode

Add features for presenting:
- Timer
- Notes view
- Remote control
- Dual-screen mode

## Debugging Tips

### Enable Debug Output

1. Open Extension Development Host
2. Open Developer Tools (Help → Toggle Developer Tools)
3. Check Console tab for messages

### Common Debug Points

- **SCSS compilation**: Check console for Sass errors
- **Template processing**: Log template variables before replacement
- **File watching**: Log when file watcher fires
- **Preview updates**: Log when `updatePreview()` is called

### Breakpoints

Set breakpoints in TypeScript files:
- `extension.ts:12` - Command registration
- `previewProvider.ts:28` - Preview creation
- `previewProvider.ts:77` - SCSS compilation
- `previewProvider.ts:95` - HTML generation

## Code Quality

### TypeScript Strict Mode

All files use strict TypeScript settings:
- No implicit `any`
- Null checking
- Strict function types

### ESLint Rules

Enforces:
- Consistent naming conventions
- Semicolons
- Curly braces
- No throw literals

### Error Handling

All async operations properly handle errors with try-catch or Promise.catch()
