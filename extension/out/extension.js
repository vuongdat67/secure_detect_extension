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
const API_BASE = "http://localhost:8000";
const output = vscode.window.createOutputChannel("SecureCopilot");
function mapLanguage(languageId) {
    if (languageId === "c" || languageId === "cpp")
        return languageId;
    if (languageId === "python")
        return "python";
    return undefined;
}
async function runAnalyze(document, selection) {
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
        const result = await (0, api_1.analyze)(API_BASE, {
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
        vscode.window.showWarningMessage(`SecureCopilot: phát hiện ${result.vulnerabilities.length} lỗ hổng. Xem output panel.`);
        result.vulnerabilities.forEach((vuln, idx) => {
            output.appendLine(`[#${idx + 1}] ${vuln.type.toUpperCase()} (${vuln.severity})`);
            output.appendLine(`- Lines ${vuln.line_start}-${vuln.line_end}`);
            output.appendLine(`- Snippet: ${vuln.code_snippet}`);
            output.appendLine(`- Explanation: ${vuln.explanation}`);
            output.appendLine(`- Fix: ${vuln.suggested_fix}`);
            output.appendLine("");
        });
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
}
function deactivate() { }
//# sourceMappingURL=extension.js.map