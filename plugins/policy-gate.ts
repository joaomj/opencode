import type { Plugin } from "@opencode-ai/plugin"

const ENV_RE = /(?:^|[\/\s])(\.env(?:\.[^\/\s]*)?)$/m
const EM_DASH = /[ \t]*\u2014[ \t]*/g
const EMOJI_RE = /[\p{Emoji_Presentation}\p{Extended_Pictographic}]/gu

const SEGMENT_RE = /\s*(?:&&|\|\||[;&|\n])\s*/

const GREP_RE = /^grep\b/
const ENV_PRINTENV_RE = /^(?:env|printenv)\b/
const PYTHON_RE = /^(?:python3?|pip3?)\b/

function blockCommand(command: string): string | null {
  const segments = command.split(SEGMENT_RE).map((s) => s.trim())
  for (const segment of segments) {
    if (!segment) continue
    if (GREP_RE.test(segment)) {
      return `shell grep blocked, use rg: ${segment}`
    }
    if (ENV_PRINTENV_RE.test(segment)) {
      return `env/printenv blocked (never-read-env), read files or use os.getenv(): ${segment}`
    }
    if (PYTHON_RE.test(segment)) {
      return `bare python blocked, use uv run or uvx: ${segment}`
    }
  }
  return null
}

export default (async () => {
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

        const reason = blockCommand(cmd)
        if (reason) {
          throw new Error(`policy-gate: ${reason}`)
        }
      }
    },
    "experimental.text.complete": async (_input, output) => {
      output.text = output.text.replace(EM_DASH, ", ").replace(EMOJI_RE, "")
    },
  }
}) satisfies Plugin
