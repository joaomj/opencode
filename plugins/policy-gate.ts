import { mkdir, readFile, unlink } from "node:fs/promises"
import path from "node:path"
import { tool, type Plugin } from "@opencode-ai/plugin"

const z = tool.schema

const POLICY_VERSION = "2.0.0"
const LINTER_ROOT = path.resolve(import.meta.dir, "..")
const LINTER_PROJECT = path.resolve(import.meta.dir, "../opencode_lint")
const AGENT_ARTIFACT_DIR = ".agents"
const SAFE_ENV_PATH_RE = /(?:^|[\\/])\.env\.example$/i
const CREDENTIAL_PATH_RE = /(?:^|[\\/])(?:\.env(?:\.[^\\/]*)?|\.npmrc|\.pypirc|\.git-credentials|\.netrc|\.authinfo|credentials(?:\.json)?|.*\.credentials\.json|.*\.pem|.*\.key|id_(?:rsa|ed25519))$/i
const CREDENTIAL_CONFIG_PATH_RE = /(?:^|\/)(?:\.docker\/config\.json|\.config\/gh\/hosts\.yml)$/i
const EMOJI_RE = /[\p{Emoji_Presentation}\p{Extended_Pictographic}]/u

const WORKFLOW_FILES = {
  "direct-assistance": "skills/workflows/direct-assistance/SKILL.md",
  "focused-exploration": "skills/workflows/focused-exploration/SKILL.md",
  "codebase-investigation": "skills/workflows/codebase-investigation/SKILL.md",
  "project-opportunities": "skills/workflows/project-opportunities/SKILL.md",
  "implementation-planning": "skills/workflows/implementation-planning/SKILL.md",
  "product-definition": "skills/workflows/product-definition/SKILL.md",
  "software-delivery": "skills/workflows/software-delivery/SKILL.md",
  "bug-resolution": "skills/workflows/bug-resolution/SKILL.md",
  research: "skills/engineering/research/SKILL.md",
  "improve-agent": "skills/maintenance/improve-agent/SKILL.md",
  "create-pull-request": "skills/maintenance/create-pull-request/SKILL.md",
  "write-postmortem": "skills/maintenance/write-postmortem/SKILL.md",
  "architecture-decision": "skills/engineering/architecture-decision/SKILL.md",
  "doc-maintenance": "skills/documentation/doc-maintenance/SKILL.md",
  "code-review": "skills/maintenance/code-review/SKILL.md",
} as const

type WorkflowName = keyof typeof WORKFLOW_FILES
type VerificationStatus = "unknown" | "stale" | "passed" | "failed"

type Verification = {
  status: VerificationStatus
  command?: string
  exit?: number
  reason?: string
}

type SessionState = {
  owner?: WorkflowName
  reason?: string
  deliverable?: string
  sideEffectBoundary?: string
  planPath?: string
  sideEffects: number
  changed: boolean
  loadedSkills: Set<string>
  verification: Verification
  dependencyCalls: Set<string>
  inheritanceResolved: boolean
  terminal: boolean
}

const sessions = new Map<string, SessionState>()

function newSessionState(): SessionState {
  return {
    sideEffects: 0,
    changed: false,
    loadedSkills: new Set(),
    verification: { status: "unknown" },
    dependencyCalls: new Set(),
    inheritanceResolved: false,
    terminal: false,
  }
}

function stateFor(sessionID: string): SessionState {
  const existing = sessions.get(sessionID)
  if (existing) return existing
  const state = newSessionState()
  sessions.set(sessionID, state)
  return state
}

function isWorkflowName(value: string): value is WorkflowName {
  return value in WORKFLOW_FILES
}

function canonicalPath(directory: string, filePath: string): string {
  return path.resolve(directory, filePath)
}

function isWithin(parent: string, candidate: string): boolean {
  const relative = path.relative(path.resolve(parent), path.resolve(candidate))
  return relative === "" || (!relative.startsWith("..") && !path.isAbsolute(relative))
}

function isCredentialPath(filePath: string): boolean {
  const normalized = filePath.replaceAll("\\", "/")
  if (SAFE_ENV_PATH_RE.test(normalized)) return false
  return CREDENTIAL_PATH_RE.test(normalized) || CREDENTIAL_CONFIG_PATH_RE.test(normalized)
}

function stringPaths(value: unknown, key = ""): string[] {
  if (typeof value === "string") {
    const normalizedKey = key.toLowerCase()
    return ["path", "file", "target", "directory"].some((part) => normalizedKey.includes(part))
      ? [value]
      : []
  }
  if (Array.isArray(value)) return value.flatMap((item) => stringPaths(item, key))
  if (!value || typeof value !== "object") return []
  return Object.entries(value).flatMap(([childKey, childValue]) =>
    stringPaths(childValue, childKey),
  )
}

function patchTargets(patchText: string): Array<{ operation: string; filePath: string }> {
  return [
    ...[...patchText.matchAll(/^\*\*\* (Add|Update|Delete) File: (.+?)\s*$/gm)].map(
      (match) => ({ operation: match[1], filePath: match[2] }),
    ),
    ...[...patchText.matchAll(/^\*\*\* Move to: (.+?)\s*$/gm)].map((match) => ({
      operation: "Move to",
      filePath: match[1],
    })),
  ]
}

function commandFromArgs(args: unknown): string {
  if (!args || typeof args !== "object") return ""
  const raw = (args as { command?: unknown }).command
  return typeof raw === "string" ? raw : Array.isArray(raw) ? raw.join(" ") : ""
}

function commandTokens(command: string): string[] {
  return command
    .replace(/\\\r?\n/g, "")
    .replace(/["'\\]/g, "")
    .split(/[\s;&|<>()]+/)
    .map((token) => token.replace(/^[${}]+|[${}]+$/g, ""))
    .filter(Boolean)
}

function commandContainsCredentialPath(command: string): boolean {
  return commandTokens(command).some(isCredentialPath)
}

function isSafeLocalCommand(command: string): boolean {
  return new Set([
    "pwd", "date", "whoami", "id", "uname -a", "arch", "hostname", "ps", "tty", "uptime",
    "git status", "git status --short", "git status --porcelain", "git diff", "git diff --cached",
    "git log", "git branch", "git branch --show-current", "git branch --list", "git branch -a",
    "git branch -r", "git branch -vv", "gh auth status", "gh status", "docker images", "docker info",
    "docker ps", "docker version",
  ]).has(command.trim())
}

function isDependencyCommand(command: string): boolean {
  return /(?:^|[;&|]\s*)(?:env\s+)?(?:[A-Za-z_][A-Za-z0-9_]*=[^\s;&|]+\s+)*(?:npm|pnpm|yarn|bun)\s+(?:install|i|ci|update|add|remove|upgrade)(?:\s|$)/.test(command) ||
    /(?:^|[;&|]\s*)(?:env\s+)?(?:[A-Za-z_][A-Za-z0-9_]*=[^\s;&|]+\s+)*uv\s+(?:add|remove|lock|sync|pip)(?:\s|$)/.test(command)
}

function isVerificationCommand(command: string): boolean {
  return /\b(?:test|check|lint|format|verify|typecheck)\b/i.test(command) ||
    /(?:^|\s)(?:pytest|ruff|pyright|mypy)(?:\s|$)/.test(command)
}

function isMutationTool(toolName: string): boolean {
  return ["apply_patch", "edit", "write", "write_file"].includes(toolName)
}

function isReadTool(toolName: string): boolean {
  return ["read", "glob", "grep", "list"].includes(toolName)
}

async function readWorkflowInstructions(workflow: WorkflowName): Promise<string> {
  const filePath = path.resolve(import.meta.dir, "..", WORKFLOW_FILES[workflow])
  try {
    return await readFile(filePath, "utf8")
  } catch (error) {
    throw new Error(
      `policy-gate: workflow instructions are unavailable: ${WORKFLOW_FILES[workflow]}`,
      { cause: error },
    )
  }
}

function sessionIDFromEvent(event: unknown): string | undefined {
  if (!event || typeof event !== "object") return undefined
  const properties = (event as { properties?: unknown }).properties
  if (!properties || typeof properties !== "object") return undefined
  const directID = (properties as { sessionID?: unknown }).sessionID
  if (typeof directID === "string") return directID
  const info = (properties as { info?: unknown }).info
  if (!info || typeof info !== "object") return undefined
  const id = (info as { id?: unknown }).id
  return typeof id === "string" ? id : undefined
}

async function inheritParentState(
  sessionID: string,
  client: Parameters<Plugin>[0]["client"],
): Promise<SessionState> {
  const state = stateFor(sessionID)
  if (state.inheritanceResolved) return state
  state.inheritanceResolved = true

  const result = await client.session.get({ path: { id: sessionID } })
  const parentID = (result as { data?: { parentID?: string } }).data?.parentID
  if (!parentID) return state

  const parent = await inheritParentState(parentID, client)
  if (!state.owner && parent.owner) {
    state.owner = parent.owner
    state.reason = parent.reason
    state.deliverable = parent.deliverable
    state.sideEffectBoundary = parent.sideEffectBoundary
    state.planPath = parent.planPath
    state.sideEffects = parent.sideEffects
    state.changed = parent.changed
    state.verification = parent.verification
  }
  return state
}

function formatOwner(state: SessionState): string {
  return [
    `Owner: ${state.owner}`,
    `Deliverable: ${state.deliverable}`,
    `Allowed side effects: ${state.sideEffectBoundary}`,
    "Handoff: call create_handoff before changing the owner or authority.",
  ].join("\n")
}

const selectWorkflow = tool({
  description: "Select and lock the one owning workflow for this session.",
  args: {
    workflow: z.enum(Object.keys(WORKFLOW_FILES) as [WorkflowName, ...WorkflowName[]]),
    reason: z.string().min(1),
    deliverable: z.string().min(1),
    sideEffectBoundary: z.string().min(1),
    planPath: z.string().optional(),
  },
  async execute(args, context) {
    const state = stateFor(context.sessionID)
    if (state.owner && state.owner !== args.workflow) {
      throw new Error("policy-gate: create a handoff before changing workflow ownership")
    }
    if (state.sideEffects > 0 && state.owner !== args.workflow) {
      throw new Error("policy-gate: workflow ownership is locked after the first side effect")
    }
    state.owner = args.workflow
    state.reason = args.reason
    state.deliverable = args.deliverable
    state.sideEffectBoundary = args.sideEffectBoundary
    state.planPath = args.planPath
    const instructions = await readWorkflowInstructions(args.workflow)
    context.metadata({ title: `Workflow selected: ${args.workflow}` })
    return `${formatOwner(state)}\n\nSelected workflow instructions:\n\n${instructions}`
  },
})

const policyHealth = tool({
  description: "Report the active policy plugin health state.",
  args: {},
  async execute(_args, context) {
    return JSON.stringify({
      active: true,
      policyVersion: POLICY_VERSION,
      approvalMode: "native-permissions",
      customApprovalTool: false,
      sessionID: context.sessionID,
    })
  },
})

const createHandoff = tool({
  description: "Create a validated workflow handoff under .agents/handoffs.",
  args: {
    targetWorkflow: z.string().min(1),
    goal: z.string().min(1),
    evidence: z.string().min(1),
    paths: z.array(z.string()),
    commands: z.array(z.string()),
    results: z.array(z.string()),
    decisions: z.array(z.string()),
    gaps: z.array(z.string()),
    allowedNextAction: z.string().min(1),
  },
  async execute(args, context) {
    const state = stateFor(context.sessionID)
    if (!state.owner) throw new Error("policy-gate: select a workflow before creating a handoff")
    if (!isWorkflowName(args.targetWorkflow)) throw new Error("policy-gate: unknown target workflow")
    const safeName = `${context.sessionID}-${args.targetWorkflow}.md`.replace(/[^A-Za-z0-9._-]/g, "_")
    const handoffRoot = path.resolve(context.worktree, AGENT_ARTIFACT_DIR, "handoffs")
    const handoffPath = path.resolve(handoffRoot, safeName)
    if (!isWithin(handoffRoot, handoffPath)) throw new Error("policy-gate: invalid handoff path")

    const body = [
      "---",
      `source_workflow: ${state.owner}`,
      `target_workflow: ${args.targetWorkflow}`,
      `session_id: ${context.sessionID}`,
      "---",
      "",
      `# Goal\n${args.goal}`,
      `# Evidence\n${args.evidence}`,
      `# Paths\n${args.paths.map((item) => `- ${item}`).join("\n") || "- None"}`,
      `# Commands\n${args.commands.map((item) => `- ${item}`).join("\n") || "- None"}`,
      `# Results\n${args.results.map((item) => `- ${item}`).join("\n") || "- None"}`,
      `# Decisions\n${args.decisions.map((item) => `- ${item}`).join("\n") || "- None"}`,
      `# Gaps\n${args.gaps.map((item) => `- ${item}`).join("\n") || "- None"}`,
      `# Allowed Next Action\n${args.allowedNextAction}`,
      "",
    ].join("\n")
    if (EMOJI_RE.test(body)) throw new Error("policy-gate: handoff contains an emoji")

    await mkdir(handoffRoot, { recursive: true })
    await Bun.write(handoffPath, body)
    state.sideEffects += 1
    state.terminal = true
    return `Handoff created at ${path.relative(context.worktree, handoffPath)}. The source session is now terminal for tools.`
  },
})

const importHandoff = tool({
  description: "Read and validate a handoff attached by path, then remove it.",
  args: { handoffPath: z.string().min(1) },
  async execute(args, context) {
    const handoffPath = canonicalPath(context.worktree, args.handoffPath)
    const handoffRoot = path.resolve(context.worktree, AGENT_ARTIFACT_DIR, "handoffs")
    if (!isWithin(handoffRoot, handoffPath)) {
      throw new Error("policy-gate: handoff must be under .agents/handoffs")
    }
    const content = await readFile(handoffPath, "utf8")
    for (const heading of ["# Goal", "# Evidence", "# Paths", "# Commands", "# Results", "# Decisions", "# Gaps", "# Allowed Next Action"]) {
      if (!content.includes(heading)) throw new Error(`policy-gate: handoff is missing ${heading}`)
    }
    const targetMatch = content.match(/^target_workflow:\s*(\S+)\s*$/m)
    if (!targetMatch || !isWorkflowName(targetMatch[1])) {
      throw new Error("policy-gate: handoff has an invalid target workflow")
    }
    const state = stateFor(context.sessionID)
    state.owner = targetMatch[1]
    state.sideEffects = 0
    state.changed = false
    state.terminal = false
    await unlink(handoffPath)
    return content
  },
})

type Shell = Parameters<Plugin>[0]["$"]
let shellRuntime: Shell | undefined

function shellQuote(value: string): string {
  return `'${value.replaceAll("'", "'\\''")}'`
}

async function contextShell(directory: string, command: string): Promise<{ exitCode: number }> {
  if (!shellRuntime) throw new Error("policy-gate: shell runtime is unavailable")
  const result = await shellRuntime.cwd(directory)`sh -c ${command}`.quiet().nothrow()
  return { exitCode: result.exitCode }
}

const finishWorkflow = tool({
  description: "Run the non-mutating coding workflow gate and record its result.",
  args: {},
  async execute(_args, context) {
    const state = stateFor(context.sessionID)
    if (!state.owner) throw new Error("policy-gate: select a workflow before finishing")
    if (!state.changed) return "No project change was recorded; coding verification was not required."

    const command = [
      `PYTHONPATH=${shellQuote(LINTER_ROOT)}`,
      "uv",
      "run",
      "--project",
      shellQuote(LINTER_PROJECT),
      "--directory",
      shellQuote(LINTER_PROJECT),
      "python",
      "-m",
      "opencode_lint.cli",
      "--profile",
      "coding",
      shellQuote(context.directory),
    ].join(" ")
    const result = await contextShell(context.directory, command)
    state.verification = {
      status: result.exitCode === 0 ? "passed" : "failed",
      command: "opencode-lint --profile coding",
      exit: result.exitCode,
    }
    if (result.exitCode !== 0) {
      throw new Error("policy-gate: finish_workflow blocked; opencode-lint failed")
    }
    return "opencode-lint: passed\nVerification is current. Warnings remain in the linter result."
  },
})

export default (async ({ $, directory, client }) => {
  shellRuntime = $

  return {
    tool: {
      select_workflow: selectWorkflow,
      finish_workflow: finishWorkflow,
      create_handoff: createHandoff,
      import_handoff: importHandoff,
      policy_health: policyHealth,
    },
    config: async () => undefined,
    event: async ({ event }) => {
      if (event.type !== "session.deleted") return
      const sessionID = sessionIDFromEvent(event)
      if (sessionID) sessions.delete(sessionID)
    },
    "tool.execute.before": async (input, output) => {
      const state = await inheritParentState(input.sessionID, client)
      const args = output.args

      for (const filePath of stringPaths(args)) {
        if (isCredentialPath(filePath)) {
          throw new Error(`policy-gate: protected credential path blocked: ${path.basename(filePath)}`)
        }
      }
      if (input.tool === "bash" && commandContainsCredentialPath(commandFromArgs(args))) {
        throw new Error("policy-gate: protected credential path blocked in shell command")
      }
      if (input.tool === "apply_patch" && typeof args?.patchText === "string") {
        for (const target of patchTargets(args.patchText)) {
          if (isCredentialPath(target.filePath)) {
            throw new Error(`policy-gate: protected credential path blocked in patch: ${path.basename(target.filePath)}`)
          }
        }
      }

      if (input.tool === "import_handoff") return
      if (state.terminal) throw new Error("policy-gate: source session is terminal after handoff creation")

      if (input.tool === "skill") {
        const name = typeof args?.name === "string" ? args.name : undefined
        if (name === "workflow") {
          state.loadedSkills.add(name)
          return
        }
        if (!state.owner) throw new Error("policy-gate: load workflow and call select_workflow before other skills")
        if (name && isWorkflowName(name)) {
          throw new Error("policy-gate: select_workflow loads top-level workflow instructions")
        }
        if (name) state.loadedSkills.add(name)
        return
      }

      if (input.tool === "bash") {
        const command = commandFromArgs(args)
        if (!state.owner && !isSafeLocalCommand(command)) {
          throw new Error("policy-gate: select_workflow before non-read shell actions")
        }
        if (isDependencyCommand(command)) state.dependencyCalls.add(input.callID)
        return
      }

      if ((input.tool === "webfetch" || input.tool === "websearch") && !state.owner) {
        throw new Error("policy-gate: select_workflow before external reads")
      }

      const policyTools = ["select_workflow", "finish_workflow", "create_handoff", "import_handoff", "policy_health"]
      if (!state.owner && !isReadTool(input.tool) && !policyTools.includes(input.tool)) {
        throw new Error("policy-gate: select_workflow is required before this tool")
      }
    },
    "tool.execute.after": async (input, output) => {
      const state = stateFor(input.sessionID)
      if (isMutationTool(input.tool)) {
        state.sideEffects += 1
        state.changed = true
        state.verification = { status: "stale", reason: "project change" }
      }
      if (input.tool !== "bash") return

      const command = commandFromArgs(input.args)
      const exit = output.metadata?.exit
      const verification = isVerificationCommand(command)
      if (!isSafeLocalCommand(command) && !verification && exit === 0) {
        state.sideEffects += 1
        state.changed = true
        state.verification = { status: "stale", reason: "non-read shell command" }
      }
      if (verification) {
        state.verification = typeof exit === "number"
          ? { status: exit === 0 ? "passed" : "failed", command, exit }
          : { status: "failed", command, reason: "missing metadata.exit" }
      }
      state.dependencyCalls.delete(input.callID)
    },
    "shell.env": async (input, output) => {
      if (!input.sessionID || !input.callID) return
      const state = stateFor(input.sessionID)
      if (!state.dependencyCalls.has(input.callID)) return
      output.env.UV_EXCLUDE_NEWER = "1 week"
      output.env.NPM_CONFIG_MIN_RELEASE_AGE = "7"
      output.env.PNPM_CONFIG_MINIMUM_RELEASE_AGE = "10080"
      output.env.BUN_MINIMUM_RELEASE_AGE = "604800"
    },
  }
}) satisfies Plugin
