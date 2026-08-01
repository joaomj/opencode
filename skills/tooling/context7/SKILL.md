---
name: context7
description: Retrieve current library and framework documentation through the Context7 API. Use when an API or library behavior may have changed.
---

# Context7

Use this skill as a source adapter for the `research` skill. State the question,
read the smallest relevant documentation, preserve identifiers and examples,
and separate observed facts from interpretation.

## Search

```bash
curl -s "https://context7.com/api/v2/libs/search?libraryName=LIBRARY_NAME&query=TOPIC"
```

Select the correct result and preserve its `id`. Do not assume the first result
is correct without checking its title and description.

## Fetch

```bash
curl -s "https://context7.com/api/v2/context?libraryId=LIBRARY_ID&query=TOPIC&type=txt"
```

Use a specific query. URL-encode spaces. Use `type=txt` for readable output or
`json` when structured fields are needed. Report failed requests and unknowns.

Do not use this skill for a general information search. Use `research` to choose
the source and record the decision that the documentation will support.
