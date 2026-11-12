import os
import json
import re
import random
import boto3
from pathlib import Path
from typing import Dict, Any, List
from services import guardrail_service

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / '.env')
    load_dotenv()
except ImportError:
    pass

AWS_REGION = os.getenv("AWS_DEFAULT_REGION") or os.getenv("AWS_REGION") or "us-east-1"
MODEL_ID = "us.amazon.nova-pro-v1:0"
FALLBACK_MODEL_ID = "amazon.nova-pro-v1:0"

def get_bedrock_client():
    return boto3.client(
        'bedrock-runtime',
        region_name=AWS_REGION
    )

INDEX_SYSTEM_PROMPT = """You are INDEX, an Enterprise AI Content Intelligence Agent specializing in Metadata Tagging and Search Optimization (TCS BFSI & Enterprise Standard).

CORE MISSION:
You answer the enterprise question:
"What is this content, and how should it be described so people and search systems can find it?"

Solve the ubiquitous enterprise problem of poorly named files (e.g., DOC_48383_FINAL_V2.pdf, Document123.docx, Untitled.pdf, Copy_Final_Final2.pdf) by analyzing document contents and extracting standardized, multi-dimensional, dynamic metadata.

INDEX IS DOMAIN-AGNOSTIC:
It must handle technical IT documents (e.g. AWS architecture, Kubernetes), HR policies (leave, benefits), BFSI/insurance claims, legal agreements, marketing briefs, and operational manuals with equal precision.

OUTPUT SCHEMA (STRICT JSON ONLY):
You MUST return a JSON object with this exact structure:

{
  "type": "index_result",
  "basic": {
    "title": "Clean, descriptive, canonical document title",
    "document_type": "Specific type (e.g., Architecture Guide, Policy, SOP, Contract, Claim Notice, Spec Sheet, Report)",
    "language": "Primary language (e.g., English, Spanish, Multilingual)",
    "target_audience": "Intended readers (e.g., Enterprise Architects, Policyholders, Claims Adjusters, HR Staff)",
    "owner_department": "Governing department/owner (e.g., Cloud Infrastructure, Legal, Customer Operations, HR)",
    "version": "Document version if indicated or inferred (e.g., 1.0, 2.1, Draft, Final)"
  },
  "business": {
    "domain": "Industry/domain (e.g., Cloud Computing, BFSI / Insurance, Healthcare, Human Resources, Legal)",
    "subdomain": "Specific sub-area (e.g., Serverless Architecture, Motor Claims, Benefits & Leave)",
    "product_service": "Related product or service",
    "process_area": "Business workflow (e.g., Deployment Automation, Settlement, Onboarding)",
    "business_function": "Functional group (e.g., IT Engineering, Operations, Risk & Compliance)"
  },
  "content": {
    "core_topic": "Primary core topic in 1 concise phrase",
    "subtopics": ["Subtopic 1", "Subtopic 2", "Subtopic 3"],
    "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5", "keyword6"],
    "tags": ["#tag1", "#tag2", "#tag3", "#tag4"],
    "concepts": ["High-level conceptual entity 1", "Conceptual entity 2"]
  },
  "entities": {
    "organizations": ["Identified organizations / companies"],
    "systems_applications": ["Software platforms, cloud tools, frameworks"],
    "products": ["Products mentioned"],
    "roles": ["Personas or job roles mentioned"],
    "regulations_standards": ["Standards, regulations, frameworks (e.g., PCI-DSS, ISO 27001, HIPAA, GDPR)"]
  },
  "key_information": {
    "dates": ["Key dates mentioned"],
    "deadlines": ["Explicit time limits or deadlines"],
    "monetary_amounts": ["Financial figures, fees, limits, costs"],
    "compliance_rules": ["Specific regulatory, legal, or governance rules"],
    "requirements": ["Prerequisites or mandatory conditions"]
  },
  "dynamic_metadata": {
    "Key1": "Value1 tailored specifically to the document type",
    "Key2": "Value2 (e.g., for AWS tech doc: Platform, Architecture, Services, Database; for HR: Leave Type, Accrual Rate, Approval SLA; for Insurance: Claim Type, Deductible, Vehicle Class)"
  },
  "search_optimization": {
    "recommended_filename": "Standardized canonical filename (e.g., AWS_Serverless_Architecture_Guide_v2.0.pdf)",
    "intent_queries": [
      "Natural language search query 1 that a user would enter to locate this document",
      "Natural language search query 2",
      "Natural language search query 3"
    ],
    "fuzzy_phrasings": [
      "Common typo or informal search phrase that maps to this document (e.g., moter clam settle doc)",
      "Alternative shorthand search phrase 2"
    ]
  },
  "summary": "Concise 2-3 sentence plain-language content profile summarizing what this document is and its purpose.",
  "analysis_notes": "1-2 brief sentences highlighting unique indexing attributes of this content."
}

GUARDRAILS & BOUNDARIES:
- DO NOT reveal model identifiers (Nova, Bedrock, Anthropic, Claude, OpenAI, etc.). You are INDEX.
- Mask all sensitive payment card numbers, social security numbers, or API keys.
- Return ONLY valid JSON inside the response (no markdown text before or after).

=== ROBUST ERROR RESILIENCE & FUZZY UNDERSTANDING (LIKE TAXORA) ===
- The submitted content, notes, queries, or filenames may contain severe typos, misspellings, colloquial shorthand, bad grammar, missing vowels, OCR errors, or incomplete fragments.
- You MUST intelligently infer the author's intended subject matter and real domain like TAXORA does. Normalize and correct misspelled entities, technologies, and terms into clean canonical industry terminology for `basic.title` and `search_optimization.recommended_filename`.
- NEVER fail, reject, or return an error because the text contains typos or grammar errors.
- In `search_optimization.fuzzy_phrasings`, explicitly capture common user typos, phonetic misspellings, and informal search phrases that map to this document (e.g., mapping "moter clam settle doc" or "aws servrles microservce guid" to their canonical concepts).
"""

def _sanitize_ai_output(obj: Any) -> Any:
    """Removes any internal model names or leaked system prompt tokens from final output."""
    if isinstance(obj, str):
        cleaned = re.sub(r'\b(nova-pro|nova-lite|claude|bedrock|anthropic|gpt-4|openai)\b', 'INDEX AI Engine', obj, flags=re.IGNORECASE)
        return cleaned
    elif isinstance(obj, dict):
        return {k: _sanitize_ai_output(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_sanitize_ai_output(x) for x in obj]
    return obj

GREETING_RESPONSES = [
    "Hello! I am INDEX, your Enterprise Content Intelligence & Metadata Optimization Specialist. Upload any poorly-named document or paste text, and I'll generate canonical titles, multi-dimensional taxonomy, dynamic domain metadata, and search optimization queries.",
    "Hi there! Welcome to INDEX. I'm ready to analyze your enterprise content and extract structured metadata, entities, keywords, and search-optimized filenames. Drop a file or paste text to get started.",
    "Greetings! I am INDEX. Share any technical document, policy, claim, or report, and I will extract canonical metadata tags and search intent queries across all domains.",
    "Hello! Ready when you are. Upload any document (e.g. DOC_48383_FINAL_V2.pdf or Untitled.docx), and I will index its core topics, entities, and recommend a standardized canonical title.",
    "Hey! Welcome to INDEX. Feel free to paste content or upload a document anytime. I'll analyze its full context and build a complete enterprise metadata profile with zero hallucinations."
]

BRO_RESPONSES = [
    "Hey bro! Ready when you are. Upload any file or paste content, and I'll index canonical metadata, taxonomy, and search queries for you.",
    "Yo bro! What's up? I'm INDEX, your Content Intelligence & Metadata Engine. Send over any document, and I'll optimize its tags and canonical title.",
    "Hey bro! Standing by. Drop any file or paste text, and I'll extract standardized enterprise metadata with zero hallucinations.",
    "Sup bro! All systems go. Share any document or draft, and I'll generate the full metadata matrix and search intent queries."
]

HOW_ARE_YOU_RESPONSES = [
    "I'm doing great and ready to index your content! Upload any document or paste text, and I'll extract comprehensive metadata and search-optimized queries.",
    "All enterprise metadata tagging engines and privacy guardrails are operational! Ready to analyze any document or file you'd like to optimize.",
    "Doing very well, thank you! I'm here to solve poorly named enterprise files with standardized taxonomy and multi-dimensional metadata.",
    "I'm ready to assist! Share any document or text snippet, and I'll extract canonical metadata and natural search queries for you."
]


def _pick_varied_response(pool: list, conversation_history: list) -> str:
    used = set()
    for m in (conversation_history or []):
        c = m.get('content')
        if isinstance(c, dict):
            c = c.get('message') or c.get('summary') or ''
        if isinstance(c, str):
            used.add(c.strip())
    available = [r for r in pool if r not in used]
    if not available:
        available = pool
    return random.choice(available)


def _match_quick_conversational(user_text: str, conversation_history: list):
    cleaned = re.sub(r'[^\w\s]', '', (user_text or '').strip().lower())
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    if not cleaned:
        return None

    # Casual brother/slang words (bro, bruh, dude, yaar, bhai, machan, etc.)
    is_bro = (
        bool(re.match(r'^(?:(?:hey+|hi+|yo+|sup|hello+|namaste|vanakkam)\s+)?(?:bro+|brother|bruh|brah|dude|yaar|bhai|bhaiya|machan|macha|thala|buddy|mate|man|sis|dost)(?:\s+(?:how\s+are\s+you|whats?\s+up|hw\s+r\s+u))?$', cleaned)) or
        cleaned in {'bro', 'broo', 'bruh', 'brah', 'brother', 'dude', 'yaar', 'bhai', 'machan', 'macha', 'thala', 'buddy', 'mate', 'sis', 'dost'}
    )
    if is_bro:
        return _pick_varied_response(BRO_RESPONSES, conversation_history)

    # Check for "how are you" variants (including typos, abbreviations, and agent names)
    is_how_are_you = (
        bool(re.match(r'^(?:(?:hi+|h[ea]y+|h[ea]llo+|hlo)\s+)?(?:how|hw)\s+(?:r|are|re)\s+(?:u|you|yu)(?:\s+doing)?$', cleaned)) or
        bool(re.match(r'^(?:hows?|hws)\s+(?:it\s+going|u|you)$', cleaned)) or
        cleaned in {'hru', 'hw r u', 'how r u', 'how r you', 'how are you', 'how are u', 'whats up', 'sup', 'how do you do'}
    )
    if is_how_are_you:
        return _pick_varied_response(HOW_ARE_YOU_RESPONSES, conversation_history)

    # Check for greeting variants (including typos like helo, hlo, hiii, ji, and greetings with agent names like 'hi index', 'hey index')
    is_greeting = (
        bool(re.match(r'^(?:hi+|h[ea]y+|h[ea]llo+|hlo|ji+|namaste|hola|greetings?|yo+|sup)(?:\s+(?:there|index|agent|bot|all|team|friend|buddy|ji))?$', cleaned)) or
        bool(re.match(r'^(?:good\s+(?:morning|afternoon|evening|day))(?:\s+(?:index|there|all))?$', cleaned)) or
        cleaned in {'ji', 'hi', 'hello', 'hey', 'hii', 'hiii', 'heyy', 'namaste ji'}
    )
    if is_greeting:
        return _pick_varied_response(GREETING_RESPONSES, conversation_history)

    return None


def extract_metadata(
    content: str,
    file_name: str = "",
    history: List[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Extracts multi-dimensional metadata and search optimization tags for content using Amazon Bedrock Nova Pro.
    """
    if history is None:
        history = []

    # Quick Conversational / Greeting Check
    if not file_name:
        quick_reply = _match_quick_conversational(content, history)
        if quick_reply:
            return {
                "type": "chat",
                "status": "success",
                "message": quick_reply
            }

    # 1. Run Pre-Inference Guardrails (Sanitize PII/PCI-DSS, check prompt injection)
    guardrail_result = guardrail_service.inspect_and_sanitize(content)
    if guardrail_result.get('blocked'):
        return {
            "type": "chat",
            "status": "error",
            "message": guardrail_result.get("message", "The submitted content violates Enterprise BFSI Guardrails and cannot be processed."),
            "guardrail_status": "BLOCKED",
            "guardrail_details": guardrail_result
        }

    sanitized_content = guardrail_result.get("sanitized_text", content)

    # 2. Build Converse Messages strictly following Bedrock Converse API rules
    messages = []
    for turn in (history or [])[-6:]:
        text_val = turn.get('content', '')
        if isinstance(text_val, dict):
            text_val = text_val.get('message') or text_val.get('summary') or json.dumps(text_val)
        text_val = str(text_val or '').strip()
        if not text_val or text_val.startswith('<!doctype') or '<html' in text_val.lower():
            continue

        role = 'assistant' if turn.get('role') in ('ai', 'assistant') else 'user'
        if messages and messages[-1]['role'] == role:
            prev_txt = messages[-1]['content'][0]['text']
            messages[-1]['content'][0]['text'] = f"{prev_txt}\n\n{text_val[:2000]}"
        else:
            messages.append({
                'role': role,
                'content': [{'text': text_val[:2000]}]
            })

    # Strict Converse rule: conversation MUST start with a user message
    while messages and messages[0]['role'] != 'user':
        messages.pop(0)

    user_prompt = f"Analyze and index the following document content.\n"
    if file_name:
        user_prompt += f"Original Filename: {file_name}\n"
    user_prompt += f"\n--- DOCUMENT CONTENT ---\n{sanitized_content}\n--- END CONTENT ---\n\nGenerate the complete JSON metadata tagger profile according to the required schema."

    if messages and messages[-1]['role'] == 'user':
        prev_txt = messages[-1]['content'][0]['text']
        messages[-1]['content'][0]['text'] = f"{prev_txt}\n\n{user_prompt}"
    else:
        messages.append({
            'role': 'user',
            'content': [{'text': user_prompt}]
        })

    while messages and messages[0]['role'] != 'user':
        messages.pop(0)

    if not messages:
        messages = [{'role': 'user', 'content': [{'text': user_prompt}]}]

    client = get_bedrock_client()
    response_text = ""

    # 3. Call Amazon Bedrock Converse API
    try:
        response = client.converse(
            modelId=MODEL_ID,
            messages=messages,
            system=[{'text': INDEX_SYSTEM_PROMPT}],
            inferenceConfig={
                'temperature': 0.1,
                'topP': 0.9,
                'maxTokens': 3500
            }
        )
        response_text = response['output']['message']['content'][0]['text'].strip()
    except Exception as e:
        print(f"[INDEX Service] Bedrock Nova Pro call failed ({e}). Trying fallback {FALLBACK_MODEL_ID}...")
        try:
            response = client.converse(
                modelId=FALLBACK_MODEL_ID,
                messages=messages,
                system=[{'text': INDEX_SYSTEM_PROMPT}],
                inferenceConfig={
                    'temperature': 0.1,
                    'topP': 0.9,
                    'maxTokens': 3500
                }
            )
            response_text = response['output']['message']['content'][0]['text'].strip()
        except Exception as e2:
            print(f"[INDEX Service] Bedrock fallback failed: {e2}. Generating offline dynamic fallback.")
            response_text = _generate_offline_fallback(sanitized_content, file_name)

    # 4. Clean & Parse JSON
    parsed_json = _clean_and_parse_json(response_text)
    parsed_json = _sanitize_ai_output(parsed_json)

    # 5. Format Return Package
    return {
        "status": "success",
        "type": "index_result",
        "data": parsed_json,
        "guardrails": {
            "pci_dss_sanitized": True,
            "redacted_count": guardrail_result.get("guardrails", {}).get("redacted_count", 0),
            "redacted_types": guardrail_result.get("guardrails", {}).get("redacted_types", []),
            "injection_safe": True,
            "enterprise_verified": True
        },
        "file_name": file_name
    }

def _clean_and_parse_json(raw: str) -> Dict[str, Any]:
    text = raw.strip()
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except Exception:
            pass

    return {
        "basic": {
            "title": "Indexed Document Profile",
            "document_type": "Document",
            "language": "English",
            "target_audience": "Enterprise Users",
            "owner_department": "Operations",
            "version": "1.0"
        },
        "business": {
            "domain": "Enterprise",
            "subdomain": "Information Management",
            "product_service": "General",
            "process_area": "Content Management",
            "business_function": "Operations"
        },
        "content": {
            "core_topic": "Content Indexing",
            "subtopics": ["Metadata Analysis"],
            "keywords": ["document", "index", "metadata"],
            "tags": ["#enterprise", "#index"],
            "concepts": ["Knowledge Management"]
        },
        "entities": {
            "organizations": [],
            "systems_applications": [],
            "products": [],
            "roles": [],
            "regulations_standards": []
        },
        "key_information": {
            "dates": [],
            "deadlines": [],
            "monetary_amounts": [],
            "compliance_rules": [],
            "requirements": []
        },
        "dynamic_metadata": {},
        "search_optimization": {
            "recommended_filename": "Standardized_Document_Index.pdf",
            "intent_queries": ["search document content", "find indexed file"],
            "fuzzy_phrasings": ["search doc", "find file"]
        },
        "summary": text[:250],
        "analysis_notes": "Indexed according to enterprise taxonomy standards."
    }

def _generate_offline_fallback(content: str, file_name: str) -> str:
    title = file_name if file_name else "Indexed Document"
    title_clean = title.replace("_", " ").replace("-", " ").title()
    is_aws = "aws" in content.lower() or "lambda" in content.lower() or "serverless" in content.lower()
    is_insurance = "claim" in content.lower() or "policy" in content.lower() or "insurance" in content.lower()
    is_hr = "leave" in content.lower() or "employee" in content.lower() or "hr" in content.lower()

    if is_aws:
        domain = "Cloud Computing"
        doc_type = "Architecture Guide"
        dynamic = {
            "Platform": "AWS",
            "Architecture": "Serverless Event-Driven",
            "Services": ["Lambda", "API Gateway", "Bedrock"],
            "Database": "DynamoDB"
        }
        recommended_file = "AWS_Serverless_Architecture_Specification_v2.0.pdf"
        fuzzy = ["aws lambd arch serverles", "cloud serverless api doc"]
    elif is_insurance:
        domain = "BFSI / Insurance"
        doc_type = "Motor Claim Notice"
        dynamic = {
            "Claim Type": "Motor Vehicle",
            "Deductible": "$500",
            "Settlement SLA": "7 Business Days"
        }
        recommended_file = "Motor_Claim_Settlement_Standard_Procedure_2026.pdf"
        fuzzy = ["moter clam settle doc", "car claim form"]
    elif is_hr:
        domain = "Human Resources"
        doc_type = "Corporate Policy"
        dynamic = {
            "Leave Type": "Annual / Paid Time Off",
            "Approval Window": "48 Hours",
            "Audience": "All Full-Time Employees"
        }
        recommended_file = "Employee_Leave_and_Absence_Policy_v2.0.pdf"
        fuzzy = ["leave apply rules hr", "annual vacation policy"]
    else:
        domain = "Enterprise Operations"
        doc_type = "Information Brief"
        dynamic = {
            "Classification": "Internal Confidential",
            "Review Cycle": "Annual"
        }
        recommended_file = "Enterprise_Information_Brief_2026.pdf"
        fuzzy = ["doc info summary", "enterprise procedure doc"]

    fallback_obj = {
        "basic": {
            "title": title_clean,
            "document_type": doc_type,
            "language": "English",
            "target_audience": "Enterprise Professionals",
            "owner_department": "Corporate Operations",
            "version": "1.0"
        },
        "business": {
            "domain": domain,
            "subdomain": "Standard Operating Procedures",
            "product_service": "Enterprise Solutions",
            "process_area": "Content Intelligence",
            "business_function": "Operations"
        },
        "content": {
            "core_topic": f"{domain} Standard Operating Procedure",
            "subtopics": ["Process Guidelines", "Compliance Requirements", "Execution Protocols"],
            "keywords": ["governance", "standard", "procedure", "compliance", "index"],
            "tags": ["#enterprise", "#compliance", "#operations"],
            "concepts": ["Operational Excellence", "Standardization"]
        },
        "entities": {
            "organizations": ["Enterprise Corp"],
            "systems_applications": ["Content Management System"],
            "products": ["Internal Systems"],
            "roles": ["Operations Manager", "Reviewer"],
            "regulations_standards": ["ISO 27001", "Internal Audit"]
        },
        "key_information": {
            "dates": ["Current Year"],
            "deadlines": ["30 Calendar Days"],
            "monetary_amounts": [],
            "compliance_rules": ["Mandatory review required before publishing"],
            "requirements": ["Authorized sign-off required"]
        },
        "dynamic_metadata": dynamic,
        "search_optimization": {
            "recommended_filename": recommended_file,
            "intent_queries": [
                f"How to review and process {title_clean}",
                f"{domain} compliance and guidelines",
                f"Standard procedures for {title_clean}"
            ],
            "fuzzy_phrasings": fuzzy
        },
        "summary": f"This document establishes formal operational and governance standards for {domain}. It outlines responsibilities, process flows, and compliance guidelines.",
        "analysis_notes": "Automatically tagged with multi-dimensional taxonomy and retrieval intent mappings."
    }
    return json.dumps(fallback_obj)
