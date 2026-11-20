# Company-in-a-Box Specification v1.0

Status: build-ready for tracks T0 to T3. Tracks T5 to T7 start only after
spikes S-01 to S-03 pass. This file governs. Where an earlier design
document differs, this file is correct.

## 1. Purpose

A repository that stands up a company's operating system on Google
Workspace: mail, records, legal documents, people and approvals, sales and
campaign tracking, policies and compliance evidence. Claude Code executes
the tasks in `tasks/`. The first deployment is described by `company.yaml`
and `content/`. No other path contains a company-specific value.

### In scope

- Tenant configuration: users, groups, DNS, shared drives, security baseline.
- Cockpit: one Apps Script web application over one register workbook.
- Legal documents in three domains: company, partner, notices and records.
- Template intake, bracket binding, company data, document refresh.
- Sending, approval, signature tracking, executed-copy filing, packages.
- People, roles, approval rules.
- Sales orders, campaigns, leads, meeting filing.
- Policy set, controls, evidence collection, recurring control tasks.
- Onboarding dashboard.
- Five Gemini assistants.

### Out of scope for v1

- Any hosted application or database server.
- Automated signature requests. Google eSignature has no API. The sender
  clicks once to request signature.
- Calling Gemini from code. It is billed through Google Cloud, outside the
  subscription.
- Accounting, payroll, banking.
- More than one company per deployment.

## 2. Design rules

Every task must meet these. A task that cannot states the exception.

| ID | Rule | Test |
| --- | --- | --- |
| R1 | Domain-agnostic | No company name, domain, address or person outside `company.yaml`, `directory/`, `drive/`, `content/`. `box check-literals` passes. |
| R2 | Google-native | Every runtime component is in the Workspace subscription or free from Google. Outside systems attach only at the two connection points (section 10). |
| R3 | Configuration over code | A new group, drive, role, document type, package, policy or control is a data change. |
| R4 | Repeatable | Every script can run twice with the same result. |
| R5 | Manual steps are declared | A step with no API is a checklist item with an expected value and an evidence file. |
| R6 | Evidence by default | Each apply writes what it did to the Admin drive and the `Setup` tab. |
| R7 | One register | All records are in one workbook. All reads and writes go through `engine/cockpit/data.js`. |
| R8 | Least access | Access is granted to groups. Scripts request only listed scopes. |
| R9 | AI proposes | No AI step sends, approves, signs, changes a role or publishes. AI output is written only to columns named `suggested_*`. |
| R10 | Events are append-only | Every state change writes one `Events` row. Rows are never edited or deleted. |

## 3. Platform decisions

| Item | Decision |
| --- | --- |
| Edition | Google Workspace Business Plus, one edition for all users |
| DNS | Cloudflare, managed by Terraform |
| Declarative tooling | Terraform >= 1.9 with `cloudflare` and `google` providers. The archived `googleworkspace` provider is not used. |
| Scripted tooling | GAM7 and Admin SDK calls from the `box` CLI |
| CLI | `box`, Python 3.12, Typer, in `engine/cli/` |
| Cockpit | Apps Script, V8 runtime, JavaScript with JSDoc, HTML Service front end, deployed with `clasp` |
| Cockpit identity | Web app executes as the service user; access limited to the domain |
| Data store | One Google Sheets workbook, `Register`, in `90 Admin` |
| Signature | Google eSignature behind `engine/cockpit/signature/` with two functions: `request(doc)` and `status(doc)` |
| Assistants | Workspace Studio flows, Gems, NotebookLM; configuration stored as text in `assistants/` |
| Pipeline | GitHub Actions; workload identity federation to Google; no stored keys |
| Tests | `pytest` for the CLI; Node test runner for pure cockpit modules; task exit checks for the rest |

## 4. Repository layout

```
company.yaml              the deployment's values
schema/                   JSON schema for company.yaml
directory/                users.yaml, groups.yaml, send-as.yaml
drive/                    shared-drives.yaml, folders/, labels.yaml
content/                  company-specific content
  legal-pack/             catalogue.yaml, packages.yaml, dictionary.yaml,
                          brackets.csv
  policies/               policy text, rendered from defaults on first run
  authority-matrix.yaml
  retention.yaml
defaults/                 generic starting set: groups, drives, roles,
                          policies index, controls, retention
engine/
  cli/                    box CLI
  terraform/              dns/, gcp/, groups/
  register/schema.yaml    workbook tabs and columns
  cockpit/                Apps Script sources
assistants/               flow, Gem and notebook configurations as text
runbooks/                 manual checklists, generated from configuration
expected-state/           values the drift checks compare against
tasks/                    one file per task
spikes/                   test tasks that gate T5 to T7
docs/SPEC.md              this file
CLAUDE.md                 working instructions for Claude Code
```

## 5. Tracks

| Track | Delivers | Priority | Size | Depends on |
| --- | --- | --- | --- | --- |
| T0 Foundation | Repository, configuration validation, status store, Google Cloud admin project, pipeline | P0 | S | none |
| T1 Tenant and identity | Users, organisational units, groups, send-as, security baseline, limited admin role | P0 | M | T0 |
| T2 DNS and mail | Records, MTA-STS, probe test, DMARC staging | P0 | S | T1 |
| T3 Drive and records | Shared drives, folders, label, register workbook, retention checklist | P0 | M | T1 |
| T4 Cockpit core | Web app shell, data access, authorisation, home, inbound endpoint | P0 | M | T3 |
| T5 People and approvals | People and roles, approval rules, delegation | P0 | M | T4, S-03 |
| T6 Templates and company data | Intake, brackets, bindings, dictionary, render, refresh | P0 | L | T4, S-01 |
| T7 Documents | Send, approve, sign, file, packages, notices and records, reminders | P0 | L | T5, T6, S-02 |
| T8 Onboarding dashboard | Setup steps, views, weekly checks, joiner checklists | P0 | M | T4 |
| T9 Sales and campaigns | Quotations, orders, campaigns, leads, meeting filing | P1 | M | T7 |
| T10 Policies | Policy rendering, publication, acknowledgement | P1 | M | T3 |
| T11 Compliance | Controls, evidence collectors, recurring tasks, inventories | P1 | L | T1, T10 |
| T12 Assistants | Five Gemini assistants | P1 | M | T7, T9 |
| T13 Product packaging | Second-company dry run, installer guide | P2 | M | all |

Size is in Claude Code sessions: S one, M two to four, L five or more.

Mapping from the design document's track numbers: old T4 is now T4 to T7;
old T5 is T9; old T6 is T10; old T7 is T11; old T8 is unchanged; old T9 is
T13; old T10 is T12.

## 6. Identity model

- Paid users: the founder and the service user. Others are added through the cockpit.
- Administrator accounts: two, on Cloud Identity Free, no mailbox, security key only.
- Organisational units: `/People`, `/Service`, `/Admins`.
- Every role address is a group. Aliases are for personal name variants only.
- Three kinds of group, all defined in `directory/groups.yaml`:
  - `mail`: receives mail, has an archive.
  - `access`: prefix `grp-`, grants drive access, receives no mail.
  - `role`: prefix `role-`, grants a cockpit role, receives no mail.
- The repository owns which groups exist and their settings. The cockpit
  owns membership of `role` groups. Drift checks ignore role membership.
- The service user holds a custom admin role limited to user and group
  management.

## 7. Legal document model

### Domains

| Domain | Counterparty | Stored in | Default classification |
| --- | --- | --- | --- |
| `company` | Founders, directors, staff, advisers | `00 Corporate`, `70 People` | Restricted |
| `partner` | Customers, resellers, suppliers | `10 Legal` by counterparty | Confidential |
| `notice` | None | `10 Legal/07 Notices and records` | Internal or Public |

### Classes

| Class | Handling |
| --- | --- |
| `signed` | Sent from the cockpit and tracked to execution |
| `attached` | Sent only as part of a package; no signature of its own |
| `published` | Posted to a website or trust centre; tracked by version, publication date, review date |
| `record` | Held internally; tracked by owner and review date |

The catalogue for the first deployment is `content/legal-pack/catalogue.yaml`.

### Reference numbers

Each template carries its own reference pattern, read from its header block
at intake, for example `PS-NDA-[____]`. The cockpit issues the next number
per pattern. Bracketed year tokens resolve to the current year. No other
prefix scheme exists.

### Brackets

Square brackets are the only markers. Double-brace fields are not used.
The first deployment's pack has 358 bracket occurrences, listed with a
suggested kind in `content/legal-pack/brackets.csv`. Each occurrence has
one kind:

| Kind | Meaning | Treatment |
| --- | --- | --- |
| `deal` | Differs per counterparty | A form field |
| `constant` | The company's own detail | Filled from the dictionary; never on the form |
| `choice` | One of several drafted alternatives | A choice field; unchosen text is removed |
| `note` | A drafting instruction | An open item in the dictionary; blocks sending until confirmed |
| `reference` | Part of the document's reference number | Filled by the cockpit's numbering |

A binding ties one bracket occurrence, identified by template, bracket text
and occurrence index with surrounding context, to a dictionary key or a
deal field. Binding is by occurrence, never by text alone.

### Template states

`NEEDS_REVIEW`, `ACTIVE`, `SUPERSEDED`, `RETIRED`.

A template can be activated when every bracket is bound. A document can be
sent from it only when every `constant` and `note` it uses is `CONFIRMED`.

### Document states

`DRAFT`, `IN_REVIEW`, `READY`, `SENT`, `EXECUTED`, `DECLINED`, `EXPIRED`,
`VOIDED`, `EXTERNAL_PAPER`.

Allowed transitions:

```
DRAFT -> IN_REVIEW -> READY -> SENT -> EXECUTED
DRAFT -> READY                      (no approval rule matches)
IN_REVIEW -> DRAFT                  (approver returns it)
SENT -> DECLINED | EXPIRED | VOIDED
DRAFT | IN_REVIEW | READY -> VOIDED
EXTERNAL_PAPER -> IN_REVIEW -> READY -> SENT -> EXECUTED
```

Google eSignature reports no intermediate states to code, so `VIEWED` and
partial signature are not tracked.

### Sensitive fields

A field marked `never_store: true` in the catalogue is neither stored nor
merged. The signer completes it by hand. The first deployment has one: the
taxpayer number on the 83(b) election.

## 8. Company data and refresh

- The dictionary holds every `constant` and `note`: key, label, kind,
  value per language, status (`EMPTY`, `PROVISIONAL`, `CONFIRMED`), owner.
- `company.yaml > data` seeds the dictionary on first run. After that the
  cockpit owns the values and exports them nightly.
- A master template never contains a typed-in company value.
- Changing a value shows the affected templates before saving.
- `signed` and `attached` templates take the new value at the next send.
- `published` and `record` documents are re-rendered as a new version and
  queued for approval.
- An executed document never changes. A document in `SENT` is flagged when
  a value it used changes.
- A wording change is a new template version through intake. A data change
  is a dictionary update.
- A later pack carries bindings forward where bracket text and context are
  unchanged. The cockpit can export the full set rendered with current data.

## 9. People, roles and approvals

Roles are `role` groups. Defaults are in `defaults/roles.yaml`.

| Role | May |
| --- | --- |
| `owner` | Change people, roles, approval rules, company data |
| `legal-approver` | Release partner documents held for approval |
| `company-legal-admin` | See, send and approve company documents |
| `signer` | Request signature for the company |
| `sender` | Create and send documents from active templates |
| `finance-approver` | Release order forms outside the price book |
| `control-owner` | Complete assigned compliance tasks |

Approval rule fields: scope (domain, document code or template), condition
(`always`, `external_paper`, `value_above`), approver role, optional second
approver role, fallback role and days. The most specific matching rule
applies. If none matches, the domain default applies.

Safeguards:

- A sender cannot approve their own document while another holder of the
  approver role exists. Otherwise the self-approval is recorded on the
  document.
- Role and rule changes are checked on the server against `owner`.
- A delegate acts for a dated period under their own name.
- Removing a person reassigns open approvals to the fallback role.

## 10. Connection points

| Direction | Mechanism | Used for |
| --- | --- | --- |
| Inbound | `doPost` on the cockpit web app; JSON body; shared secret in script properties | Leads from website forms; sale events from the order system; document requests |
| Outbound | `UrlFetchApp` from execution actions | Order system on execution of an order form |

Inbound message types: `lead.create`, `order.announce`, `document.request`.
Each is validated against a JSON schema in `engine/cockpit/inbound/`.

## 11. Cockpit screens

Home, My queue, Send, Documents, Templates, Company data, Counterparties,
Packages, Notices and records, People and roles, Approval rules, Orders,
Campaigns, Setup, Compliance.

Visibility: `company` domain items are returned only to
`company-legal-admin` and `owner`. All checks are server-side.

## 12. Onboarding dashboard

Each setup step is a `Setup` row: step id, track, title, kind (`automated`,
`manual`, `input`), status (`NOT_STARTED`, `WAITING_ON_INPUT`,
`IN_PROGRESS`, `DONE`, `FAILED`, `DRIFTED`), owner, check, last checked,
evidence link, blocks.

- Before the cockpit exists, status is held in `setup-status.json` and
  printed by `box status`. The cockpit imports it on first run.
- A manual step cannot be marked done without evidence.
- Checks re-run weekly. A passed step that fails becomes `DRIFTED`.
- Stages: details entered, tenant secured, mail live, records ready, legal
  ready, policies approved, compliance running.

## 13. Sales and campaigns

- Quotation: a `signed`-class template in the catalogue when one is
  supplied; until then quotations use the order form. Outbound mail whose
  subject starts with a bracketed register number is blind-copied to the
  quotes group by a Gmail compliance rule (manual step).
- Orders: the order system is the system of record for licences.
  `order.announce` creates an order-form document. Execution calls the
  order system and stores the returned identifier.
- Campaigns: registered before running; each has a tracking code. Website
  forms pass the code in `lead.create`.
- Meetings: a nightly job moves notes and recordings from the host's Drive
  to the account folder and writes a `Meetings` row.

## 14. Policies and compliance

- Policies are Markdown templates in `defaults/policies/`, rendered with
  company values into `content/policies/`. Index: `defaults/policies.yaml`.
- A policy change and its enforcing setting are made in one pull request.
- `Controls` maps each control to a criteria reference, owner, frequency
  and evidence source. `Evidence` holds one row per artefact.
- Collectors: monthly user and 2-Step status, admin role holders, group
  membership, drive permissions, allowed apps; weekly audit log export,
  drift report, mail authentication status.
- `ControlTasks` raises recurring tasks on their due date. A task closes
  only with its output attached.
- Frameworks are data: `Controls.mappings` holds one entry per framework.

## 15. Assistants

| ID | Assistant | Mechanism | Accepted when |
| --- | --- | --- | --- |
| A1 | Morning brief | Studio flow, scheduled | Arrives each working day; register items match Home |
| A2 | Role-address triage | Studio flow on incoming mail | Ten test messages in five classes logged correctly; nothing sent without a person |
| A3 | Meeting to record | Studio flow on transcript | Meeting row and draft follow-up exist within one hour |
| A4 | Contract comparison | Shared Gem over templates and playbook | Every planted change in three sample NDAs is listed |
| A5 | Company answers | NotebookLM over Legal and Compliance drives | Twenty test questions return the correct source; a question with no source gets no answer |

Flows are built by hand in the Studio editor. Their configuration is kept
in `assistants/` so they can be rebuilt. Each is a `manual` setup step.

## 16. Spikes

| ID | Question | Gates |
| --- | --- | --- |
| S-01 | Do the pack's Word files convert to Google Docs with tables intact, and can each bracket occurrence be located and replaced? | T6 |
| S-02 | How can completion of a Google eSignature request be detected by script? | T7-04 |
| S-03 | Can the service user create users and manage groups from Apps Script with a custom admin role? | T5-01 |
| S-04 | Which console settings does the Cloud Identity Policy API return, and what are the Apps Script quotas against expected volumes? | T1-05, T8-03 |

A spike ends with a written finding in `spikes/findings/` and, if the
answer is no, a proposed change to this specification. Claude Code stops
and reports when a spike fails.

## 17. Open inputs

Listed in `content/inputs-required.md`. None blocks T0 to T4.
