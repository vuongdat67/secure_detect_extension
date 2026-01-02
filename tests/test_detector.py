from backend.core.detector import VulnerabilityDetector
from backend.core.exploitgen_engine import ExploitGenEngine


def _build_detector() -> VulnerabilityDetector:
    engine = ExploitGenEngine(load_models=False)
    return VulnerabilityDetector(engine)


def test_detects_buffer_overflow():
    detector = _build_detector()
    code = """
    char buffer[8];
    strcpy(buffer, user_input);
    """

    vulns = detector.detect_buffer_overflow(code, "c")

    assert len(vulns) == 1
    assert vulns[0].type.value == "buffer_overflow"


def test_detects_format_string():
    detector = _build_detector()
    code = """
    printf(user_input);
    """

    vulns = detector.detect_format_string(code, "c")

    assert len(vulns) == 1
    assert "printf" in vulns[0].code_snippet


def test_detects_sql_injection_in_python():
    detector = _build_detector()
    code = """
    query = "SELECT * FROM users WHERE id = " + user_id
    cursor.execute(query)
    """

    vulns = detector.detect_sql_injection(code, "python")

    assert len(vulns) == 1
    assert vulns[0].cwe_id == "CWE-89"


def test_detects_cmd_injection():
    detector = _build_detector()
    code = """
    import os
    os.system("ping " + user_input)
    """

    vulns = detector.detect_cmd_injection(code, "python")

    assert vulns
    assert vulns[0].type.value == "cmd_injection"


def test_detects_eval_exec():
    detector = _build_detector()
    code = """
    def calc(expr):
        return eval(expr)
    """

    vulns = detector.detect_dangerous_eval(code, "python")

    assert vulns
    assert vulns[0].type.value == "dangerous_eval"


def test_detects_yaml_load():
    detector = _build_detector()
    code = """
    import yaml
    cfg = yaml.load(data)
    """

    vulns = detector.detect_insecure_yaml(code, "python")

    assert vulns
    assert vulns[0].type.value == "insecure_yaml"


def test_detects_pickle_loads():
    detector = _build_detector()
    code = """
    import pickle
    obj = pickle.loads(data)
    """

    vulns = detector.detect_deserialization(code, "python")

    assert vulns
    assert vulns[0].type.value == "deserialization"


def test_detects_hardcoded_secret():
    detector = _build_detector()
    code = """
    API_KEY = "sk_test_123"
    """

    vulns = detector.detect_hard_coded_secret(code, "python")

    assert vulns
    assert vulns[0].type.value == "hard_coded_secret"


def test_detects_xss():
    detector = _build_detector()
    code = """
    const msg = req.query.q;
    document.write("<div>" + msg + "</div>");
    """

    vulns = detector.detect_xss(code, "javascript")

    assert len(vulns) == 1
    assert vulns[0].type.value == "xss"


def test_detects_auth_bypass():
    detector = _build_detector()
    code = """
    if user.is_admin: return True
    allow_all = True
    """

    vulns = detector.detect_auth_bypass(code, "python")

    assert len(vulns) >= 1
    assert vulns[0].type.value == "auth_bypass"


def test_detects_crypto_misuse():
    detector = _build_detector()
    code = """
    import hashlib
    digest = hashlib.md5(b"pwd").hexdigest()
    """

    vulns = detector.detect_crypto_misuse(code, "python")

    assert len(vulns) == 1
    assert vulns[0].type.value == "crypto_misuse"


def test_detects_asm_buffer_overflow():
    detector = _build_detector()
    code = """
    ; simple copy loop
    rep movsb ; no bounds check
    """

    vulns = detector.detect_buffer_overflow(code, "asm")

    assert vulns
    assert any(v.type.value == "buffer_overflow" for v in vulns)
