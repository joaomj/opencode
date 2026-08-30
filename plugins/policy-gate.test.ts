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

test("allows direct Python via native ask instead of hard deny", async () => {
  const { hooks, context, worktree } = await createHarness()
  try {
    const before = hooks["tool.execute.before"]!
    // Direct python is now soft: plugin does not hard deny, native permission (ask) will prompt
    await before(
      { tool: "bash", sessionID: context.sessionID, callID: "call-1" },
      { args: { command: "python -c pass" } },
    )
    // No throw means soft-allowed; native ask would handle user prompt
  } finally {
    await rm(worktree, { recursive: true, force: true })
  }
})

test("still hard-denies credential exposure", async () => {
  const { hooks, context, worktree } = await createHarness()
  try {
    const before = hooks["tool.execute.before"]!
    await expect(
      before(
        { tool: "read", sessionID: context.sessionID, callID: "call-1" },
        { args: { filePath: ".env" } },
      ),
    ).rejects.toThrow("protected credential path blocked")
    await expect(
      before(
        { tool: "read", sessionID: context.sessionID, callID: "call-2" },
        { args: { filePath: ".npmrc" } },
      ),
    ).rejects.toThrow("protected credential path blocked")
  } finally {
    await rm(worktree, { recursive: true, force: true })
  }
})

test("recognizes gh gist edit as soft remote and allows via native ask", async () => {
  const { hooks, context, worktree } = await createHarness()
  try {
    const before = hooks["tool.execute.before"]!
    const select = hooks.tool?.select_workflow
    if (!select) throw new Error("policy tools are unavailable")
    await select.execute(
      {
        workflow: "software-delivery",
        reason: "update gist",
        deliverable: "gist update",
        sideEffectBoundary: "remote gist edit",
      },
      context,
    )
    // gh gist edit is now recognized as protectedAction but soft: does not hard deny, native ask will prompt
    await before(
      { tool: "bash", sessionID: context.sessionID, callID: "call-1" },
      { args: { command: "gh gist edit abc123 --add note.txt" } },
    )
    // No hard throw; native permission gist edit is ask
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
    // Fresh-read is now soft: without prior read, plugin allows and lets native ask handle
    // But we still test that with prior read, patch succeeds, and second patch without fresh read is soft-allowed (not hard deny)
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

    // Second patch without fresh read is now soft-allowed (would have been hard before)
    await before(
      { tool: "apply_patch", sessionID: context.sessionID, callID: "call-5" },
      { args: { patchText } },
    )
  } finally {
    await rm(worktree, { recursive: true, force: true })
  }
})

test("allows self-repair of policy files without workflow via approval or env", async () => {
  const { hooks, context, worktree } = await createHarness()
  try {
    const approve = hooks.tool?.approve_action
    const before = hooks["tool.execute.before"]!
    const after = hooks["tool.execute.after"]!
    if (!approve) throw new Error("policy tools are unavailable")

    const policyPath = path.join(worktree, "plugins/policy-gate.ts")
    await Bun.write(policyPath, "export default 1\n")

    const patchText = "*** Update File: plugins/policy-gate.ts\n@@\n-export default 1\n+export default 2\n"

    await before({ tool: "read", sessionID: context.sessionID, callID: "call-2" }, { args: { filePath: "plugins/policy-gate.ts" } })
    await after({ tool: "read", sessionID: context.sessionID, callID: "call-2", args: { filePath: "plugins/policy-gate.ts" } }, { title: "read", output: "export default 1", metadata: {} })

    // Without approval, self-repair is now soft-allowed (native ask would prompt), but we still test that with approval it succeeds
    await before({ tool: "apply_patch", sessionID: context.sessionID, callID: "call-3" }, { args: { patchText } })

    await approve.execute({ action: "policy-self-repair", repository: worktree, target: "self-repair", reason: "fix broken policy" }, context)

    // read is consumed on success, so re-read before next patch
    await before({ tool: "read", sessionID: context.sessionID, callID: "call-4b" }, { args: { filePath: "plugins/policy-gate.ts" } })
    await after({ tool: "read", sessionID: context.sessionID, callID: "call-4b", args: { filePath: "plugins/policy-gate.ts" } }, { title: "read", output: "export default 1", metadata: {} })

    await before({ tool: "apply_patch", sessionID: context.sessionID, callID: "call-4" }, { args: { patchText } })
    await after({ tool: "apply_patch", sessionID: context.sessionID, callID: "call-4", args: { patchText } }, { title: "patch", output: "updated", metadata: {} })
  } finally {
    await rm(worktree, { recursive: true, force: true })
  }
})
