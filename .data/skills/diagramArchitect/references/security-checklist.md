# Diagram Security & Confidentiality Checklist

Diagrams leak architecture as effectively as code does, and they are shared more widely. Run this before committing, publishing, or rendering externally.

## Critical

- [ ] **No secrets in labels/notes** — tokens, passwords, API keys, connection strings (`postgres://user:pass@…`), private keys. *Why*: diagram sources are committed and rendered into images that outlive rotation. **OWASP A02 (Cryptographic Failures) / A07 (Identification & Auth Failures)** — credentials exposure.
  - Grep: `(password|passwd|secret|token|api[_-]?key|BEGIN .*PRIVATE KEY|://[^/ ]+:[^@ ]+@)`

## High

- [ ] **No public render servers for confidential diagrams** — public PlantUML server (`plantuml.com/plantuml/...`), public Kroki (`kroki.io`), Mermaid Live share links all **encode the full diagram source into the URL**. *Why*: the URL is logged by the server, proxies, and browser history. Use local `mmdc`, local PlantUML jar/Docker, or a self-hosted Kroki. **OWASP A01 (Broken Access Control)** — information disclosure.
- [ ] **Mermaid `securityLevel` stays `strict`** on any site that renders untrusted or user-contributed diagram content. `loose` enables HTML labels and JS click callbacks → stored XSS. **OWASP A03 (Injection)**. `antiscript` is a partial mitigation only; `sandbox` renders in an iframe.
- [ ] **No `click … call jsFunction()`** callbacks in committed diagrams — they require `loose`.

## Medium

- [ ] **PlantUML includes are repo-local** — no `!includeurl` or `!include https://…`. *Why*: remote includes execute third-party content at render time and change without review. Vendor C4-PlantUML and style files. **OWASP A08 (Software & Data Integrity Failures)**.
- [ ] **No internal hostnames, IPs, account/tenant IDs, bucket names, or customer names** in diagrams published outside the team. Use logical names (`Orders DB`, `Payment Gateway`). **OWASP A05 (Security Misconfiguration)** — reconnaissance aid.
- [ ] **Generator commands never embed DSNs** — pass via env var; never commit generated output that includes connection details.
- [ ] **Mermaid `%%{init}%%` does not override `securityLevel`** — per-diagram init can loosen site policy in some renderers; set `secure` config keys site-wide.

## Low

- [ ] **Audience confirmed** before publishing architecture diagrams revealing unannounced components in public repos.
- [ ] **PII-free examples** — sample data in sequence notes uses synthetic values (`user@example.com`).
- [ ] **Rendered images stripped of metadata** when exported from draw.io/Excalidraw (embedded source may contain hidden layers/notes).

## Per-Component Quick Check

| Component                   | Check                                                         | Severity |
| --------------------------- | ------------------------------------------------------------- | -------- |
| Sequence notes / messages   | No real tokens in example headers (`Authorization: Bearer <token>`) | Critical |
| Deployment / C4 diagrams    | Logical names only, no IPs/hostnames                           | Medium   |
| Docs site Mermaid config    | `securityLevel: strict`                                        | High     |
| PlantUML files              | Only local `!include`                                          | Medium   |
| Render step in CI           | Local CLI / self-hosted renderer                               | High     |
| draw.io files               | No hidden layers with sensitive notes                          | Low      |
