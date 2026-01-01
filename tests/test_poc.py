"""
Test suite for SecureCopilot POC
Run with: pytest tests/test_poc.py -v
"""

def test_buffer_overflow_detection():
    """Test buffer overflow detection"""
    code = """
    char buffer[64];
    strcpy(buffer, user_input);
    """
    
    from backend.core.analyzer import CodeAnalyzer
    analyzer = CodeAnalyzer("", "")
    result = analyzer.analyze(code, "c")
    
    assert len(result.vulnerabilities) > 0
    assert any(v.type.value == "buffer_overflow" for v in result.vulnerabilities)

def test_format_string_detection():
    """Test format string detection"""
    code = """
    printf(user_input);
    """
    
    from backend.core.analyzer import CodeAnalyzer
    analyzer = CodeAnalyzer("", "")
    result = analyzer.analyze(code, "c")
    
    assert len(result.vulnerabilities) > 0
    assert any(v.type.value == "format_string" for v in result.vulnerabilities)

def test_sql_injection_detection():
    """Test SQL injection detection"""
    code = """
    query = "SELECT * FROM users WHERE id = " + user_id
    cursor.execute(query)
    """
    
    from backend.core.analyzer import CodeAnalyzer
    analyzer = CodeAnalyzer("", "")
    result = analyzer.analyze(code, "python")
    
    assert len(result.vulnerabilities) > 0


def test_cmd_injection_detection():
    code = """
    import os
    os.system("ping " + user_input)
    """

    from backend.core.analyzer import CodeAnalyzer
    analyzer = CodeAnalyzer("", "")
    result = analyzer.analyze(code, "python")

    assert any(v.type.value == "cmd_injection" for v in result.vulnerabilities)


def test_eval_detection():
    code = """
    def run(expr):
        return eval(expr)
    """

    from backend.core.analyzer import CodeAnalyzer
    analyzer = CodeAnalyzer("", "")
    result = analyzer.analyze(code, "python")

    assert any(v.type.value == "dangerous_eval" for v in result.vulnerabilities)


def test_yaml_load_detection():
    code = """
    import yaml
    cfg = yaml.load(data)
    """

    from backend.core.analyzer import CodeAnalyzer
    analyzer = CodeAnalyzer("", "")
    result = analyzer.analyze(code, "python")

    assert any(v.type.value == "insecure_yaml" for v in result.vulnerabilities)


def test_pickle_deserialization_detection():
    code = """
    import pickle
    obj = pickle.loads(data)
    """

    from backend.core.analyzer import CodeAnalyzer
    analyzer = CodeAnalyzer("", "")
    result = analyzer.analyze(code, "python")

    assert any(v.type.value == "deserialization" for v in result.vulnerabilities)


def test_hardcoded_secret_detection():
    code = """
    SECRET_KEY = "sk_live_123"
    """

    from backend.core.analyzer import CodeAnalyzer
    analyzer = CodeAnalyzer("", "")
    result = analyzer.analyze(code, "python")

    assert any(v.type.value == "hard_coded_secret" for v in result.vulnerabilities)

# ===== FILE 7: demo.py - POC Demo =====
"""
SecureCopilot POC Demo
Run with: python demo.py
"""

def demo_buffer_overflow():
    """Demo: Buffer overflow detection"""
    print("\n" + "="*60)
    print("DEMO 1: Buffer Overflow Detection")
    print("="*60)
    
    vulnerable_code = """
void process_input(char *user_input) {
    char buffer[64];
    strcpy(buffer, user_input);  // VULNERABLE!
    printf("Processed: %s\\n", buffer);
}
"""
    
    print("\n📝 Vulnerable Code:")
    print(vulnerable_code)
    
    from backend.core.analyzer import CodeAnalyzer
    analyzer = CodeAnalyzer("", "")
    result = analyzer.analyze(vulnerable_code, "c", "example.c")
    
    print(f"\n🔍 Analysis Results:")
    print(f"   Found {len(result.vulnerabilities)} vulnerabilities")
    
    for vuln in result.vulnerabilities:
        print(f"\n❌ {vuln.type.value.upper()}")
        print(f"   Severity: {vuln.severity.value}")
        print(f"   Line: {vuln.line_start}")
        print(f"   Explanation: {vuln.explanation}")
        print(f"   Suggested Fix: {vuln.suggested_fix}")

def demo_format_string():
    """Demo: Format string detection"""
    print("\n" + "="*60)
    print("DEMO 2: Format String Vulnerability")
    print("="*60)
    
    vulnerable_code = """
void log_message(char *msg) {
    printf(msg);  // VULNERABLE!
}
"""
    
    print("\n📝 Vulnerable Code:")
    print(vulnerable_code)
    
    from backend.core.analyzer import CodeAnalyzer
    analyzer = CodeAnalyzer("", "")
    result = analyzer.analyze(vulnerable_code, "c")
    
    for vuln in result.vulnerabilities:
        print(f"\n❌ {vuln.type.value.upper()}")
        print(f"   {vuln.explanation}")
        print(f"   Fix: {vuln.suggested_fix}")

def demo_sql_injection():
    """Demo: SQL injection detection"""
    print("\n" + "="*60)
    print("DEMO 3: SQL Injection")
    print("="*60)
    
    vulnerable_code = """
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    cursor.execute(query)  # VULNERABLE!
"""
    
    print("\n📝 Vulnerable Code:")
    print(vulnerable_code)
    
    from backend.core.analyzer import CodeAnalyzer
    analyzer = CodeAnalyzer("", "")
    result = analyzer.analyze(vulnerable_code, "python")
    
    for vuln in result.vulnerabilities:
        print(f"\n❌ {vuln.type.value.upper()}")
        print(f"   {vuln.explanation}")
        print(f"   Fix: {vuln.suggested_fix}")

if __name__ == "__main__":
    print("\n🚀 SecureCopilot POC Demo\n")
    
    demo_buffer_overflow()
    demo_format_string()
    demo_sql_injection()
    
    print("\n" + "="*60)
    print("✅ Demo Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Run API server: uvicorn backend.api.main:app --reload")
    print("2. Test API: curl -X POST http://localhost:8000/api/v1/analyze")
    print("3. Build VSCode extension")