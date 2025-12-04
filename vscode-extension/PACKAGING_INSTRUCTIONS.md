# Packaging the Extension for Distribution

## What You Now Have

Your extension now works in **two modes**:

1. **Zero-config mode**: Anyone can use it with just a `.md` file - no template directory needed!
2. **Advanced mode**: Power users (like you) can still use custom `template/` directories

## Quick Package Steps

### 1. Install the packaging tool (one-time)

```bash
npm install -g @vscode/vsce
```

### 2. Navigate and compile

```bash
cd vscode-extension
npm install
npm run compile
```

### 3. Package it!

```bash
vsce package
```

This creates: `remark-preview-0.1.0.vsix`

## What to Share

### Minimum (Just the Extension)

Share the `.vsix` file with these instructions:

**Installation:**
1. Open VS Code
2. Extensions → `...` menu → "Install from VSIX..."
3. Select the `.vsix` file
4. Done!

**Usage:**
1. Create a `.md` file
2. Press `Cmd+Shift+V` (Mac) or `Ctrl+Shift+V` (Windows)

### Recommended (Complete Package)

Create a folder with:

```
remark-preview-package/
├── remark-preview-0.1.0.vsix
├── INSTALL.txt (simple instructions)
├── README-SIMPLE.md (beginner guide)
├── example-presentation.md (copy from resources/)
└── screenshots/ (optional - show what it looks like)
```

## Testing Before Distribution

1. **Package it** (see above)

2. **Install in VS Code**:
   - Extensions → Install from VSIX
   - Choose your `.vsix` file

3. **Test with no template directory**:
   - Create a new folder (empty except for a `.md` file)
   - Open in VS Code
   - Create a simple `.md` file
   - Press `Cmd+Shift+V`
   - Should work with default styles!

4. **Test with template directory**:
   - Use your existing captionpoint-plays folder
   - Open a `.md` file
   - Press `Cmd+Shift+V`
   - Should use your custom templates!

## Simple Install Instructions for Recipients

Create a file called `INSTALL.txt`:

```
REMARK.JS PREVIEW - INSTALLATION INSTRUCTIONS

STEP 1: Install VS Code (if you don't have it)
Download from: https://code.visualstudio.com/

STEP 2: Install This Extension
1. Open VS Code
2. Click the Extensions icon (looks like blocks) or press:
   - Mac: Cmd+Shift+X
   - Windows: Ctrl+Shift+X
3. Click the "..." menu at the top of Extensions panel
4. Choose "Install from VSIX..."
5. Select the "remark-preview-0.1.0.vsix" file
6. Click "Reload" if prompted

STEP 3: Create Your First Presentation
1. In VS Code, create a new file: "test.md"
2. Type this:

   title: My First Talk

   ---

   # Hello World

   This is my first slide!

   ---

   # Second Slide

   - Point 1
   - Point 2

3. Save the file (Cmd+S or Ctrl+S)
4. Press Cmd+Shift+V (Mac) or Ctrl+Shift+V (Windows)
5. See your presentation on the right!

STEP 4: Learn More
- Open README-SIMPLE.md for complete beginner guide
- Open example-presentation.md to see what's possible
- Press 'H' during presentation for keyboard shortcuts

NEED HELP?
The extension works with just a .md file - no other setup needed!

Questions? [Your contact info]
```

## What Makes This Beginner-Friendly

The extension now:

✅ **Works immediately** - No template directory required
✅ **Has beautiful defaults** - Professional-looking presentations out of the box
✅ **Uses CDN for Remark.js** - No need to download libraries
✅ **Gives clear errors** - Helpful messages if something's wrong
✅ **Fallbacks gracefully** - If custom templates fail, uses defaults

## For Your Advanced Users

They can still create a `template/` directory and customize:

```
their-project/
├── template/
│   ├── style.scss (custom styles)
│   ├── index.html (custom template)
│   └── font/ (custom fonts)
└── presentation.md
```

The extension automatically detects and uses it!

## Version History

When you make updates:

1. Update version in `package.json`:
   ```json
   "version": "0.2.0"
   ```

2. Add a `CHANGELOG.md`:
   ```markdown
   # Changelog

   ## [0.2.0] - 2024-XX-XX
   ### Added
   - New feature here

   ### Fixed
   - Bug fix here

   ## [0.1.0] - 2024-XX-XX
   - Initial release
   ```

3. Repackage:
   ```bash
   npm run compile
   vsce package
   ```

## Optional: Publish to Marketplace

Want to make it publicly available in VS Code's extension marketplace?

1. **Create publisher account**: https://marketplace.visualstudio.com/manage

2. **Get Personal Access Token** from Azure DevOps

3. **Login**:
   ```bash
   vsce login your-publisher-name
   ```

4. **Publish**:
   ```bash
   vsce publish
   ```

Now anyone can install it directly from VS Code without downloading files!

## Troubleshooting Package Creation

### "WARNING: Missing publisher name"

Add to `package.json`:
```json
"publisher": "your-name-here"
```

### "WARNING: Missing repository"

Either add to `package.json`:
```json
"repository": {
  "type": "git",
  "url": "https://github.com/yourusername/remark-preview"
}
```

Or ignore - it's just a warning, not an error.

### Package is too large

Check what's included:
```bash
vsce ls
```

Make sure `node_modules/` is excluded in `.vscodeignore`

## What's Included in the Package

The `.vsix` contains:

- ✅ Compiled JavaScript (`out/` folder)
- ✅ Default template HTML
- ✅ Default styles CSS
- ✅ Example presentation
- ✅ Dependencies (sass, etc.)
- ❌ Source TypeScript files (excluded)
- ❌ Development files (excluded)

## Quick Distribution Checklist

Before sending to others:

- [ ] Extension compiled (`npm run compile`)
- [ ] Package created (`vsce package`)
- [ ] Tested in clean VS Code (no template directory)
- [ ] Tested with template directory (for your workflow)
- [ ] Created installation instructions
- [ ] Included example presentation
- [ ] Version number is correct

## Ready to Share!

You now have:

1. **The extension file** (`.vsix`) - The actual extension
2. **User guides** - For different skill levels
3. **Examples** - Ready-to-use presentations
4. **Installation instructions** - Step-by-step for beginners

Anyone can install it and start creating presentations in minutes, even if they've never used VS Code before!

## Example Distribution Email

```
Subject: Easy Presentation Tool for VS Code

Hi team,

I've created a simple tool for making slide presentations using plain
text files. It works in Visual Studio Code (a free text editor).

WHAT YOU GET:
- Create presentations by writing simple text
- See live preview as you type
- No PowerPoint, no complex tools
- Works offline
- Free forever

TO INSTALL:
1. Install VS Code: https://code.visualstudio.com/
2. Follow the steps in INSTALL.txt (included)
3. That's it!

TO USE:
1. Create a .md file
2. Type some text
3. Press Cmd+Shift+V (Mac) or Ctrl+Shift+V (Windows)
4. See your presentation!

Included in this package:
- The extension file (.vsix)
- Installation guide (INSTALL.txt)
- Beginner tutorial (README-SIMPLE.md)
- Example presentation (example-presentation.md)

Even if you've never coded before, this is super easy. The instructions
walk you through everything!

Questions? Just reply to this email.

Cheers!
```

---

**You're ready to share your extension with the world!** 🎉

The beauty is: they don't need your specific setup. It works standalone!
