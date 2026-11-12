# INDEX · Project Memory & Architecture Guide
**Agent #3: Enterprise Metadata Tagger & Search Optimization Specialist**

---

## 1. Executive Summary & Live AWS Deployment

| Asset | AWS Endpoint / Identifier |
| :--- | :--- |
| **CloudFront Live URL** | **[`https://d33eb1zoxf1g08.cloudfront.net`](https://d33eb1zoxf1g08.cloudfront.net)** |
| **API Gateway (HTTP API)** | `https://tl1aqbynmf.execute-api.us-east-1.amazonaws.com` |
| **S3 Hosting Bucket** | `s3://index-ui-984625844016` (Protected with Origin Access Control) |
| **AWS Lambda Compute** | `index-backend-api` (Python 3.11, Bedrock Nova Pro Converse API) |
| **IAM Execution Role** | `arn:aws:iam::984625844016:role/index-backend-lambda-role` |
| **Local Project Path** | `c:\Users\ELCOT\OneDrive\Desktop\Agent\index\` |
| **Beginner Study Guide PDF** | `c:\Users\ELCOT\OneDrive\Desktop\Agent\index\INDEX_BEGINNER_STUDY_GUIDE.pdf` |

---

## 2. Core Question & Enterprise Problem Solved

### Core Question:
> *"What is this content, and how should it be described so people and systems can find it?"*

### Problem:
Organizations have thousands of documents with terrible filenames such as:
- `DOC_48383_FINAL_V2.pdf`
- `Document123.docx`
- `Copy_Final_Final2.pdf`

Searching for and governing this unstructured data is notoriously difficult.

### What INDEX Does:
INDEX reads the complete document content and extracts a multi-dimensional metadata profile:
1. **Basic Metadata:** Canonical Title, Document Type, Target Audience, Language, Owner/Department, Version.
2. **Business Taxonomy:** Domain, Subdomain, Process Area, Product/Service, Business Function.
3. **Content Tags:** Core Topic, Subtopics, 6-12 Keywords, Dynamic Hashtags, Conceptual Entities.
4. **Named Entities:** Organizations, Systems/Applications, Products, Roles, Regulations/Standards.
5. **Key Information:** Dates, Deadlines, Monetary Amounts, Compliance Rules, Requirements.
6. **Dynamic Attributes:** Domain-specific adaptation (e.g. AWS tech guide produces *Platform, Architecture, Services, Database*; HR policy produces *Leave Type, Accrual Rate, Approval Window*; Insurance claim produces *Claim Type, Deductible, Settlement SLA*).
7. **Search Optimization & Retrieval Intent:** Standardized recommended filename (e.g., `AWS_Serverless_Architecture_Specification_v2.0.pdf`) and fuzzy mapping for typos and shorthand search terms (e.g., `moter clam settle doc` &rarr; *Motor Claim Settlement Standard Procedure*).

---

## 3. UI Requirements & Bug Prevention Standards (Ported from TAXORA & CLARIA)

1. **Strict Viewport Lockdown (Zero Outer Page Scrolling):**
   - `html, body, #root, .app, .chatPage` are locked with `position: fixed; inset: 0; width: 100%; height: 100%; overflow: hidden !important; overscroll-behavior: none !important;`.
   - The header, composer, and sidebar are 100% stationary and NEVER scroll, wiggle, or leave the viewport.
   - ONLY `.messages` and `.histList` scroll independently with thin 6px custom scrollbars (`overscroll-behavior: contain !important;`).
2. **Hover-Only Edit & Delete in Sidebar:**
   - Action buttons (`[ ✎ ]` rename, `[ 🗑 ]` delete) are set to `opacity: 0` by default.
   - They appear smoothly only when hovering over `.histRow:hover .histActions { opacity: 1; pointer-events: auto; }`.
   - On touch/mobile screens, `.histActions` is automatically visible.
   - Includes inline deletion confirmation state (`"Delete this session?" [Delete] [Cancel]`).
3. **Click-to-Edit Header Title:**
   - Clicking the title directly turns it into an inline editable input.
   - **NO** edit pencil icon next to the title.
4. **Smart Top-Scroll on AI Reply:**
   - Opening/switching sessions resets scroll to `top: 0`.
   - When a new AI reply arrives, the view scrolls smoothly using `el.scrollTo({ top: targetTop, behavior: 'smooth' })`, focusing directly on the **TOP of the AI Result Card** without triggering parent window scroll.
5. **Mobile Drawer Scrim:**
   - Tapping outside the sidebar drawer on mobile smoothly closes the drawer via a backdrop scrim.
6. **Electric Blue & Deep Navy Theme:**
   - `--a1: #078cff` (Electric Blue)
   - `--a2: #0a3154` (Deep Navy)
   - Background: `#020c16`
   - Panels: `#051a2c`
   - Radial dot pattern background.

---

## 4. Security & Guardrails

- **PCI-DSS v4.0 Sanitization:** Masking of credit card numbers, passwords, CVVs, API tokens, and secret keys.
- **Prompt Injection Defense:** Multi-pattern filter blocking jailbreak attempts.
- **Zero Model Disclosure:** Model identifiers (Nova, Bedrock, Anthropic, Claude) are strictly sanitized to `"INDEX AI Engine"`.
- **Traceability:** Badges indicating guardrails passed and zero hallucinated actions.
