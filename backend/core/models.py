from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from datetime import datetime

class VulnType(Enum):
    """Vulnerability types"""
    BUFFER_OVERFLOW = "buffer_overflow"
    FORMAT_STRING = "format_string"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    USE_AFTER_FREE = "use_after_free"
    INTEGER_OVERFLOW = "integer_overflow"
    NULL_POINTER = "null_pointer_dereference"

class Severity(Enum):
    """Severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class Vulnerability:
    """Represents a detected vulnerability"""
    id: str
    type: VulnType
    severity: Severity
    line_start: int
    line_end: int
    code_snippet: str
    explanation: str
    suggested_fix: str
    confidence: float
    cwe_id: Optional[str] = None
    references: List[str] = field(default_factory=list)

@dataclass
class AnalysisResult:
    """Complete analysis result"""
    file_path: str
    language: str
    vulnerabilities: List[Vulnerability]
    analysis_time: float
    timestamp: datetime
    metadata: dict = field(default_factory=dict)