export type AnalyzeRequest = {
  code: string;
  language: string;
  file_path?: string;
};

export type VulnerabilityResponse = {
  id: string;
  type: string;
  severity: string;
  line_start: number;
  line_end: number;
  code_snippet: string;
  explanation: string;
  suggested_fix: string;
  confidence: number;
  cwe_id?: string;
  references: string[];
};

export type AnalyzeResponse = {
  file_path: string;
  language: string;
  vulnerabilities: VulnerabilityResponse[];
  analysis_time: number;
  metadata: Record<string, unknown>;
};

export async function analyze(
  apiBase: string,
  payload: AnalyzeRequest
): Promise<AnalyzeResponse> {
  const response = await fetch(`${apiBase}/api/v1/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`SecureCopilot API error (${response.status}): ${text}`);
  }

  return (await response.json()) as AnalyzeResponse;
}
