"""OpenCode Lint Rules.

This module contains all lint rules implementing AGENTS.md guidelines.
"""

from opencode_lint.rules.absolute_imports import AbsoluteImportsPreferred
from opencode_lint.rules.exclude_newer_configured import ExcludeNewerConfigured
from opencode_lint.rules.lockfile_required import LockfileRequired
from opencode_lint.rules.no_blind_upgrade import NoBlindUpgrade
from opencode_lint.rules.no_env_file_access import NoEnvFileAccess
from opencode_lint.rules.no_hardcoded_config import NoHardcodedConfig
from opencode_lint.rules.no_privileged_containers import NoPrivilegedContainers
from opencode_lint.rules.no_raw_dict_api import NoRawDictAPISchema
from opencode_lint.rules.no_test_mock_abuse import NoTestMockAbuse
from opencode_lint.rules.no_unsafe_downloads import NoUnsafeDownloads
from opencode_lint.rules.registry_sync import RegistrySync
from opencode_lint.rules.routing_consistency import RoutingConsistency
from opencode_lint.rules.skill_descriptions import SkillDescriptions
from opencode_lint.rules.strict_type_hints import StrictTypeHints

__all__ = [
    "NoRawDictAPISchema",
    "NoEnvFileAccess",
    "NoPrivilegedContainers",
    "AbsoluteImportsPreferred",
    "StrictTypeHints",
    "LockfileRequired",
    "ExcludeNewerConfigured",
    "NoBlindUpgrade",
    "NoUnsafeDownloads",
    "NoTestMockAbuse",
    "NoHardcodedConfig",
    "RegistrySync",
    "RoutingConsistency",
    "SkillDescriptions",
]
