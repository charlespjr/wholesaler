# gv-texter — Google Voice agent texter

Sends your personalized outreach texts through **your own Google Voice number**,
one message every **2–3 minutes** (randomized) so Google doesn't flag the account.
It drives `voice.google.com` in a real Chrome window using your logged-in profile,
and keeps a resume log so it never double-texts an agent.

> Runs on **your computer**, not in the cloud. Google Voice has no API, so this
> automates the website. Keep volume low and the throttle on.

## One-time setup

```bash
cd gv-texter
npm install
npx playwright install chrome
```

## 1. Export the campaign from the app

In the Wholesaler dashboard, click **"Export Campaign (GV)"**. It downloads
`gv_campaign.json` — one frozen, personalized message per lead that has a phone
number. Drop that file into this `gv-texter/` folder.

You can open the JSON and edit any `message` before sending.

## 2. Log into Google Voice (first time only)

```bash
node send.js --login
```

A Chrome window opens. Sign into the Google account that owns your Google Voice
number (do any 2FA). When you can see your Messages, return to the terminal and
press Enter. Your login is saved in `.gv-profile/` so you won't repeat this.

## 3. Test without sending

```bash
node send.js --dry-run
```

Walks through composing each message but never presses Send. Watch the window to
confirm recipients and text look right.

## 4. Send for real

```bash
node send.js
```

It sends one text every 2–3 minutes. Leave the window open and your computer
awake. Progress is logged, and every sent number is recorded in `gv-sent.json`,
so if you stop and re-run it picks up where it left off.

### Useful flags

| Flag | Effect |
|------|--------|
| `--limit 5` | Send at most 5 this run (good for a cautious first batch) |
| `--min 180 --max 300` | Slower: 3–5 minutes between sends |
| `--file path.json` | Use a different campaign file |
| `--dry-run` | Compose but never send |
| `--headless` | No visible window (only after it's working reliably) |

## Notes & gotchas

- **Throttle matters.** Google will temporarily block messaging if you blast
  texts. The default 2–3 min is conservative; raise it (`--min/--max`) if you
  send a lot. Small batches with `--limit` are safest.
- **Selectors can drift.** This automates Google's website, so a GV redesign can
  break the compose/recipient/send selectors in `send.js`. If a send fails, a
  screenshot lands in `errors/` — update the locator lists near the top of
  `sendOne()`.
- **Resume / re-run.** Delete an entry from `gv-sent.json` (or the whole file) to
  re-text someone. Failed sends are not logged, so they retry automatically.
- **Compliance.** You're texting agents about their own public listings. Keep it
  relevant, honor opt-outs, and don't mass-blast — that's both good practice and
  what keeps the GV account healthy.
