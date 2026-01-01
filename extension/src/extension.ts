import * as vscode from "vscode";

import { analyze } from "./api";

const API_BASE = "http://localhost:8000";
const output = vscode.window.createOutputChannel("SecureCopilot");

function mapLanguage(languageId: string): string | undefined {
  if (languageId === "c" || languageId === "cpp") return languageId;
  if (languageId === "python") return "python";
  return undefined;
}

async function runAnalyze(document: vscode.TextDocument, selection?: vscode.Selection) {
  const code = selection && !selection.isEmpty
    ? document.getText(selection)
    : document.getText();

  const language = mapLanguage(document.languageId);
  if (!language) {
    vscode.window.showWarningMessage("SecureCopilot chưa hỗ trợ ngôn ngữ này.");
    return;
  }

  output.clear();
  output.appendLine(`Analyzing ${document.fileName}...`);

  try {
    const result = await analyze(API_BASE, {
      code,
      language,
      file_path: document.fileName,
    });

    if (!result.vulnerabilities.length) {
      vscode.window.showInformationMessage("SecureCopilot: Không tìm thấy lỗ hổng.");
      output.appendLine("No vulnerabilities found.");
      output.show(true);
      return;
    }

    vscode.window.showWarningMessage(
      `SecureCopilot: phát hiện ${result.vulnerabilities.length} lỗ hổng. Xem output panel.`
    );

    result.vulnerabilities.forEach((vuln, idx) => {
      output.appendLine(`[#${idx + 1}] ${vuln.type.toUpperCase()} (${vuln.severity})`);
      output.appendLine(`- Lines ${vuln.line_start}-${vuln.line_end}`);
      output.appendLine(`- Snippet: ${vuln.code_snippet}`);
      output.appendLine(`- Explanation: ${vuln.explanation}`);
      output.appendLine(`- Fix: ${vuln.suggested_fix}`);
      output.appendLine("");
    });

    output.show(true);
  } catch (err: any) {
    const message = err?.message || String(err);
    vscode.window.showErrorMessage(`SecureCopilot lỗi: ${message}`);
    output.appendLine(`Error: ${message}`);
    output.show(true);
  }
}

export function activate(context: vscode.ExtensionContext) {
  const analyzeSelection = vscode.commands.registerCommand(
    "securecopilot.analyzeSelection",
    async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor) return;
      await runAnalyze(editor.document, editor.selection);
    }
  );

  const analyzeFile = vscode.commands.registerCommand(
    "securecopilot.analyzeFile",
    async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor) return;
      await runAnalyze(editor.document);
    }
  );

  context.subscriptions.push(analyzeSelection, analyzeFile, output);
}

export function deactivate() {}
