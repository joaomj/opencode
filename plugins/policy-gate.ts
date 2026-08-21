import type { Plugin } from "@opencode-ai/plugin"
import path from "node:path"

type Shell = Parameters<Plugin>[0]["$"]

const ENV_RE = /(?:^|[\/\s])(\.env(?:\.[^\/\s]*)?)$/m
const EM_DASH = /[ \t]*\u2014[ \t]*/g
const EMOJI_RE = /[\p{Emoji_Presentation}\p{Extended_Pictographic}]/gu

const SEGMENT_RE = /\s*(?:&&|\|\||[;&|\n])\s*/

const ENV_PRINTENV_RE = /^(?:env|printenv)\b/
const PYTHON_RE =
  /^(?:python3?|pip3?|pytest|ruff|mypy|pyright|coverage|tox|nox|poetry|pipenv|conda)\b/

const GIT_REMOTE_WRITE_RE =
  /\bgit(?:-[^\s]+)?\s+(?:-\S+\s+)*push(?:\s|$)/
const GIT_LFS_REMOTE_WRITE_RE =
  /\bgit(?:-[^\s]+)?\s+(?:-\S+\s+)*lfs\s+push(?:\s|$)/
const GITHUB_HTTP_RE = /\b(?:curl|wget)\b[^\n]*github/i

const CLI_REPLACEMENTS = [
  ["cat", "bat"],
  ["grep", "rg"],
  ["find", "fd"],
  ["ls", "eza"],
  ["less", "moor"],
  ["df", "duf"],
  ["du", "dust"],
] as const

const loadedSkills = new Map<string, Set<string>>()
const readFiles = new Map<string, Map<string, number>>()
const patchSequences = new Map<string, number>()

function commandName(segment: string): string | undefined {
  return segment.match(/^(?:env\s+\S+=\S+\s+)?([A-Za-z0-9_.-]+)/)?.[1]
}

function blockCliCommand(segment: string, available: Set<string>): string | null {
  const command = commandName(segment)
  if (!command) return null

  const replacement = CLI_REPLACEMENTS.find(([legacy]) => legacy === command)
  if (!replacement || !available.has(replacement[1])) return null

  return `shell ${replacement[0]} blocked because ${replacement[1]} is installed, use ${replacement[1]}: ${segment}`
}

function blockCommand(command: string, availableCliTools: Set<string>): string | null {
  const segments = command.split(SEGMENT_RE).map((s) => s.trim())
  for (const segment of segments) {
    if (!segment) continue
    const cliReason = blockCliCommand(segment, availableCliTools)
    if (cliReason) {
      return cliReason
    }
    if (ENV_PRINTENV_RE.test(segment)) {
      return `env/printenv blocked (never-read-env), read files or use os.getenv(): ${segment}`
    }
    if (PYTHON_RE.test(segment)) {
      const name = segment.match(PYTHON_RE)?.[0] ?? "python tool"
      return `${name} blocked, use uv run or uvx: ${segment}`
    }
    if (GIT_REMOTE_WRITE_RE.test(segment) || GIT_LFS_REMOTE_WRITE_RE.test(segment)) {
      return `remote Git write blocked, use an approved gh workflow: ${segment}`
    }
    if (GITHUB_HTTP_RE.test(segment)) {
      return `GitHub access through curl/wget blocked, use gh: ${segment}`
    }
  }
  return null
}

async function detectAvailableCliTools($: Shell): Promise<Set<string>> {
  const available = new Set<string>()
  const tools = [...new Set(CLI_REPLACEMENTS.flatMap(([, preferred]) => [preferred]))]

  await Promise.all(
    tools.map(async (tool) => {
      const result = await $`command -v ${tool}`.quiet().nothrow()
      if (result.exitCode === 0) available.add(tool)
    }),
  )

  return available
}

function sessionIDFromEvent(event: unknown): string | undefined {
  if (!event || typeof event !== "object") return undefined
  const properties = (event as { properties?: unknown }).properties
  if (!properties || typeof properties !== "object") return undefined
  const sessionID = (properties as { sessionID?: unknown }).sessionID
  if (typeof sessionID === "string") return sessionID

  const info = (properties as { info?: unknown }).info
  if (!info || typeof info !== "object") return undefined
  const id = (info as { id?: unknown }).id
  return typeof id === "string" ? id : undefined
}

function resolvedPath(directory: string, filePath: string): string {
  return path.resolve(directory, filePath)
}

function patchTargets(patchText: string): Array<{ operation: string; filePath: string }> {
  return [
    ...[...patchText.matchAll(
      /^\*\*\* (Add|Update|Delete) File: (.+?)\s*$/gm,
    )].map((match) => ({ operation: match[1], filePath: match[2] })),
    ...[...patchText.matchAll(/^\*\*\* Move to: (.+?)\s*$/gm)].map((match) => ({
      operation: "Move to",
      filePath: match[1],
    })),
  ]
}

function requireFreshPatchReads(sessionID: string, directory: string, patchText: string): void {
  const targets = patchTargets(patchText)
  if (!targets.length) return

  const sequence = (patchSequences.get(sessionID) ?? 0) + 1
  patchSequences.set(sessionID, sequence)
  const reads = readFiles.get(sessionID) ?? new Map<string, number>()

  for (const target of targets) {
    const { operation, filePath } = target
    if (operation === "Add" || operation === "Move to") continue

    const lastRead = reads.get(resolvedPath(directory, filePath)) ?? -1
    if (lastRead < sequence - 1) {
      throw new Error(
        `policy-gate: read the target immediately before apply_patch and re-read it after a failed patch: ${filePath}`,
      )
    }
  }
}

export default (async ({ $, directory }) => {
  const availableCliTools = await detectAvailableCliTools($)

  return {
    event: async ({ event }) => {
      if (event.type !== "session.compacted" && event.type !== "session.deleted") return
      const sessionID = sessionIDFromEvent(event)
      if (sessionID) {
        loadedSkills.delete(sessionID)
        readFiles.delete(sessionID)
        patchSequences.delete(sessionID)
      }
    },
    "tool.execute.before": async (input, output) => {
      if (input.tool === "read") {
        const filePath = output.args?.filePath
        if (typeof filePath === "string") {
          const reads = readFiles.get(input.sessionID) ?? new Map<string, number>()
          reads.set(
            resolvedPath(directory, filePath),
            patchSequences.get(input.sessionID) ?? 0,
          )
          readFiles.set(input.sessionID, reads)
        }
      }

      if (input.tool === "skill") {
        const name =
          output.args && typeof output.args === "object" && typeof output.args.name === "string"
            ? output.args.name
            : undefined
        if (name) {
          const sessionSkills = loadedSkills.get(input.sessionID) ?? new Set<string>()
          if (sessionSkills.has(name)) {
            throw new Error(`policy-gate: skill already loaded in this session: ${name}`)
          }
          sessionSkills.add(name)
          loadedSkills.set(input.sessionID, sessionSkills)
        }
      }

      if (input.tool === "apply_patch") {
        const patchText = output.args?.patchText
        if (typeof patchText === "string") {
          requireFreshPatchReads(input.sessionID, directory, patchText)
          for (const { filePath } of patchTargets(patchText)) {
            if (filePath && ENV_RE.test(filePath)) {
              throw new Error(
                `policy-gate: .env file access blocked in patch: ${filePath}`,
              )
            }
          }
        }
      }

      if (input.tool === "bash") {
        const raw = output.args?.command
        const cmd =
          typeof raw === "string" ? raw : Array.isArray(raw) ? raw.join(" ") : ""

        const reason = blockCommand(cmd, availableCliTools)
        if (reason) {
          throw new Error(`policy-gate: ${reason}`)
        }
      }

      if (input.tool === "webfetch") {
        const url = output.args?.url
        if (typeof url === "string" && /github/i.test(url)) {
          throw new Error(
            "policy-gate: GitHub access through webfetch blocked, use gh",
          )
        }
      }
    },
    "experimental.text.complete": async (_input, output) => {
      output.text = output.text.replace(EM_DASH, ", ").replace(EMOJI_RE, "")
    },
  }
}) satisfies Plugin
