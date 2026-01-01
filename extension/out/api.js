"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.analyze = analyze;
const node_fetch_1 = __importDefault(require("node-fetch"));
async function analyze(apiBase, payload) {
    const response = await (0, node_fetch_1.default)(`${apiBase}/api/v1/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
    if (!response.ok) {
        const text = await response.text();
        throw new Error(`SecureCopilot API error (${response.status}): ${text}`);
    }
    return (await response.json());
}
//# sourceMappingURL=api.js.map