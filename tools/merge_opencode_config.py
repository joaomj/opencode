"""Merge OpenCode JSONC while preserving selected local configuration paths."""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import NoReturn

DEFAULT_PRESERVED_PATHS = (
    "/provider",
    "/permission",
    "/model",
    "/small_model",
    "/agent",
    "/mcp",
)


@dataclass
class JsonNode:
    kind: str
    start: int
    end: int
    value: object
    members: list[JsonMember] = field(default_factory=list)


@dataclass
class JsonMember:
    key: str
    key_start: int
    value_start: int
    value_end: int
    value: JsonNode


@dataclass
class Edit:
    start: int
    end: int
    text: str


class JsoncParser:
    def __init__(self, source: str, label: str) -> None:
        self.source = source
        self.label = label
        self.index = 0

    def parse(self) -> JsonNode:
        self.skip_ignored()
        node = self.parse_value()
        self.skip_ignored()
        if self.index != len(self.source):
            self.fail("unexpected content after the root value")
        return node

    def parse_value(self) -> JsonNode:
        self.skip_ignored()
        start = self.index
        character = self.source[start] if start < len(self.source) else ""
        if character == "{":
            return self.parse_object(start)
        if character == "[":
            return self.parse_array(start)
        if character == '"':
            return self.parse_string(start)
        for raw, value in (("true", True), ("false", False), ("null", None)):
            if self.source.startswith(raw, start):
                self.index += len(raw)
                return JsonNode("literal", start, self.index, value)
        return self.parse_number(start)

    def parse_object(self, start: int) -> JsonNode:
        self.index += 1
        members: list[JsonMember] = []
        keys: set[str] = set()
        self.skip_ignored()
        while True:
            if self.index >= len(self.source):
                self.fail("unterminated object")
            if self.source[self.index] == "}":
                self.index += 1
                break
            key_start = self.index
            key = self.parse_string(key_start).value
            if not isinstance(key, str):
                self.fail("object key must be a string")
            if key in keys:
                self.fail(f"duplicate object key: {key}")
            keys.add(key)
            self.skip_ignored()
            self.expect(":")
            self.skip_ignored()
            value = self.parse_value()
            members.append(JsonMember(key, key_start, value.start, value.end, value))
            self.skip_ignored()
            if self.index < len(self.source) and self.source[self.index] == ",":
                self.index += 1
                self.skip_ignored()
                continue
            if self.index >= len(self.source) or self.source[self.index] != "}":
                self.fail("expected ',' or '}'")
        values = {member.key: member.value.value for member in members}
        return JsonNode("object", start, self.index, values, members)

    def parse_array(self, start: int) -> JsonNode:
        self.index += 1
        values: list[JsonNode] = []
        self.skip_ignored()
        while True:
            if self.index >= len(self.source):
                self.fail("unterminated array")
            if self.source[self.index] == "]":
                self.index += 1
                break
            values.append(self.parse_value())
            self.skip_ignored()
            if self.index < len(self.source) and self.source[self.index] == ",":
                self.index += 1
                self.skip_ignored()
                continue
            if self.index >= len(self.source) or self.source[self.index] != "]":
                self.fail("expected ',' or ']'")
        return JsonNode("array", start, self.index, [value.value for value in values])

    def parse_string(self, start: int) -> JsonNode:
        self.index += 1
        escaped = False
        while self.index < len(self.source):
            character = self.source[self.index]
            self.index += 1
            if escaped:
                escaped = False
                continue
            if character == "\\":
                escaped = True
                continue
            if character == '"':
                raw = self.source[start : self.index]
                try:
                    value = json.loads(raw)
                except json.JSONDecodeError as error:
                    self.fail(f"invalid string escape: {error.msg}")
                return JsonNode("string", start, self.index, value)
            if character in "\r\n":
                self.fail("unterminated string")
        self.fail("unterminated string")

    def parse_number(self, start: int) -> JsonNode:
        match = re.match(r"-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?", self.source[start:])
        if match is None:
            self.fail("expected a JSON value")
        raw = match.group(0)
        self.index += len(raw)
        return JsonNode("number", start, self.index, json.loads(raw))

    def skip_ignored(self) -> None:
        while self.index < len(self.source):
            if self.source[self.index].isspace():
                self.index += 1
                continue
            if self.source.startswith("//", self.index):
                newline = self.source.find("\n", self.index + 2)
                self.index = len(self.source) if newline == -1 else newline + 1
                continue
            if self.source.startswith("/*", self.index):
                end = self.source.find("*/", self.index + 2)
                if end == -1:
                    self.fail("unterminated block comment")
                self.index = end + 2
                continue
            return

    def expect(self, expected: str) -> None:
        if not self.source.startswith(expected, self.index):
            self.fail(f"expected '{expected}'")
        self.index += len(expected)

    def fail(self, message: str) -> NoReturn:
        raise ValueError(f"{self.label}: {message} at character {self.index}")


def parse_jsonc(source: str, label: str) -> JsonNode:
    node = JsoncParser(source, label).parse()
    if node.kind != "object":
        raise ValueError(f"{label}: the root value must be an object")
    return node


def top_level_path(path: str) -> str:
    parts = path.split("/")
    if len(parts) != 2 or parts[0] != "":
        raise ValueError(f"protected path must identify a top-level key: {path}")
    return parts[1].replace("~1", "/").replace("~0", "~")


def line_indent(source: str, position: int) -> str:
    line_start = source.rfind("\n", 0, position) + 1
    match = re.match(r"[ \t]*", source[line_start:position])
    return match.group(0) if match else "  "


def apply_edits(source: str, edits: list[Edit]) -> str:
    result = source
    for edit in sorted(edits, key=lambda item: item.start, reverse=True):
        result = f"{result[:edit.start]}{edit.text}{result[edit.end:]}"
    return result


def member_insertion_edit(
    source: str,
    root: JsonNode,
    local_members: list[JsonMember],
    local_source: str,
) -> Edit:
    raw_members = [local_source[member.key_start : member.value_end] for member in local_members]
    if not root.members:
        return Edit(
            root.start + 1,
            root.start + 1,
            f"\n  {',\n  '.join(raw_members)}\n",
        )
    last_member = root.members[-1]
    indent = line_indent(source, last_member.key_start)
    return Edit(
        last_member.value_end,
        last_member.value_end,
        f",\n{indent}{f',\n{indent}'.join(raw_members)}",
    )


def merge_jsonc(
    upstream_source: str,
    local_source: str,
    preserved_paths: tuple[str, ...] = DEFAULT_PRESERVED_PATHS,
) -> str:
    upstream = parse_jsonc(upstream_source, "upstream configuration")
    local = parse_jsonc(local_source, "local configuration")
    upstream_members = {member.key: member for member in upstream.members}
    local_members = {member.key: member for member in local.members}
    edits: list[Edit] = []
    additions: list[JsonMember] = []

    for path in preserved_paths:
        key = top_level_path(path)
        local_member = local_members.get(key)
        if local_member is None:
            continue
        upstream_member = upstream_members.get(key)
        if upstream_member is None:
            additions.append(local_member)
        else:
            edits.append(
                Edit(
                    upstream_member.value_start,
                    upstream_member.value_end,
                    local_source[local_member.value_start : local_member.value_end],
                )
            )

    preserved_keys = {top_level_path(path) for path in preserved_paths}
    additions.extend(
        member
        for member in local.members
        if member.key not in upstream_members and member.key not in preserved_keys
    )
    if additions:
        edits.append(member_insertion_edit(upstream_source, upstream, additions, local_source))

    return apply_edits(upstream_source, edits)


def write_output(output_path: Path | None, content: str) -> None:
    if output_path is None:
        sys.stdout.write(content)
        return
    output_path = output_path.resolve()
    mode = stat.S_IMODE(output_path.stat().st_mode) if output_path.exists() else None
    with tempfile.NamedTemporaryFile(
        dir=output_path.parent,
        prefix=f".{output_path.name}.",
        delete=False,
        mode="w",
        encoding="utf-8",
    ) as temporary:
        temporary.write(content)
        temporary_path = Path(temporary.name)
    try:
        if mode is not None:
            os.chmod(temporary_path, mode)
        os.replace(temporary_path, output_path)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise


def parse_arguments(arguments: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--local", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--preserve", dest="preserved_paths", action="append")
    options = parser.parse_args(arguments)
    if not options.preserved_paths:
        options.preserved_paths = list(DEFAULT_PRESERVED_PATHS)
    return options


def main(arguments: list[str] | None = None) -> int:
    try:
        options = parse_arguments(sys.argv[1:] if arguments is None else arguments)
        upstream_source = options.upstream.read_text(encoding="utf-8")
        local_source = options.local.read_text(encoding="utf-8")
        merged = merge_jsonc(upstream_source, local_source, tuple(options.preserved_paths))
        parse_jsonc(merged, "merged configuration")
        write_output(options.output, merged)
        return 0
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
