#!/usr/bin/env bun
import { readFile } from "node:fs/promises"
import path from "node:path"

const CONFIG_DIR = path.resolve(import.meta.dir, "..")
const POLICY_PATH = path.resolve(CONFIG_DIR, "plugins/policy-gate.ts")
const CONFIG_PATH = path.resolve(CONFIG_DIR, "opencode.jsonc")

function fail(message: string): never {
  console.error(`policy-check failed: ${message}`)
  process.exit(1)
}

if (process.env.OPENCODE_PURE === "1") {
  fail("OPENCODE_PURE=1 is blocked because it disables credential protection. Restore a known-good configuration with external Git before launch.")
}

let configText: string
try {
  configText = await readFile(CONFIG_PATH, "utf8")
} catch {
  fail(`cannot read ${CONFIG_PATH}`)
}

if (!configText.includes("policy-gate")) {
  fail(`opencode.jsonc must include "./plugins/policy-gate.ts" in plugin list. Found no policy-gate entry.`)
}

// Verify plugin syntax via bun build dry run
const build = await Bun.build({
  entrypoints: [POLICY_PATH],
  target: "bun",
  minify: false,
})

if (!build.success) {
  for (const log of build.logs) console.error(log)
  fail(`policy plugin failed to build: ${POLICY_PATH}`)
}

console.log("policy-check: ok")
console.log(`  plugin: ${path.relative(CONFIG_DIR, POLICY_PATH)}`)
console.log(`  config: ${path.relative(CONFIG_DIR, CONFIG_PATH)} includes policy-gate`)
