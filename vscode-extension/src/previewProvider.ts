import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import * as sass from 'sass';

export class RemarkPreviewProvider {
  private panel: vscode.WebviewPanel | undefined;
  private context: vscode.ExtensionContext;
  private currentDocument: vscode.TextDocument | undefined;
  private templateWatcher: vscode.FileSystemWatcher | undefined;
  private compiledCss: string = '';

  constructor(context: vscode.ExtensionContext) {
    this.context = context;
    this.setupTemplateWatcher();
  }

  /**
   * Shows the preview panel
   */
  public async showPreview(document: vscode.TextDocument, sideBySide: boolean) {
    this.currentDocument = document;

    const column = sideBySide
      ? vscode.ViewColumn.Beside
      : vscode.ViewColumn.Active;

    if (this.panel) {
      this.panel.reveal(column);
    } else {
      this.panel = vscode.window.createWebviewPanel(
        'remarkPreview',
        'Remark Preview',
        column,
        {
          enableScripts: true,
          retainContextWhenHidden: true,
          localResourceRoots: [
            vscode.Uri.file(this.getWorkspaceRoot()),
            vscode.Uri.file(path.join(this.context.extensionPath, 'media'))
          ]
        }
      );

      this.panel.onDidDispose(() => {
        this.panel = undefined;
      });
    }

    await this.updatePreview(document);
  }

  /**
   * Updates the preview with the current document content
   */
  public async updatePreview(document: vscode.TextDocument) {
    if (!this.panel || document !== this.currentDocument) {
      return;
    }

    const html = await this.generatePreviewHtml(document);
    this.panel.webview.html = html;
  }

  /**
   * Syncs the preview to show the slide at the current cursor position
   */
  public syncPreviewToEditor(editor: vscode.TextEditor) {
    if (!this.panel || editor.document !== this.currentDocument) {
      return;
    }

    const cursorLine = editor.selection.active.line;
    const slideIndex = this.getSlideIndexAtLine(editor.document, cursorLine);

    // Send message to webview to jump to slide
    this.panel.webview.postMessage({
      command: 'gotoSlide',
      slideIndex: slideIndex
    });
  }

  /**
   * Calculates which slide the cursor is on based on line number
   */
  private getSlideIndexAtLine(document: vscode.TextDocument, line: number): number {
    const text = document.getText();
    const lines = text.split('\n');

    let slideIndex = 0;
    for (let i = 0; i <= line && i < lines.length; i++) {
      // Slide separator is ---
      if (lines[i].trim() === '---') {
        slideIndex++;
      }
    }

    return slideIndex;
  }

  /**
   * Compiles SCSS to CSS and fixes relative URLs
   */
  private async compileScss(): Promise<string> {
    const workspaceRoot = this.getWorkspaceRoot();
    const scssPath = path.join(workspaceRoot, 'template', 'style.scss');

    // Check if custom template exists
    if (!fs.existsSync(scssPath)) {
      // Use default styles
      console.log('Using default styles (no template/style.scss found)');
      return this.getDefaultStyles();
    }

    try {
      const result = sass.compile(scssPath, {
        loadPaths: [path.join(workspaceRoot, 'template')],
        style: 'compressed'
      });

      // Fix relative URLs in the CSS to use webview URIs
      let css = result.css;
      if (this.panel) {
        css = this.fixCssUrls(css, workspaceRoot);
      }

      return css;
    } catch (error) {
      console.error('SCSS compilation error:', error);
      vscode.window.showErrorMessage(`SCSS compilation failed: ${error}`);
      return this.getDefaultStyles();
    }
  }

  /**
   * Converts relative URLs in CSS to webview URIs
   */
  private fixCssUrls(css: string, workspaceRoot: string): string {
    // Match url(...) patterns in CSS
    const urlPattern = /url\(['"]?([^'")]+)['"]?\)/g;

    return css.replace(urlPattern, (match, url) => {
      // Skip absolute URLs, data URIs, and URLs that start with http/https
      if (url.startsWith('http') || url.startsWith('data:') || url.startsWith('/')) {
        return match;
      }

      // Resolve relative URL to absolute path
      const absolutePath = path.join(workspaceRoot, 'template', url);

      // Check if file exists
      if (!fs.existsSync(absolutePath)) {
        console.warn(`Font file not found: ${absolutePath}`);
        return match;
      }

      // Convert to webview URI
      const webviewUri = this.panel!.webview.asWebviewUri(
        vscode.Uri.file(absolutePath)
      );

      return `url('${webviewUri}')`;
    });
  }

  /**
   * Generates the HTML for the preview
   */
  private async generatePreviewHtml(document: vscode.TextDocument): Promise<string> {
    const workspaceRoot = this.getWorkspaceRoot();
    const templatePath = path.join(workspaceRoot, 'template', 'index.html');
    const remarkJsPath = path.join(workspaceRoot, 'template', 'remark.min.js');

    // Compile SCSS if not already compiled or if template changed
    if (!this.compiledCss) {
      this.compiledCss = await this.compileScss();
    }

    // Read the markdown content
    const markdownContent = document.getText();

    // Extract configuration from markdown frontmatter
    const config = this.extractConfig(markdownContent);
    console.log('Extracted config:', JSON.stringify(config));

    // Get remark.js URI for webview
    let remarkJsScript = '';
    if (fs.existsSync(remarkJsPath)) {
      const remarkJsUri = this.panel!.webview.asWebviewUri(
        vscode.Uri.file(remarkJsPath)
      );
      remarkJsScript = `<script src="${remarkJsUri}"></script>`;
    } else {
      // Fallback to CDN if local file doesn't exist (no warning - this is expected for beginners)
      remarkJsScript = '<script src="https://remarkjs.com/downloads/remark-latest.min.js"></script>';
    }

    // Read template or use default
    let template = '';
    if (fs.existsSync(templatePath)) {
      template = fs.readFileSync(templatePath, 'utf-8');
    } else {
      template = this.getDefaultTemplate();
    }

    // Process template - replace all template variables
    console.log('Compiled CSS length:', this.compiledCss.length);
    console.log('First 100 chars of CSS:', this.compiledCss.substring(0, 100));

    let html = template
      .replace(/\{\{title\}\}/g, config.title)
      .replace(/\{\{\{title\}\}\}/g, config.title)
      .replace('{{{style}}}', `<style>${this.compiledCss}</style>`)
      .replace('{{{source}}}', `source: ${this.escapeMarkdown(markdownContent)}`)
      .replace('{{{remarkScript}}}', remarkJsScript);

    // Inject ratio from YAML frontmatter if specified
    if (config.ratio) {
      console.log('Attempting to inject ratio:', config.ratio);
      const beforeReplace = html.substring(0, 500);
      html = html.replace(/ratio:\s*['"][^'"]*['"]/g, `ratio: '${config.ratio}'`);
      console.log('Ratio injected. HTML snippet before:', beforeReplace.match(/ratio:\s*['"][^'"]*['"]/));
    }

    // Inject custom font-size if specified
    if (config.fontSize) {
      console.log('Injecting custom fontSize:', config.fontSize);
      const fontSizeStyle = `<style>.remark-slide-content { font-size: ${config.fontSize} !important; }</style>`;
      html = html.replace('</head>', `${fontSizeStyle}</head>`);
    }

    // Add debug comment to HTML
    const debugComment = `<!-- CaptionPoint Config: ${JSON.stringify(config)} -->`;
    html = html.replace('<head>', `<head>${debugComment}`);

    console.log('HTML contains <style>?', html.includes('<style>'));
    console.log('HTML contains CSS?', html.includes('remark-slide-content'));

    // Also handle old-style template (for backwards compatibility with custom templates)
    html = html.replace(/<script src="remark\.min\.js"><\/script>/g, remarkJsScript);

    // Add auto-refresh capability
    html = this.addRefreshScript(html);

    // Log a snippet of the generated HTML to verify structure
    const headEnd = html.indexOf('</head>');
    if (headEnd > 0) {
      console.log('HEAD section (first 500 chars):', html.substring(0, Math.min(500, headEnd)));
    }

    // Write full HTML to temp file for debugging
    const tempPath = path.join(require('os').tmpdir(), 'remark-preview-debug.html');
    fs.writeFileSync(tempPath, html);
    console.log('Full HTML written to:', tempPath);
    console.log('Open this in browser to see what we are generating');

    return html;
  }

  /**
   * Extracts title from markdown frontmatter
   */
  private extractTitle(markdown: string): string {
    const titleMatch = markdown.match(/^title:\s*(.+)$/m);
    return titleMatch ? titleMatch[1].trim() : 'Remark Presentation';
  }

  /**
   * Extracts configuration from markdown frontmatter
   * Looks for YAML frontmatter at the very start: ---\nkey: value\n---
   */
  private extractConfig(markdown: string): { title: string; ratio?: string; template?: string; fontSize?: string } {
    // Check if file starts with YAML frontmatter (must be at position 0)
    const yamlMatch = markdown.match(/^---\s*\n([\s\S]*?)\n---/);

    let title = 'Remark Presentation';
    let ratio: string | undefined;
    let template: string | undefined;
    let fontSize: string | undefined;

    if (yamlMatch) {
      const yamlContent = yamlMatch[1];
      console.log('Found YAML frontmatter:', yamlContent);

      const titleMatch = yamlContent.match(/^title:\s*(.+)$/m);
      const ratioMatch = yamlContent.match(/^ratio:\s*['"]?([^'"\n]+)['"]?$/m);
      const templateMatch = yamlContent.match(/^template:\s*(.+)$/m);
      const fontSizeMatch = yamlContent.match(/^fontSize:\s*(.+)$/m);

      title = titleMatch ? titleMatch[1].trim() : title;
      ratio = ratioMatch ? ratioMatch[1].trim() : undefined;
      template = templateMatch ? templateMatch[1].trim() : undefined;
      fontSize = fontSizeMatch ? fontSizeMatch[1].trim() : undefined;
    } else {
      // Fallback: try to find title anywhere in the document
      const titleMatch = markdown.match(/^title:\s*(.+)$/m);
      if (titleMatch) {
        title = titleMatch[1].trim();
      }
    }

    return { title, ratio, template, fontSize };
  }

  /**
   * Escapes markdown content for embedding in JavaScript
   */
  private escapeMarkdown(markdown: string): string {
    return JSON.stringify(markdown).replace(/<\/script>/g, '<\\/script>');
  }

  /**
   * Adds auto-refresh script to HTML
   */
  private addRefreshScript(html: string): string {
    const script = `
      <script>
        (function() {
          const vscode = acquireVsCodeApi();

          // Listen for messages from the extension
          window.addEventListener('message', event => {
            const message = event.data;
            if (message.command === 'refresh') {
              location.reload();
            }
          });
        })();
      </script>
    `;

    return html.replace('</body>', `${script}</body>`);
  }

  /**
   * Gets default styles if no template exists
   */
  private getDefaultStyles(): string {
    const defaultStylePath = path.join(this.context.extensionPath, 'resources', 'default-style.css');

    console.log('Looking for default styles at:', defaultStylePath);
    console.log('Extension path:', this.context.extensionPath);
    console.log('File exists?', fs.existsSync(defaultStylePath));

    if (fs.existsSync(defaultStylePath)) {
      const styles = fs.readFileSync(defaultStylePath, 'utf-8');
      console.log('Loaded default styles, length:', styles.length);
      return styles;
    }

    // Fallback inline styles if resource file doesn't exist
    console.warn('Default style file not found, using fallback styles');
    return `
      body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
      h1, h2, h3 { font-weight: 400; margin-bottom: 0; }
      .remark-slide-content { font-size: 20px; padding: 1em 4em; }
      .remark-code, .remark-inline-code { font-family: 'Monaco', 'Courier New', monospace; }
      .inverse { background: #272822; color: #f3f3f3; }
    `;
  }

  /**
   * Gets default template if none exists
   */
  private getDefaultTemplate(): string {
    const defaultTemplatePath = path.join(this.context.extensionPath, 'resources', 'default-template.html');

    if (fs.existsSync(defaultTemplatePath)) {
      return fs.readFileSync(defaultTemplatePath, 'utf-8');
    }

    // Fallback template if resource file doesn't exist
    return `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>{{title}}</title>
  {{{style}}}
  <script src="https://remarkjs.com/downloads/remark-latest.min.js"></script>
  <script>
    function create() {
      return remark.create({
        {{{source}}},
        ratio: '16:9',
        highlightLines: true,
        countIncrementalSlides: false,
        highlightStyle: 'github'
      });
    }
  </script>
</head>
<body onload="slideshow = create()">
</body>
</html>`;
  }

  /**
   * Sets up file watcher for template directory
   */
  private setupTemplateWatcher() {
    const workspaceRoot = this.getWorkspaceRoot();
    const templateGlob = new vscode.RelativePattern(
      workspaceRoot,
      'template/**/*.{scss,css,html,js}'
    );

    this.templateWatcher = vscode.workspace.createFileSystemWatcher(templateGlob);

    this.templateWatcher.onDidChange(async () => {
      // Recompile SCSS when template files change
      this.compiledCss = await this.compileScss();
      if (this.currentDocument) {
        await this.updatePreview(this.currentDocument);
      }
    });

    this.templateWatcher.onDidCreate(async () => {
      this.compiledCss = await this.compileScss();
      if (this.currentDocument) {
        await this.updatePreview(this.currentDocument);
      }
    });
  }

  /**
   * Gets the workspace root directory
   */
  private getWorkspaceRoot(): string {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (workspaceFolders && workspaceFolders.length > 0) {
      return workspaceFolders[0].uri.fsPath;
    }
    return '';
  }

  /**
   * Disposes of resources
   */
  public dispose() {
    if (this.panel) {
      this.panel.dispose();
    }
    if (this.templateWatcher) {
      this.templateWatcher.dispose();
    }
  }
}
