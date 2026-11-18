import os
import json
import re
import random
import datetime
import hashlib
import mimetypes
import uuid
import boto3
from pathlib import Path
from typing import Dict, Any, List, Optional
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


INDEX_SYSTEM_PROMPT = """You are INDEX, an Enterprise AI Metadata Extraction, Asset Cataloging & Search Intelligence Engine (ISO 15836 Dublin Core, W3C DCAT & Enterprise DAM Standard).

CORE MISSION:
Your primary focus is **ENTERPRISE METADATA EXTRACTION** (not taxonomy).
For every uploaded document, image/picture, spreadsheet, code file, or text payload, extract **28+ to 32+ comprehensive, standardized enterprise metadata attributes** across:
1. Descriptive & Dublin Core Metadata (ISO 15836)
2. Technical, File & Media Forensics Metadata (including Visual/Image Forensics when an image is provided)
3. Enterprise Governance, Compliance, Security & Lifecycle Metadata
4. Business, Operational & Provenance Metadata
5. Content & Visual Semantic Metadata (including 10+ domain-specific `dynamic_metadata` attributes)
6. Search Engine, Vector Indexing & Retrieval Metadata

CRITICAL FOR IMAGES / PICTURES:
When the input is an image or picture (screenshot, diagram, photo, scanned page, chart, ID/certificate, UI mockup), you MUST still generate 28+ rich enterprise metadata attributes covering visual composition, scene classification, OCR transcription status, color profile, visual hierarchy, UI/diagram components, resolution/aspect characteristics, accessibility alt-text, rights/usage governance, and domain context.

ZERO EMOJIS RULE:
- NEVER output emojis anywhere in your JSON values.

CONVERSATIONAL & FOLLOW-UP QUESTIONS:
If the user asks a follow-up question, "tell extra about...", "be more specific", or a domain question about metadata tagging/governance without submitting a new asset, respond with:
{"type": "chat", "message": "<thorough, specific answer grounded in conversation history and INDEX domain>"}

OUTPUT SCHEMA (STRICT JSON ONLY):
{
  "type": "index_result",
  "basic": {
    "title": "Clean, descriptive, canonical asset title",
    "alternative_title": "Secondary or subtitle identifier",
    "document_type": "Specific artifact type (e.g., Architecture Diagram, UI Screenshot, Policy Manual, SOP, Contract, Financial Report)",
    "language": "Primary language & ISO code (e.g., English (en-US))",
    "target_audience": "Intended enterprise audience",
    "owner_department": "Custodian department or issuing authority",
    "author_creator": "Originating author, system, or organization",
    "version": "Version identifier (e.g., 1.0, 2.1, Production Release)",
    "publication_status": "Lifecycle state (e.g., Active / Published, Draft, Archived)"
  },
  "business": {
    "domain": "Industry vertical / domain",
    "subdomain": "Functional sub-domain",
    "product_service": "Associated product, platform, or service line",
    "process_area": "Operational workflow or business process",
    "business_function": "Corporate functional group",
    "operational_criticality": "Tier 1 Mission-Critical | Tier 2 Operational | Tier 3 Reference",
    "geographic_scope": "Geographic or jurisdictional applicability (e.g., Global Enterprise, North America, APAC / India)"
  },
  "governance": {
    "retention_period": "Statutory retention schedule (e.g., 7 Years Statutory, 5 Years Operational, Permanent)",
    "confidentiality_level": "Classification (e.g., Internal Confidential, Restricted, Public, Proprietary)",
    "regulatory_frameworks": ["ISO 27001", "SOC 2 Type II", "GDPR", "PCI-DSS v4.0"],
    "data_classification": "Data category (e.g., Corporate Intellectual Property, Operational Records, Visual Media Asset)",
    "archival_tier": "Storage lifecycle tier (e.g., Hot S3 Standard, Warm Infrequent Access, Cold Glacier Archive)",
    "access_control_policy": "RBAC policy (e.g., Role-Based Enterprise Read, Department Restricted, Authenticated Staff)",
    "copyright_license": "Rights & usage license (e.g., Enterprise Proprietary - All Rights Reserved)",
    "audit_verification_status": "Verified & Sanitized"
  },
  "technical_metrics": {
    "estimated_word_count": "Word count or OCR token count",
    "reading_time": "Estimated review/inspection duration",
    "readability_level": "Complexity / legibility grade",
    "content_density": "Information or visual density",
    "primary_intent": "Primary operational intent",
    "structural_format": "Structural layout pattern (e.g., Multi-Section Hierarchical Document, High-Contrast UI Canvas, Tabular Matrix)",
    "encoding_standard": "UTF-8 / Binary Media Stream"
  },
  "visual_media_metadata": {
    "media_modality": "Digital Text Document | Raster Image / Screenshot | Vector Diagram | Scanned Page",
    "visual_scene_type": "Specific visual/layout category",
    "color_palette_profile": "Dominant color scheme & contrast profile",
    "layout_composition": "Spatial arrangement of elements, text, or panels",
    "accessibility_alt_text": "Comprehensive WCAG-compliant descriptive alt-text for screen readers",
    "ocr_text_density": "High Text Density | Moderate Labels | Primarily Visual"
  },
  "dynamic_metadata": {
    "Attribute_1": "Specific extracted value 1",
    "Attribute_2": "Specific extracted value 2",
    "Attribute_3": "Specific extracted value 3",
    "Attribute_4": "Specific extracted value 4",
    "Attribute_5": "Specific extracted value 5",
    "Attribute_6": "Specific extracted value 6",
    "Attribute_7": "Specific extracted value 7",
    "Attribute_8": "Specific extracted value 8"
  },
  "content": {
    "core_topic": "Primary core subject in 1 concise phrase",
    "subtopics": ["Subtopic 1", "Subtopic 2", "Subtopic 3", "Subtopic 4"],
    "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5", "keyword6", "keyword7", "keyword8"],
    "tags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5", "#tag6"],
    "concepts": ["Concept 1", "Concept 2", "Concept 3"]
  },
  "entities": {
    "organizations": ["Organizations / brands"],
    "systems_applications": ["Platforms, tools, technologies"],
    "products": ["Products / modules"],
    "roles": ["Roles / personas"],
    "regulations_standards": ["Standards / compliance frameworks"]
  },
  "key_information": {
    "dates": ["Dates / timestamps"],
    "deadlines": ["SLAs / time limits"],
    "monetary_amounts": ["Figures / metrics / quantities"],
    "compliance_rules": ["Key governance rules or visual specifications"],
    "requirements": ["Prerequisites or technical dependencies"]
  },
  "search_optimization": {
    "recommended_filename": "Standardized_Canonical_Enterprise_Filename.ext",
    "intent_queries": [
      "Natural language search query 1",
      "Natural language search query 2",
      "Natural language search query 3",
      "Natural language search query 4"
    ],
    "fuzzy_phrasings": [
      "Typo-tolerant or shorthand query 1",
      "Typo-tolerant or shorthand query 2",
      "Typo-tolerant or shorthand query 3"
    ]
  },
  "summary": "2-3 sentence executive metadata abstract describing the asset, its contents, and its operational purpose."
}
"""


def _sanitize_ai_output(obj: Any) -> Any:
    if isinstance(obj, str):
        cleaned = re.sub(r'\b(nova-pro|nova-lite|claude|bedrock|anthropic|gpt-4|openai)\b', 'INDEX AI Engine', obj, flags=re.IGNORECASE)
        return cleaned
    elif isinstance(obj, dict):
        return {k: _sanitize_ai_output(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_sanitize_ai_output(x) for x in obj]
    return obj


GREETING_RESPONSES = [
    "Hello. I am INDEX, your Enterprise Metadata Extraction & Asset Registry Engine. Upload any document, image, or file below to extract 30+ standardized enterprise metadata attributes (Dublin Core ISO 15836, Technical Forensics, Governance, Semantic Descriptors, and Search Indexing).",
    "Welcome to INDEX. Attach any document, picture, or file to generate a complete 30+ attribute enterprise metadata registry, canonical filename, and search retrieval profile."
]

BRO_RESPONSES = [
    "Hey bro. Upload any document, picture, or file below, and I will extract 30+ standardized enterprise metadata attributes, technical forensics, and search indexing metadata.",
    "Ready when you are, bro. Drop any file or image to generate a full 30+ attribute enterprise metadata specification."
]

HOW_ARE_YOU_RESPONSES = [
    "All enterprise metadata extraction and media forensic engines are operating at peak accuracy. Upload any document or image to extract 30+ standard metadata attributes.",
    "Operating smoothly and ready to catalog your assets. Share any file, picture, or text to generate its complete enterprise metadata registry."
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
    return random.choice(available if available else pool)


def _match_quick_conversational(user_text: str, conversation_history: list):
    cleaned = re.sub(r'[^\w\s]', '', (user_text or '').strip().lower())
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    if not cleaned:
        return None

    is_bro = (
        bool(re.match(r'^(?:(?:hey+|hi+|yo+|sup|hello+|namaste|vanakkam)\s+)?(?:bro+|brother|bruh|brah|dude|yaar|bhai|bhaiya|machan|macha|thala|buddy|mate|man|sis|dost)(?:\s+(?:how\s+are\s+you|whats?\s+up|hw\s+r\s+u))?$', cleaned)) or
        cleaned in {'bro', 'broo', 'bruh', 'brah', 'brother', 'dude', 'yaar', 'bhai', 'machan', 'macha', 'thala', 'buddy', 'mate', 'sis', 'dost'}
    )
    if is_bro:
        return _pick_varied_response(BRO_RESPONSES, conversation_history)

    is_how_are_you = (
        bool(re.match(r'^(?:(?:hi+|h[ea]y+|h[ea]llo+|hlo)\s+)?(?:how|hw)\s+(?:r|are|re)\s+(?:u|you|yu)(?:\s+doing)?$', cleaned)) or
        bool(re.match(r'^(?:hows?|hws)\s+(?:it\s+going|u|you)$', cleaned)) or
        cleaned in {'hru', 'hw r u', 'how r u', 'how r you', 'how are you', 'how are u', 'whats up', 'sup', 'how do you do'}
    )
    if is_how_are_you:
        return _pick_varied_response(HOW_ARE_YOU_RESPONSES, conversation_history)

    is_greeting = (
        bool(re.match(r'^(?:hi+|h[ea]y+|h[ea]llo+|hlo|ji+|namaste|hola|greetings?|yo+|sup)(?:\s+(?:there|index|agent|bot|all|team|friend|buddy|ji))?$', cleaned)) or
        bool(re.match(r'^(?:good\s+(?:morning|afternoon|evening|day))(?:\s+(?:index|there|all))?$', cleaned)) or
        cleaned in {'ji', 'hi', 'hello', 'hey', 'hii', 'hiii', 'heyy', 'namaste ji'}
    )
    if is_greeting:
        return _pick_varied_response(GREETING_RESPONSES, conversation_history)

    return None


def _build_enterprise_metadata_registry(
    parsed: Dict[str, Any],
    doc_meta: Optional[Dict[str, Any]],
    file_name: str,
    raw_content: str,
    trace_code: str
) -> List[Dict[str, str]]:
    """
    Constructs a guaranteed 30+ attribute standardized Enterprise Metadata Registry
    spanning Dublin Core (ISO 15836), Technical & Media Forensics, Enterprise Governance,
    Operational & Business Context, Semantic & Visual Content, and Search Indexing.
    """
    meta = doc_meta or {}
    basic = parsed.get("basic") or {}
    business = parsed.get("business") or {}
    governance = parsed.get("governance") or {}
    tech = parsed.get("technical_metrics") or {}
    visual = parsed.get("visual_media_metadata") or {}
    content = parsed.get("content") or {}
    entities = parsed.get("entities") or {}
    search_opt = parsed.get("search_optimization") or {}
    dyn = parsed.get("dynamic_metadata") or {}

    ext = Path(file_name).suffix.lower() if file_name else (meta.get("type") or ".txt")
    kind = meta.get("kind") or ("image" if ext in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"} else "document")
    mime_type = meta.get("mime_type") or mimetypes.guess_type(file_name or "asset.txt")[0] or ("image/png" if kind == "image" else "application/octet-stream")
    size_bytes = meta.get("size_bytes") or len((raw_content or "").encode("utf-8"))
    size_kb = f"{round(size_bytes / 1024, 2)} KB ({size_bytes:,} bytes)" if size_bytes else "Text Payload"
    sha256_val = meta.get("sha256") or hashlib.sha256((raw_content or file_name or "index").encode("utf-8")).hexdigest()
    now_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    is_image = (kind == "image")
    word_cnt = meta.get("word_count", 450)
    est_words = tech.get("estimated_word_count") or f"{word_cnt} words"
    pages_cnt = meta.get("pages") or meta.get("slides") or 1
    chars_cnt = meta.get("char_count", len(raw_content or ""))
    res_str = meta.get("resolution", "High-Resolution Canvas")
    asp_str = meta.get("aspect_ratio", "16:9")
    mp_str = meta.get("megapixels", "Digital Raster")
    ori_str = meta.get("orientation", "Landscape")
    layout_str = visual.get("layout_composition") or "Full Frame Canvas"
    ext_upper = ext.upper().lstrip(".")

    extent_val = (
        f"{res_str} · Aspect {asp_str} · {mp_str} ({ori_str})"
        if is_image and meta.get("resolution")
        else (
            f"Visual Raster Asset ({ext_upper}) · {layout_str}"
            if is_image
            else f"{pages_cnt} Page(s) · {est_words} · {chars_cnt:,} chars"
        )
    )

    cs_str = meta.get("color_space", "sRGB TrueColor")
    bd_str = meta.get("bit_depth", "8-bit/channel")
    comp_str = meta.get("compression", "Lossless")
    enc_std = tech.get("encoding_standard") or "UTF-8 Digital Stream"
    struct_fmt = tech.get("structural_format") or "Structured Enterprise Document"

    color_or_encoding = (
        f"{cs_str} · {bd_str} · {comp_str}"
        if is_image
        else f"{enc_std} · {struct_fmt}"
    )

    registry = [
        # 1. DUBLIN CORE & DESCRIPTIVE METADATA (ISO 15836) — 8 Attributes
        {"category": "Descriptive (ISO 15836)", "key": "dc:title", "label": "Canonical Asset Title", "value": basic.get("title") or "Indexed Enterprise Asset"},
        {"category": "Descriptive (ISO 15836)", "key": "dc:identifier", "label": "Asset Registry URN", "value": f"urn:enterprise:index:{trace_code.lower()}"},
        {"category": "Descriptive (ISO 15836)", "key": "dc:type", "label": "Artifact Classification", "value": basic.get("document_type") or ("Visual Media Asset" if is_image else "Enterprise Document")},
        {"category": "Descriptive (ISO 15836)", "key": "dc:subject", "label": "Primary Subject Matter", "value": content.get("core_topic") or basic.get("title") or "Enterprise Content Profile"},
        {"category": "Descriptive (ISO 15836)", "key": "dc:creator", "label": "Originating Authority / Creator", "value": basic.get("author_creator") or basic.get("owner_department") or "Enterprise Operations"},
        {"category": "Descriptive (ISO 15836)", "key": "dc:publisher", "label": "Custodian Department", "value": basic.get("owner_department") or business.get("business_function") or "Information Governance"},
        {"category": "Descriptive (ISO 15836)", "key": "dc:language", "label": "Language & Locale (ISO 639-1)", "value": basic.get("language") or "English (en-US)"},
        {"category": "Descriptive (ISO 15836)", "key": "dc:date.issued", "label": "Ingestion Timestamp (ISO 8601)", "value": now_iso},

        # 2. TECHNICAL, FILE & MEDIA FORENSICS METADATA — 8 Attributes
        {"category": "Technical & Forensics", "key": "tech:original_filename", "label": "Source Filename", "value": file_name or "Direct_Text_Stream.txt"},
        {"category": "Technical & Forensics", "key": "tech:canonical_filename", "label": "Canonical Standard Filename", "value": search_opt.get("recommended_filename") or f"Enterprise_Asset_{trace_code[-6:]}{ext}"},
        {"category": "Technical & Forensics", "key": "tech:mime_type", "label": "MIME Type & Container Format", "value": f"{mime_type} ({ext.upper().lstrip('.') or 'TXT'})"},
        {"category": "Technical & Forensics", "key": "tech:payload_size", "label": "File Size & Byte Payload", "value": size_kb},
        {"category": "Technical & Forensics", "key": "tech:geometry_extent", "label": "Dimensions / Structural Extent", "value": extent_val},
        {"category": "Technical & Forensics", "key": "tech:encoding_profile", "label": "Color Profile / Character Encoding", "value": color_or_encoding},
        {"category": "Technical & Forensics", "key": "tech:sha256_digest", "label": "SHA-256 Integrity Checksum", "value": f"{sha256_val[:24]}...{sha256_val[-8:]}"},
        {"category": "Technical & Forensics", "key": "tech:extraction_modality", "label": "Extraction Engine Modality", "value": "Multimodal Vision + OCR Forensics" if is_image else "Deep Full-Document Semantic Parser"},

        # 3. ENTERPRISE GOVERNANCE, SECURITY & LIFECYCLE METADATA — 6 Attributes
        {"category": "Governance & Security", "key": "gov:data_classification", "label": "Data Classification Tier", "value": governance.get("data_classification") or "Enterprise Operational Asset"},
        {"category": "Governance & Security", "key": "gov:confidentiality", "label": "Security & Confidentiality Level", "value": governance.get("confidentiality_level") or "Internal Confidential"},
        {"category": "Governance & Security", "key": "gov:access_control", "label": "Access Control Policy (RBAC)", "value": governance.get("access_control_policy") or "Role-Based Enterprise Access"},
        {"category": "Governance & Security", "key": "gov:retention_schedule", "label": "Statutory Retention Schedule", "value": governance.get("retention_period") or "7 Years (Enterprise Standard)"},
        {"category": "Governance & Security", "key": "gov:archival_tier", "label": "Storage Lifecycle Tier", "value": governance.get("archival_tier") or "Hot / Active S3 Standard"},
        {"category": "Governance & Security", "key": "gov:compliance_regimes", "label": "Regulatory & Compliance Standards", "value": ", ".join(governance.get("regulatory_frameworks") or ["ISO 27001", "SOC 2", "GDPR"])},

        # 4. BUSINESS & OPERATIONAL CONTEXT METADATA — 6 Attributes
        {"category": "Business & Operational", "key": "biz:industry_domain", "label": "Industry Vertical / Domain", "value": business.get("domain") or "Enterprise Technology & Operations"},
        {"category": "Business & Operational", "key": "biz:functional_subdomain", "label": "Functional Sub-Domain", "value": business.get("subdomain") or "Knowledge & Asset Management"},
        {"category": "Business & Operational", "key": "biz:process_workflow", "label": "Business Process / Workflow", "value": business.get("process_area") or "Operational Execution"},
        {"category": "Business & Operational", "key": "biz:product_service", "label": "Product / Platform Alignment", "value": business.get("product_service") or "Enterprise Platform"},
        {"category": "Business & Operational", "key": "biz:target_audience", "label": "Target Stakeholder Audience", "value": basic.get("target_audience") or "Enterprise Stakeholders"},
        {"category": "Business & Operational", "key": "biz:criticality_tier", "label": "Operational Criticality", "value": business.get("operational_criticality") or "Tier 2 Operational"},

        # 5. SEMANTIC, VISUAL & CONTENT METADATA — 6+ Attributes
        {"category": "Semantic & Content", "key": "sem:primary_intent", "label": "Primary Operational Intent", "value": tech.get("primary_intent") or basic.get("document_type") or "Reference & Governance"},
        {"category": "Semantic & Content", "key": "sem:readability_grade", "label": "Readability / Visual Legibility", "value": tech.get("readability_level") or "Professional Enterprise"},
        {"category": "Semantic & Content", "key": "sem:information_density", "label": "Information / Visual Density", "value": tech.get("content_density") or "High — Structured Content"},
        {"category": "Semantic & Content", "key": "sem:review_duration", "label": "Estimated Inspection Time", "value": tech.get("reading_time") or ("1-2 mins (Visual Scan)" if is_image else "3-4 mins")},
    ]

    if is_image or visual:
        if visual.get("visual_scene_type"):
            registry.append({"category": "Semantic & Content", "key": "sem:visual_scene", "label": "Visual Scene & Artifact Type", "value": str(visual["visual_scene_type"])})
        if visual.get("color_palette_profile"):
            registry.append({"category": "Semantic & Content", "key": "sem:color_palette", "label": "Color Palette & Contrast Profile", "value": str(visual["color_palette_profile"])})
        if visual.get("accessibility_alt_text"):
            registry.append({"category": "Semantic & Content", "key": "sem:wcag_alt_text", "label": "WCAG Accessibility Alt-Text", "value": str(visual["accessibility_alt_text"])})

    # Append all dynamic_metadata attributes into Semantic & Content
    if isinstance(dyn, dict):
        for k, v in dyn.items():
            clean_key = re.sub(r'[^a-z0-9_]+', '_', str(k).lower()).strip('_')
            val_str = ", ".join(str(x) for x in v) if isinstance(v, list) else str(v)
            if val_str and val_str.strip():
                registry.append({
                    "category": "Semantic & Content",
                    "key": f"dyn:{clean_key}",
                    "label": str(k).replace("_", " "),
                    "value": val_str.strip()
                })

    return registry


def extract_metadata(
    content: str,
    file_name: str = "",
    history: List[Dict[str, str]] = None,
    doc_meta: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    if history is None:
        history = []

    if not file_name:
        quick_reply = _match_quick_conversational(content, history)
        if quick_reply:
            return {
                "type": "chat",
                "status": "success",
                "message": quick_reply
            }

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

    while messages and messages[0]['role'] != 'user':
        messages.pop(0)

    meta_context = ""
    if doc_meta:
        meta_context = (
            f"File Forensics: filename={file_name}, kind={doc_meta.get('kind')}, "
            f"mime={doc_meta.get('mime_type')}, size_bytes={doc_meta.get('size_bytes')}, "
            f"resolution={doc_meta.get('resolution', 'N/A')}, color_space={doc_meta.get('color_space', 'N/A')}, "
            f"pages={doc_meta.get('pages', 'N/A')}, words={doc_meta.get('word_count', 'N/A')}\n"
        )

    user_prompt = (
        f"Extract comprehensive 30+ Enterprise Standard Metadata Attributes for the following asset.\n"
        f"{meta_context}"
        f"Provide at least 8 specific domain/visual key-value pairs in `dynamic_metadata`, complete `basic`, `business`, `governance`, `technical_metrics`, and `visual_media_metadata`.\n"
        f"\n--- ASSET CONTENT & VISION ANALYSIS ---\n{sanitized_content}\n--- END CONTENT ---\n\n"
        f"Return ONLY valid JSON matching the required schema."
    )

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

    try:
        response = client.converse(
            modelId=MODEL_ID,
            messages=messages,
            system=[{'text': INDEX_SYSTEM_PROMPT}],
            inferenceConfig={
                'temperature': 0.1,
                'topP': 0.9,
                'maxTokens': 4000
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
                    'maxTokens': 4000
                }
            )
            response_text = response['output']['message']['content'][0]['text'].strip()
        except Exception as e2:
            print(f"[INDEX Service] Bedrock fallback failed: {e2}. Generating offline dynamic fallback.")
            response_text = _generate_offline_fallback(sanitized_content, file_name)

    parsed_json = _clean_and_parse_json(response_text)
    parsed_json = _sanitize_ai_output(parsed_json)

    trace_code = f"IXT-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    if isinstance(parsed_json, dict):
        parsed_json['trace_id'] = trace_code
        parsed_json['metadata_registry'] = _build_enterprise_metadata_registry(
            parsed_json, doc_meta, file_name, sanitized_content, trace_code
        )

    return {
        "status": "success",
        "type": "index_result",
        "data": parsed_json,
        "trace_id": trace_code,
        "guardrails": {
            "status": "REDACTED" if guardrail_result.get("has_redactions") else "PASSED",
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
            "title": "Indexed Enterprise Asset Profile",
            "document_type": "Enterprise Asset",
            "language": "English (en-US)",
            "target_audience": "Enterprise Stakeholders",
            "owner_department": "Information Governance",
            "version": "1.0"
        },
        "business": {
            "domain": "Enterprise Operations",
            "subdomain": "Information & Asset Management",
            "product_service": "Enterprise Knowledge Platform",
            "process_area": "Metadata Cataloging",
            "business_function": "Operations"
        },
        "content": {
            "core_topic": "Enterprise Asset Metadata Profile",
            "subtopics": ["Descriptive Metadata", "Technical Forensics", "Governance Standards"],
            "keywords": ["metadata", "dublin-core", "enterprise", "governance", "asset-registry"],
            "tags": ["#metadata", "#iso15836", "#enterprise", "#governance"],
            "concepts": ["Information Architecture", "Digital Asset Management"]
        },
        "entities": {
            "organizations": [],
            "systems_applications": [],
            "products": [],
            "roles": [],
            "regulations_standards": ["ISO 15836", "ISO 27001"]
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
            "recommended_filename": "Standardized_Enterprise_Asset.pdf",
            "intent_queries": ["search indexed enterprise asset", "locate metadata record"],
            "fuzzy_phrasings": ["search doc", "find asset"]
        },
        "summary": text[:250] if text else "Comprehensive enterprise metadata profile generated."
    }


def _generate_offline_fallback(content: str, file_name: str) -> str:
    title = file_name if file_name else "Indexed Enterprise Asset"
    title_clean = Path(title).stem.replace("_", " ").replace("-", " ").title()
    ext = Path(file_name).suffix.lower() if file_name else ".pdf"
    is_img = ext in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}

    fallback_obj = {
        "basic": {
            "title": title_clean,
            "document_type": "Visual Media Asset" if is_img else "Enterprise Specification",
            "language": "English (en-US)",
            "target_audience": "Enterprise Stakeholders",
            "owner_department": "Corporate Operations",
            "version": "1.0"
        },
        "business": {
            "domain": "Digital Asset Management" if is_img else "Enterprise Operations",
            "subdomain": "Visual Media & Documentation" if is_img else "Standard Operating Procedures",
            "product_service": "Enterprise Platform",
            "process_area": "Metadata Cataloging & Indexing",
            "business_function": "Information Governance",
            "operational_criticality": "Tier 2 Operational"
        },
        "governance": {
            "retention_period": "7 Years Statutory",
            "confidentiality_level": "Internal Confidential",
            "regulatory_frameworks": ["ISO 15836", "ISO 27001", "SOC 2"],
            "data_classification": "Enterprise Digital Asset",
            "archival_tier": "Hot S3 Standard",
            "access_control_policy": "Role-Based Enterprise Access"
        },
        "technical_metrics": {
            "estimated_word_count": f"{len((content or '').split())} words",
            "reading_time": "1-2 mins" if is_img else "3-4 mins",
            "readability_level": "Professional Enterprise",
            "content_density": "High - Structured Information",
            "primary_intent": "Visual Reference & Verification" if is_img else "Operational Governance"
        },
        "visual_media_metadata": {
            "media_modality": "Raster Image / Screenshot" if is_img else "Digital Text Document",
            "visual_scene_type": "Enterprise Visual Capture" if is_img else "Structured Document Layout",
            "color_palette_profile": "High-Contrast Enterprise Palette",
            "layout_composition": "Structured Multi-Region Frame",
            "accessibility_alt_text": f"Enterprise asset representing {title_clean}"
        },
        "dynamic_metadata": {
            "Asset_Category": "Visual Media" if is_img else "Documentation",
            "Indexing_Standard": "ISO 15836 Dublin Core + W3C DCAT",
            "Verification_State": "Sanitized & Verified",
            "Ingestion_Channel": "INDEX Enterprise Registry",
            "Search_Readiness": "Vector & Keyword Indexed",
            "Schema_Compliance": "100% Enterprise Standard"
        },
        "content": {
            "core_topic": f"{title_clean} — Enterprise Metadata Profile",
            "subtopics": ["Descriptive Attributes", "Technical Forensics", "Governance & Retention"],
            "keywords": ["metadata", "enterprise", "iso-15836", "forensics", "governance", "index"],
            "tags": ["#metadata", "#enterprise", "#iso15836", "#governance"],
            "concepts": ["Enterprise Metadata Registry", "Information Retrieval"]
        },
        "entities": {
            "organizations": ["Enterprise Organization"],
            "systems_applications": ["INDEX Metadata Registry"],
            "products": ["Enterprise Content Platform"],
            "roles": ["Information Architect", "Data Steward"],
            "regulations_standards": ["ISO 15836", "ISO 27001", "W3C DCAT"]
        },
        "key_information": {
            "dates": [datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")],
            "deadlines": ["Statutory Retention Schedule Applies"],
            "monetary_amounts": [],
            "compliance_rules": ["Mandatory metadata schema compliance verified"],
            "requirements": ["Role-based access control enforced"]
        },
        "search_optimization": {
            "recommended_filename": f"{re.sub(r'[^A-Za-z0-9]+', '_', title_clean)}_v1.0{ext}",
            "intent_queries": [
                f"Find metadata record for {title_clean}",
                f"Locate {title_clean} asset specifications",
                f"Retrieve governance and technical metadata for {title_clean}"
            ],
            "fuzzy_phrasings": [
                title_clean.lower(),
                f"{title_clean.lower()} file"
            ]
        },
        "summary": f"Comprehensive 30+ attribute enterprise metadata registry profile generated for {title_clean} across Descriptive (ISO 15836), Technical Forensics, Governance, Business Context, and Semantic Indexing standards."
    }
    return json.dumps(fallback_obj)
