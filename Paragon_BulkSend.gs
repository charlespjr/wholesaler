/**
 * Paragon Government Solutions — Gmail bulk sender (free, sends from your own Gmail)
 * --------------------------------------------------------------------------------
 * Sends the personalized owner offers from a Google Sheet, one-to-one, throttled,
 * resumable, and CAN-SPAM compliant.
 *
 * SETUP (one time):
 * 1) Create a new Google Sheet. File > Import > Upload > Paragon_Owner_Mailmerge_DEDUPED.csv
 *    (Import location: "Replace current sheet". Make sure row 1 is the header.)
 * 2) Confirm the tab has header columns: Email | Subject | Body | Property_Count
 * 3) Extensions > Apps Script. Delete any sample code, paste THIS file, click Save.
 * 4) Run > sendBatch  (first run asks for authorization — allow it; it's your own account).
 *
 * HOW IT SENDS:
 * - It adds two columns ("Status", "SentAt") and marks each row as it goes, so you can
 *   stop/re-run anytime without double-sending.
 * - It sends up to BATCH_SIZE per run (Apps Script caps a single run at ~6 minutes),
 *   pausing DELAY_SECONDS between each to avoid spam flags.
 * - 193 emails: either run sendBatch a few times, OR run installAutoTrigger() once and it
 *   will keep going every 10 minutes on its own until done, then stop itself.
 *
 * STOP / RESET:
 * - removeAutoTrigger()  -> stops the automatic runs.
 * - To resend everything, clear the "Status" column.
 */

// ====================== CONFIG ======================
var CONFIG = {
  SHEET_NAME:    '',          // '' = the active/first sheet tab; or put the tab name
  FROM_NAME:     'Charles Pleasant',
  REPLY_TO:      'charlesp@paragongovsolutions.net',
  BATCH_SIZE:    60,          // emails per run (keep <= ~80 to stay under the 6-min limit)
  DELAY_SECONDS: 4,           // pause between emails (human-like; 3–8 is good)
  DAILY_SAFETY_BUFFER: 10,    // leave this many in your daily quota untouched
  // CAN-SPAM required physical postal address (appended to every email):
  POSTAL_ADDRESS: 'Paragon Government Solutions LLC · 11166 Fairfax Blvd, Suite 500, Fairfax, VA 22030'
};
// ====================================================

function sendBatch() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = CONFIG.SHEET_NAME ? ss.getSheetByName(CONFIG.SHEET_NAME) : ss.getSheets()[0];
  var range = sheet.getDataRange();
  var data = range.getValues();
  var header = data[0].map(function(h){ return String(h).trim().toLowerCase(); });

  var cEmail = header.indexOf('email');
  var cSubj  = header.indexOf('subject');
  var cBody  = header.indexOf('body');
  if (cEmail < 0 || cSubj < 0 || cBody < 0) {
    throw new Error('Header must include Email, Subject, Body. Found: ' + header.join(', '));
  }

  // Ensure Status / SentAt columns exist
  var cStatus = header.indexOf('status');
  var cSent   = header.indexOf('sentat');
  if (cStatus < 0) { cStatus = header.length; sheet.getRange(1, cStatus+1).setValue('Status'); }
  if (cSent < 0)   { cSent = (cStatus===header.length ? cStatus+1 : header.length);
                     sheet.getRange(1, cSent+1).setValue('SentAt'); }

  var remainingQuota = MailApp.getRemainingDailyQuota() - CONFIG.DAILY_SAFETY_BUFFER;
  if (remainingQuota <= 0) { Logger.log('Daily quota exhausted — try again tomorrow.'); return; }

  var sentThisRun = 0;
  for (var i = 1; i < data.length; i++) {
    if (sentThisRun >= CONFIG.BATCH_SIZE) break;
    if (remainingQuota <= 0) { Logger.log('Hit daily quota — stopping.'); break; }

    var status = String(sheet.getRange(i+1, cStatus+1).getValue()).trim();
    if (status === 'Sent') continue;                 // already done

    var to = String(data[i][cEmail]).trim();
    var subject = String(data[i][cSubj]).trim();
    var body = String(data[i][cBody]);
    if (!to || to.indexOf('@') < 0 || !subject || !body) {
      sheet.getRange(i+1, cStatus+1).setValue('Skipped (missing field)');
      continue;
    }

    // Append CAN-SPAM postal address if not already present
    if (body.indexOf('Fairfax') < 0) {
      body = body + '\n\n' + CONFIG.POSTAL_ADDRESS;
    }

    try {
      GmailApp.sendEmail(to, subject, body, {
        name: CONFIG.FROM_NAME,
        replyTo: CONFIG.REPLY_TO
      });
      sheet.getRange(i+1, cStatus+1).setValue('Sent');
      sheet.getRange(i+1, cSent+1).setValue(new Date());
      sentThisRun++;
      remainingQuota--;
      SpreadsheetApp.flush();
      Utilities.sleep(CONFIG.DELAY_SECONDS * 1000);
    } catch (e) {
      sheet.getRange(i+1, cStatus+1).setValue('Error: ' + e.message);
    }
  }
  Logger.log('Run complete. Sent this run: ' + sentThisRun + '. Quota left: ' + MailApp.getRemainingDailyQuota());
}

/** Count how many are left to send. */
function countRemaining() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = CONFIG.SHEET_NAME ? ss.getSheetByName(CONFIG.SHEET_NAME) : ss.getSheets()[0];
  var data = sheet.getDataRange().getValues();
  var header = data[0].map(function(h){ return String(h).trim().toLowerCase(); });
  var cStatus = header.indexOf('status');
  var left = 0, sent = 0;
  for (var i=1;i<data.length;i++){
    var s = cStatus>=0 ? String(data[i][cStatus]).trim() : '';
    if (s === 'Sent') sent++; else left++;
  }
  Logger.log('Sent: ' + sent + ' | Remaining: ' + left + ' | Quota left today: ' + MailApp.getRemainingDailyQuota());
}

/** Run sendBatch automatically every 10 minutes until everything is sent, then stop. */
function installAutoTrigger() {
  removeAutoTrigger();
  ScriptApp.newTrigger('autoRun').timeBased().everyMinutes(10).create();
  Logger.log('Auto-trigger installed: will send every 10 minutes until done.');
}

function removeAutoTrigger() {
  ScriptApp.getProjectTriggers().forEach(function(t){
    if (t.getHandlerFunction() === 'autoRun') ScriptApp.deleteTrigger(t);
  });
}

function autoRun() {
  sendBatch();
  // Auto-stop when nothing left to send
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = CONFIG.SHEET_NAME ? ss.getSheetByName(CONFIG.SHEET_NAME) : ss.getSheets()[0];
  var data = sheet.getDataRange().getValues();
  var header = data[0].map(function(h){ return String(h).trim().toLowerCase(); });
  var cStatus = header.indexOf('status');
  var left = 0;
  for (var i=1;i<data.length;i++){ if (String(data[i][cStatus]).trim() !== 'Sent') left++; }
  if (left === 0) { removeAutoTrigger(); Logger.log('All sent — auto-trigger removed.'); }
}
