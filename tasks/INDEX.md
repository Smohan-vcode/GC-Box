# Task index

In dependency order within each track. Spikes are in `spikes/`.

| ID | Title | Priority | Size | Depends on | Human step |
| --- | --- | --- | --- | --- | --- |
| S-01 | Word to Google Docs conversion and bracket location | P0 | S | T3-01 |  |
| S-02 | Detecting completion of a Google eSignature request | P0 | S | T3-01 | yes |
| S-03 | Creating users and managing groups from Apps Script with a limited admin role | P0 | S | T1-06 |  |
| S-04 | Policy API coverage and Apps Script quotas | P1 | S | T1-01 |  |
| T0-01 | Repository scaffold and configuration validation | P0 | S | none |  |
| T0-02 | Status store and evidence writer | P0 | S | T0-01 |  |
| T0-03 | Google Cloud admin project and pipeline identity | P0 | S | T0-01 | yes |
| T0-04 | Pipeline: validate, plan, apply, weekly drift skeleton | P0 | S | T0-02, T0-03 |  |
| T1-01 | Tenant bootstrap checklist | P0 | S | T0-02 | yes |
| T1-02 | Organisational units and users | P0 | S | T1-01, T0-03 |  |
| T1-03 | Groups, settings, aliases and role groups | P0 | M | T1-02 |  |
| T1-04 | Send-as identities and Gmail filters | P0 | S | T1-03 |  |
| T1-05 | Security baseline verification | P0 | S | T1-01, S-04 |  |
| T1-06 | Limited admin role for the service user | P0 | S | T1-02 | yes |
| T2-01 | DNS records | P0 | S | T1-01, T0-03 | yes |
| T2-02 | MTA-STS policy | P0 | S | T2-01 |  |
| T2-03 | Address probe test | P0 | S | T1-04, T2-01 |  |
| T2-04 | DMARC staging and report summary | P1 | S | T2-03 |  |
| T3-01 | Shared drives and access | P0 | S | T1-03 |  |
| T3-02 | Folder trees | P0 | S | T3-01 |  |
| T3-03 | Classification label | P1 | S | T3-01 |  |
| T3-04 | Register workbook | P0 | M | T3-02 |  |
| T3-05 | Retention checklist | P1 | S | T1-01 |  |
| T4-01 | Apps Script project, deployment and web app shell | P0 | M | T3-04 | yes |
| T4-02 | Data access module and events | P0 | M | T4-01 |  |
| T4-03 | Authorisation | P0 | S | T4-02 |  |
| T4-04 | Home and My queue | P0 | S | T4-03 |  |
| T4-05 | Inbound endpoint | P0 | S | T4-02 |  |
| T5-01 | People and roles | P0 | M | T4-03, S-03 |  |
| T5-02 | Approval rules | P0 | M | T5-01 |  |
| T5-03 | Delegation, leavers and membership export | P1 | S | T5-02 |  |
| T6-01 | Template intake scan | P0 | M | T4-02, S-01 |  |
| T6-02 | Bracket extraction and suggested classification | P0 | M | T6-01 |  |
| T6-03 | Template review and activation | P0 | M | T6-02 |  |
| T6-04 | Company data screen | P0 | M | T6-03 |  |
| T6-05 | Render engine and preview | P0 | M | T6-04 |  |
| T6-06 | Refresh of notices and records; pack export | P1 | M | T6-05 |  |
| T6-07 | Carry-over for new pack versions | P1 | M | T6-03 |  |
| T7-01 | Send form, numbering and drafts | P0 | M | T5-02, T6-05 |  |
| T7-02 | Approval hold and release | P0 | S | T7-01 |  |
| T7-03 | Signature module: manual Google eSignature | P0 | S | T7-02 | yes |
| T7-04 | Completion detection, filing and execution actions | P0 | M | T7-03, S-02 |  |
| T7-05 | Packages | P1 | M | T7-04 |  |
| T7-06 | Notices and records register | P1 | S | T6-06 |  |
| T7-07 | Reminders and expiry | P0 | S | T7-04 |  |
| T7-08 | Counterparties and external paper | P1 | S | T7-01 |  |
| T8-01 | Setup steps in the register | P0 | S | T4-02 |  |
| T8-02 | Setup screen | P0 | S | T8-01 |  |
| T8-03 | Weekly checks and drift | P1 | M | T8-01, T1-05, S-04 |  |
| T8-04 | Joiner and leaver checklists | P1 | S | T5-01 |  |
| T9-01 | Quotations and order forms | P1 | S | T7-04 | yes |
| T9-02 | Order system connection | P1 | M | T9-01, T4-05 | yes |
| T9-03 | Campaigns and leads | P1 | S | T4-05 |  |
| T9-04 | Meeting filing | P1 | S | T7-08 |  |
| T10-01 | Policy templates and rendering | P1 | M | T3-02 |  |
| T10-02 | Publication and acknowledgement | P1 | S | T10-01, T4-03 |  |
| T11-01 | Controls and evidence registers | P1 | S | T3-04, T10-01 |  |
| T11-02 | Evidence collectors | P1 | M | T11-01, T0-04 |  |
| T11-03 | Recurring control tasks | P1 | S | T11-01, T5-01 |  |
| T11-04 | Inventories and system description | P2 | S | T11-01 |  |
| T12-01 | Morning brief | P1 | S | T4-04 | yes |
| T12-02 | Role-address triage | P1 | S | T4-05, T7-01 | yes |
| T12-03 | Meeting to record | P1 | S | T9-04 | yes |
| T12-04 | Contract comparison | P1 | S | T6-03 | yes |
| T12-05 | Company answers | P1 | S | T10-02, T7-06 | yes |
| T13-01 | Second-company dry run | P2 | M | T7-07, T8-02, T10-02 |  |
| T13-02 | Installer guide | P2 | S | T13-01 |  |
