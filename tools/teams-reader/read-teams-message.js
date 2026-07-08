#!/usr/bin/env node
import { chromium } from "playwright";
import { fileURLToPath } from "node:url";
import path from "node:path";

const BRAVE_EXECUTABLE = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser";
const TEAMS_ORIGIN = "https://teams.microsoft.com";
const DEFAULT_TIMEOUT_MS = 45000;
const DEFAULT_AROUND = 3;
const SETTLE_TIMEOUT_MS = 10000;
const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const DEFAULT_PROFILE_DIR = path.join(SCRIPT_DIR, "profile");

function usage() {
  return `Usage:
  /opt/homebrew/opt/node@22/bin/node /Users/joao/.config/opencode/tools/teams-reader/read-teams-message.js --url "https://teams.microsoft.com/l/message/..." [--around 3] [--headed]
  /opt/homebrew/opt/node@22/bin/node /Users/joao/.config/opencode/tools/teams-reader/read-teams-message.js --status

Options:
  --url <url>              Teams message URL. Required.
  --around <count>         Number of visible messages to return around target. Default: ${DEFAULT_AROUND}.
  --message-only           Return only the last visible message after opening the permalink.
  --raw                    Include raw extracted DOM text for debugging.
  --status                 Check whether the isolated Teams profile is authenticated.
  --profile-dir <path>     Isolated browser profile directory. Default: ${DEFAULT_PROFILE_DIR}.
  --browser <path>         Browser executable. Default: Brave app.
  --headed                 Show browser window. Default is headless.
  --timeout-ms <number>    Load timeout. Default: ${DEFAULT_TIMEOUT_MS}.
  --help                   Show this help.

The profile directory must be isolated. The script refuses common personal Chrome/Brave profile paths.`;
}

function parseArgs(argv) {
  const args = {
    around: DEFAULT_AROUND,
    browser: BRAVE_EXECUTABLE,
    headed: false,
    messageOnly: false,
    profileDir: DEFAULT_PROFILE_DIR,
    raw: false,
    status: false,
    timeoutMs: DEFAULT_TIMEOUT_MS,
    url: "",
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--help" || arg === "-h") {
      args.help = true;
    } else if (arg === "--headed") {
      args.headed = true;
    } else if (arg === "--message-only") {
      args.messageOnly = true;
      args.around = 1;
    } else if (arg === "--raw") {
      args.raw = true;
    } else if (arg === "--status") {
      args.status = true;
    } else if (arg === "--url") {
      args.url = argv[++index] || "";
    } else if (arg === "--around") {
      args.around = Number.parseInt(argv[++index] || "", 10);
    } else if (arg === "--profile-dir") {
      args.profileDir = argv[++index] || "";
    } else if (arg === "--browser") {
      args.browser = argv[++index] || "";
    } else if (arg === "--timeout-ms") {
      args.timeoutMs = Number.parseInt(argv[++index] || "", 10);
    } else if (!arg.startsWith("--") && !args.url) {
      args.url = arg;
    } else {
      throw new Error(`Unknown argument: ${arg}`);
    }
  }

  if (!Number.isInteger(args.around) || args.around < 1 || args.around > 20) {
    throw new Error("--around must be an integer between 1 and 20");
  }
  if (!Number.isInteger(args.timeoutMs) || args.timeoutMs < 5000) {
    throw new Error("--timeout-ms must be an integer >= 5000");
  }
  return args;
}

function parseTeamsMessageUrl(rawUrl) {
  let parsed;
  try {
    parsed = new URL(rawUrl);
  } catch (error) {
    throw new Error(`Invalid Teams URL: ${rawUrl}`, { cause: error });
  }

  if (parsed.hostname !== "teams.microsoft.com") {
    throw new Error("URL host must be teams.microsoft.com");
  }

  const parts = parsed.pathname.split("/").filter(Boolean);
  if (parts[0] !== "l" || parts.length < 3) {
    throw new Error("URL must match https://teams.microsoft.com/l/message/<thread-id>/<message-id> or https://teams.microsoft.com/l/chat/<thread-id>/conversations");
  }
  const isChat = parts[1] === "chat";

  let context = {};
  const contextParam = parsed.searchParams.get("context");
  if (contextParam) {
    try {
      context = JSON.parse(contextParam);
    } catch (error) {
      throw new Error("Teams URL context parameter is not valid JSON", { cause: error });
    }
  }

  return {
    contextType: context.contextType || null,
    isChat,
    messageId: isChat ? null : decodeURIComponent(parts[3]),
    threadId: decodeURIComponent(isChat ? parts[2] : parts[2]),
    url: parsed.toString(),
    chatUrl: isChat ? parsed.toString() : null,
  };
}

function assertIsolatedProfile(profileDir) {
  const resolved = path.resolve(profileDir);
  const home = process.env.HOME ? path.resolve(process.env.HOME) : "";
  const forbidden = [
    "Library/Application Support/BraveSoftware/Brave-Browser",
    "Library/Application Support/Google/Chrome",
    "Library/Application Support/Chromium",
    "Library/Application Support/Microsoft Edge",
  ].map((suffix) => path.join(home, suffix));

  if (forbidden.some((dir) => resolved === dir || resolved.startsWith(`${dir}${path.sep}`))) {
    throw new Error(`Refusing to use a personal browser profile: ${resolved}`);
  }

  const allowedRoot = path.resolve(SCRIPT_DIR);
  if (!resolved.startsWith(`${allowedRoot}${path.sep}`)) {
    throw new Error(`Profile must live under ${allowedRoot}. Received: ${resolved}`);
  }

  return resolved;
}

function isLoginUrl(url) {
  const parsed = new URL(url);
  return parsed.hostname === "login.microsoftonline.com" || parsed.hostname.endsWith(".login.microsoftonline.com");
}

async function waitForLoginCompletion(page, timeoutMs) {
  await page.waitForURL((url) => !isLoginUrl(url.toString()), { timeout: timeoutMs });
  await page.waitForLoadState("domcontentloaded", { timeout: SETTLE_TIMEOUT_MS }).catch(() => undefined);
  await page.waitForTimeout(3000);
}

async function settlePage(page) {
  await page.waitForLoadState("domcontentloaded", { timeout: SETTLE_TIMEOUT_MS }).catch(() => undefined);
  await page.waitForTimeout(3000);
}

async function ensureAuthenticated(page, headed, timeoutMs) {
  const loginLocator = page.locator('input[type="email"], input[name="loginfmt"], text=/sign in/i').first();
  await page.goto(TEAMS_ORIGIN, { waitUntil: "domcontentloaded", timeout: timeoutMs });
  await settlePage(page);

  const loginVisible = isLoginUrl(page.url()) || (await loginLocator.isVisible({ timeout: 3000 }).catch(() => false));
  if (loginVisible && !headed) {
    throw new Error(
      "Teams is not authenticated in the isolated profile. Run once with --headed and log in."
    );
  }

  if (loginVisible) {
    console.error("Teams login is open in the isolated browser profile. Complete login to continue.");
    await waitForLoginCompletion(page, timeoutMs);
  }
}

async function checkStatus(page, profileDir, timeoutMs) {
  const loginLocator = page.locator('input[type="email"], input[name="loginfmt"], text=/sign in/i').first();
  await page.goto(TEAMS_ORIGIN, { waitUntil: "domcontentloaded", timeout: timeoutMs });
  await settlePage(page);

  const loginVisible = isLoginUrl(page.url()) || (await loginLocator.isVisible({ timeout: 3000 }).catch(() => false));
  return {
    authenticated: !loginVisible,
    profileDir,
    title: await page.title().catch(() => ""),
    url: page.url(),
  };
}

async function openMessageUrl(page, messageUrl, headed, timeoutMs, isChat) {
  await page.goto(messageUrl, { waitUntil: "domcontentloaded", timeout: timeoutMs });
  await settlePage(page);
  await page.waitForTimeout(isChat ? 8000 : 5000);

  const useWebAppButton = page.getByRole("button", { name: /use the web app instead/i });
  if (await useWebAppButton.isVisible({ timeout: 3000 }).catch(() => false)) {
    await useWebAppButton.click();
    await settlePage(page);
    await page.waitForTimeout(10000);
  }

  const loginVisible =
    isLoginUrl(page.url()) ||
    (await page
      .locator('input[type="email"], input[name="loginfmt"], text=/sign in/i')
      .first()
      .isVisible({ timeout: 3000 })
      .catch(() => false));
  if (loginVisible && !headed) {
    throw new Error(
      "Teams is not authenticated in the isolated profile. Run once with --headed and log in."
    );
  }

  if (loginVisible) {
    console.error("Teams login is open in the isolated browser profile. Complete login to continue.");
    await waitForLoginCompletion(page, timeoutMs);
    await page.goto(messageUrl, { waitUntil: "domcontentloaded", timeout: timeoutMs });
    await page.waitForTimeout(5000);
  }
}

async function extractMessages(page, around) {
  return page.evaluate((limit) => {
    const headingSelectors = 'h4, [role="heading"][aria-level="4"], [aria-level="4"]';
    const headings = Array.from(document.querySelectorAll(headingSelectors));

    function normalizedText(node) {
      return (node?.innerText || node?.textContent || "").replace(/\s+\n/g, "\n").trim();
    }

    function smallestMessageContainer(heading) {
      let candidate = heading;
      let best = heading;
      for (let depth = 0; candidate && depth < 8; depth += 1) {
        const text = normalizedText(candidate);
        if (text.length > normalizedText(best).length && text.length < 5000) {
          best = candidate;
        }
        const role = candidate.getAttribute?.("role") || "";
        const aria = candidate.getAttribute?.("aria-label") || "";
        if (/article|listitem/i.test(role) || /message/i.test(aria)) {
          return candidate;
        }
        candidate = candidate.parentElement;
      }
      return best;
    }

    function firstTimestampIndex(lines) {
      return lines.findIndex((line) => /\b(\d{1,2}:\d{2}\s*(am|pm)|yesterday|today|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b/i.test(line));
    }

    function cleanBodyLine(line) {
      return !/^(translate|\d+\s+like reactions?.*|by using youtube.*|privacy policy|terms of use|permissions|open|[,.;]+|,\s*and|\d+)$/i.test(line);
    }

    function parseMessage(text) {
      const lines = text.split("\n").map((line) => line.trim()).filter(Boolean);
      const timestampIndex = firstTimestampIndex(lines);
      const sender = timestampIndex > 0 ? lines[timestampIndex - 1] : null;
      const timestamp = timestampIndex >= 0 ? lines[timestampIndex] : null;
      const bodyStart = timestampIndex >= 0 ? timestampIndex + 1 : 0;
      const bodyLines = lines.slice(bodyStart).filter(cleanBodyLine);
      return {
        sender,
        text: bodyLines.join("\n"),
        timestamp,
      };
    }

    const recent = headings.slice(-limit);
    return recent
      .map((heading, index) => {
        const container = smallestMessageContainer(heading);
        const text = normalizedText(container);
        const parsed = parseMessage(text);
        return {
          index,
          rawText: text,
          sender: parsed.sender,
          timestamp: parsed.timestamp,
          text: parsed.text || text,
        };
      })
      .filter((message) => message.rawText);
  }, around);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    console.log(usage());
    return;
  }
  if (!args.status && !args.url) {
    throw new Error("--url is required");
  }

  const target = args.url ? parseTeamsMessageUrl(args.url) : null;
  const profileDir = assertIsolatedProfile(args.profileDir);

  let browser;
  try {
    browser = await chromium.launchPersistentContext(profileDir, {
      executablePath: args.browser,
      headless: !args.headed,
      viewport: { height: 1000, width: 1440 },
    });
  } catch (error) {
    if (error.message.includes("ProcessSingleton") || error.message.includes("SingletonLock")) {
      throw new Error(
        "The isolated Teams browser profile is already in use. Close the other Teams reader browser/process and retry."
      );
    }
    throw error;
  }

  try {
    const page = browser.pages()[0] || (await browser.newPage());
    if (args.status) {
      console.log(JSON.stringify(await checkStatus(page, profileDir, args.timeoutMs), null, 2));
      return;
    }
    await ensureAuthenticated(page, args.headed, args.timeoutMs);
    await openMessageUrl(page, target.url, args.headed, args.timeoutMs, target.isChat);
    const extractedMessages = await extractMessages(page, args.around);
    const selectedMessages = args.messageOnly ? extractedMessages.slice(-1) : extractedMessages;
    const messages = args.raw
      ? selectedMessages
      : selectedMessages.map(({ rawText: _rawText, ...message }) => message);
    const { isChat, chatUrl: _chatUrl, ...cleanTarget } = target;
    console.log(JSON.stringify({ ...cleanTarget, messages }, null, 2));
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(JSON.stringify({ error: error.message }, null, 2));
  process.exitCode = 1;
});
