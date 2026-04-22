# Data Governance Framework Design — SwiftPay Case Study

---

## Task 1: Governance Roles Assignment

### Customer Master Data (name, email, phone, address)

**Data Owner:** Product Team / Chief Product Officer (CPO)

**Data Steward:** CRM Analyst within the Product Team

**Justification:**
The Product team defines how customer data is collected, which fields are required, and how it feeds into the user experience. They hold business responsibility for the completeness and accuracy of customer profiles — they know what "correct customer data" actually means in a business context. The CRM Analyst acts as Data Steward because they work with customer records daily and can identify quality issues early.

---

### Transaction Data (amount, timestamp, sender, receiver)

**Data Owner:** Finance Department / Chief Financial Officer (CFO)

**Data Steward:** Data Engineer within the Engineering Team

**Justification:**
Transaction data is a financial record. The Finance department is legally and regulatorily accountable for its accuracy — the CFO signs off on financial statements and is responsible to auditors and regulators (PSD2, AML). The Data Engineer serves as Steward because they maintain the pipelines and database schemas that produce and transform this data.

---

### KYC Documents (ID scans, proof of address)

**Data Owner:** Compliance Team / Chief Compliance Officer (CCO)

**Data Steward:** KYC Analyst within the Compliance Team

**Justification:**
KYC data exists solely because of regulatory requirements (AML, PSD2). The Compliance team understands which documents are valid, how long they must be retained, and when re-verification is needed. They are the ones who answer to regulators in the event of a violation. The KYC Analyst as Steward handles day-to-day document review and quality checks.

---

### Why the Data Owner must come from a business department, not IT

IT is a service function — it knows *how* to store data, but not *why* it exists or what "correct" means in business terms. A Data Owner must understand the business value of data, make decisions about who can access it, what quality standards apply, and how long it should be kept. Without business ownership, data quality rules remain technical suggestions with no priority or budget behind them. For example, IT might define a valid address as "a non-empty string" — but the business knows that for KYC compliance, a valid address must include street, city, postal code, and country. That is a business decision, not a technical one.

---

## Task 2: Data Policies

### Policy 1: Data Quality Standards for Customer Email and Address

**Purpose:**
To ensure that customer contact data is accurate, complete, and consistently formatted across all SwiftPay systems. Reliable contact data is essential for customer communication, fraud detection, and meeting regulatory obligations under PSD2 and AML requirements.

**Scope:**
All customer email addresses and physical addresses stored in the CRM system, the transaction database, and any downstream systems operated by SwiftPay, including data held by third-party processors.

**Rules:**
- Email addresses must pass RFC 5322 syntax validation and be confirmed via a one-time verification link at the point of registration. Re-verification is mandatory every 12 months for active accounts.
- Physical addresses must include: street, city, postal code, and country — all fields are mandatory. Addresses must be standardised against an external address validation service (e.g. Google Address Validation API) within 24 hours of entry or update.
- Duplicate customer records, identified by matching email or identity document number, must be automatically flagged and routed to the responsible Data Steward for review and merging within 5 business days.
- A quarterly data quality audit must be conducted by the Data Steward and results reported to the Data Owner.

**Consequences:**
Teams that use data known to be non-compliant without notifying the Data Steward are responsible for any resulting operational or regulatory consequences. If a quarterly audit finds that more than 5% of records fail to meet the standard, the Data Owner must produce and approve a corrective action plan within 30 days. Repeated failure to meet quality targets will be escalated to the Data Governance Council.

---

### Policy 2: Data Access Control for Sensitive Customer Data

**Purpose:**
To protect customer personal and financial data from unauthorised access, reduce the risk of data breaches, and ensure compliance with GDPR, PSD2, and applicable AML regulations. Access to sensitive data must be controlled, auditable, and granted on a need-to-know basis only.

**Scope:**
All data assets classified as Confidential or Restricted, including: KYC documents, full payment card numbers, transaction history, account balances, and any database table or file containing personally identifiable information (PII). This policy applies to all employees, contractors, and third-party vendors with access to SwiftPay systems.

**Rules:**
- Access is granted on a least-privilege basis: each individual receives only the permissions required to perform their specific role. Broad or standing access to sensitive data is not permitted.
- All requests for access to Restricted data must be submitted through the IAM (Identity and Access Management) system, including a documented business justification, an expiry date not exceeding 90 days, and approval from the relevant Data Owner.
- Full payment card numbers (PAN) must never be stored in plain text. The Data Science team must work exclusively with anonymised or synthetic datasets; direct access to production PII for model training is prohibited.
- All access to Restricted data is logged. Logs are retained for a minimum of 12 months and are available for audit review.
- Access rights must be reviewed every quarter. Any access that is no longer justified must be revoked within 5 business days of the review.

**Consequences:**
Unauthorised access to sensitive data results in immediate account suspension and a formal investigation. Intentional sharing of customer data with unauthorised parties is grounds for contract termination and may result in criminal liability under applicable data protection law. All confirmed breaches must be reported to the relevant supervisory authority within 72 hours as required by GDPR Article 33.

---

## Task 3: Operating Model Recommendation

**Recommended model: Federated (Hybrid)**

For SwiftPay, a federated governance model is the most appropriate choice. A fully centralised model — where a single data governance team controls all standards and decisions — would create a bottleneck and lose domain-specific context that is critical in a regulated fintech environment. A fully decentralised model, on the other hand, would preserve the current situation where each team applies its own standards, maintains its own identifiers, and operates in a silo. The federated model combines centralised standards and policies with decentralised ownership and accountability: each domain retains autonomy over its data while being required to comply with company-wide rules on quality, security, lineage documentation, and access control.

This model directly addresses SwiftPay's problems. The issue of three different customer IDs across systems is solved by a shared Business Glossary and a Master Data Management process governed by the central council. Unclear ownership is resolved by formally assigning Data Owners and Stewards per domain. The Compliance team gains access to centralised lineage documentation they can present to auditors. The Data Science team can subscribe to change notifications for source tables through the shared Data Catalog, eliminating the stale data problem.

**Data Governance Council composition:**
- Chief Data Officer (CDO) — Chair
- Product Team representative — Customer data domain
- CFO / Finance representative — Transaction data domain
- Chief Compliance Officer (CCO) — KYC data domain
- Head of Data Science — Primary data consumer
- Head of Engineering — Technical standards execution

The Council meets quarterly to review and update policies, and operates through Data Stewards on a weekly basis for operational issues.

---

## Task 4: Metrics & KPIs

### KPI 1: Customer Data Completeness Rate

**What it measures:**
The proportion of active customer records in which all mandatory fields (email, phone, address, date of birth, KYC status) are populated and non-null.

**How it is calculated:**
```
(Number of records with no NULL in mandatory fields / Total active customer records) × 100%
```

**Target:** ≥ 98%

**Reporting frequency:** Weekly, via an automated dashboard. Monthly written report from Data Steward to Data Owner.

---

### KPI 2: Data Lineage Coverage

**What it measures:**
The proportion of critical data assets (source tables, transformed datasets, ML model inputs, regulatory reports) for which full end-to-end lineage is documented in the Data Catalog — from the original data source through to the final consumer.

**How it is calculated:**
```
(Number of critical assets with documented lineage / Total number of critical assets) × 100%
```
The list of critical assets is defined by the Compliance team and approved by the Data Governance Council.

**Target:** ≥ 95% for Tier-1 assets (those used in regulatory reporting)

**Reporting frequency:** Monthly. Mandatory review before every regulatory audit.

---

### KPI 3: Access Review Compliance Rate

**What it measures:**
The proportion of active access grants to sensitive data that have undergone their mandatory quarterly review on time, without expiring unreviewed.

**How it is calculated:**
```
(Access grants reviewed within the deadline / Total access grants due for review) × 100%
```

**Target:** 100% — zero tolerance for overdue reviews on Restricted data

**Reporting frequency:** Quarterly. Automated reminders are sent 14 days before the review deadline to responsible Data Owners.

---

## Task 5: Data Catalog Implementation Proposal

### Proposal: Implementing a Data Catalog at SwiftPay

**Background**

SwiftPay currently operates without a unified view of its data landscape. Customer records carry different identifiers in the CRM, the transaction database, and the fraud detection system. No team has a reliable way to trace where a piece of data came from or what transformations it went through. The Compliance team cannot demonstrate data lineage to auditors, and the Data Science team regularly retrains fraud models on stale data because there is no notification mechanism when source tables change. Implementing a Data Catalog — tools such as DataHub, Collibra, or Alation are evaluated options — would serve as the foundational layer of SwiftPay's governance programme.

---

**Two Key Required Features**

**1. Automated End-to-End Data Lineage**

The catalog must automatically capture and visually display the full chain of data movement: from raw ingestion (payment gateway events, KYC provider feeds) through ETL transformations, into analytical tables and ML feature stores, and finally into regulatory reports and dashboards. This lineage must cover both technical lineage (table-to-table via SQL or pipeline code) and business lineage (KYC document → AML risk score → regulatory submission).

This feature directly solves two of SwiftPay's most critical problems. First, the Compliance team will be able to walk auditors through a visual lineage graph showing exactly where any data point originated and every transformation it passed through — satisfying PSD2 and AML audit requirements. Second, the Data Science team can subscribe to lineage-based change alerts: whenever a source table changes its schema or update frequency, the relevant model owners are automatically notified, eliminating the stale data retraining problem that currently costs the team time and reduces model accuracy.

**2. Business Glossary with Data Certification**

The catalog must host a governed Business Glossary that defines canonical business terms ("Customer", "Verified Transaction", "KYC Status") and maps each term to the physical assets — tables, columns, APIs — that represent it across all systems. Certified datasets, formally approved by the responsible Data Owner, must be clearly distinguished from uncertified ones through a visual badge or status indicator.

This feature directly addresses the "no single source of truth" problem. Today, an engineer searching for customer data may find three tables with conflicting definitions of "customer ID." With the Glossary in place, that search returns one certified, canonical definition linked to the authoritative source system. Any team building a new feature or model starts from the same agreed starting point, preventing divergence before it begins.

---

**How the Catalog Solves the Single Source of Truth Problem**

The catalog does not replace existing databases — it creates a navigation and governance layer above them. Each physical data asset is registered with its business owner, quality score, certification status, and lineage graph. The MDM (Master Data Management) process, supported by the Glossary, defines the golden record for customer identity and provides a mapping from legacy identifiers in each system to a single canonical customer key. Any team looking for customer data follows the catalog link to the certified golden record rather than querying whichever system they happen to know about.

---

**Roles Responsible for Catalog Maintenance**

- **Data Stewards (per domain):** Update metadata, descriptions, and quality annotations within their domain. Review and certify assets quarterly. Responsible for keeping the catalog accurate as source systems evolve.
- **Data Engineers:** Configure and maintain automated connectors between the catalog and source systems — database crawlers, dbt model integration, Kafka Schema Registry sync. Ensure technical lineage is captured automatically rather than manually.
- **CDO Office (Central Governance Team):** Owns the Business Glossary governance process, resolves cross-domain terminology conflicts, monitors catalog adoption metrics, and drives company-wide standards.

---

**Anticipated Challenge: Low Adoption by Engineering Teams**

The most common reason data catalog projects fail is that engineers view metadata documentation as bureaucratic overhead with no direct personal benefit. If filling in descriptions and ownership fields is purely manual and mandatory, it will be done poorly or avoided entirely.

To address this, adoption at SwiftPay will be driven by reducing friction and demonstrating immediate value rather than by mandate. Catalog search will be integrated into the IDE and a Slack bot so engineers can find data assets without leaving their workflow. The CI/CD pipeline will include a lightweight automated check: any new table deployed to production without a registered owner and description fails the pipeline gate — making compliance the path of least resistance. Most importantly, the Data Science team will be positioned as the first power-users: their immediate gain from lineage-based change alerts provides a concrete, visible benefit that generates organic advocacy across teams. Adoption will be tracked as a governance KPI — percentage of Tier-1 assets with complete metadata — reviewed monthly for the first six months post-launch, with findings reported to the Data Governance Council.
