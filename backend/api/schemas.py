"""Pydantic schemas for API IO."""

from typing import List, Optional

from pydantic import BaseModel

from ..core.models import AnalysisResult


class AnalyzeRequest(BaseModel):
    code: str
    language: str
    file_path: Optional[str] = None


class VulnerabilityResponse(BaseModel):
    id: str
    type: str
    severity: str
    line_start: int
    line_end: int
    code_snippet: str
    explanation: str
    suggested_fix: str
    confidence: float
    cwe_id: Optional[str] = None
    references: List[str] = []


class AnalyzeResponse(BaseModel):
    file_path: str
    language: str
    vulnerabilities: List[VulnerabilityResponse]
    analysis_time: float
    metadata: dict


def build_response(result: AnalysisResult) -> AnalyzeResponse:
    return AnalyzeResponse(
        file_path=result.file_path,
        language=result.language,
        vulnerabilities=[
            VulnerabilityResponse(
                id=v.id,
                type=v.type.value,
                severity=v.severity.value,
                line_start=v.line_start,
                line_end=v.line_end,
                code_snippet=v.code_snippet,
                explanation=v.explanation,
                suggested_fix=v.suggested_fix,
                confidence=v.confidence,
                cwe_id=v.cwe_id,
                references=v.references,
            )
            for v in result.vulnerabilities
        ],
        analysis_time=result.analysis_time,
        metadata=result.metadata,
    )
