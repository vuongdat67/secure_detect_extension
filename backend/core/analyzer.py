import time
from datetime import datetime
from typing import Optional

from .models import AnalysisResult, Severity, Vulnerability
from .detector import VulnerabilityDetector
from .exploitgen_engine import ExploitGenEngine

class CodeAnalyzer:
    """Main code analyzer orchestrating vulnerability detection."""

    def __init__(self, model_path_asm: str = "", model_path_py: str = "", load_models: bool = False):
        """Create analyzer.

        Args:
            model_path_asm: Optional path to assembly checkpoint.
            model_path_py: Optional path to Python checkpoint.
            load_models: Whether to attempt loading heavy models (defaults to False for POC).
        """

        print("🚀 Initializing SecureCopilot...")

        self.engine = ExploitGenEngine(model_path_asm, model_path_py, load_models=load_models)
        self.detector = VulnerabilityDetector(self.engine)

        print("✓ SecureCopilot ready!")
    
    def analyze(
        self, 
        code: str, 
        language: str,
        file_path: Optional[str] = None
    ) -> AnalysisResult:
        """
        Analyze code for vulnerabilities
        
        Args:
            code: Source code to analyze
            language: Programming language (c, python, cpp)
            file_path: Optional file path for context
            
        Returns:
            AnalysisResult with detected vulnerabilities
        """
        start_time = time.time()
        
        print(f"\n🔍 Analyzing {language} code...")

        vulnerabilities = self.detector.detect_all(code, language)
        analysis_time = time.time() - start_time

        print(f"✓ Analysis complete in {analysis_time:.2f}s")
        print(f"   Found {len(vulnerabilities)} vulnerabilities")
        
        # Create result
        result = AnalysisResult(
            file_path=file_path or "stdin",
            language=language,
            vulnerabilities=vulnerabilities,
            analysis_time=analysis_time,
            timestamp=datetime.now(),
            metadata={
                'total_lines': len(code.split('\n')),
                'critical_count': sum(1 for v in vulnerabilities if v.severity == Severity.CRITICAL),
                'high_count': sum(1 for v in vulnerabilities if v.severity == Severity.HIGH),
            }
        )
        
        return result
    
    def explain_vulnerability(self, vuln: Vulnerability) -> str:
        """Render a human-readable vulnerability description."""

        references = "\n".join(f"- {ref}" for ref in vuln.references)
        return (
            f"Vulnerability: {vuln.type.value}\n"
            f"Severity: {vuln.severity.value}\n"
            f"CWE: {vuln.cwe_id}\n\n"
            f"Description:\n{vuln.explanation}\n\n"
            f"Location:\nLine {vuln.line_start}: {vuln.code_snippet}\n\n"
            f"Suggested Fix:\n{vuln.suggested_fix}\n\n"
            f"References:\n{references}"
        )