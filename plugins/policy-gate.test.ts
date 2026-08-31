import { mkdtemp, readFile, rm } from "node:fs/promises"
import path from "node:path"
import { expect, test } from "bun:test"
import policyPlugin from "./policy-gate"

let sessionSequence = 0

function shellResult(exitCode = 0) {
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
  const sessionID = `session-${++sessionSequence}`
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
    sessionID,
    messageID: "message-1",
    agent: "build",
    directory: worktree,
    worktree,
    abort: new AbortController().signal,
    metadata: () => undefined,
    ask: () => {
      throw new Error("policy plugin must not request custom approval")
    },
  }
  return { hooks, context, worktree }
}

async function selectSoftwareDelivery(harness: Awaited<ReturnType<typeof createHarness>>) {
  const select = harness.hooks.tool?.select_workflow
  if (!select) throw new Error("select_workflow is unavailable")
  await select.execute(
    {
      workflow: "software-delivery",
      reason: "test policy behavior",
      deliverable: "verified policy",
      sideEffectBoundary: "test fixture only",
    },
    harness.context,
  )
}

test("exports workflow tools without a custom approval tool", async () => {
  const harness = await createHarness()
  try {
    expect(harness.hooks.tool?.select_workflow).toBeDefined()
    expect(harness.hooks.tool?.finish_workflow).toBeDefined()
    expect(harness.hooks.tool?.approve_action).toBeUndefined()
    const health = harness.hooks.tool?.policy_health
    if (!health) throw new Error("policy_health is unavailable")
    expect(JSON.parse(await health.execute({}, harness.context))).toMatchObject({
      approvalMode: "native-permissions",
      customApprovalTool: false,
    })
  } finally {
    await rm(harness.worktree, { recursive: true, force: true })
  }
})

test("hard-denies credential paths and permits the safe environment example", async () => {
  const harness = await createHarness()
  try {
    const before = harness.hooks["tool.execute.before"]!
    for (const [index, filePath] of [
      ".env",
      ".env.local",
      ".npmrc",
      ".netrc",
      "id_rsa",
      "credentials.json",
      "service.credentials.json",
      "private.key",
      "~/.docker/config.json",
      "~/.config/gh/hosts.yml",
    ].entries()) {
      await expect(
        before(
          { tool: "read", sessionID: harness.context.sessionID, callID: `credential-${index}` },
          { args: { filePath } },
        ),
      ).rejects.toThrow("protected credential path blocked")
    }
    await before(
      { tool: "read", sessionID: harness.context.sessionID, callID: "safe-example" },
      { args: { filePath: ".env.example" } },
    )
  } finally {
    await rm(harness.worktree, { recursive: true, force: true })
  }
})

test("hard-denies credential paths in shell commands and patches", async () => {
  const harness = await createHarness()
  try {
    const before = harness.hooks["tool.execute.before"]!
    await selectSoftwareDelivery(harness)
    for (const [index, command] of [
      "source .env",
      'cat .e""nv',
      "cat .e\\\nnv",
      "cat<.env",
      "cat credentials.json",
      "cat ~/.docker/config.json",
    ].entries()) {
      await expect(
        before(
          { tool: "bash", sessionID: harness.context.sessionID, callID: `shell-credential-${index}` },
          { args: { command } },
        ),
      ).rejects.toThrow("protected credential path blocked")
    }
    await expect(
      before(
        { tool: "apply_patch", sessionID: harness.context.sessionID, callID: "patch-credential" },
        { args: { patchText: "*** Add File: .env\n+SECRET=value\n" } },
      ),
    ).rejects.toThrow("protected credential path blocked")
  } finally {
    await rm(harness.worktree, { recursive: true, force: true })
  }
})

test("defers non-credential protected actions to native permissions", async () => {
  const harness = await createHarness()
  try {
    const before = harness.hooks["tool.execute.before"]!
    await selectSoftwareDelivery(harness)
    for (const [index, command] of [
      "python -c pass",
      "sudo true",
      "docker run --privileged image",
      "git reset --hard HEAD~1",
      'git commit -m "test commit"',
      "git push origin test-branch",
      "gh gist edit abc123 --add note.txt",
      "printenv HOME",
    ].entries()) {
      await before(
        { tool: "bash", sessionID: harness.context.sessionID, callID: `native-${index}` },
        { args: { command } },
      )
    }
  } finally {
    await rm(harness.worktree, { recursive: true, force: true })
  }
})

test("loads the router before ownership and selected workflow instructions after selection", async () => {
  const harness = await createHarness()
  try {
    const before = harness.hooks["tool.execute.before"]!
    await before(
      { tool: "skill", sessionID: harness.context.sessionID, callID: "router" },
      { args: { name: "workflow" } },
    )
    await expect(
      before(
        { tool: "skill", sessionID: harness.context.sessionID, callID: "capability" },
        { args: { name: "coding-standards" } },
      ),
    ).rejects.toThrow("call select_workflow")

    const select = harness.hooks.tool?.select_workflow
    if (!select) throw new Error("select_workflow is unavailable")
    const output = await select.execute(
      {
        workflow: "direct-assistance",
        reason: "answer one question",
        deliverable: "one answer",
        sideEffectBoundary: "read-only",
      },
      harness.context,
    )
    expect(output).toContain("Selected workflow instructions")
    expect(output).toContain("# Direct Assistance")
    await expect(
      before(
        { tool: "skill", sessionID: harness.context.sessionID, callID: "top-level" },
        { args: { name: "direct-assistance" } },
      ),
    ).rejects.toThrow("select_workflow loads top-level workflow instructions")
  } finally {
    await rm(harness.worktree, { recursive: true, force: true })
  }
})

test("selects code review as an owning workflow", async () => {
  const harness = await createHarness()
  try {
    const select = harness.hooks.tool?.select_workflow
    if (!select) throw new Error("select_workflow is unavailable")
    const output = await select.execute(
      {
        workflow: "code-review",
        reason: "review a change",
        deliverable: "P0 and P1 findings",
        sideEffectBoundary: "read-only",
      },
      harness.context,
    )
    expect(output).toContain("# Code Review")
  } finally {
    await rm(harness.worktree, { recursive: true, force: true })
  }
})

test("tracks successful unknown shell commands as project changes", async () => {
  const harness = await createHarness()
  try {
    await selectSoftwareDelivery(harness)
    const before = harness.hooks["tool.execute.before"]!
    const after = harness.hooks["tool.execute.after"]!
    const input = {
      tool: "bash",
      sessionID: harness.context.sessionID,
      callID: "prefixed-mutation",
      args: { command: "env FLAG=1 touch generated.txt" },
    }
    await before(input, { args: input.args })
    await after(input, { title: "bash", output: "", metadata: { exit: 0 } })

    const finish = harness.hooks.tool?.finish_workflow
    if (!finish) throw new Error("finish_workflow is unavailable")
    await expect(finish.execute({}, harness.context)).resolves.toContain("opencode-lint: passed")
  } finally {
    await rm(harness.worktree, { recursive: true, force: true })
  }
})

test("applies dependency age controls to environment-prefixed installs", async () => {
  const harness = await createHarness()
  try {
    await selectSoftwareDelivery(harness)
    const before = harness.hooks["tool.execute.before"]!
    const input = {
      tool: "bash",
      sessionID: harness.context.sessionID,
      callID: "prefixed-install",
      args: { command: "env CI=1 bun install" },
    }
    await before(input, { args: input.args })
    const output = { env: {} as Record<string, string> }
    await harness.hooks["shell.env"]?.(input, output)
    expect(output.env.BUN_MINIMUM_RELEASE_AGE).toBe("604800")
  } finally {
    await rm(harness.worktree, { recursive: true, force: true })
  }
})

test("policy verification rejects pure mode", async () => {
  const process = Bun.spawn(["bun", "scripts/verify-policy.ts"], {
    cwd: path.resolve(import.meta.dir, ".."),
    env: { ...Bun.env, OPENCODE_PURE: "1" },
    stdout: "pipe",
    stderr: "pipe",
  })
  expect(await process.exited).toBe(1)
  expect(await new Response(process.stderr).text()).toContain("OPENCODE_PURE=1 is blocked")
})

test("requires a handoff before changing workflow ownership", async () => {
  const harness = await createHarness()
  try {
    const select = harness.hooks.tool?.select_workflow
    if (!select) throw new Error("select_workflow is unavailable")
    await selectSoftwareDelivery(harness)
    await expect(
      select.execute(
        {
          workflow: "research",
          reason: "change scope",
          deliverable: "research result",
          sideEffectBoundary: "read-only",
        },
        harness.context,
      ),
    ).rejects.toThrow("create a handoff")
  } finally {
    await rm(harness.worktree, { recursive: true, force: true })
  }
})

test("creates handoffs without requesting custom approval", async () => {
  const harness = await createHarness()
  try {
    await selectSoftwareDelivery(harness)
    const create = harness.hooks.tool?.create_handoff
    if (!create) throw new Error("create_handoff is unavailable")
    const output = await create.execute(
      {
        targetWorkflow: "research",
        goal: "verify one external fact",
        evidence: "implementation needs a source",
        paths: [],
        commands: [],
        results: [],
        decisions: [],
        gaps: ["source missing"],
        allowedNextAction: "perform read-only research",
      },
      harness.context,
    )
    expect(output).toContain("Handoff created")
    const handoffDir = path.join(harness.worktree, ".agents", "handoffs")
    expect((await readFile(path.join(handoffDir, `${harness.context.sessionID}-research.md`), "utf8"))).toContain("target_workflow: research")
  } finally {
    await rm(harness.worktree, { recursive: true, force: true })
  }
})

test("native permission configuration asks for normal edits and denies credentials", async () => {
  const config = JSON.parse(
    await readFile(path.resolve(import.meta.dir, "../opencode.jsonc"), "utf8"),
  ) as {
    permission: {
      bash: Record<string, string>
      read: Record<string, string>
      edit: Record<string, string>
    }
  }
  expect(config.permission.bash["*"]).toBe("ask")
  expect(config.permission.bash["gh *"]).toBeUndefined()
  expect(Object.keys(config.permission.bash).filter((pattern) => pattern !== "*").every((pattern) => !pattern.includes("*"))).toBe(true)
  expect(config.permission.edit["*"]).toBe("ask")
  expect(config.permission.edit["*.env"]).toBe("deny")
  expect(config.permission.edit["**/.docker/config.json"]).toBe("deny")
  expect(config.permission.read["*.env"]).toBe("deny")
  expect(config.permission.read["*.env.example"]).toBe("allow")
})
