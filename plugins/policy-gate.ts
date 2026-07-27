import type { Plugin } from "@opencode-ai/plugin"
import { readFileSync } from "node:fs"
import { join } from "node:path"

const ENV_RE = /(?:^|[\/\s])(\.env(?:\.[^\/\s]*)?)$/m
const EM_DASH = /[ \t]*\u2014[ \t]*/g
const EMOJI_RE = /[\p{Emoji_Presentation}\p{Extended_Pictographic}]/gu
const PR_CREATE_RE = /^gh\s+pr\s+create\b/
const SKIP_COMMIT_RE = /\[skip-review\]/

interface ReviewReceipt {
  commit: string
  result: "pass" | "fail"
  p0: number
  p1: number
  timestamp: string
}

function readReceipt(worktree: string): ReviewReceipt | null {
  try {
    const data = readFileSync(
      join(worktree, ".git", "opencode", "review-receipt.json"),
      "utf-8",
    )
    return JSON.parse(data)
  } catch {
    return null
  }
}

function gitHead(worktree: string): string {
  const proc = Bun.spawnSync(["git", "rev-parse", "HEAD"], {
    cwd: worktree,
    stdout: "pipe",
    stderr: "pipe",
  })
  return proc.stdout?.toString().trim() ?? ""
}

function commitMessage(worktree: string): string {
  const proc = Bun.spawnSync(
    ["git", "log", "-1", "--format=%B", "HEAD"],
    { cwd: worktree, stdout: "pipe", stderr: "pipe" },
  )
  return proc.stdout?.toString().trim() ?? ""
}

function isSkipped(worktree: string): boolean {
  if (process.env.OPENCODE_SKIP_REVIEW === "1") return true
  if (SKIP_COMMIT_RE.test(commitMessage(worktree))) return true
  return false
}

export default (async ({ worktree }) => {
  return {
    "tool.execute.before": async (input, output) => {
      if (input.tool === "apply_patch") {
        const patchText = output.args?.patchText
        if (typeof patchText === "string") {
          for (const m of patchText.matchAll(
            /^\*\*\* (?:Add|Update|Move to|Delete) File: (.+?)\s*$/gm,
          )) {
            if (m[1] && ENV_RE.test(m[1])) {
              throw new Error(
                `policy-gate: .env file access blocked in patch: ${m[1]}`,
              )
            }
          }
        }
      }

      if (input.tool === "bash") {
        const raw = output.args?.command
        const cmd =
          typeof raw === "string" ? raw : Array.isArray(raw) ? raw.join(" ") : ""

        if (PR_CREATE_RE.test(cmd)) {
          if (isSkipped(worktree)) return

          const head = gitHead(worktree)
          const receipt = readReceipt(worktree)

          if (!receipt || receipt.commit !== head) {
            output.args.command =
              'echo "policy-gate: PR blocked - no review for HEAD. Run /code-review then retry." && exit 1'
            return
          }

          if (receipt.result === "fail" && (receipt.p0 > 0 || receipt.p1 > 0)) {
            throw new Error(
              `policy-gate: PR blocked — review failed (P0: ${receipt.p0}, P1: ${receipt.p1}).\n` +
                `Fix P0/P1 issues, re-review, then retry.\n` +
                `Skip: [skip-review] in commit message or OPENCODE_SKIP_REVIEW=1.`,
            )
          }
        }
      }
    },
    "experimental.text.complete": async (_input, output) => {
      output.text = output.text.replace(EM_DASH, ", ").replace(EMOJI_RE, "")
    },
  }
}) satisfies Plugin
