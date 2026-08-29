import { Effect } from "effect"
import { mkdtemp, rm } from "node:fs/promises"
import path from "node:path"
import { expect, test } from "bun:test"
import policyPlugin from "./policy-gate"

function shellResult(exitCode = 1) {
  const promise = Promise.resolve({ exitCode, text: () => "" })
  return Object.assign(promise, {
    quiet() {
      return this
    },
    nothrow() {
      return this
    },
  })
}

function fakeShell(_strings: TemplateStringsArray, ..._expressions: unknown[]) {
  return shellResult()
}

fakeShell.cwd = () => fakeShell

async function createHarness() {
  const worktree = await mkdtemp(path.join("/tmp", "policy-gate-test-"))
  const hooks = await policyPlugin({
    client: {
      session: {
        get: async () => ({ data: {} }),
      },
    },
    project: {} as never,
    directory: worktree,
    worktree,
    experimental_workspace: {} as never,
    serverUrl: new URL("http://localhost"),
    $: fakeShell as never,
  })
  const context = {
    sessionID: "session-1",
    messageID: "message-1",
    agent: "build",
    directory: worktree,
    worktree,
    abort: new AbortController().signal,
    metadata: () => undefined,
    ask: () => Effect.succeed(undefined),
  }
  return { hooks, context, worktree }
}

test("blocks direct Python commands before workflow selection", async () => {
  const { hooks, context, worktree } = await createHarness()
  try {
    const before = hooks["tool.execute.before"]!
    await expect(
      before(
        { tool: "bash", sessionID: context.sessionID, callID: "call-1" },
        { args: { command: "python -c pass" } },
      ),
    ).rejects.toThrow("direct python is blocked")
  } finally {
    await rm(worktree, { recursive: true, force: true })
  }
})

test("requires a fresh read and one-time approval before a patch", async () => {
  const { hooks, context, worktree } = await createHarness()
  try {
    const filePath = path.join(worktree, "file.py")
    await Bun.write(filePath, "value = 1\n")
    const select = hooks.tool?.select_workflow
    const approve = hooks.tool?.approve_action
    const before = hooks["tool.execute.before"]!
    const after = hooks["tool.execute.after"]!
    if (!select || !approve) throw new Error("policy tools are unavailable")

    await select.execute(
      {
        workflow: "software-delivery",
        reason: "update the example",
        deliverable: "updated example",
        sideEffectBoundary: "local project edits",
      },
      context,
    )
    await approve.execute(
      {
        action: "project-edit",
        repository: worktree,
        target: "file.py",
        reason: "the requested example change",
      },
      context,
    )

    const patchText = "*** Update File: file.py\n@@\n-value = 1\n+value = 2\n"
    await expect(
      before(
        { tool: "apply_patch", sessionID: context.sessionID, callID: "call-2" },
        { args: { patchText } },
      ),
    ).rejects.toThrow("read the existing target")

    await before(
      { tool: "read", sessionID: context.sessionID, callID: "call-3" },
      { args: { filePath: "file.py" } },
    )
    await after(
      {
        tool: "read",
        sessionID: context.sessionID,
        callID: "call-3",
        args: { filePath: "file.py" },
      },
      { title: "read", output: "value = 1", metadata: {} },
    )
    await before(
      { tool: "apply_patch", sessionID: context.sessionID, callID: "call-4" },
      { args: { patchText } },
    )
    await after(
      {
        tool: "apply_patch",
        sessionID: context.sessionID,
        callID: "call-4",
        args: { patchText },
      },
      { title: "patch", output: "updated", metadata: {} },
    )

    await expect(
      before(
        { tool: "apply_patch", sessionID: context.sessionID, callID: "call-5" },
        { args: { patchText } },
      ),
    ).rejects.toThrow("read the existing target")
  } finally {
    await rm(worktree, { recursive: true, force: true })
  }
})
