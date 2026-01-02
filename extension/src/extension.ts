import * as vscode from "vscode";

import { analyze } from "./api";

const output = vscode.window.createOutputChannel("SecureCopilot");
const diagnostics = vscode.languages.createDiagnosticCollection("securecopilot");

function mapLanguage(languageId: string): string | undefined {
  const id = languageId.toLowerCase();
  if (id === "c" || id === "cpp") return id;
  if (id === "python") return "python";

  // Common assembly language IDs across themes/extensions; fallback if id contains "asm"
  const asmIds = ["asm", "assembly", "nasm", "asm-intel", "asm-att", "x86asm", "asmx86", "asm_x86", "gas", "armasm", "masm"];
  if (asmIds.includes(id) || id.includes("asm") || id.startsWith("x86")) return "asm";

  return undefined;
}

function mapByFilename(fileName: string): string | undefined {
  const lower = fileName.toLowerCase();
  if (lower.endsWith(".c")) return "c";
  if (lower.endsWith(".cpp") || lower.endsWith(".cc") || lower.endsWith(".cxx")) return "cpp";
  if (lower.endsWith(".py")) return "python";
  if (lower.endsWith(".asm") || lower.endsWith(".s") || lower.endsWith(".S")) return "asm";
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
  let resolvedLanguage = language ?? mapByFilename(document.fileName);

  // Extra fallbacks: any languageId containing intel/att/x86 or asm-like, or filename containing .asm/.s anywhere
  if (!resolvedLanguage) {
    const id = document.languageId.toLowerCase();
    const fname = document.fileName.toLowerCase();
    if (id.includes("asm") || id.includes("intel") || id.includes("att") || id.startsWith("x86")) {
      resolvedLanguage = "asm";
    } else if (fname.includes(".asm") || fname.endsWith(".s")) {
      resolvedLanguage = "asm";
    }
  }
  if (!resolvedLanguage) {
    vscode.window.showWarningMessage(`SecureCopilot chưa hỗ trợ ngôn ngữ này (id: ${document.languageId}).`);
    output.appendLine(`Unsupported languageId: ${document.languageId}; file: ${document.fileName}`);
    output.appendLine(`Detected resolvedLanguage: ${resolvedLanguage ?? "<none>"}`);
    output.show(true);
    return;
  }

  output.clear();
  diagnostics.clear();
  output.appendLine(`Analyzing ${document.fileName} with language=${resolvedLanguage} (languageId=${document.languageId})...`);

  try {
    const result = await analyze(getApiBase(), {
      code,
      language: resolvedLanguage,
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
    const lineOffset = selection ? selection.start.line : 0; // Keep diagnostics aligned with original file
    const colOffset = selection ? selection.start.character : 0; // Offset first-line columns when selection starts mid-line

    result.vulnerabilities.forEach((vuln, idx) => {
      const displayStart = vuln.line_start + lineOffset;
      const displayEnd = vuln.line_end + lineOffset;

      output.appendLine(`[#${idx + 1}] ${vuln.type.toUpperCase()} (${vuln.severity})`);
      output.appendLine(`- Lines ${displayStart}-${displayEnd}`);
      output.appendLine(`- Snippet: ${vuln.code_snippet}`);
      output.appendLine(`- Explanation: ${vuln.explanation}`);
      output.appendLine(`- Fix: ${vuln.suggested_fix}`);
      output.appendLine("");

      const startLine = Math.max(0, lineOffset + vuln.line_start - 1);
      const endLine = Math.max(0, lineOffset + vuln.line_end - 1);

      // If selection starts mid-line, shift the first line's column start; otherwise cover the whole line.
      const startColumn = selection && vuln.line_start === 1 ? colOffset : 0;
      const endColumn = document.lineAt(endLine).range.end.character;
      const range = new vscode.Range(
        new vscode.Position(startLine, startColumn),
        new vscode.Position(endLine, endColumn)
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
