"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.analyze = analyze;
async function analyze(apiBase, payload) {
    const response = await fetch(`${apiBase}/api/v1/analyze`, {
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