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
            VulnType.XSS: [
                r'document\.write\s*\([^)]*\+[^)]*\)',
                r'innerHTML\s*=\s*[^;]*\+[^;]*',
                r'render_template\s*\([^)]*request\.args',
            ],
            VulnType.AUTH_BYPASS: [
                r'if\s+user\.is_admin:\s*return\s+True',
                r'allow_all\s*=\s*True',
            ],
            VulnType.CRYPTO_MISUSE: [
                r'md5\s*\(',
                r'sha1\s*\(',
                r'ECB',
            ],
            VulnType.CMD_INJECTION: [
                r'os\.system\s*\(',
                r'subprocess\.(Popen|call|run)\s*\([^)]*shell\s*=\s*True',
            ],
            VulnType.DESERIALIZATION: [
                r'pickle\.loads\s*\(',
                r'pickle\.load\s*\(',
            ],
            VulnType.INSECURE_YAML: [
                r'yaml\.load\s*\(',
            ],
            VulnType.DANGEROUS_EVAL: [
                r'\beval\s*\(',
                r'exec\s*\(',
            ],
            VulnType.HARD_CODED_SECRET: [
                r'(API_KEY|SECRET_KEY|SECRET|TOKEN|PASSWORD|PRIVATE_KEY)\s*=\s*"[^"]+"',
                r'(API_KEY|SECRET_KEY|SECRET|TOKEN|PASSWORD|PRIVATE_KEY)\s*=\s*\'[^\']+\'',
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

        # Detect XSS
        vulnerabilities.extend(self.detect_xss(code, language))

        # Detect auth bypass
        vulnerabilities.extend(self.detect_auth_bypass(code, language))

        # Detect crypto misuse
        vulnerabilities.extend(self.detect_crypto_misuse(code, language))

        # Detect command injection
        vulnerabilities.extend(self.detect_cmd_injection(code, language))

        # Detect dangerous deserialization
        vulnerabilities.extend(self.detect_deserialization(code, language))

        # Detect insecure yaml load
        vulnerabilities.extend(self.detect_insecure_yaml(code, language))

        # Detect dangerous eval/exec
        vulnerabilities.extend(self.detect_dangerous_eval(code, language))

        # Detect hard-coded secrets
        vulnerabilities.extend(self.detect_hard_coded_secret(code, language))
        
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

    def detect_xss(self, code: str, language: str) -> List[Vulnerability]:
        vulnerabilities = []
        lines = code.split('\n')

        if language not in {'javascript', 'python', 'html'}:
            return vulnerabilities

        for i, line in enumerate(lines):
            if any(re.search(pattern, line, re.IGNORECASE) for pattern in self.patterns[VulnType.XSS]):
                code_snippet = line.strip()
                vulnerabilities.append(
                    Vulnerability(
                        id=f"XSS-{i}",
                        type=VulnType.XSS,
                        severity=Severity.HIGH,
                        line_start=i + 1,
                        line_end=i + 1,
                        code_snippet=code_snippet,
                        explanation="Unescaped user input is written to the DOM, enabling XSS.",
                        suggested_fix="Escape or sanitize user input and use textContent/innerText instead of innerHTML; for Flask use render_template with autoescape.",
                        confidence=0.75,
                        cwe_id="CWE-79",
                        references=["https://cwe.mitre.org/data/definitions/79.html"],
                    )
                )
        return vulnerabilities

    def detect_auth_bypass(self, code: str, language: str) -> List[Vulnerability]:
        vulnerabilities = []
        lines = code.split('\n')

        for i, line in enumerate(lines):
            if any(re.search(pattern, line) for pattern in self.patterns[VulnType.AUTH_BYPASS]):
                code_snippet = line.strip()
                vulnerabilities.append(
                    Vulnerability(
                        id=f"AUTH-{i}",
                        type=VulnType.AUTH_BYPASS,
                        severity=Severity.CRITICAL,
                        line_start=i + 1,
                        line_end=i + 1,
                        code_snippet=code_snippet,
                        explanation="Authentication/authorization check can be bypassed due to hardcoded allow logic.",
                        suggested_fix="Enforce role/permission checks via centralized middleware; remove allow_all flags and validate JWT/session claims.",
                        confidence=0.70,
                        cwe_id="CWE-287",
                        references=["https://cwe.mitre.org/data/definitions/287.html"],
                    )
                )
        return vulnerabilities

    def detect_crypto_misuse(self, code: str, language: str) -> List[Vulnerability]:
        vulnerabilities = []
        lines = code.split('\n')

        for i, line in enumerate(lines):
            if any(re.search(pattern, line, re.IGNORECASE) for pattern in self.patterns[VulnType.CRYPTO_MISUSE]):
                code_snippet = line.strip()
                vulnerabilities.append(
                    Vulnerability(
                        id=f"CRYPTO-{i}",
                        type=VulnType.CRYPTO_MISUSE,
                        severity=Severity.HIGH,
                        line_start=i + 1,
                        line_end=i + 1,
                        code_snippet=code_snippet,
                        explanation="Insecure cryptography usage detected (weak hash or insecure block mode).",
                        suggested_fix="Use modern primitives (e.g., SHA-256/Bcrypt/Argon2) and AEAD modes (AES-GCM/ChaCha20-Poly1305).",
                        confidence=0.70,
                        cwe_id="CWE-328",
                        references=["https://cwe.mitre.org/data/definitions/328.html"],
                    )
                )
        return vulnerabilities

    def detect_cmd_injection(self, code: str, language: str) -> List[Vulnerability]:
        vulnerabilities = []
        if language != 'python':
            return vulnerabilities

        for i, line in enumerate(code.split('\n')):
            if any(re.search(pattern, line) for pattern in self.patterns[VulnType.CMD_INJECTION]):
                code_snippet = line.strip()
                vulnerabilities.append(
                    Vulnerability(
                        id=f"CMD-{i}",
                        type=VulnType.CMD_INJECTION,
                        severity=Severity.CRITICAL,
                        line_start=i + 1,
                        line_end=i + 1,
                        code_snippet=code_snippet,
                        explanation="Command built from user input executed via shell, enabling command injection.",
                        suggested_fix="Use subprocess with shell=False and pass args list; validate/whitelist commands.",
                        confidence=0.70,
                        cwe_id="CWE-78",
                        references=["https://cwe.mitre.org/data/definitions/78.html"],
                    )
                )
        return vulnerabilities

    def detect_deserialization(self, code: str, language: str) -> List[Vulnerability]:
        vulnerabilities = []
        if language != 'python':
            return vulnerabilities

        for i, line in enumerate(code.split('\n')):
            if any(re.search(pattern, line) for pattern in self.patterns[VulnType.DESERIALIZATION]):
                code_snippet = line.strip()
                vulnerabilities.append(
                    Vulnerability(
                        id=f"DESER-{i}",
                        type=VulnType.DESERIALIZATION,
                        severity=Severity.CRITICAL,
                        line_start=i + 1,
                        line_end=i + 1,
                        code_snippet=code_snippet,
                        explanation="Unsafe pickle deserialization can lead to arbitrary code execution.",
                        suggested_fix="Avoid pickle on untrusted data; use safe formats (json) or restrict with safe loaders.",
                        confidence=0.70,
                        cwe_id="CWE-502",
                        references=["https://cwe.mitre.org/data/definitions/502.html"],
                    )
                )
        return vulnerabilities

    def detect_insecure_yaml(self, code: str, language: str) -> List[Vulnerability]:
        vulnerabilities = []
        if language != 'python':
            return vulnerabilities

        for i, line in enumerate(code.split('\n')):
            if any(re.search(pattern, line) for pattern in self.patterns[VulnType.INSECURE_YAML]):
                code_snippet = line.strip()
                vulnerabilities.append(
                    Vulnerability(
                        id=f"YAML-{i}",
                        type=VulnType.INSECURE_YAML,
                        severity=Severity.HIGH,
                        line_start=i + 1,
                        line_end=i + 1,
                        code_snippet=code_snippet,
                        explanation="yaml.load without SafeLoader may execute arbitrary objects.",
                        suggested_fix="Use yaml.safe_load for untrusted input.",
                        confidence=0.65,
                        cwe_id="CWE-502",
                        references=["https://cwe.mitre.org/data/definitions/502.html"],
                    )
                )
        return vulnerabilities

    def detect_dangerous_eval(self, code: str, language: str) -> List[Vulnerability]:
        vulnerabilities = []
        if language != 'python':
            return vulnerabilities

        for i, line in enumerate(code.split('\n')):
            if any(re.search(pattern, line) for pattern in self.patterns[VulnType.DANGEROUS_EVAL]):
                code_snippet = line.strip()
                vulnerabilities.append(
                    Vulnerability(
                        id=f"EVAL-{i}",
                        type=VulnType.DANGEROUS_EVAL,
                        severity=Severity.CRITICAL,
                        line_start=i + 1,
                        line_end=i + 1,
                        code_snippet=code_snippet,
                        explanation="Use of eval/exec on input can execute arbitrary code.",
                        suggested_fix="Avoid eval/exec; use safe parsers or whitelisted operations.",
                        confidence=0.70,
                        cwe_id="CWE-94",
                        references=["https://cwe.mitre.org/data/definitions/94.html"],
                    )
                )
        return vulnerabilities

    def detect_hard_coded_secret(self, code: str, language: str) -> List[Vulnerability]:
        vulnerabilities = []
        lines = code.split('\n')

        for i, line in enumerate(lines):
            if any(re.search(pattern, line, re.IGNORECASE) for pattern in self.patterns[VulnType.HARD_CODED_SECRET]):
                code_snippet = line.strip()
                vulnerabilities.append(
                    Vulnerability(
                        id=f"SECRET-{i}",
                        type=VulnType.HARD_CODED_SECRET,
                        severity=Severity.HIGH,
                        line_start=i + 1,
                        line_end=i + 1,
                        code_snippet=code_snippet,
                        explanation="Hard-coded secret detected; credentials should not be in source.",
                        suggested_fix="Move secrets to environment variables or secret manager and load securely.",
                        confidence=0.60,
                        cwe_id="CWE-798",
                        references=["https://cwe.mitre.org/data/definitions/798.html"],
                    )
                )
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

