# TetraGen Security Assessment

This folder documents a static cyber-risk assessment of **TetraGen — AI Virtual Development Pod**, an undeployed local prototype that uses a sequential multi-agent GenAI workflow.

## Documents
- [Cyber Risk Assessment — full Markdown report](TetraGen_Cyber_Risk_Assessment.md)

## Assessment scope
The assessment reviewed the active Streamlit-to-CrewAI workflow, model integration, guardrails, ChromaDB usage, secrets handling, information lifecycle, logging, generated-code handling and relevant repository configuration. It included architecture and data-flow analysis, asset/CIA inventory, STRIDE threat modelling, an 11-item risk register, proposed treatments and a conservative NIST CSF 2.0 alignment.

**Important limitation:** this was a static source-code and design review. It was not a penetration test, exploit exercise, production infrastructure review, legal opinion or compliance certification. The project was assessed as a local, undeployed prototype.

## Headline findings
- Raw RFI content is sent to the Groq inference service before the current post-execution PII redaction step.
- Generated source code is downloadable without a SAST security scan; the application does not execute the generated code.
- Uploaded document content is interpolated into agent prompts, creating a prompt-injection design concern.
- Current regex guardrails do not provide semantic detection of malicious instructions or technical secrets.
- The Testing Agent generates textual test reports; it does not execute tests.
- Agents have no registered shell, Python, filesystem or network execution tools, and delegation is disabled.

## Risk register overview
The consolidated register contains 11 risks: 1 High, 9 Medium and 1 Low. Scores are qualitative judgements for this prototype context, not statistical probabilities. Proposed residual scores are illustrative targets, not verified outcomes.

## Use and disclosure
This assessment describes security weaknesses in a public project. Do not treat it as proof of exploitation or a breach. Revalidate each finding against the current code before remediation. Do not add API keys, environment files, real client RFI documents or other secrets to this repository.
