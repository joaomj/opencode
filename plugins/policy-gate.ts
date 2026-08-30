import { Effect } from "effect"
import { mkdir, readFile, unlink } from "node:fs/promises"
import { existsSync } from "node:fs"
import path from "node:path"
import { tool, type Plugin, type ToolContext } from "@opencode-ai/plugin"

const z = tool.schema

const POLICY_VERSION = "1.0.0"
const PLUGIN_API_VERSION = "1.4.6"
const LINTER_ROOT = path.resolve(import.meta.dir, "..")
const LINTER_PROJECT = path.resolve(import.meta.dir, "../opencode_lint")
const AGENT_ARTIFACT_DIR = ".agents"
const SELF_REPAIR_ENV = "OPENCODE_POLICY_REPAIR"
const SELF_REPAIR_ACTION = "policy-self-repair"
const SELF_REPAIR_ALLOWLIST = new Set([
  "plugins/policy-gate.ts",
  "plugins/policy-gate.test.ts",
  "opencode.jsonc",
  "package.json",
  "package-lock.json",
  "bun.lock",
])

const ENV_PRINT_RE = /^(?:env|printenv)(?:\s|$)/
const DIRECT_PYTHON_RE = /^(?:python3?|pip3?|pytest|ruff|mypy|pyright|coverage|tox|nox|poetry|pipenv|conda)$/
const GITHUB_HTTP_RE = /\b(?:curl|wget)\b[^\n]*github/i
const REMOTE_SCRIPT_RE = /\b(?:curl|wget)\b[^\n;&]*\|\s*(?:bash|sh|zsh|python3?|perl|ruby)\b/i
const SECRET_PATH_RE = /(?:^|[\\/])(?:\.env(?:\.[^\\/]*)?|\.npmrc|\.pypirc|\.git-credentials|credentials|.*\.credentials\.json|.*\.pem|.*\.key|id_(?:rsa|ed25519)|config\.json)$/i
const SAFE_ENV_PATH_RE = /(?:^|[\\/])\.env\.example$/i
const EMOJI_RE = /[\p{Emoji_Presentation}\p{Extended_Pictographic}]/u

const CLI_REPLACEMENTS = [
  ["cat", "bat"],
  ["grep", "rg"],
  ["find", "fd"],
  ["ls", "eza"],
  ["less", "moor"],
  ["df", "duf"],
  ["du", "dust"],
] as const

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
} as const

type WorkflowName = keyof typeof WORKFLOW_FILES
type VerificationStatus = "unknown" | "stale" | "passed" | "failed"

type Approval = {
  action: string
  repository: string
  target: string
  reason: string
  remaining: number
}

type Verification = {
  status: VerificationStatus
  command?: string
  exit?: number
  revision?: string
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
  reads: Map<string, number>
  patchGeneration: number
  loadedSkills: Set<string>
  approvals: Map<string, Approval>
  verification: Verification
  acceptedCalls: Map<string, { dependencyResolution: boolean }>
  inheritanceResolved: boolean
  terminal: boolean
}

type CommandPolicy = {
  mutation: boolean
  remote: boolean
  protectedAction?: string
  dependencyResolution: boolean
  verification: boolean
}

const sessions = new Map<string, SessionState>()

function newSessionState(): SessionState {
  return {
    sideEffects: 0,
    changed: false,
    reads: new Map(),
    patchGeneration: 0,
    loadedSkills: new Set(),
    approvals: new Map(),
    verification: { status: "unknown" },
    acceptedCalls: new Map(),
    inheritanceResolved: false,
    terminal: false,
  }
}

function stateFor(sessionID: string): SessionState {
  const state = sessions.get(sessionID)
  if (state) return state
  const created = newSessionState()
  sessions.set(sessionID, created)
  return created
}

function isWorkflowName(value: string): value is WorkflowName {
  return value in WORKFLOW_FILES
}

function workflowProfile(workflow: WorkflowName): {
  readOnly: boolean
  remote: boolean
  requiresPlanPath: boolean
} {
  if (
    workflow === "direct-assistance" ||
    workflow === "focused-exploration" ||
    workflow === "codebase-investigation" ||
    workflow === "project-opportunities" ||
    workflow === "improve-agent" ||
    workflow === "research" ||
    workflow === "implementation-planning"
  ) {
    return {
      readOnly: true,
      remote: false,
      requiresPlanPath: workflow === "implementation-planning",
    }
  }

  return {
    readOnly: workflow === "create-pull-request",
    remote: workflow === "create-pull-request" || workflow === "software-delivery",
    requiresPlanPath: false,
  }
}

function canonicalPath(directory: string, filePath: string): string {
  return path.resolve(directory, filePath)
}

function isWithin(parent: string, candidate: string): boolean {
  const relative = path.relative(path.resolve(parent), path.resolve(candidate))
  return relative === "" || (!relative.startsWith("..") && !path.isAbsolute(relative))
}

function isProtectedPath(filePath: string): boolean {
  const normalized = filePath.replaceAll("\\", "/")
  if (SAFE_ENV_PATH_RE.test(normalized)) return false
  return SECRET_PATH_RE.test(normalized)
}

function stringValues(value: unknown, key = ""): string[] {
  if (typeof value === "string") {
    return [
      key.toLowerCase().includes("path") ||
        key.toLowerCase().includes("file") ||
        key.toLowerCase().includes("target") ||
        key.toLowerCase().includes("directory")
        ? value
        : "",
    ].filter(Boolean)
  }
  if (Array.isArray(value)) return value.flatMap((item) => stringValues(item, key))
  if (!value || typeof value !== "object") return []
  return Object.entries(value).flatMap(([childKey, childValue]) =>
    stringValues(childValue, childKey),
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

function splitShellSegments(command: string): string[] {
  const segments: string[] = []
  let current = ""
  let quote: "'" | '"' | undefined
  let escaped = false

  for (let index = 0; index < command.length; index += 1) {
    const character = command[index]
    const next = command[index + 1]

    if (escaped) {
      current += character
      escaped = false
      continue
    }
    if (character === "\\" && quote !== "'") {
      current += character
      escaped = true
      continue
    }
    if (character === "'" || character === '"') {
      if (!quote) quote = character
      else if (quote === character) quote = undefined
      current += character
      continue
    }
    if (!quote && character === "$" && (next === "(" || next === "{")) {
      throw new Error("shell command contains an unsupported nested expansion")
    }
    if (!quote && character === "`") {
      throw new Error("shell command contains an unsupported command substitution")
    }
    if (!quote && (character === ";" || character === "\n" || character === "|" || character === "&")) {
      if (current.trim()) segments.push(current.trim())
      current = ""
      if ((character === "|" || character === "&") && next === character) index += 1
      continue
    }
    current += character
  }

  if (quote || escaped) throw new Error("shell command contains an incomplete quote or escape")
  if (current.trim()) segments.push(current.trim())
  return segments
}

function shellWords(segment: string): string[] {
  const words: string[] = []
  let current = ""
  let quote: "'" | '"' | undefined
  let escaped = false

  for (const character of segment) {
    if (escaped) {
      current += character
      escaped = false
      continue
    }
    if (character === "\\" && quote !== "'") {
      escaped = true
      continue
    }
    if (character === "'" || character === '"') {
      if (!quote) quote = character
      else if (quote === character) quote = undefined
      continue
    }
    if (!quote && /\s/.test(character)) {
      if (current) words.push(current)
      current = ""
      continue
    }
    current += character
  }
  if (quote || escaped) throw new Error("shell command contains an incomplete quote or escape")
  if (current) words.push(current)
  return words
}

function commandParts(segment: string): string[] {
  const words = shellWords(segment)
  while (words[0]?.match(/^[A-Za-z_][A-Za-z0-9_]*=/)) words.shift()
  if (words[0] === "env") {
    words.shift()
    while (words[0]?.match(/^[A-Za-z_][A-Za-z0-9_]*=/)) words.shift()
  }
  if (words[0] === "command" || words[0] === "exec") words.shift()
  return words
}

function commandName(segment: string): string | undefined {
  return commandParts(segment)[0]?.split("/").pop()
}

function isSafeLocalRead(parts: string[]): boolean {
  const command = parts[0]
  if (!command) return true
  if (["pwd", "date", "whoami", "id", "uname", "arch", "which", "file", "realpath", "readlink", "stat", "type", "wc", "rg", "fd", "bat", "eza", "moor", "duf", "dust"].includes(command)) return true
  if (command === "git") {
    return ["status", "diff", "log", "show", "branch", "rev-parse", "ls-files", "describe"].includes(parts[1] ?? "")
  }
  if (command === "gh") {
    return ["auth", "browse", "help", "search", "status"].includes(parts[1] ?? "")
  }
  return false
}

function isGitCloneStudyCommand(parts: string[]): boolean {
  return parts[0] === "git" && parts[1] === "clone"
}

function validateGitClone(parts: string[], directory: string, worktree: string): string | null {
  if (!isGitCloneStudyCommand(parts)) return null
  const hasDepth = parts.some((part, index) => part === "--depth" && parts[index + 1] === "1")
  const hasSingleBranch = parts.includes("--single-branch")
  if (!hasDepth || !hasSingleBranch) {
    return "study clones require git clone --depth 1 --single-branch"
  }

  const nonOptions: string[] = []
  for (let index = 2; index < parts.length; index += 1) {
    const part = parts[index]
    if (part === "--depth") {
      index += 1
      continue
    }
    if (part.startsWith("-")) continue
    nonOptions.push(part)
  }
  const destination = nonOptions[1]
  if (!destination) return "study clones require a destination outside the worktree"
  const resolvedDestination = canonicalPath(directory, destination)
  if (isWithin(worktree, resolvedDestination)) {
    return "study clone destination must be outside the active worktree"
  }
  return null
}

function evaluateCommand(command: string, directory: string, worktree: string): CommandPolicy {
  if (REMOTE_SCRIPT_RE.test(command)) throw new Error("remote script pipelines are blocked")

  const policy: CommandPolicy = {
    mutation: false,
    remote: false,
    dependencyResolution: false,
    verification: false,
  }

  for (const segment of splitShellSegments(command)) {
    const parts = commandParts(segment)
    const executable = parts[0]
    if (!executable) continue

    if (parts.slice(1).some((part) => isProtectedPath(part))) {
      throw new Error("protected credential path blocked in shell command")
    }

    if (ENV_PRINT_RE.test(segment) || executable === "export" || executable === "set") {
      throw new Error("environment value printing is blocked")
    }
    if (DIRECT_PYTHON_RE.test(executable)) {
      throw new Error(`direct ${executable} is blocked, use uv run or uvx`)
    }
    if (executable === "sudo" || executable === "chown") {
      throw new Error(`${executable} is blocked by policy`)
    }
    if (GITHUB_HTTP_RE.test(segment)) {
      throw new Error("GitHub access through curl or wget is blocked, use gh")
    }
    if (executable === "docker" && /(?:^|\s)(?:run\s+)?[^\n]*--privileged(?:\s|$)/.test(segment)) {
      throw new Error("privileged containers are blocked")
    }
    if (executable === "docker" && /--cap-add(?:=|\s+)ALL(?:\s|$)/i.test(segment)) {
      throw new Error("all-capability containers are blocked")
    }
    if (executable === "docker" && /--security-opt(?:=|\s+)[^\s]*unconfined/i.test(segment)) {
      throw new Error("unconfined container security profiles are blocked")
    }

    const cloneError = validateGitClone(parts, directory, worktree)
    if (cloneError) throw new Error(cloneError)

    if (executable === "git") {
      const subcommand = parts[1]
      if (subcommand === "push") {
        policy.mutation = true
        policy.remote = true
        policy.protectedAction = "git-push"
      }
      if (subcommand === "commit") {
        policy.mutation = true
        policy.protectedAction = "git-commit"
      }
      if (subcommand === "clone" || subcommand === "fetch" || subcommand === "pull") {
        policy.remote = true
        policy.mutation = true
      }
      if (subcommand === "reset" || subcommand === "clean" || subcommand === "restore") {
        throw new Error("destructive Git command blocked")
      }
      if (subcommand === "checkout" && parts.includes("--")) {
        throw new Error("checkout-based file replacement is blocked")
      }
      if (subcommand === "switch" && parts.some((part) => part === "-c" || part === "--create")) {
        policy.mutation = true
        policy.protectedAction = "git-branch"
      }
      if (subcommand === "checkout" && parts.some((part) => part === "-b" || part === "--orphan")) {
        policy.mutation = true
        policy.protectedAction = "git-branch"
      }
      if (subcommand === "merge" || subcommand === "rebase") {
        policy.mutation = true
        policy.protectedAction = `git-${subcommand}`
      }
    }

    if (executable === "gh") {
      const remoteWrite = /^(?:pr\s+(?:create|close|edit|merge|reopen|ready|review|unlock)|issue\s+(?:create|close|comment|delete|edit|lock|reopen|unlock)|release\s+(?:create|delete|edit|upload)|repo\s+(?:create|delete|edit|rename|archive)|workflow\s+(?:run|enable|disable)|secret\s+(?:set|delete)|gist\s+(?:create|edit|delete|list|view))$/.test(
        `${parts[1] ?? ""} ${parts[2] ?? ""}`,
      )
      if (remoteWrite) {
        policy.mutation = true
        policy.remote = true
        policy.protectedAction = parts[1] === "pr" && parts[2] === "create" ? "pull-request" : "github-write"
      }
    }

    if (["npm", "pnpm", "yarn", "bun"].includes(executable)) {
      if (["install", "i", "ci", "update", "add", "remove", "upgrade"].includes(parts[1] ?? "")) {
        policy.mutation = true
        policy.remote = true
        policy.dependencyResolution = true
      }
    }
    if (executable === "uv" && ["add", "remove", "lock", "sync", "pip"].includes(parts[1] ?? "")) {
      policy.mutation = true
      policy.remote = true
      policy.dependencyResolution = true
    }

    if (executable === "rm" || executable === "mv" || executable === "cp" || executable === "mkdir") {
      policy.mutation = true
    }
    if (executable === "git" && ["status", "diff", "log", "show", "branch", "rev-parse", "ls-files", "describe"].includes(parts[1] ?? "")) {
      policy.verification ||= parts[1] === "diff"
    }
    if (["ruff", "pytest", "pyright", "mypy", "opencode-lint"].includes(executable)) {
      policy.verification = true
    }
    if (executable === "uv" && (parts[1] === "run" || parts[1] === "x")) {
      policy.verification ||= parts.some((part) => ["ruff", "pytest", "pyright", "mypy"].includes(part))
    }
  }

  return policy
}

function approvalKey(action: string, repository: string, target: string): string {
  return `${action}\u0000${repository}\u0000${target}`
}

function consumeApproval(
  state: SessionState,
  action: string,
  repository: string,
  target: string,
): boolean {
  const key = approvalKey(action, repository, target)
  const approval = state.approvals.get(key)
  if (!approval || approval.remaining < 1) return false
  approval.remaining -= 1
  if (approval.remaining === 0) state.approvals.delete(key)
  return true
}

async function askForApproval(
  context: ToolContext,
  state: SessionState,
  action: string,
  repository: string,
  target: string,
  reason: string,
): Promise<void> {
  const safeTarget = target.length > 240 ? `${target.slice(0, 237)}...` : target
  try {
    await Effect.runPromise(
      context.ask({
        permission: `policy:${action}`,
        patterns: [safeTarget],
        always: [],
        metadata: { action, repository, target: safeTarget, reason },
      }),
    )
  } catch {
    throw new Error(`policy-gate: approval denied for ${action}`)
  }
  state.approvals.set(approvalKey(action, repository, target), {
    action,
    repository,
    target: safeTarget,
    reason,
    remaining: 1,
  })
}

function requireApproval(
  state: SessionState,
  action: string,
  repository: string,
  target: string,
): void {
  if (!consumeApproval(state, action, repository, target)) {
    throw new Error(`policy-gate: call approve_action before ${action} for this target`)
  }
}

function isHardCredentialDeny(message: string): boolean {
  return (
    message.includes('protected credential path') ||
    message.includes('protected file read') ||
    message.includes('protected path blocked in patch')
  )
}

function softActionForMessage(message: string): string {
  if (message.includes('remote script')) return 'remote-script'
  if (message.includes('environment value')) return 'env-exposure'
  if (message.includes('direct ')) return 'direct-python'
  if (message.includes('sudo') || message.includes('chown')) return 'privileged-shell'
  if (message.includes('GitHub access')) return 'github-http'
  if (message.includes('privileged containers')) return 'container-privileged'
  if (message.includes('cap-add')) return 'container-caps'
  if (message.includes('security profiles')) return 'container-security'
  if (message.includes('study clones')) return 'study-clone'
  if (message.includes('destructive Git')) return 'destructive-git'
  if (message.includes('checkout-based')) return 'checkout-replacement'
  if (message.includes('blocked because')) return 'cli-replacement'
  if (message.includes('does not permit project changes')) return 'workflow-mutation'
  if (message.includes('does not permit remote actions')) return 'workflow-remote'
  if (message.includes('select_workflow before')) return 'workflow-selection'
  if (message.includes('does not permit edits')) return 'workflow-edit'
  if (message.includes('cannot execute')) return 'workflow-command'
  if (message.includes('call approve_action before')) {
    const m = message.match(/before ([^ ]+)/)
    return m ? m[1] : 'approval-required'
  }
  if (message.includes('read the existing target')) return 'fresh-read'
  if (message.includes('workflow ownership is locked')) return 'workflow-lock'
  if (message.includes('planning workflow may write only')) return 'plan-path'
  return 'policy-soft-block'
}

function patchTargetRequiresRead(operation: string): boolean {
  return operation === "Update" || operation === "Delete"
}

function requireFreshPatchReads(
  state: SessionState,
  directory: string,
  patchText: string,
): void {
  const targets = patchTargets(patchText)
  if (!targets.length) throw new Error("policy-gate: apply_patch contains no recognized targets")
  for (const target of targets) {
    if (!patchTargetRequiresRead(target.operation)) continue
    const absolutePath = canonicalPath(directory, target.filePath)
    if (!existsSync(absolutePath)) continue
    const lastRead = state.reads.get(absolutePath)
    if (lastRead !== state.patchGeneration) {
      throw new Error(
        `policy-gate: read the existing target immediately before apply_patch: ${target.filePath}`,
      )
    }
  }
  for (const target of targets) {
    if (patchTargetRequiresRead(target.operation)) {
      state.reads.delete(canonicalPath(directory, target.filePath))
    }
  }
  state.patchGeneration += 1
}

function isSelfRepairTargets(directory: string, targets: string[]): boolean {
  if (!targets.length) return false
  return targets.every((target) => {
    const relative = path.relative(path.resolve(directory), canonicalPath(directory, target))
    const normalized = relative.replaceAll("\\", "/")
    return SELF_REPAIR_ALLOWLIST.has(normalized)
  })
}

function isSelfRepairPatch(directory: string, patchText: string): boolean {
  const targets = patchTargets(patchText).map((target) => target.filePath)
  return isSelfRepairTargets(directory, targets)
}

function isSelfRepairActive(): boolean {
  return process.env[SELF_REPAIR_ENV] === "1"
}

function isMutationTool(toolName: string): boolean {
  return ["apply_patch", "edit", "write", "write_file"].includes(toolName)
}

function isReadTool(toolName: string): boolean {
  return ["read", "glob", "grep", "list"].includes(toolName)
}

function commandFromArgs(args: unknown): string {
  if (!args || typeof args !== "object") return ""
  const raw = (args as { command?: unknown }).command
  return typeof raw === "string" ? raw : Array.isArray(raw) ? raw.join(" ") : ""
}

function isVerificationCommand(policy: CommandPolicy, command: string): boolean {
  return policy.verification || /\b(?:test|check|lint|format|verify|typecheck)\b/i.test(command)
}

async function readWorkflowInstructions(workflow: WorkflowName): Promise<string> {
  const filePath = path.resolve(import.meta.dir, "..", WORKFLOW_FILES[workflow])
  try {
    return await readFile(filePath, "utf8")
  } catch {
    throw new Error(`policy-gate: workflow instructions are unavailable: ${WORKFLOW_FILES[workflow]}`)
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
    if (state.sideEffects > 0) {
      throw new Error("policy-gate: workflow ownership is locked after the first side effect")
    }
    if (args.workflow === "implementation-planning" && !args.planPath) {
      throw new Error("policy-gate: implementation-planning requires the approved plan path")
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

const approveAction = tool({
  description: "Request one native user approval for one exact protected action.",
  args: {
    action: z.string().min(1),
    repository: z.string().min(1),
    target: z.string().min(1),
    reason: z.string().min(1),
  },
  async execute(args, context) {
    const state = stateFor(context.sessionID)
    const isSelfRepairApproval = args.action === SELF_REPAIR_ACTION || args.action === "project-edit"
    if (!state.owner && !isSelfRepairApproval && !isSelfRepairActive()) throw new Error("policy-gate: select a workflow before requesting approval")
    if (!state.owner && isSelfRepairApproval) {
      const normalizedTarget = args.target.replaceAll("\\", "/")
      const allowlisted = [...SELF_REPAIR_ALLOWLIST].some((allowed) => normalizedTarget.includes(allowed) || normalizedTarget === "self-repair")
      if (!allowlisted && !isSelfRepairActive()) throw new Error("policy-gate: self-repair approval without workflow is limited to policy files")
    }
    await askForApproval(context, state, args.action, args.repository, args.target, args.reason)
    context.metadata({ title: `Approval recorded: ${args.action}` })
    return `One-time approval recorded for ${args.action} on ${args.target}.`
  },
})

const policyHealth = tool({
  description: "Report the active policy plugin and API health state.",
  args: {},
  async execute(_args, context) {
    return JSON.stringify({
      active: true,
      policyVersion: POLICY_VERSION,
      pluginApiVersion: PLUGIN_API_VERSION,
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
    if (!isWithin(handoffRoot, handoffPath)) {
      throw new Error("policy-gate: invalid handoff path")
    }
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
    await askForApproval(context, state, "agent-artifact-directory", context.worktree, handoffRoot, "create the local handoff directory")
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
    if (!isWithin(handoffRoot, handoffPath)) throw new Error("policy-gate: handoff must be under .agents/handoffs")
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

const finishWorkflow = tool({
  description: "Run the non-mutating coding workflow gate and record its result.",
  args: {
    verificationCommand: z.string().optional(),
    createHandoffFor: z.string().optional(),
  },
  async execute(args, context) {
    const state = stateFor(context.sessionID)
    if (!state.owner) throw new Error("policy-gate: select a workflow before finishing")
    if (!state.changed) return "No project change was recorded; coding verification was not required."

    const linterCommand = [
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
    const linterResult = await contextShell(context.directory, linterCommand)
    const checks = [`opencode-lint: ${linterResult.exitCode === 0 ? "passed" : "failed"}`]
    if (linterResult.exitCode !== 0) state.verification = { status: "failed", command: "opencode-lint --profile coding", exit: linterResult.exitCode }

    if (args.verificationCommand) {
      const policy = evaluateCommand(args.verificationCommand, context.directory, context.worktree)
      if (policy.mutation || policy.remote) throw new Error("policy-gate: verification command must be non-mutating")
      const result = await contextShell(context.directory, args.verificationCommand)
      checks.push(`repository verification: ${result.exitCode === 0 ? "passed" : "failed"}`)
      state.verification = {
        status: result.exitCode === 0 && linterResult.exitCode === 0 ? "passed" : "failed",
        command: args.verificationCommand,
        exit: result.exitCode,
      }
    } else if (linterResult.exitCode === 0) {
      state.verification = { status: "passed", command: "opencode-lint --profile coding", exit: 0 }
    }

    if (state.verification.status !== "passed") {
      throw new Error(`policy-gate: finish_workflow blocked; ${checks.join("; ")}`)
    }
    return `${checks.join("; ")}\nVerification is current. Warnings remain in the linter result.`
  },
})

type Shell = Parameters<Plugin>[0]["$"]
let shellRuntime: Shell | undefined

function shellQuote(value: string): string {
  return `'${value.replaceAll("'", "'\\''")}'`
}

async function contextShell(directory: string, command: string): Promise<{ exitCode: number; output: string }> {
  if (!shellRuntime) throw new Error("policy-gate: shell runtime is unavailable")
  const result = await shellRuntime.cwd(directory)`sh -c ${command}`.quiet().nothrow()
  return { exitCode: result.exitCode, output: result.text() }
}

export default (async ({ $, directory, worktree, client }) => {
  shellRuntime = $
  const availableCliTools = new Set<string>()
  await Promise.all(
    CLI_REPLACEMENTS.map(async ([, preferred]) => {
      const result = await $`command -v ${preferred}`.quiet().nothrow()
      if (result.exitCode === 0) availableCliTools.add(preferred)
    }),
  )

  const tools = {
    select_workflow: selectWorkflow,
    approve_action: approveAction,
    finish_workflow: finishWorkflow,
    create_handoff: createHandoff,
    import_handoff: importHandoff,
    policy_health: policyHealth,
  }

  return {
    tool: tools,
    config: async () => undefined,
    event: async ({ event }) => {
      if (event.type !== "session.deleted") return
      const sessionID = sessionIDFromEvent(event)
      if (!sessionID) return
      sessions.delete(sessionID)
    },
    "tool.execute.before": async (input, output) => {
      const state = await inheritParentState(input.sessionID, client)
      const args = output.args

      for (const filePath of stringValues(args)) {
        if (isProtectedPath(filePath)) throw new Error(`policy-gate: protected credential path blocked: ${path.basename(filePath)}`)
      }

      if (input.tool === "read") {
        const filePath = typeof args?.filePath === "string" ? args.filePath : undefined
        if (filePath && isProtectedPath(filePath)) throw new Error("policy-gate: protected file read blocked")
      }

      try {
        if (state.terminal) {
          throw new Error("policy-gate: source session is terminal after handoff creation")
        }
      if (input.tool === "skill") {
        if (!state.owner) throw new Error("policy-gate: select_workflow must run before loading skills")
        const name = typeof args?.name === "string" ? args.name : undefined
        if (name && name in WORKFLOW_FILES) throw new Error("policy-gate: top-level workflows can only be activated by select_workflow")
        if (name) {
          if (state.loadedSkills.has(name)) throw new Error(`policy-gate: skill already loaded in this session: ${name}`)
          state.loadedSkills.add(name)
        }
      }

      if (input.tool === "apply_patch" && typeof args?.patchText === "string") {
        const targets = patchTargets(args.patchText)
        for (const target of targets) {
          if (isProtectedPath(target.filePath)) throw new Error(`policy-gate: protected path blocked in patch: ${path.basename(target.filePath)}`)
          if (state.owner === "implementation-planning" && canonicalPath(directory, target.filePath) !== canonicalPath(directory, state.planPath ?? "")) {
            throw new Error("policy-gate: planning workflow may write only its approved plan path")
          }
        }
        requireFreshPatchReads(state, directory, args.patchText)
      }

      if (input.tool === "bash") {
        const command = commandFromArgs(args)
        const policy = evaluateCommand(command, directory, worktree)
        if (!state.owner && !policy.verification && !splitShellSegments(command).every((segment) => isSafeLocalRead(commandParts(segment)))) {
          throw new Error("policy-gate: select_workflow before non-read shell actions")
        }
        for (const segment of splitShellSegments(command)) {
          const executable = commandName(segment)
          const replacement = CLI_REPLACEMENTS.find(([legacy]) => legacy === executable)
          if (replacement && availableCliTools.has(replacement[1])) {
            throw new Error(`shell ${replacement[0]} is blocked because ${replacement[1]} is installed`)
          }
        }
        if (state.owner) {
          const profile = workflowProfile(state.owner)
          if (policy.mutation && profile.readOnly && !(policy.remote && profile.remote)) throw new Error(`policy-gate: ${state.owner} does not permit project changes`)
          if (policy.remote && !profile.remote) throw new Error(`policy-gate: ${state.owner} does not permit remote actions`)
          if (policy.protectedAction) requireApproval(state, policy.protectedAction, worktree, command)
        }
        state.acceptedCalls.set(input.callID, { dependencyResolution: policy.dependencyResolution })
      }

      if (input.tool === "webfetch" || input.tool === "websearch") {
        const url = typeof args?.url === "string" ? args.url : ""
        if (!state.owner) throw new Error("policy-gate: select_workflow before external reads")
        if (url && /github\.com/i.test(url)) {
          // Public GitHub reads are allowed. GitHub writes remain restricted to gh.
          return
        }
      }

      if (!isReadTool(input.tool) && !["select_workflow", "approve_action", "finish_workflow", "create_handoff", "import_handoff", "policy_health"].includes(input.tool) && !state.owner) {
        if (isMutationTool(input.tool)) {
          const patchText = typeof args?.patchText === "string" ? args.patchText : undefined
          const editPath = typeof args?.filePath === "string" ? args.filePath : undefined
          const mutationTargets = patchText ? patchTargets(patchText).map((target) => target.filePath) : editPath ? [editPath] : []
          const isSelfRepair = isSelfRepairTargets(directory, mutationTargets)
          if (isSelfRepair) {
            if (isSelfRepairActive()) return
            const selfRepairKey = approvalKey(SELF_REPAIR_ACTION, worktree, "self-repair")
            if (state.approvals.has(selfRepairKey) || consumeApproval(state, SELF_REPAIR_ACTION, worktree, "self-repair")) {
              return
            }
            // Allow self-repair if user already approved a project-edit for these targets in this session
            const fallbackTarget = mutationTargets.join(",")
            if (fallbackTarget && (consumeApproval(state, "project-edit", worktree, fallbackTarget) || consumeApproval(state, SELF_REPAIR_ACTION, worktree, fallbackTarget))) {
              return
            }
          }
        }
        throw new Error("policy-gate: select_workflow is required before this tool")
      }

      if (isMutationTool(input.tool)) {
        const patchText = typeof args?.patchText === "string" ? args.patchText : undefined
        const editPath = typeof args?.filePath === "string" ? args.filePath : undefined
        const mutationTargets = patchText ? patchTargets(patchText).map((target) => target.filePath) : editPath ? [editPath] : []
        const isSelfRepair = isSelfRepairTargets(directory, mutationTargets)
        if (isSelfRepair) {
          if (isSelfRepairActive()) return
          const selfRepairKey = approvalKey(SELF_REPAIR_ACTION, worktree, "self-repair")
          if (state.approvals.has(selfRepairKey)) {
            consumeApproval(state, SELF_REPAIR_ACTION, worktree, "self-repair")
            return
          }
          if (consumeApproval(state, SELF_REPAIR_ACTION, worktree, mutationTargets.join(","))) return
          // Also accept a narrow project-edit approval that was scoped to the self-repair targets
          if (mutationTargets.length && consumeApproval(state, "project-edit", worktree, mutationTargets.join(","))) return
        }
        const profile = state.owner ? workflowProfile(state.owner) : undefined
        if (!profile || profile.readOnly) throw new Error(`policy-gate: ${state.owner ?? "unowned"} workflow does not permit edits`)
        const targets = patchText ? mutationTargets.join(",") : input.tool
        // Soft: let native edit permission (ask) handle user prompt instead of hard deny
        if (!consumeApproval(state, "project-edit", worktree, targets)) {
          return
        }
      }
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e)
        if (isHardCredentialDeny(msg)) throw e
        // Soft policy block: allow and let native permission (ask) handle user prompt
        return
      }
    },
    "tool.execute.after": async (input, output) => {
      const state = stateFor(input.sessionID)
      if (input.tool === "read") {
        const filePath = typeof input.args?.filePath === "string" ? input.args.filePath : undefined
        if (filePath) state.reads.set(canonicalPath(directory, filePath), state.patchGeneration)
      }
      if (isMutationTool(input.tool)) {
        state.sideEffects += 1
        state.changed = true
        state.verification = { status: "stale", reason: "project change" }
      }
      if (input.tool === "bash") {
        const command = commandFromArgs(input.args)
        let policy: CommandPolicy
        try {
          policy = evaluateCommand(command, directory, worktree)
        } catch {
          return
        }
        const exit = output.metadata?.exit
        if (policy.mutation && exit === 0) {
          state.sideEffects += 1
          state.changed = true
          state.verification = { status: "stale", reason: "mutating shell command" }
        }
        if (isVerificationCommand(policy, command)) {
          if (typeof exit !== "number") {
            state.verification = { status: "failed", command, reason: "missing metadata.exit" }
          } else {
            state.verification = { status: exit === 0 ? "passed" : "failed", command, exit }
          }
        }
        state.acceptedCalls.delete(input.callID)
      }
    },
    "shell.env": async (input, output) => {
      if (!input.sessionID || !input.callID) return
      const state = stateFor(input.sessionID)
      const accepted = state.acceptedCalls.get(input.callID)
      if (!accepted?.dependencyResolution) return
      output.env.UV_EXCLUDE_NEWER = "1 week"
      output.env.NPM_CONFIG_MIN_RELEASE_AGE = "7"
      output.env.PNPM_CONFIG_MINIMUM_RELEASE_AGE = "10080"
      output.env.BUN_MINIMUM_RELEASE_AGE = "604800"
    },
    "command.execute.before": async (input) => {
      const state = await inheritParentState(input.sessionID, client)
      if (!state.owner) throw new Error("policy-gate: select_workflow before executing commands")
      if (["commit", "create-pr", "release"].includes(input.command)) {
        const profile = workflowProfile(state.owner)
        if (profile.readOnly) throw new Error(`policy-gate: ${state.owner} cannot execute ${input.command}`)
      }
    },
  }
}) satisfies Plugin
