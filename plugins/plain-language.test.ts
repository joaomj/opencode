import { expect, test } from "bun:test"
import plainLanguagePlugin, {
  buildReminder,
  countWords,
  extractProseLines,
  extractSentences,
  lint,
  shouldBlock,
} from "./plain-language"

test("reminder states the product-first contract", () => {
  const reminder = buildReminder()
  expect(reminder).toContain("user-visible result")
  expect(reminder).toContain("Preserve code")
})

test("clean product explanation does not block", () => {
  const text = "OpenCode keeps a short stored copy of earlier details. This copy helps the agent continue after a long session."
  const result = lint(text)
  expect(result.points).toBe(0)
  expect(shouldBlock(result)).toBe(false)
})

test("flags filler, opener, contrast frame, and em dash", () => {
  const text = "Great question. This seamless solution will leverage robust caching. It is not slow, it is fast. The cache uses speed — and scale."
  const result = lint(text)
  const rules = new Set(result.violations.map((item) => item.rule))
  expect(rules.has("opener")).toBe(true)
  expect(rules.has("filler")).toBe(true)
  expect(rules.has("contrastive")).toBe(true)
  expect(rules.has("emDash")).toBe(true)
  expect(shouldBlock(result)).toBe(true)
})

test("flags a long sentence and passive voice with a named actor", () => {
  const longSentence = "OpenCode keeps a copy of earlier conversation details so the agent can continue after compaction without losing track of decisions files and verification state today reliably."
  expect(countWords(longSentence)).toBeGreaterThan(25)
  expect(lint(longSentence).violations.some((item) => item.rule === "longSentence")).toBe(true)
  expect(lint("The cache was proposed by the team.").violations.some((item) => item.rule === "passiveActor")).toBe(true)
})

test("excludes code, paths, errors, tables, and quotes", () => {
  const text = [
    "```ts",
    "const value = await this.seamless.robust.leverage(); // Great question — not X, it is Y",
    "```",
    "Use `seamless --leverage` in `/Users/test/project`.",
    "| robust | seamless |",
    "> Great question — it is not slow, it is fast with a seamless robust leverage.",
    "> Error: seamless leverage failed at /tmp/test with not X, it is Y — Great question.",
  ].join("\n")
  const result = lint(text)
  expect(result.points).toBe(0)
  expect(extractProseLines("```\ncode\n```\nReal prose.").length).toBe(1)
  expect(extractSentences("First sentence. Second sentence.").length).toBe(2)
})

test("system transform is idempotent and text complete fails open", async () => {
  const hooks = await plainLanguagePlugin({
    client: { app: { log: async () => undefined } },
    project: {},
    directory: "/tmp",
    worktree: "/tmp",
    experimental_workspace: {},
    serverUrl: new URL("http://localhost"),
    $: (() => {}) as never,
  } as never)
  const system = { system: ["base"] }
  await hooks["experimental.chat.system.transform"]!({}, system as never)
  await hooks["experimental.chat.system.transform"]!({}, system as never)
  expect(system.system.filter((item) => item.includes("user-visible result")).length).toBe(1)

  const clean = { text: "Short clean reply." }
  await hooks["experimental.text.complete"]!({ sessionID: "s", messageID: "m", partID: "p" }, clean as never)
  expect(clean.text).toBe("Short clean reply.")

  const bad = { text: undefined }
  await hooks["experimental.text.complete"]!({ sessionID: "s", messageID: "m", partID: "p" }, bad as never)
})
