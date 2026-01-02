"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const api_1 = require("./api");
const output = vscode.window.createOutputChannel("SecureCopilot");
const diagnostics = vscode.languages.createDiagnosticCollection("securecopilot");
function mapLanguage(languageId) {
    const id = languageId.toLowerCase();
    if (id === "c" || id === "cpp")
        return id;
    if (id === "python")
        return "python";
    // Common assembly language IDs across themes/extensions; fallback if id contains "asm"
    const asmIds = ["asm", "assembly", "nasm", "asm-intel", "asm-att", "x86asm", "asmx86", "asm_x86", "gas", "armasm", "masm"];
    if (asmIds.includes(id) || id.includes("asm") || id.startsWith("x86"))
        return "asm";
    return undefined;
}
function mapByFilename(fileName) {
    const lower = fileName.toLowerCase();
    if (lower.endsWith(".c"))
        return "c";
    if (lower.endsWith(".cpp") || lower.endsWith(".cc") || lower.endsWith(".cxx"))
        return "cpp";
    if (lower.endsWith(".py"))
        return "python";
    if (lower.endsWith(".asm") || lower.endsWith(".s") || lower.endsWith(".S"))
        return "asm";
    return undefined;
}
function getApiBase() {
    const config = vscode.workspace.getConfiguration("securecopilot", documentUri());
    return config.get("apiBase", "http://localhost:8000");
}
function documentUri() {
    return vscode.window.activeTextEditor?.document.uri;
}
function severityToDiagnostic(severity) {
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
async function runAnalyze(document, selection) {
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
        }
        else if (fname.includes(".asm") || fname.endsWith(".s")) {
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
        const result = await (0, api_1.analyze)(getApiBase(), {
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
        vscode.window.showWarningMessage(`SecureCopilot: phát hiện ${result.vulnerabilities.length} lỗ hổng. Xem output panel.`);
        const diagList = [];
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
            const range = new vscode.Range(new vscode.Position(startLine, startColumn), new vscode.Position(endLine, endColumn));
            const diag = new vscode.Diagnostic(range, `${vuln.type.toUpperCase()}: ${vuln.explanation}`, severityToDiagnostic(vuln.severity));
            diag.source = "SecureCopilot";
            diagList.push(diag);
        });
        diagnostics.set(document.uri, diagList);
        output.show(true);
    }
    catch (err) {
        const message = err?.message || String(err);
        vscode.window.showErrorMessage(`SecureCopilot lỗi: ${message}`);
        output.appendLine(`Error: ${message}`);
        output.show(true);
    }
}
function activate(context) {
    const analyzeSelection = vscode.commands.registerCommand("securecopilot.analyzeSelection", async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor)
            return;
        await runAnalyze(editor.document, editor.selection);
    });
    const analyzeFile = vscode.commands.registerCommand("securecopilot.analyzeFile", async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor)
            return;
        await runAnalyze(editor.document);
    });
    context.subscriptions.push(analyzeSelection, analyzeFile, output);
    context.subscriptions.push(diagnostics);
}
function deactivate() { }
//# sourceMappingURL=extension.js.map