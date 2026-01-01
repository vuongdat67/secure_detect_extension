import * as vscode from "vscode";

import { analyze } from "./api";

const output = vscode.window.createOutputChannel("SecureCopilot");
const diagnostics = vscode.languages.createDiagnosticCollection("securecopilot");

function mapLanguage(languageId: string): string | undefined {
  if (languageId === "c" || languageId === "cpp") return languageId;
  if (languageId === "python") return "python";
  return undefined;
}

function getApiBase(): string {
  const config = vscode.workspace.getConfiguration("securecopilot", documentUri());
  return config.get<string>("apiBase", "http://localhost:8000");
}

function documentUri(): vscode.Uri | undefined {
  return vscode.window.activeTextEditor?.document.uri;
}

function severityToDiagnostic(severity: string): vscode.DiagnosticSeverity {
  switch (severity.toLowerCase()) {
    case "critical":
    case "high":
      return vscode.DiagnosticSeverity.Error;
    case "medium":
      return vscode.DiagnosticSeverity.Warning;
    default:
      return vscode.DiagnosticSeverity.Information;
  }
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
  diagnostics.clear();
  output.appendLine(`Analyzing ${document.fileName}...`);

  try {
    const result = await analyze(getApiBase(), {
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

    const diagList: vscode.Diagnostic[] = [];
    result.vulnerabilities.forEach((vuln, idx) => {
      output.appendLine(`[#${idx + 1}] ${vuln.type.toUpperCase()} (${vuln.severity})`);
      output.appendLine(`- Lines ${vuln.line_start}-${vuln.line_end}`);
      output.appendLine(`- Snippet: ${vuln.code_snippet}`);
      output.appendLine(`- Explanation: ${vuln.explanation}`);
      output.appendLine(`- Fix: ${vuln.suggested_fix}`);
      output.appendLine("");

      const offset = selection ? selection.start.line : 0;
      const startLine = Math.max(0, offset + vuln.line_start - 1);
      const endLine = Math.max(0, offset + vuln.line_end - 1);
      const range = new vscode.Range(
        new vscode.Position(startLine, 0),
        new vscode.Position(endLine, Number.MAX_SAFE_INTEGER)
      );
      const diag = new vscode.Diagnostic(
        range,
        `${vuln.type.toUpperCase()}: ${vuln.explanation}`,
        severityToDiagnostic(vuln.severity)
      );
      diag.source = "SecureCopilot";
      diagList.push(diag);
    });

    diagnostics.set(document.uri, diagList);

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
  context.subscriptions.push(diagnostics);
}

export function deactivate() {}
