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
