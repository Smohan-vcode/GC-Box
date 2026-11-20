# Inputs required from the owner

None blocks T0 to T4. Each lists the first task it blocks.

| Input | Where it goes | Blocks |
| --- | --- | --- |
| Test tenant domain | `company.yaml > workspace.test_domain` | T1-01 |
| Founder's address local part and name | `directory/users.yaml` | T1-02 |
| Data region decision | `company.yaml > workspace.data_region` | M-07 |
| Registered street address and postcode | Company data | sending any template |
| EU representative name and address | Company data | publishing 4 notices |
| Answers to the 22 drafting notes | Company data (`content/legal-pack/dictionary.yaml > notes`) | sending or publishing the 11 documents concerned |
| Class of PS-SLA, PS-AI, PS-REG: attached or signed | `content/legal-pack/catalogue.yaml` | T6-03 for those codes |
| Package contents | `content/legal-pack/packages.yaml > confirmed` | T7-05 |
| Retention periods confirmed by counsel and accountant | `content/retention.yaml > status` | M-50 |
| Recording consent wording reviewed by counsel | `content/auto-replies/`, Meet setting | M-42 on live |
| Order system base URL and message format | `company.yaml > integrations` | T9-02 |
| Price book or approval threshold for order forms | Approval rules | T9-01 |
