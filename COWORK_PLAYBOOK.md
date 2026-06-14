# CoWork Playbook — Text agents via Google Voice

This is the task spec for **Claude CoWork** to run the outreach texting. CoWork
operates the browser; this app only produces the campaign and the messages.

## Goal

Send each agent a personalized text **through the user's Google Voice number**,
one message every **2–3 minutes** (randomized) so Google doesn't block the
account. Never text the same agent twice.

## Input

From the Wholesaler dashboard, click **"Export Campaign (GV)"**. It downloads:

- **`gv_campaign.csv`** — the sheet to work through. Columns:
  `id, agent, phone, phoneDisplay, address, city, toll_free, message, sent_at`
- **`gv_campaign.json`** — the same data, structured (`messages[]`, plus
  `throttleSeconds: { min: 120, max: 180 }`).

Each row already contains the **exact message to send** and the **E.164 phone**
(e.g. `+12146971742`). Do not rewrite messages — send them verbatim.

## Procedure

1. Open `https://voice.google.com/u/0/messages` and confirm the user is signed
   in to the Google account that owns their Google Voice number. If not, pause
   and ask the user to log in (including 2FA).
2. Work through the rows **top to bottom**. For each row where `sent_at` is empty:
   - **Skip if `toll_free` = YES** (Google Voice can't reliably text 800/888/877/
     866/855/844/833 numbers). Mark it `SKIPPED (toll-free)` and move on.
   - Click **Send new message** → enter the `phone` → pick the suggested number.
   - Paste the row's `message` exactly → **Send**.
   - Confirm the message appears in the thread.
   - Record the send: set `sent_at` to the current timestamp in your working copy
     of the sheet (so a re-run never double-texts).
3. **Wait a random 2–3 minutes**, then do the next row. Keep the gaps irregular.
4. After the batch, report a summary: sent, skipped (toll-free), and any failures.

## Guardrails

- **Throttle is mandatory.** Never send faster than ~1 / 2 min. If Google shows a
  "can't send" / rate-limit warning, **stop** and tell the user — don't retry in a
  loop.
- **One text per agent.** Use `sent_at` (and the prior run's filled sheet) to
  avoid duplicates.
- **Stop on opt-out.** If an agent replies STOP / "don't text me," do not message
  them again and flag it for the user.
- **Batch size.** Default to the full list (~13). If the user wants to be cautious,
  do the first 3–5, confirm they look good, then continue.
- **Don't improvise content.** Send the message as written; if something looks
  wrong, ask the user rather than editing on the fly.

## Notes on the current list

- ~13 leads have phones. A few are **toll-free or brokerage main lines**
  (e.g. 855/888 numbers, "Compass") — those are flagged `toll_free` and/or are not
  a specific agent; expect them to be skipped or to bounce.
- Leads without a phone aren't in the campaign — they're off-market listings with
  no agent attribution on Zillow. Contact those via the Zillow listing instead.
