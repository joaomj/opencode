from pathlib import Path

from opencode_lint.rules.no_hardcoded_config import NoHardcodedConfig


def test_detects_inline_url_in_runtime_call() -> None:
    rule = NoHardcodedConfig()

    violations = rule.check_file(
        Path("source.py"),
        'client.get("https://service.example/items")',
    )

    if len(violations) != 1:
        raise AssertionError(f"expected one violation, got {len(violations)}")
    if violations[0].rule_id != "OC014":
        raise AssertionError(f"unexpected rule ID: {violations[0].rule_id}")
    if violations[0].severity != "error":
        raise AssertionError(f"unexpected severity: {violations[0].severity}")


def test_detects_config_like_numeric_keyword_argument() -> None:
    rule = NoHardcodedConfig()

    violations = rule.check_file(Path("source.py"), "client.get(timeout=30)")

    if len(violations) != 1:
        raise AssertionError(f"expected one violation, got {len(violations)}")
    if violations[0].severity != "error":
        raise AssertionError(f"unexpected severity: {violations[0].severity}")


def test_allows_named_fixed_protocol_constant() -> None:
    rule = NoHardcodedConfig()

    violations = rule.check_file(
        Path("source.py"),
        'ATLASSIAN_MCP_URL = "https://mcp.atlassian.com/v1/mcp/authv2"',
    )

    if violations:
        raise AssertionError(f"unexpected violations: {violations}")
