# A2 Role-address triage (Workspace Studio flow, built by hand)

Runs as the service user, who is a member of each role group.

- Starter: When I get an email. Filter in step 1, because custom labels
  cannot start a flow.
- Step 1, Decide: continue only if the To or Cc address is one of the mail
  groups with a `label` in directory/groups.yaml.
- Step 2, Ask Gemini: "Classify this message as exactly one of: sales_lead,
  nda_request, privacy_request, supplier_invoice, security_report,
  support_request, other. Then extract: sender name, company, what they ask
  for. Return three lines: class, company, summary."
- Step 3, Call the cockpit step `Log inbound message` (custom Apps Script
  step, engine/cockpit/studio/logInbound.js) with class, company, summary,
  thread id. It writes Leads, PrivacyRequests or a DRAFT Documents row with
  source `assistant`, using suggested_* columns only for AI text.
- Step 4, Draft a reply (do not send) from the role address, using the
  acknowledgement wording for that class.

Rules: the flow never sends. A DRAFT document row needs a sender's
confirmation in the cockpit before anything else happens.

Acceptance: ten test messages across five classes are logged with the right
class; no reply is sent.
