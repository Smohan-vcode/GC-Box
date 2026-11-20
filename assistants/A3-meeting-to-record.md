# A3 Meeting to record (Workspace Studio flow, built by hand)

Runs as each meeting host in the sales access group.

- Starter: When a meeting transcript is ready.
- Step 1, Ask Gemini with the transcript: "From this meeting return:
  external company name; attendees; commitments made by us, each with owner
  and date if stated; commitments made by them; next steps. Quote the
  transcript line for each commitment. If none, say none."
- Step 2, Call the cockpit step `Log meeting` (engine/cockpit/studio/
  logMeeting.js): writes a Meetings row; AI text goes to
  suggested_commitments and suggested_next_steps.
- Step 3, Draft an email (do not send) to external attendees: thanks, next
  steps as listed.
- Step 4, Create tasks for our commitments.

Requires: transcription on and consent prompt shown (M-41, M-42).

Acceptance: Meetings row and draft exist within one hour of the meeting's
end; each commitment carries its transcript quote.
