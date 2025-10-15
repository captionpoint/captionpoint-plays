# Quick Setup Guide

## Installation Steps

### 1. Install Dependencies

```bash
cd vscode-extension
npm install
```

### 2. Compile the Extension

```bash
npm run compile
```

### 3. Test the Extension

Open the extension directory in VS Code:

```bash
code .
```

Then press `F5` to launch a new VS Code window with the extension loaded.

### 4. Try It Out

In the new VS Code window that opens:

1. Open your captionpoint-plays project folder (the parent directory)
2. Open any `.md` file (e.g., `starter/presentation.md`)
3. Press `Cmd+Shift+V` (Mac) or `Ctrl+Shift+V` (Windows/Linux)
4. The preview should open to the side!

### 5. Make Changes

Edit your markdown file and watch the preview update in real-time!

## Troubleshooting

### "Cannot find module" errors

Run `npm install` again to ensure all dependencies are installed.

### TypeScript errors

Run `npm run compile` to compile the TypeScript files.

### Preview doesn't show

Make sure:
- You have a `template/` directory in your workspace root
- The `template/style.scss` file exists
- The `template/remark.min.js` file exists (or it will fall back to CDN)

## What's Next?

Once you've tested it and it works, you can:

1. **Use it regularly**: Just open any markdown file and press `Cmd+Shift+V`
2. **Package it**: Run `vsce package` to create a `.vsix` file you can share
3. **Customize it**: Edit the TypeScript files in `src/` to add features

## Project Structure

```
vscode-extension/
├── src/
│   ├── extension.ts        # Main extension entry point
│   └── previewProvider.ts  # Preview logic and SCSS compilation
├── package.json            # Extension manifest
├── tsconfig.json          # TypeScript configuration
└── README.md              # Full documentation
```

## Development Tips

- Run `npm run watch` to automatically recompile on file changes
- Press `Cmd+R` (Mac) or `Ctrl+R` (Windows/Linux) in the Extension Development Host to reload
- Check the Debug Console for error messages
