#!/usr/bin/env node
/**
 * gv-texter — throttled Google Voice SMS sender.
 *
 * Drives voice.google.com in a real (non-headless) Chrome using your own
 * logged-in profile, and sends one message every 2-3 minutes (randomized) so
 * Google doesn't flag the account. Keeps a resume log so it never double-texts.
 *
 * It does NOT run in the cloud — run it on your own computer.
 *
 *   npm install
 *   npx playwright install chrome
 *   node send.js --login        # first time: log into Google Voice, then it's remembered
 *   node send.js --dry-run      # walk through everything EXCEPT pressing send
 *   node send.js                # send for real, 2-3 min apart
 *
 * Flags:
 *   --login            Open the browser, wait until you're logged into GV, then exit.
 *   --dry-run          Do everything except actually send (no text leaves your number).
 *   --file <path>      Campaign JSON (default: ./gv_campaign.json).
 *   --min <seconds>    Min gap between sends (default: 120, or campaign throttle).
 *   --max <seconds>    Max gap between sends (default: 180, or campaign throttle).
 *   --limit <n>        Send at most n messages this run.
 *   --headless         Run without a visible window (not recommended for first runs).
 */

const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");
const readline = require("readline");

// ---------- CLI args ----------
function arg(name, fallback) {
  const i = process.argv.indexOf("--" + name);
  if (i === -1) return fallback;
  const next = process.argv[i + 1];
  return next && !next.startsWith("--") ? next : true;
}
const FLAGS = {
  login: process.argv.includes("--login"),
  dryRun: process.argv.includes("--dry-run"),
  headless: process.argv.includes("--headless"),
  file: arg("file", path.join(process.cwd(), "gv_campaign.json")),
  min: arg("min", null),
  max: arg("max", null),
  limit: arg("limit", null),
};

const PROFILE_DIR = path.join(__dirname, ".gv-profile");
const SENT_LOG = path.join(__dirname, "gv-sent.json");
const ERROR_DIR = path.join(__dirname, "errors");

// ---------- helpers ----------
const sleep = ms => new Promise(r => setTimeout(r, ms));
const rand = (min, max) => Math.floor(min + Math.random() * (max - min));
function log(...a) { console.log(`[${new Date().toLocaleTimeString()}]`, ...a); }

function loadJSON(p, fallback) {
  try { return JSON.parse(fs.readFileSync(p, "utf8")); } catch (e) { return fallback; }
}
function saveJSON(p, obj) { fs.writeFileSync(p, JSON.stringify(obj, null, 2)); }

// Try a list of locators, return the first that becomes visible within `timeout`.
async function firstVisible(page, locators, timeout = 8000) {
  const deadline = Date.now() + timeout;
  while (Date.now() < deadline) {
    for (const loc of locators) {
      try { if (await loc.first().isVisible()) return loc.first(); } catch (e) {}
    }
    await sleep(250);
  }
  return null;
}

async function isLoggedIn(page) {
  // The "Send new message" compose control only exists once you're signed in.
  const compose = await firstVisible(page, composeLocators(page), 6000);
  return !!compose;
}

function composeLocators(page) {
  return [
    page.getByRole("link", { name: /send new message/i }),
    page.getByRole("button", { name: /send new message/i }),
    page.locator('[aria-label="Send new message"]'),
    page.locator('[gv-test-id="send-new-message"]'),
  ];
}

// ---------- the send ----------
async function sendOne(page, msg) {
  // 1) open a fresh compose
  await page.goto("https://voice.google.com/u/0/messages", { waitUntil: "domcontentloaded" });
  const compose = await firstVisible(page, composeLocators(page), 15000);
  if (!compose) throw new Error("Could not find the 'Send new message' button (are you logged in?).");
  await compose.click();
  await sleep(rand(800, 1500));

  // 2) recipient
  const recipient = await firstVisible(page, [
    page.getByRole("combobox"),
    page.getByPlaceholder(/type a name or phone number/i),
    page.locator('input[aria-label*="phone" i]'),
    page.locator('input[type="text"]'),
  ], 10000);
  if (!recipient) throw new Error("Could not find the recipient field.");
  await recipient.click();
  await recipient.fill("");
  await recipient.type(msg.phone, { delay: rand(40, 110) });
  await sleep(rand(1200, 2200)); // let the suggestion chip resolve

  // Pick the suggested contact/number, then fall back to Enter.
  const suggestion = await firstVisible(page, [
    page.getByRole("option").first(),
    page.locator('[role="option"]').first(),
    page.locator(`text=/${msg.phone.replace(/[^0-9]/g, "").slice(-4)}/`).first(),
  ], 4000);
  if (suggestion) { await suggestion.click().catch(() => {}); }
  else { await recipient.press("Enter"); }
  await sleep(rand(800, 1500));

  // 3) message body
  const body = await firstVisible(page, [
    page.getByRole("textbox", { name: /type a message|text message/i }),
    page.getByPlaceholder(/type a message|text message/i),
    page.locator('textarea'),
    page.locator('[contenteditable="true"]'),
  ], 10000);
  if (!body) throw new Error("Could not find the message box.");
  await body.click();
  await body.type(msg.message, { delay: rand(15, 45) });
  await sleep(rand(600, 1200));

  if (FLAGS.dryRun) {
    log(`   DRY-RUN: would send to ${msg.phoneDisplay || msg.phone}`);
    return;
  }

  // 4) send — try the Send button, fall back to Enter
  const sendBtn = await firstVisible(page, [
    page.getByRole("button", { name: /^send message$/i }),
    page.locator('[aria-label="Send message"]'),
  ], 4000);
  if (sendBtn) await sendBtn.click();
  else await body.press("Enter");
  await sleep(rand(1500, 2500));
}

async function captureError(page, id) {
  try {
    if (!fs.existsSync(ERROR_DIR)) fs.mkdirSync(ERROR_DIR);
    await page.screenshot({ path: path.join(ERROR_DIR, `${id}-${Date.now()}.png`), fullPage: true });
  } catch (e) {}
}

function ask(question) {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  return new Promise(res => rl.question(question, a => { rl.close(); res(a); }));
}

// ---------- main ----------
(async () => {
  const campaign = loadJSON(FLAGS.file, null);
  if (!campaign && !FLAGS.login) {
    console.error(`Campaign file not found: ${FLAGS.file}\nExport one from the app ("Export Campaign (GV)") and place it here, or pass --file <path>.`);
    process.exit(1);
  }
  const throttle = (campaign && campaign.throttleSeconds) || { min: 120, max: 180 };
  const minS = Number(FLAGS.min || throttle.min || 120);
  const maxS = Number(FLAGS.max || throttle.max || 180);
  const limit = FLAGS.limit ? Number(FLAGS.limit) : Infinity;

  const sentLog = loadJSON(SENT_LOG, { sent: {} });
  sentLog.sent = sentLog.sent || {};

  log(`Launching Chrome (profile: ${PROFILE_DIR})...`);
  const ctx = await chromium.launchPersistentContext(PROFILE_DIR, {
    headless: FLAGS.headless,
    channel: "chrome",
    viewport: { width: 1100, height: 850 },
  });
  const page = ctx.pages()[0] || await ctx.newPage();

  await page.goto("https://voice.google.com/u/0/messages", { waitUntil: "domcontentloaded" });
  if (!(await isLoggedIn(page))) {
    console.log("\n=== Log into Google Voice in the window that just opened. ===");
    console.log("Once you can see your Messages list, come back here and press Enter.\n");
    await ask("Press Enter when you're logged into Google Voice... ");
    await page.goto("https://voice.google.com/u/0/messages", { waitUntil: "domcontentloaded" });
    if (!(await isLoggedIn(page))) {
      console.error("Still not logged in — exiting. Re-run after signing in.");
      await ctx.close();
      process.exit(1);
    }
  }
  log("Logged into Google Voice. ✔");

  if (FLAGS.login) {
    log("Login saved to the profile. You can now run `node send.js` to send.");
    await ctx.close();
    return;
  }

  const queue = campaign.messages.filter(m => m.phone && !sentLog.sent[m.phone]);
  log(`${campaign.messages.length} in campaign, ${queue.length} still to send, throttle ${minS}-${maxS}s.`);
  if (FLAGS.dryRun) log("DRY-RUN mode: nothing will actually be sent.");

  let done = 0;
  for (let i = 0; i < queue.length && done < limit; i++) {
    const msg = queue[i];
    log(`(${done + 1}) Texting ${msg.name || msg.phoneDisplay || msg.phone} re: ${msg.address}`);
    try {
      await sendOne(page, msg);
      if (!FLAGS.dryRun) {
        sentLog.sent[msg.phone] = { id: msg.id, name: msg.name, at: new Date().toISOString() };
        saveJSON(SENT_LOG, sentLog);
        log(`   ✔ sent & logged`);
      }
    } catch (err) {
      log(`   ✖ failed: ${err.message}`);
      await captureError(page, msg.id || "unknown");
      // don't mark as sent; it'll be retried next run
    }
    done++;

    const more = (done < limit) && (i + 1 < queue.length);
    if (more) {
      const waitMs = rand(minS * 1000, maxS * 1000);
      const next = new Date(Date.now() + waitMs);
      log(`   waiting ${Math.round(waitMs / 1000)}s — next send ~${next.toLocaleTimeString()}`);
      await sleep(waitMs);
    }
  }

  log(`Done. ${done} processed this run.`);
  await ctx.close();
})().catch(err => { console.error(err); process.exit(1); });
