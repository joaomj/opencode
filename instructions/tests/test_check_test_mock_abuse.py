#!/usr/bin/env python3
"""Self-tests for the mock policy pre-commit checker."""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType
from typing import Iterator


MODULE_PATH = Path(__file__).resolve().parents[1] / "check_test_mock_abuse.py"


def _load_checker_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_test_mock_abuse", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load checker module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


CHECKER = _load_checker_module()


@contextmanager
def _temporary_cwd(path: Path) -> Iterator[None]:
    original = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(original)


class MockPolicyCheckerTests(unittest.TestCase):
    def _write(self, root: Path, relative: str, content: str) -> Path:
        file_path = root / relative
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return file_path

    def test_internal_python_patch_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            content = (
                "from unittest.mock import patch\n"
                "@pa" "tch('myapp.billing.charge')\n"
                "def test_charge() -> None:\n"
                "    assert True\n"
            )
            target = self._write(root, "tests/test_billing.py", content)
            violations = CHECKER._check_file(target, CHECKER.DEFAULT_PY_EXTERNAL_PREFIXES)

        self.assertGreater(len(violations), 0)

    def test_external_python_patch_is_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            content = (
                "from unittest.mock import patch\n"
                "@pa" "tch('requests.get')\n"
                "def test_http_call() -> None:\n"
                "    assert True\n"
            )
            target = self._write(root, "tests/test_http.py", content)
            violations = CHECKER._check_file(target, CHECKER.DEFAULT_PY_EXTERNAL_PREFIXES)

        self.assertEqual(violations, [])

    def test_allow_marker_suppresses_internal_mock_violation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            content = (
                "from unittest.mock import patch\n"
                "# mock-allow-internal: temporary adapter seam\n"
                "@pa" "tch('myapp.adapters.legacy')\n"
                "def test_legacy() -> None:\n"
                "    assert True\n"
            )
            target = self._write(root, "tests/test_legacy.py", content)
            violations = CHECKER._check_file(target, CHECKER.DEFAULT_PY_EXTERNAL_PREFIXES)

        self.assertEqual(violations, [])

    def test_file_disable_marker_suppresses_checks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            content = (
                "# mock-policy: disable\n"
                "from unittest.mock import patch\n"
                "@pa" "tch('myapp.anything')\n"
                "def test_disabled() -> None:\n"
                "    assert True\n"
            )
            target = self._write(root, "tests/test_disabled.py", content)
            violations = CHECKER._check_file(target, CHECKER.DEFAULT_PY_EXTERNAL_PREFIXES)

        self.assertEqual(violations, [])

    def test_local_javascript_mock_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            content = (
                "describe('client', () => {\n"
                "  je" "st.mock('./api/client')\n"
                "})\n"
            )
            target = self._write(root, "tests/client.spec.ts", content)
            violations = CHECKER._check_file(target, CHECKER.DEFAULT_PY_EXTERNAL_PREFIXES)

        self.assertGreater(len(violations), 0)

    def test_custom_allowlist_file_is_used(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".test-mock-external-allowlist").write_text(
                "vendor_sdk\n# comment\n", encoding="utf-8"
            )

            with _temporary_cwd(root):
                prefixes = CHECKER._external_prefixes_from_env()

            self.assertEqual(prefixes, ("vendor_sdk",))

            content = (
                "from unittest.mock import patch\n"
                "@pa" "tch('vendor_sdk.client.fetch')\n"
                "def test_sdk_call() -> None:\n"
                "    assert True\n"
            )
            target = self._write(root, "tests/test_sdk.py", content)
            violations = CHECKER._check_file(target, prefixes)

        self.assertEqual(violations, [])


if __name__ == "__main__":
    unittest.main()
