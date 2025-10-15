import * as vscode from 'vscode';
import { RemarkPreviewProvider } from './previewProvider';

let previewProvider: RemarkPreviewProvider | undefined;

export function activate(context: vscode.ExtensionContext) {
  console.log('Remark.js Preview extension is now active');

  // Initialize the preview provider
  previewProvider = new RemarkPreviewProvider(context);

  // Register the preview commands
  context.subscriptions.push(
    vscode.commands.registerCommand('remarkPreview.openPreview', () => {
      if (vscode.window.activeTextEditor) {
        previewProvider?.showPreview(vscode.window.activeTextEditor.document, false);
      } else {
        vscode.window.showInformationMessage('Open a markdown file to preview');
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('remarkPreview.openPreviewToSide', () => {
      if (vscode.window.activeTextEditor) {
        previewProvider?.showPreview(vscode.window.activeTextEditor.document, true);
      } else {
        vscode.window.showInformationMessage('Open a markdown file to preview');
      }
    })
  );

  // Auto-update preview when active editor changes
  context.subscriptions.push(
    vscode.window.onDidChangeActiveTextEditor(editor => {
      if (editor && editor.document.languageId === 'markdown') {
        previewProvider?.updatePreview(editor.document);
      }
    })
  );

  // Auto-update preview when document changes
  context.subscriptions.push(
    vscode.workspace.onDidChangeTextDocument(e => {
      if (e.document.languageId === 'markdown') {
        previewProvider?.updatePreview(e.document);
      }
    })
  );

  // Jump to slide when cursor position changes
  context.subscriptions.push(
    vscode.window.onDidChangeTextEditorSelection(e => {
      if (e.textEditor.document.languageId === 'markdown') {
        previewProvider?.syncPreviewToEditor(e.textEditor);
      }
    })
  );
}

export function deactivate() {
  previewProvider?.dispose();
}
