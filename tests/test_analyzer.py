from backend.core.analyzer import CodeAnalyzer


def test_analyzer_counts_metadata():
    analyzer = CodeAnalyzer(load_models=False)
    code = """
    char buffer[64];
    strcpy(buffer, user_input);
    printf(user_input);
    """

    result = analyzer.analyze(code, "c")

    assert result.metadata["total_lines"] >= 3
    assert result.metadata["critical_count"] >= 1
    assert any(v.type.value == "buffer_overflow" for v in result.vulnerabilities)


def test_analyzer_explain_format():
    analyzer = CodeAnalyzer(load_models=False)
    vuln = analyzer.detector.detect_format_string("printf(user_input);", "c")[0]

    explanation = analyzer.explain_vulnerability(vuln)

    assert "printf" in explanation
    assert "Suggested Fix" in explanation
