# TetraGen Cyber Risk Assessment Report

**Assessment date:** 2 November 2026  
**Assessment type:** Static source-code and design review  
**Repository:** https://github.com/pratyayc19/AI-virtual-dev-pod

> Advisory assessment of an undeployed local prototype. This is not a penetration-test certificate, legal opinion, compliance attestation, or assurance that the system is secure. Findings should be revalidated against the current repository before remediation or external distribution.

Cyber Risk
Assessment Report
Repository: github.com/pratyayc19/AI-virtual-dev-pod
Assessment date: 2 November 2026 | Assessment type: Static source-code and design review
ASSESSMENT BASIS
Static source-code and design review of an undeployed local prototype
This report is an advisory assessment based on the source material reviewed. It is not a penetration-test certificate, legal opinion, compliance attestation, or assurance that the system is secure. Findings should be revalidated against the current repository before remediation or external distribution.
1. Executive Summary
2. Assessment Scope and Methodology
3. System Architecture and Data Flow
4. Asset Inventory and CIA Assessment
5. STRIDE Threat Model
6. Cyber Risk Assessment and Risk Register
7. Risk Treatment Plan
8. NIST CSF 2.0 Mapping
9. Prioritised Remediation Roadmap
10. Existing Positive Controls
11. Assumptions, Limitations and Conclusion
## 1. Executive Summary
Purpose: This report consolidates seven investigations of TetraGen, an undeployed local prototype that uses a sequential multi-agent generative-AI workflow to transform uploaded business requirements into project briefs, user stories, designs, source code and AI-generated test reports.
Overall conclusion: The prototype demonstrates a useful multi-agent workflow and several positive baseline practices, but it is not ready to process sensitive client information or be treated as a production-grade development system without remediation. The most significant concern is that raw RFI text is sent to the external Groq inference service before the current post-execution PII redaction runs.
Highest-priority risks: The leading risks are pre-inference transmission of unscrubbed personal information (RSK-01, High), insecure AI-generated code without security validation (RSK-02, Medium), regex guardrail evasion (RSK-03, Medium), indirect prompt injection through uploaded RFI documents (RSK-04, Medium), and technical credential ingestion into prompts and in-memory storage (RSK-05, Medium).
Important operational boundary: The agents do not have registered shell, Python, filesystem or network execution tools. The application does not execute generated code or tests. Downstream code-execution risk arises if a person downloads generated code and runs it outside the application.
Assessment status: The seven investigations are complete. The proposed controls and target residual risk scores in this report are recommendations and illustrative estimates; they are not evidence that remediation has been implemented or tested.
### 1.1 Overall Risk Position
The risk counts reflect the inherent/current risk scores in the consolidated register. They are not a statement that the prototype has suffered a breach.
### 1.2 Executive Priorities
Prevent sensitive RFI content from being sent to Groq before redaction.
Add security scanning and a clear warning/download gate for generated code.
Separate untrusted document content from agent instructions and test prompt-injection resistance.
Detect common technical secrets before prompts, memory indexing and logs.
Make synthetic QA status explicit; do not represent generated test narratives as executed tests.
## 2. Assessment Scope and Methodology
### 2.1 Scope
Included: static review of the repository structure, active Streamlit UI path, CrewAI orchestrator, agent/task definitions, responsible-AI guardrails, ChromaDB wrapper, environment configuration, dependency manifest, README claims, and related local configuration evidence.
Included: architecture and data-flow review; asset inventory and CIA assessment; STRIDE-oriented threat modelling; risk scoring; review of secrets handling, privacy, logging, AI-agent boundaries, generated-code handling and control recommendations.
Excluded: penetration testing, exploitation, dynamic application testing, source-to-binary verification, live infrastructure/cloud configuration review, network testing, host workstation hardening, production deployment review, vendor assurance review, and formal legal/compliance certification.
Deployment context: local, undeployed prototype; Groq cloud inference over HTTPS; in-memory ChromaDB; no established production identity, access-management, tenant-isolation or operational recovery model.
### 2.2 Method
Architecture and code-path review of the active Streamlit-to-CrewAI pipeline.
Secrets and configuration review, including `.env`, `.gitignore`, environment-variable loading and Git history checks.
AI-agent security review, including tool permissions, delegation, prompt construction, output handling and memory use.
Privacy and information-lifecycle review of uploaded documents, model-bound data, memory, logs and UI output.
Asset inventory with qualitative Confidentiality, Integrity and Availability ratings.
STRIDE threat modelling and OWASP LLM Top 10 (2025) contextual references where applicable.
Risk scoring using Likelihood × Impact on a 1–5 scale, followed by proposed treatment and illustrative target residual scores.
### 2.3 Risk Scoring
Risk scores are qualitative judgements based on the prototype context, not statistical probabilities. Inherent/current scores describe exposure before the proposed treatments. Residual scores are illustrative targets assuming the proposed controls are implemented effectively and verified.
## 3. System Architecture and Data Flow
### 3.1 Architecture Components
### 3.2 Active Request Lifecycle
User uploads PDF/DOCX → Streamlit extracts raw text → session state stores the extracted text.
User starts the pipeline → worker invokes `run_pipeline()` → input regex checks run.
Raw requirement text is interpolated into agent task prompts → prompts and intermediate context are sent to Groq over HTTPS.
Six agents run sequentially; the Testing Agent produces textual/synthetic test results and the Critic evaluates the generated outputs.
Output handling applies PII redaction after `crew.kickoff()`; code output uses an `is_code=True` path that bypasses the general output guardrail filter.
Requirement, brief and code artifacts are saved in the in-memory ChromaDB collection; the UI renders outputs and offers downloads.
### 3.3 Trust Boundaries
### 3.4 Architecture Clarifications
The active workflow is orchestrated by `agents/project_lead.py`; standalone agent scripts are not the active Streamlit execution path.
The active model integration is Groq via LangChain `ChatGroq`. The `cloud/bedrock_client.py` module is unreferenced and is not an AWS Bedrock integration.
The S3 handler exists in the repository but is not invoked by the active workflow; therefore S3 persistence and its encryption code are not active controls.
ChromaDB is in-memory. The active pipeline queries it, but the retrieved content is not injected into the active prompts. A separate standalone BA prototype has different retrieval behaviour.
The Testing Agent produces textual test reports; it does not execute tests. Generated source code is downloaded by the user and is not executed by the application.
## 4. Asset Inventory and CIA Assessment
CIA ratings represent the relative importance of confidentiality, integrity and availability for each asset in this prototype context. They are not vulnerability severity scores. Inactive components are marked not rated for current operational exposure.
### 4.1 CIA Rating Guide
The API key, uploaded RFI documents, Groq inference service, generated artifacts and orchestrator are among the most important active assets. Asset criticality should be revisited if the prototype becomes multi-user, persistent or production-hosted.
## 5. STRIDE Threat Model
STRIDE is used to organise threat scenarios across Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service and Elevation of Privilege. The table records design-level scenarios; it does not claim that attacks were executed.
### 5.1 AI-Specific Threat Context
## 6. Cyber Risk Assessment and Risk Register
The following register consolidates the 11 validated risks. Risk statements are framed around the confirmed weakness and a plausible consequence. A plausible threat scenario is not treated as proof of exploitation.
### 6.1 Risk Heat Map (Inherent Risk)
The heat map uses likelihood on the horizontal axis and impact on the vertical axis. The numeric risk register is authoritative. Coordinates: RSK-01 (L4,I4); RSK-02/04/05 (L3,I4); RSK-03/06 (L4,I3); RSK-07/10 (L3,I3); RSK-08 (L4,I2); RSK-09 (L5,I2); RSK-11 (L5,I1).
### 6.2 Detailed Risk Narratives
#### RSK-01 — Pre-inference transmission of unscrubbed personal information
Observed weakness: Raw document text is inserted into prompts before `redact_pii()` runs after `crew.kickoff()`. Email, phone and card-pattern redaction after inference cannot prevent the original content from reaching Groq.
Primary impact / assets: Confidentiality; AST-01, AST-02, AST-10.
Treatment: CTL-01: move structured PII scrubbing to the ingestion stage before `run_pipeline()` and before prompt construction. Expand coverage carefully and include tests for false positives/negatives. Do not assume regex detects trade secrets or all personal data.
#### RSK-02 — AI-generated code without security validation
Observed weakness: Developer output uses `safe_output(..., is_code=True)`, bypassing the general `apply_guardrails()` path. Code is rendered and downloadable without SAST. The application itself does not execute the code.
Primary impact / assets: Integrity and confidentiality; AST-03, AST-04.
Treatment: CTL-02: run Bandit or equivalent SAST against generated Python code, present findings, and conditionally restrict download for high-confidence critical findings. SAST is a detector, not proof of safety.
#### RSK-03 — Regex guardrail evasion
Observed weakness: Input checks rely on a small set of literal regex patterns. Paraphrasing, synonyms, obfuscation and context-dependent intent can evade syntactic matching.
Primary impact / assets: Integrity; AST-02, AST-06.
Treatment: CTL-03: expand tests and patterns for common cases, document the syntactic limitation, and evaluate a semantic moderation/classification layer as a future enhancement.
#### RSK-04 — Indirect prompt injection through RFI documents
Observed weakness: Extracted document text is interpolated into task prompts without robust separation between trusted instructions and untrusted document content. A crafted document could influence agent output. A successful hijack was not demonstrated in this static review.
Primary impact / assets: Integrity and confidentiality; AST-01, AST-02, AST-05.
Treatment: CTL-04: place document text in explicit untrusted-data delimiters and instruct agents to treat it as passive content. Test with adversarial documents. Delimiters reduce confusion but are not a complete prompt-injection defence.
#### RSK-05 — Technical credential ingestion
Observed weakness: Current PII patterns do not identify API tokens, private keys, bearer tokens, passwords or database connection strings. Such content in uploaded documents could flow to prompts, UI output and ChromaDB memory.
Primary impact / assets: Confidentiality; AST-01, AST-07, AST-08.
Treatment: CTL-05: add heuristic secret detection for common token formats, private-key headers and connection URIs before prompt transmission, memory indexing and logging. Use a dedicated secret scanner where feasible; pattern coverage remains incomplete.
#### RSK-06 — Synthetic QA over-reliance
Observed weakness: The Testing Agent generates textual test cases/results; it does not execute tests. The Critic can rely on those synthetic outputs, creating false confidence.
Primary impact / assets: Integrity; AST-03, AST-05.
Treatment: CTL-06: label the Test Report prominently as AI-generated and unexecuted. If live testing is later introduced, run it only in a properly isolated sandbox; do not use host `subprocess` execution for untrusted generated code.
#### RSK-07 — Resource and token exhaustion
Observed weakness: The extraction path lacks explicit content-size limits and repeated pipeline runs can consume external model capacity. A two-iteration feedback limit does not prevent repeated initial runs or multiple sessions.
Primary impact / assets: Availability; AST-01, AST-04, AST-10.
Treatment: CTL-07: set a documented extraction-size ceiling and reject oversized documents with a clear error; add a UI cooldown. A client-side cooldown is not a substitute for server-side rate limiting in multi-user deployments.
#### RSK-08 — Raw exception disclosure
Observed weakness: The UI renders raw exception strings. Such strings may reveal implementation details or request context, although actual credential disclosure was not established.
Primary impact / assets: Confidentiality; AST-04, AST-10.
Treatment: CTL-08: show generic user-facing errors; retain diagnostic tracebacks only in restricted local logs, scrub sensitive headers and define retention/access controls.
#### RSK-09 — Excessive framework verbosity
Observed weakness: `verbose=True` is hardcoded in agents and the Crew instance. This can produce unnecessary execution detail in stdout; exact contents depend on framework behavior and runtime.
Primary impact / assets: Confidentiality; AST-05, AST-08.
Treatment: CTL-09: gate verbosity behind an environment setting, defaulting to false. Avoid shared unauthenticated log destinations and apply retention controls.
#### RSK-10 — Missing API credential startup validation
Observed weakness: The application does not validate the presence/operational validity of `GROQ_API_KEY` before accepting a pipeline run, so failure may occur at the first model call.
Primary impact / assets: Availability; AST-04, AST-09, AST-10.
Treatment: CTL-10: fail fast when the key is missing and optionally provide a low-cost administrative connectivity check. Keep secrets out of the UI and logs.
#### RSK-11 — Third-party font metadata disclosure
Observed weakness: The UI loads fonts from Google Fonts. This sends ordinary browser request metadata such as IP address and User-Agent to the third party; HTTPS protects the connection in transit but does not hide request metadata from the provider.
Primary impact / assets: Confidentiality / privacy; AST-04, AST-11.
Treatment: CTL-11: self-host required font files and remove external font requests where third-party metadata disclosure is not acceptable.
## 7. Risk Treatment Plan
The controls below are recommendations. Their presence in this report does not mean they have been implemented.
### 7.1 Control Design Notes
Pre-inference redaction should occur before the first outbound model request. Post-execution redaction is not a substitute.
Regex-based redaction is heuristic. Consider a layered approach and document what is and is not detected.
Prompt delimiters are a mitigation, not a guarantee. Validate with adversarial test cases and do not rely on a single prompt instruction.
SAST should be treated as a detection aid. Findings need triage; absence of findings does not certify generated code as safe.
Do not execute generated code or tests directly on the developer host. If execution is added, use an ephemeral, isolated sandbox with least privilege and resource limits.
Client-side cooldowns and UI checks are not sufficient rate limiting for a future multi-user service; enforce server-side quotas and access controls.
Diagnostic logs can themselves contain sensitive data. Restrict access, redact secrets, define retention and avoid logging full prompt bodies by default.
## 8. NIST CSF 2.0 Mapping
Mappings below are deliberately conservative. A control may be useful without having a direct CSF subcategory mapping. The mapping is a conceptual alignment to the control's intended outcome, not a claim of compliance or framework certification.
No direct subcategory mapping is asserted for CTL-03, CTL-06, CTL-09 or CTL-11 in this report. CTL-11 reduces third-party metadata disclosure; it does not by itself establish supplier-risk management or improve transport encryption.
### 8.1 Framework Use Limitations
NIST CSF 2.0 is used as a risk-management reference. This mapping does not constitute a CSF Tier assessment, organisational profile, implementation validation or certification. The report does not claim that TetraGen is compliant with NIST or any law or regulation.
## 9. Prioritised Remediation Roadmap
### Phase 1 — Ingestion, privacy and baseline configuration (Days 1–3)
CTL-01 pre-inference PII scrubbing; CTL-05 technical-secret patterns; CTL-07 size ceiling and rejection; CTL-09 verbosity default off; CTL-10 API-key presence validation.
### Phase 2 — Output security and trust separation (Week 1–2)
CTL-02 SAST and download gating; CTL-04 untrusted-document boundaries and adversarial tests; CTL-06 synthetic test disclaimer; CTL-08 sanitised exception handling and protected diagnostics.
### Phase 3 — Further hardening (Week 3 onward)
CTL-03 expanded guardrail tests and evaluation of semantic moderation; CTL-10 optional operational API check; CTL-11 local font hosting. For any future multi-user deployment, add authentication, authorization, tenant isolation, server-side quotas, secure operations and recovery planning.
### 9.1 Suggested Order
First: CTL-01 and CTL-05, because sensitive data and technical credentials can cross the model boundary or enter application memory.
Second: CTL-02 and CTL-04, because generated code and untrusted document instructions can affect downstream outputs.
Third: CTL-06, CTL-07, CTL-08, CTL-09 and CTL-10, to improve reliability, resource control, error handling, logging exposure and configuration readiness.
Fourth: CTL-03 and CTL-11, while planning broader multi-user controls before any deployment.
## 10. Existing Positive Controls
.env is excluded by `.gitignore`; the inspected Git history did not show `.env` as committed.
No hardcoded API key was identified in Python source files during the reviewed scan.
Application credentials are obtained through environment variables rather than embedded directly in agent prompts.
Agents have no registered shell/Python/filesystem/network tools; `allow_delegation=False`.
The application does not execute generated code or run generated tests.
ChromaDB is instantiated in-memory; no active S3 persistence or AWS Bedrock integration was identified in the active pipeline.
## 11. Assumptions, Limitations and Conclusion
Static source-code/design review only. No exploit attempt, penetration test, dynamic test, production deployment test or live cloud configuration assessment was performed.
Groq's actual prompt retention, training use, logging and contractual data handling depend on vendor terms and the specific service arrangement; they cannot be established from this repository.
Host operating-system permissions, full-disk encryption, endpoint protection and local log access controls were not assessed.
Absence of application authentication/RBAC is treated as a deployment-readiness concern for multi-user exposure; it is not evidence that an unauthorised user accessed the local prototype.
Prompt injection and code-generation abuse are assessed as plausible threat scenarios based on design weaknesses; successful exploitation was not demonstrated.
ChromaDB results are not injected into the active pipeline prompt path according to the reviewed implementation. Therefore, cross-user RAG poisoning should not be described as a demonstrated active-pipeline exploit.
Residual scores are qualitative target estimates. They assume proposed controls are implemented effectively and tested; actual residual risk must be reassessed after implementation.
### 11.1 Conclusion
TetraGen is a promising local prototype, but the review identifies material gaps in privacy-by-design, prompt trust separation, generated-code assurance, secret detection, operational logging and resource controls. The most urgent remediation is to prevent raw sensitive information from being sent to the external inference provider before sanitisation. Before any pilot involving genuine client information, the project should implement and verify the priority privacy, secret-handling, prompt-boundary and output-scanning controls. Any move to multi-user or production operation would require a separate assessment covering authentication, authorization, tenant isolation, deployment hardening, vendor governance, monitoring, incident response and recovery.
## Appendix A — Key Terms

### Table 1

| Field | Value |
| --- | --- |
| Project | TetraGen – AI Virtual Development Pod |
| Assessment date | 2 November 2026 |
| Assessment type | Static source-code and design review |
| Operational state | Undeployed local prototype |
| Framework reference | NIST Cybersecurity Framework (CSF) 2.0 |
| Primary method | Architecture review, asset/CIA analysis, STRIDE threat modelling and 5×5 risk scoring |
| Status | Consolidated advisory report; proposed remediation not yet verified as implemented |


### Table 2

| Risk severity | Count | Interpretation |
| --- | --- | --- |
| High | 1 | Requires priority treatment before sensitive-data use. |
| Medium | 9 | Requires planned remediation before pilot or internal deployment. |
| Low | 1 | Basic monitoring and proportionate treatment recommended. |
| Critical | 0 | No risk scored Critical under the adopted qualitative matrix. |


### Table 3

| Score | Likelihood | Impact |
| --- | --- | --- |
| 1 | Very Low | Very Low |
| 2 | Low | Low |
| 3 | Moderate | Moderate |
| 4 | High | High |
| 5 | Very High | Very High |


### Table 4

| Risk score | Band | Treatment expectation |
| --- | --- | --- |
| 1–5 | Low | Accept with basic monitoring and proportionate controls. |
| 6–12 | Medium | Plan remediation before pilot or internal deployment. |
| 13–19 | High | Treat before handling sensitive data. |
| 20–25 | Critical | Immediate treatment / architectural redesign. |


### Table 5

| Layer | Observed implementation |
| --- | --- |
| Presentation / ingestion | Streamlit UI (`ui/streamlit_app.py`) accepts PDF/DOCX uploads, extracts text, stores session state, launches a background worker and renders results. |
| Guardrails | `responsible_ai/guardrails.py` applies narrow regex-based input checks and output PII redaction for email addresses, phone numbers and credit-card-like values. |
| Orchestration | `agents/project_lead.py` coordinates six agents in a sequential CrewAI process: Project Lead, Business Analyst, System Architect/Design, Developer, Testing and Critic. |
| Model service | LangChain `ChatGroq` sends prompts to Groq Cloud using `llama-3.3-70b-versatile`. This is an external trust boundary. |
| Memory | `memory/chroma_store.py` uses an in-memory ChromaDB collection (`dev_artifacts`). The active path queries memory, but retrieved content is not injected into the active pipeline prompts. |
| Output | The application displays and makes generated artifacts available for download. It does not execute generated source code or run the generated tests. |


### Table 6

| Boundary | From → To | Security significance |
| --- | --- | --- |
| TB-1 | User/browser → Streamlit application | Uploaded documents and user-controlled content enter the application. |
| TB-2 | Streamlit / input checks → CrewAI pipeline | Extracted text becomes model instructions/context; trust separation is insufficient. |
| TB-3 | Application → Groq Cloud API | RFI content, prompts, intermediate agent context and generated content cross to an external provider. |
| TB-4 | Application → in-memory ChromaDB | Requirements and generated artifacts are stored in process memory; this is a logical data-access boundary, not a separate network boundary. |


### Table 7

| ID | Asset | Category | State | C | I | A | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AST-01 | Uploaded RFI documents | Information | Active | H | H | M | Client requirements, possible PII and proprietary information. |
| AST-02 | In-flight requirements stream | Information | Active | H | H | M | Raw extracted requirements passed into task prompts. |
| AST-03 | Generated software artifacts | Information | Active | H | H | M | Briefs, designs, source code and synthetic test reports. |
| AST-04 | Streamlit operations center | Application | Active | M | H | H | User interface, session presentation and downloads. |
| AST-05 | CrewAI orchestrator | Application | Active | M | H | H | Controls sequential task flow and context hand-offs. |
| AST-06 | Responsible-AI guardrails | Application | Active | L | H | H | Integrity and availability of input/output checks are important. |
| AST-07 | In-memory ChromaDB | Data | Active | H | M | L | Stores requirement, brief and code content in process memory. |
| AST-08 | Streamlit session state | Data | Active | M | M | L | Contains extracted text and pipeline results. |
| AST-09 | Groq API key | Credential | Active | H | H | H | Authorises model requests; stored locally in `.env`. |
| AST-10 | Groq inference service | Third party | Active | H | H | H | Processes prompts and content; vendor retention terms not established by source review. |
| AST-11 | Google Fonts CDN | Third party | Active | L | L | L | Receives browser request metadata when external fonts load. |
| AST-12 | AWS S3 handler | Cloud / application | Inactive | — | — | — | Code exists but is not invoked by active pipeline. |
| AST-13 | Misnamed Bedrock client | Application | Inactive | — | — | — | Unreferenced module; wrapper uses ChatGroq rather than AWS Bedrock. |
| AST-14 | Repository and dependencies | Development | Active | L | H | M | Source integrity and dependency integrity matter; repository is public. |


### Table 8

| Rating | Meaning |
| --- | --- |
| High | Compromise could materially expose sensitive data, corrupt core outputs or interrupt essential operation. |
| Medium | Compromise has meaningful but bounded impact; workarounds or regeneration may exist. |
| Low | Limited direct impact in the current prototype context. |


### Table 9

| STRIDE category | TetraGen scenario / observation | Recommended treatment |
| --- | --- | --- |
| Spoofing | No application authentication/RBAC was identified in the local prototype review. This is a deployment-readiness gap, not evidence of an existing account compromise. | Introduce authentication and identity controls before multi-user or network exposure. |
| Tampering | Untrusted RFI text can influence agent outputs; generated artifacts are not security-scanned; in-memory artifacts may be contaminated by poor inputs. | Separate instructions from data, validate outputs, and gate memory promotion where retrieval is used. |
| Repudiation | Verbose stdout and ad hoc prints are not a structured, access-controlled audit trail. No formal audit process was established. | Add minimal structured security-event logs with timestamps and run identifiers; avoid logging raw sensitive content. |
| Information Disclosure | Raw RFI content is sent to Groq before redaction; secrets are not detected; raw exceptions and verbose traces may expose details; Google Fonts receives browser metadata. | Pre-inference redaction, secret scanning, generic UI errors, controlled logs, and local font hosting. |
| Denial of Service | No explicit extracted-text ceiling or robust rate limit was identified; repeated runs and large documents can consume API capacity. | Reject oversized documents, apply cooldowns and implement server-side quotas/rate limiting for multi-user use. |
| Elevation of Privilege | Agents have no registered execution tools and delegation is disabled. Generated code can still be dangerous if a human later executes it on a workstation. | Maintain least privilege; never execute generated code on the host; use isolated sandboxing if execution becomes a feature. |


### Table 10

| Area | Observed relevance | Interpretation |
| --- | --- | --- |
| Prompt injection (OWASP LLM01:2025) | Untrusted RFI text is interpolated into prompts; regex checks are narrow. | Confirmed design weakness; successful hijack not demonstrated. |
| Sensitive information disclosure (LLM02:2025) | Raw RFI content goes to Groq before post-execution redaction; technical secrets are not detected. | Outbound transmission is confirmed by code path; downstream misuse or breach is not established. |
| Insecure output handling (LLM05:2025) | Generated code bypasses general output guardrails and is downloadable without SAST. | The application does not execute it; risk depends on downstream human execution. |
| Excessive agency (LLM06:2025) | Agents have no registered execution tools and delegation is disabled. | Do not classify current agents as having arbitrary execution agency. |
| Vector / embedding weaknesses (LLM08:2025) | Chroma stores artifacts, but retrieved results are not injected into the active pipeline prompts. | Avoid claiming an active-pipeline RAG poisoning exploit. |
| Misinformation / overreliance (LLM09:2025) | Testing agent produces synthetic test results without running tests. | Confirmed reliability and reliance weakness. |
| Unbounded consumption (LLM10:2025) | No explicit extracted-text ceiling or robust run rate limit identified. | Plausible resource/token exhaustion scenario. |


### Table 11

| Risk ID | Risk description | L | I | Score | Inherent | Target residual | Residual |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RSK-01 | Pre-inference transmission of unscrubbed personal information | 4 | 4 | 16 | High | 2×3=6 | Medium |
| RSK-02 | AI-generated source code delivered without security validation | 3 | 4 | 12 | Medium | 2×3=6 | Medium |
| RSK-03 | Regex guardrail circumvention through semantic/keyword evasion | 4 | 3 | 12 | Medium | 2×2=4 | Low |
| RSK-04 | Indirect prompt injection via adversarial RFI ingestion | 3 | 4 | 12 | Medium | 2×3=6 | Medium |
| RSK-05 | Technical credential ingestion and memory contamination | 3 | 4 | 12 | Medium | 2×2=4 | Low |
| RSK-06 | Misplaced reliance on synthetic QA test results | 4 | 3 | 12 | Medium | 1×2=2 | Low |
| RSK-07 | Resource/token exhaustion through unbounded ingestion and repeated runs | 3 | 3 | 9 | Medium | 1×2=2 | Low |
| RSK-08 | Infrastructure information disclosure through raw exception rendering | 4 | 2 | 8 | Medium | 1×2=2 | Low |
| RSK-09 | Sensitive console output from excessive framework verbosity | 5 | 2 | 10 | Medium | 1×2=2 | Low |
| RSK-10 | Mid-pipeline failure due to missing API credential validation | 3 | 3 | 9 | Medium | 1×1=1 | Low |
| RSK-11 | Third-party browser metadata disclosure via external font dependencies | 5 | 1 | 5 | Low | 1×1=1 | Low |


### Table 12

| Impact ↓ / Likelihood → | 1 | 2 | 3 | 4 | 5 |
| --- | --- | --- | --- | --- | --- |
| 5 – Very High | — | — | — | — | — |
| 4 – High | — | — | RSK-02/04/05 | RSK-01 | — |
| 3 – Moderate | — | — | RSK-07/10 | RSK-03/06 | — |
| 2 – Low | — | — | — | RSK-08 | RSK-09 |
| 1 – Very Low | — | — | — | — | RSK-11 |


### Table 13

| Control | Control objective | Type | Recommended implementation | NIST alignment |
| --- | --- | --- | --- | --- |
| CTL-01 | Pre-inference PII redaction | Preventive | Move structured PII scrubbing before prompt creation and Groq transmission. | PR.DS-02 (data in transit) |
| CTL-02 | SAST for generated code | Detective + preventive export gate | Bandit/SAST scan; show findings; block download for selected critical findings. | PR.PS-06 (secure software development) |
| CTL-03 | Expanded syntactic guardrail coverage | Preventive | Expand patterns and tests; document that regex is not semantic analysis. | No direct subcategory mapping asserted |
| CTL-04 | Untrusted-document prompt boundaries | Preventive | Delimit document text and instruct agents to treat it as passive data; adversarial test cases. | PR.DS-10 (data in use), conceptual alignment |
| CTL-05 | Technical secret detection | Preventive | Detect/redact common credentials before prompts, Chroma indexing and logs. | PR.DS-01 / PR.DS-02 only where storage/transit protection is actually in scope; current Chroma is volatile in-memory |
| CTL-06 | Synthetic QA transparency notice | Transparency / reliance reduction | Label AI-generated test reports as unexecuted; no claim of test validation. | No direct subcategory mapping asserted |
| CTL-07 | Input-size ceiling and cooldown | Preventive | Reject over-limit documents; add UI cooldown; future server-side rate limits for multi-user use. | PR.IR-04 (resource capacity) |
| CTL-08 | Sanitised errors and protected diagnostics | Preventive + diagnostic | Generic UI errors; restricted logs, scrubbed headers and retention controls. | PR.DS-01 for stored diagnostic logs, if persisted |
| CTL-09 | Environment-gated verbosity | Preventive | Default `TETRAGEN_DEBUG=false`; avoid unnecessary prompt/output logging. | No direct subcategory mapping asserted |
| CTL-10 | API-key startup validation | Preventive | Check key presence at startup; optional operational API check before pipeline run. | PR.PS-01 (configuration management) |
| CTL-11 | Local font hosting | Preventive | Host fonts locally and remove external CDN requests. | No direct subcategory mapping asserted |


### Table 14

| NIST CSF 2.0 subcategory | Official outcome (short form) | Control alignment / caveat |
| --- | --- | --- |
| PR.DS-01 | Data at rest is protected. | CTL-08 only where diagnostic logs are persisted; CTL-05 only if secrets enter a stored data asset. Current ChromaDB is volatile in-memory, so do not describe it as conventional persistent data-at-rest protection. |
| PR.DS-02 | Data in transit is protected. | CTL-01: scrub sensitive data before it is transmitted to Groq. This is data minimisation before transit, not a replacement for HTTPS. |
| PR.DS-10 | Confidentiality, integrity and availability of data-in-use are protected. | CTL-04: prompt boundary handling is conceptually aligned with protecting in-use prompt integrity; delimiters are not a complete defence. |
| PR.PS-01 | Configuration management practices are established and applied. | CTL-10: validate required API configuration before accepting a run. |
| PR.PS-06 | Secure software development practices are integrated and evaluated. | CTL-02: integrate SAST into the generated-code handling workflow. |
| PR.IR-04 | Adequate capacity for technology resources is maintained. | CTL-07: size limits and cooldowns help manage resource consumption. |


### Table 15

| Term | Meaning in this report |
| --- | --- |
| Asset | Information, system component, credential or service that has value and requires protection. |
| CIA | Confidentiality, Integrity and Availability. |
| Inherent risk | Risk before proposed additional treatment. |
| Residual risk | Risk remaining after controls are implemented and operating effectively. |
| SAST | Static Application Security Testing; analysis of source code without executing it. |
| STRIDE | Threat-modelling categories: Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service and Elevation of Privilege. |
| Prompt injection | Untrusted content attempts to influence an LLM to disregard intended instructions or perform an unintended task. |
| Data in use | Data actively processed in memory or by a system component. |
