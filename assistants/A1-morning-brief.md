# A1 Morning brief (Workspace Studio flow, built by hand)

Owner: each person who wants a brief. Runs as that person.

- Starter: On a schedule. Working days at {assistants.brief_time} {assistants.brief_timezone}.
- Step 1, Get rows from Sheets: Register > view `Brief` (written nightly by
  the cockpit job `buildBriefView`: my approvals waiting, documents SENT over
  {unsigned_reminder_days} days, expiries within {expiry_notice_days} days,
  failed jobs, notices pending approval).
- Step 2, Ask Gemini: "Summarise my unread email from the last 24 hours that
  needs an action from me. One line each: sender, what is needed, by when.
  Do not include newsletters or automated alerts."
- Step 3, Ask Gemini: "List today's calendar events with time, title and
  external attendees."
- Step 4, Send me an email (or Notify me in Chat): headings Mail, Cockpit,
  Today. Cockpit section is Step 1's rows unchanged, not summarised.

Acceptance: arrives each working day; every Cockpit line matches the Home
screen at that time.
