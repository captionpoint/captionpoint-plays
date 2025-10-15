# Distribution Guide - Packaging for Others

## Prerequisites

Install the VS Code Extension packaging tool:

```bash
npm install -g @vscode/vsce
```

## Step 1: Prepare for Packaging

Make sure everything is compiled and ready:

```bash
cd vscode-extension
npm install
npm run compile
```

## Step 2: Package the Extension

Create a `.vsix` file that can be shared:

```bash
vsce package
```

This creates a file like: `remark-preview-0.1.0.vsix`

## Step 3: Test the Package

Before sharing, test it yourself:

1. Open VS Code
2. Go to Extensions (`Cmd+Shift+X` / `Ctrl+Shift+X`)
3. Click the `...` menu → "Install from VSIX..."
4. Select your `.vsix` file
5. Test it with a simple markdown file

## Step 4: Distribute to Users

### Option A: Direct File Sharing

1. Share the `.vsix` file directly (email, Dropbox, etc.)
2. Provide these installation instructions:

**Installation Instructions for Recipients:**

```
1. Download the remark-preview-X.X.X.vsix file
2. Open Visual Studio Code
3. Click Extensions icon in sidebar (or Cmd+Shift+X / Ctrl+Shift+X)
4. Click the "..." menu at the top
5. Select "Install from VSIX..."
6. Choose the downloaded .vsix file
7. Click "Reload" when prompted
8. Done! Open any .md file and press Cmd+Shift+V (Mac) or Ctrl+Shift+V (Windows)
```

### Option B: GitHub Release

1. Create a GitHub repository
2. Create a release
3. Upload the `.vsix` file as a release asset
4. Share the release URL

### Option C: VS Code Marketplace (Public Distribution)

For wider distribution:

1. Create a publisher account at https://marketplace.visualstudio.com/manage
2. Get a Personal Access Token from Azure DevOps
3. Publish:

```bash
vsce publish
```

**Note:** This makes it available to everyone via VS Code's built-in extension marketplace.

## What to Include in Your Distribution

### Minimum Package Contents

The `.vsix` file includes everything needed:
- Compiled extension code
- Default templates and styles
- All dependencies

### Recommended Additional Files

When sharing, also provide:

1. **USER_GUIDE.md** - For beginners
2. **Example markdown file** - `example-presentation.md`
3. **Quick start PDF** - One-page instructions

## Creating a Distribution Package

Create a folder to share:

```
remark-preview-distribution/
├── remark-preview-0.1.0.vsix
├── INSTALL.txt
├── USER_GUIDE.pdf
└── examples/
    ├── simple-presentation.md
    └── advanced-presentation.md
```

### Simple INSTALL.txt

```
REMARK.JS PREVIEW EXTENSION
Installation Instructions

STEP 1: Install the Extension
1. Open Visual Studio Code
2. Press Cmd+Shift+X (Mac) or Ctrl+Shift+X (Windows)
3. Click the "..." menu at the top of the Extensions panel
4. Choose "Install from VSIX..."
5. Select the remark-preview-0.1.0.vsix file
6. Click "Reload" when prompted

STEP 2: Try it Out
1. Open one of the example .md files from the examples folder
2. Press Cmd+Shift+V (Mac) or Ctrl+Shift+V (Windows)
3. See your presentation preview on the right!

STEP 3: Create Your Own
1. Create a new file ending in .md
2. Type some markdown (see USER_GUIDE for syntax)
3. Press Cmd+Shift+V to see the preview

NEED HELP?
See the USER_GUIDE.pdf for complete instructions

WEBSITE: [Your website here]
EMAIL: [Your email here]
```

## Version Updates

When you release a new version:

1. Update version in `package.json`:
   ```json
   "version": "0.2.0"
   ```

2. Recompile and repackage:
   ```bash
   npm run compile
   vsce package
   ```

3. The new `.vsix` file will have the updated version number

## Troubleshooting Common Packaging Issues

### "Missing publisher name"

Add to `package.json`:
```json
"publisher": "your-name"
```

### "Missing repository"

Add to `package.json`:
```json
"repository": {
  "type": "git",
  "url": "https://github.com/yourusername/remark-preview"
}
```

### Large package size

Check what's included:
```bash
vsce ls
```

Exclude unnecessary files in `.vscodeignore`

### Dependencies not included

Make sure to run:
```bash
npm install --production
```

Before packaging.

## For Advanced Users: Custom Templates

If you want to share a version with specific templates pre-configured:

1. Add your template files to `resources/`:
   ```
   resources/
   ├── default-template.html
   ├── default-style.css
   └── custom-theme/
       ├── style.scss
       └── fonts/
   ```

2. Modify the preview provider to use your templates

3. Package with your custom templates included

## Distribution Checklist

Before sharing your `.vsix` file:

- [ ] Tested on clean VS Code installation
- [ ] Tested on both Mac and Windows (if possible)
- [ ] Verified default styles work
- [ ] Verified custom templates work (if applicable)
- [ ] Created example presentations
- [ ] Written installation instructions
- [ ] Included USER_GUIDE
- [ ] Updated version number
- [ ] Added changelog/release notes

## Sample Email to Recipients

```
Subject: Remark.js Preview Extension for VS Code

Hi everyone!

I've packaged a VS Code extension that makes it super easy to create
slide presentations using simple markdown files.

WHAT IT DOES:
- Write presentations in plain text
- See live preview as you type
- No configuration needed - just install and go!

INSTALLATION:
1. Install Visual Studio Code (if you don't have it)
2. Install the extension (instructions in INSTALL.txt)
3. Open an example file and press Cmd+Shift+V (Mac) or Ctrl+Shift+V (Windows)

INCLUDED FILES:
- remark-preview-0.1.0.vsix (the extension)
- INSTALL.txt (step-by-step instructions)
- USER_GUIDE.pdf (complete documentation)
- examples/ folder (sample presentations)

Even if you've never used VS Code before, the instructions will guide you
through everything!

Let me know if you have any questions.

Cheers!
```

## Publishing to VS Code Marketplace (Optional)

If you want to make this publicly available:

### 1. Create Publisher Profile

```bash
vsce create-publisher your-publisher-name
```

### 2. Login

```bash
vsce login your-publisher-name
```

### 3. Publish

```bash
vsce publish
```

### 4. Update package.json

Add marketplace information:

```json
{
  "publisher": "your-publisher-name",
  "repository": {
    "type": "git",
    "url": "https://github.com/yourusername/remark-preview"
  },
  "bugs": {
    "url": "https://github.com/yourusername/remark-preview/issues"
  },
  "homepage": "https://github.com/yourusername/remark-preview#readme",
  "license": "MIT"
}
```

## Support and Maintenance

After distribution:

- Monitor for issues/questions from users
- Keep dependencies updated
- Release bug fixes as new versions
- Maintain documentation

## License Considerations

The extension bundles:
- Remark.js (MIT License) - https://github.com/gnab/remark
- Sass (MIT License) - https://github.com/sass/sass
- Google Fonts (Open Font License) - Used in default styles

Make sure to include appropriate license information if distributing publicly.

## Quick Package Command

For convenience, add to `package.json`:

```json
"scripts": {
  "package": "vsce package",
  "publish": "vsce publish"
}
```

Then just run:

```bash
npm run package
```

---

**You're ready to share your extension!** 🚀

The `.vsix` file contains everything users need - no additional setup required on their end!
