import re
from typing import List
from .models import Vulnerability, VulnType, Severity

class VulnerabilityDetector:
    """
    Detect various vulnerability types
    Uses pattern matching + ExploitGen for validation
    """
    
    def __init__(self, exploitgen_engine):
        self.engine = exploitgen_engine
        
        # Vulnerability patterns
        self.patterns = {
            VulnType.BUFFER_OVERFLOW: [
                r'strcpy\s*\(',
                r'gets\s*\(',
                r'sprintf\s*\(',
                r'scanf\s*\([^,]+,\s*[^,]+\)',  # scanf without length limit
            ],
            VulnType.FORMAT_STRING: [
                r'printf\s*\(\s*[a-zA-Z_][a-zA-Z0-9_]*\s*\)',  # printf(var)
                r'fprintf\s*\([^,]+,\s*[a-zA-Z_][a-zA-Z0-9_]*\s*\)',
            ],
            VulnType.SQL_INJECTION: [
                r'execute\s*\([^)]*\+[^)]*\)',  # SQL concatenation
                r'query\s*\([^)]*\+[^)]*\)',
            ],
        }
    
    def detect_all(self, code: str, language: str) -> List[Vulnerability]:
        """
        Detect all vulnerability types in code
        
        Args:
            code: Source code
            language: Programming language
            
        Returns:
            List of detected vulnerabilities
        """
        vulnerabilities = []
        
        # Detect buffer overflow
        vulnerabilities.extend(self.detect_buffer_overflow(code, language))
        
        # Detect format string
        vulnerabilities.extend(self.detect_format_string(code, language))
        
        # Detect SQL injection
        if language == 'python':
            vulnerabilities.extend(self.detect_sql_injection(code, language))
        
        return vulnerabilities
    
    def detect_buffer_overflow(self, code: str, language: str) -> List[Vulnerability]:
        """Detect buffer overflow vulnerabilities"""
        vulnerabilities = []
        lines = code.split('\n')
        
        for pattern in self.patterns[VulnType.BUFFER_OVERFLOW]:
            for i, line in enumerate(lines):
                if re.search(pattern, line):
                    # Extract vulnerable code
                    code_snippet = line.strip()
                    
                    # Get explanation from ExploitGen
                    explanation = self.engine.explain_behavior(code_snippet, language)
                    
                    # Create vulnerability
                    vuln = Vulnerability(
                        id=f"BO-{i}",
                        type=VulnType.BUFFER_OVERFLOW,
                        severity=Severity.CRITICAL,
                        line_start=i + 1,
                        line_end=i + 1,
                        code_snippet=code_snippet,
                        explanation=explanation,
                        suggested_fix=self._suggest_fix_buffer_overflow(code_snippet),
                        confidence=0.85,
                        cwe_id="CWE-120",
                        references=[
                            "https://cwe.mitre.org/data/definitions/120.html"
                        ]
                    )
                    vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def detect_format_string(self, code: str, language: str) -> List[Vulnerability]:
        """Detect format string vulnerabilities"""
        vulnerabilities = []
        lines = code.split('\n')
        
        for pattern in self.patterns[VulnType.FORMAT_STRING]:
            for i, line in enumerate(lines):
                if re.search(pattern, line):
                    code_snippet = line.strip()
                    
                    vuln = Vulnerability(
                        id=f"FS-{i}",
                        type=VulnType.FORMAT_STRING,
                        severity=Severity.HIGH,
                        line_start=i + 1,
                        line_end=i + 1,
                        code_snippet=code_snippet,
                        explanation="User-controlled format string can read/write arbitrary memory",
                        suggested_fix=self._suggest_fix_format_string(code_snippet),
                        confidence=0.90,
                        cwe_id="CWE-134",
                        references=[
                            "https://cwe.mitre.org/data/definitions/134.html"
                        ]
                    )
                    vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def detect_sql_injection(self, code: str, language: str) -> List[Vulnerability]:
        """Detect SQL injection vulnerabilities"""
        vulnerabilities = []
        lines = code.split('\n')

        # Track variables that were built via string concatenation.
        tainted_queries = set()

        assign_pattern = re.compile(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\b\s*=.*\+.*")
        execute_pattern = re.compile(r"execute\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)")

        for i, line in enumerate(lines):
            # Heuristic 1: direct concatenation inside execute/query call
            direct_hit = any(re.search(pattern, line) for pattern in self.patterns[VulnType.SQL_INJECTION])

            # Heuristic 2: variable assignment using concatenation, then executed later
            assign_match = assign_pattern.search(line)
            if assign_match:
                tainted_queries.add(assign_match.group(1))

            exec_match = execute_pattern.search(line)
            indirect_hit = exec_match and exec_match.group(1) in tainted_queries

            if direct_hit or indirect_hit:
                code_snippet = line.strip()

                vuln = Vulnerability(
                    id=f"SQL-{i}",
                    type=VulnType.SQL_INJECTION,
                    severity=Severity.CRITICAL,
                    line_start=i + 1,
                    line_end=i + 1,
                    code_snippet=code_snippet,
                    explanation="SQL query constructed with string concatenation allows injection",
                    suggested_fix=self._suggest_fix_sql_injection(code_snippet),
                    confidence=0.80,
                    cwe_id="CWE-89",
                    references=[
                        "https://cwe.mitre.org/data/definitions/89.html"
                    ]
                )
                vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _suggest_fix_buffer_overflow(self, code: str) -> str:
        """Suggest fix for buffer overflow"""
        if 'strcpy' in code:
            return code.replace('strcpy', 'strncpy') + " // Add buffer size limit"
        elif 'gets' in code:
            return code.replace('gets', 'fgets') + " // Use fgets with size limit"
        elif 'sprintf' in code:
            return code.replace('sprintf', 'snprintf') + " // Add buffer size"
        return "Use bounded string functions (strncpy, snprintf, fgets)"
    
    def _suggest_fix_format_string(self, code: str) -> str:
        """Suggest fix for format string"""
        # printf(var) → printf("%s", var)
        match = re.search(r'printf\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\)', code)
        if match:
            var_name = match.group(1)
            return code.replace(f'printf({var_name})', f'printf("%s", {var_name})')
        return 'Use printf("%s", user_input) instead of printf(user_input)'
    
    def _suggest_fix_sql_injection(self, code: str) -> str:
        """Suggest fix for SQL injection"""
        return "Use parameterized queries: cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))"

