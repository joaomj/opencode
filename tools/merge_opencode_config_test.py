"""Tests for the JSONC configuration merge boundary."""

from __future__ import annotations

import unittest

from merge_opencode_config import merge_jsonc, parse_jsonc


class MergeOpenCodeConfigTest(unittest.TestCase):
    def test_preserves_local_settings_and_takes_upstream_general_settings(self) -> None:
        local = """{
  \"$schema\": \"local-schema\",
  \"provider\": {
    /* Keep this local comment. */
    \"custom\": { \"models\": { \"local-model\": { \"name\": \"Local\" } } }
  },
  \"permission\": { \"bash\": \"deny\" },
  \"small_model\": \"custom/local-small\",
  \"local_only\": { \"enabled\": true },
  \"snapshot\": false
}"""
        upstream = """{
  \"$schema\": \"upstream-schema\",
  \"provider\": {
    \"upstream\": { \"models\": { \"upstream-model\": { \"name\": \"Upstream\" } } }
  },
  \"permission\": { \"bash\": \"allow\" },
  \"small_model\": \"upstream/small\",
  \"autoupdate\": \"notify\"
}"""

        merged = merge_jsonc(upstream, local)
        value = parse_jsonc(merged, "test configuration").value
        local_value = parse_jsonc(local, "local test configuration").value

        self.assertIsInstance(value, dict)
        self.assertEqual(value["provider"], local_value["provider"])
        self.assertEqual(value["permission"], local_value["permission"])
        self.assertEqual(value["small_model"], "custom/local-small")
        self.assertEqual(value["autoupdate"], "notify")
        self.assertEqual(value["local_only"], {"enabled": True})
        self.assertIn("Keep this local comment", merged)

    def test_rejects_invalid_jsonc(self) -> None:
        with self.assertRaisesRegex(ValueError, r"local configuration: expected a JSON value"):
            merge_jsonc('{ "valid": true }', '{ "broken": }')

    def test_rejects_nested_protected_paths(self) -> None:
        with self.assertRaisesRegex(ValueError, "protected path must identify a top-level key"):
            merge_jsonc("{}", "{}", ("/agent/build/model",))


if __name__ == "__main__":
    unittest.main()
