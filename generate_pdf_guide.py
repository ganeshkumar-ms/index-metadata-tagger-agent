import os
import sys
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, total_pages):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#5A6B82"))

        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "INDEX · Enterprise Metadata Tagger & Search Optimization")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)

        # Footer (all pages)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(558, 32, page_str)
        self.drawString(54, 32, "Confidential & Enterprise Learning Material · Antigravity AI Engineering")
        self.restoreState()


def build_pdf(filename="INDEX_BEGINNER_STUDY_GUIDE.pdf"):
    out_path = Path(__file__).resolve().parent / filename
    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    PRIMARY = colors.HexColor("#078cff")   # Electric Blue
    SECONDARY = colors.HexColor("#0a3154") # Deep Navy
    ACCENT = colors.HexColor("#0284c7")    # Sky Blue
    DARK_BG = colors.HexColor("#031326")
    LIGHT_BG = colors.HexColor("#F0F7FF")
    CARD_BG = colors.HexColor("#F8FAFC")
    TEXT_MAIN = colors.HexColor("#0F172A")
    TEXT_MUTED = colors.HexColor("#475569")
    SUCCESS = colors.HexColor("#059669")
    BORDER = colors.HexColor("#BAE6FD")

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=PRIMARY,
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=SECONDARY,
        spaceAfter=14,
    )
    h1_style = ParagraphStyle(
        "SectionH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=SECONDARY,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True,
    )
    h2_style = ParagraphStyle(
        "SectionH2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11.5,
        leading=15,
        textColor=PRIMARY,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=TEXT_MAIN,
        spaceAfter=6,
    )
    body_bold = ParagraphStyle(
        "BodyBold",
        parent=body_style,
        fontName="Helvetica-Bold",
    )
    code_style = ParagraphStyle(
        "CodeText",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#0369A1"),
    )
    callout_style = ParagraphStyle(
        "CalloutText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=TEXT_MAIN,
    )

    story = []

    # 1. Cover / Header Banner
    header_data = [
        [
            Paragraph("<b>INDEX · AGENT #3 SPECIFICATION & STUDY GUIDE</b>", ParagraphStyle(
                "TopTag", fontName="Helvetica-Bold", fontSize=9, textColor=PRIMARY, leading=11
            )),
            Paragraph("AWS Cloud Native & TCS BFSI Standard", ParagraphStyle(
                "TopRight", fontName="Helvetica", fontSize=8.5, textColor=TEXT_MUTED, leading=11, alignment=2
            )),
        ]
    ]
    t_header = Table(header_data, colWidths=[300, 204])
    t_header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(t_header)
    story.append(Spacer(1, 6))

    story.append(Paragraph("Enterprise Metadata Tagger & Search Optimization", title_style))
    story.append(Paragraph("Complete Beginner-to-Architect Study Guide: Multi-Dimensional Taxonomy, Dynamic Attributes, Intent-Based Retrieval, and AWS Cloud Native Architecture", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceBefore=0, spaceAfter=12))

    # Executive Summary Card
    summary_text = (
        "<b>What is INDEX?</b> INDEX is the third Content Intelligence Agent in the 10-Agent Library. "
        "It solves the ubiquitous enterprise problem of lost, unfindable knowledge caused by cryptic filenames "
        "(e.g., <i>DOC_48383_FINAL_V2.pdf</i>, <i>Document123.docx</i>). INDEX deeply inspects content to dynamically extract "
        "canonical metadata, domain taxonomies, named entities, governance rules, and fuzzy natural-language retrieval intent queries."
    )
    t_sum = Table([[Paragraph(summary_text, callout_style)]], colWidths=[504])
    t_sum.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
        ("BOX", (0, 0), (-1, -1), 1, BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(t_sum)
    story.append(Spacer(1, 10))

    # Section 1: The Core Question & The Enterprise Problem
    story.append(Paragraph("1. Core Mission & The Problem It Solves", h1_style))
    story.append(Paragraph(
        "<b>The Core Question:</b> <i>&ldquo;What is this content, and how should it be described so people and systems can find it?&rdquo;</i>",
        body_style
    ))
    story.append(Paragraph(
        "In modern enterprises (banks, insurers, cloud engineering teams, healthcare organizations), knowledge workers upload thousands "
        "of documents every single day. Traditional search systems rely on simple filename string matches or crude keyword indexes. "
        "When an engineer names an architecture guide <code>Guide_Final.docx</code>, or an adjuster names a claim standard <code>Doc_9831.pdf</code>, "
        "that document effectively becomes invisible to everyone else in the company.",
        body_style
    ))

    # Comparison Table
    prob_data = [
        [Paragraph("<b>Before INDEX (Legacy Chaotic Storage)</b>", body_bold), Paragraph("<b>After INDEX (Intelligent Multi-Dimensional Index)</b>", body_bold)],
        [
            Paragraph("• Cryptic filenames: <code>DOC_48383_FINAL_V2.pdf</code><br/>"
                      "• Search fails on natural queries like <i>'moter clam settle doc'</i><br/>"
                      "• Zero understanding of document domain, roles, or rules<br/>"
                      "• Impossible to catalog or govern across CMS repositories", body_style),
            Paragraph("• Canonical standardized filename: <code>Motor_Claim_Settlement_Standard_Procedure_2026.pdf</code><br/>"
                      "• Fuzzy intent mapping links typos and natural queries directly<br/>"
                      "• Dynamic taxonomy adapts to document type (AWS vs HR vs Claim)<br/>"
                      "• 100% structured JSON export ready for enterprise CMS/OpenSearch", body_style)
        ]
    ]
    t_prob = Table(prob_data, colWidths=[246, 258])
    t_prob.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#FEF2F2")),
        ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#F0FDF4")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t_prob)
    story.append(Spacer(1, 12))

    # Section 2: The 7-Layer Metadata Architecture
    story.append(Paragraph("2. The 7-Layer Metadata Architecture", h1_style))
    story.append(Paragraph(
        "INDEX doesn't just generate basic tags. It executes a comprehensive 7-layer extraction pipeline:",
        body_style
    ))

    layers_data = [
        [Paragraph("<b>Layer</b>", code_style), Paragraph("<b>Target Fields</b>", code_style), Paragraph("<b>Enterprise Purpose & Description</b>", code_style)],
        [
            Paragraph("<b>1. Basic</b>", body_style),
            Paragraph("Title, Document Type, Language, Target Audience, Owner, Version", body_style),
            Paragraph("Standardizes document identity, ownership, and target reading personas.", body_style)
        ],
        [
            Paragraph("<b>2. Business</b>", body_style),
            Paragraph("Domain, Subdomain, Process Area, Product/Service, Business Function", body_style),
            Paragraph("Places the content precisely within the organizational taxonomy matrix.", body_style)
        ],
        [
            Paragraph("<b>3. Content</b>", body_style),
            Paragraph("Core Topic, Subtopics, Keywords (6-12), Dynamic Tags, Concepts", body_style),
            Paragraph("Generates multi-grain semantic tags for vector and keyword search engines.", body_style)
        ],
        [
            Paragraph("<b>4. Entities</b>", body_style),
            Paragraph("Organizations, Systems/Tools, Products, Roles, Regulations/Standards", body_style),
            Paragraph("Extracts concrete entities (e.g., AWS Lambda, PCI-DSS, Claims Adjuster).", body_style)
        ],
        [
            Paragraph("<b>5. Key Info</b>", body_style),
            Paragraph("Dates, Deadlines, Monetary Amounts, Compliance Rules, Requirements", body_style),
            Paragraph("Captures critical governance constraints, SLA timelines, and obligations.", body_style)
        ],
        [
            Paragraph("<b>6. Dynamic</b>", body_style),
            Paragraph("Adaptable Key-Value dictionary tailored to specific document type", body_style),
            Paragraph("<b>Domain Agnostic:</b> AWS cloud doc produces Services/Database; HR produces Leave Type/SLA; Insurance produces Claim Type/Deductible.", body_style)
        ],
        [
            Paragraph("<b>7. Search Opt</b>", body_style),
            Paragraph("Recommended Filename, Intent Queries, Fuzzy Shorthand Mappings", body_style),
            Paragraph("Solves retrieval typos (e.g. <i>'moter clam settle doc'</i> &rarr; Motor Claim Settlement).", body_style)
        ],
    ]
    t_layers = Table(layers_data, colWidths=[70, 160, 274])
    t_layers.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E0F2FE")),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_layers)
    story.append(Spacer(1, 12))

    # Section 3: Dynamic Domain Adaptability (AWS vs HR vs BFSI)
    story.append(Paragraph("3. Dynamic Domain Adaptability (Non-BFSI Agnostic)", h1_style))
    story.append(Paragraph(
        "Crucially, <b>INDEX is not restricted to banking or finance.</b> It intelligently shifts its metadata extraction "
        "strategy depending on the nature of the document:",
        body_style
    ))

    adapt_data = [
        [Paragraph("<b>Content Type</b>", body_bold), Paragraph("<b>Sample Extracted Dynamic Metadata</b>", body_bold), Paragraph("<b>Recommended Filename</b>", body_bold)],
        [
            Paragraph("<b>AWS Technical Doc</b>", body_style),
            Paragraph("Platform: AWS<br/>Architecture: Serverless Event-Driven<br/>Services: Lambda, API Gateway<br/>Database: DynamoDB", code_style),
            Paragraph("<code>AWS_Serverless_Architecture_Specification_v2.0.pdf</code>", code_style)
        ],
        [
            Paragraph("<b>HR Leave Policy</b>", body_style),
            Paragraph("Domain: Human Resources<br/>Leave Type: Annual / Paid Time Off<br/>Approval Window: 48 Hours<br/>Audience: Full-Time Employees", code_style),
            Paragraph("<code>Employee_Leave_and_Absence_Policy_v2.0.pdf</code>", code_style)
        ],
        [
            Paragraph("<b>Auto Insurance Notice</b>", body_style),
            Paragraph("Domain: BFSI / Insurance<br/>Claim Type: Motor Vehicle<br/>Deductible: $500<br/>Settlement SLA: 7 Business Days", code_style),
            Paragraph("<code>Motor_Claim_Settlement_Standard_Procedure_2026.pdf</code>", code_style)
        ],
    ]
    t_adapt = Table(adapt_data, colWidths=[110, 204, 190])
    t_adapt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT_BG),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_adapt)
    story.append(Spacer(1, 12))

    # Section 4: Enterprise UI Standards & Bug Fixes
    story.append(Paragraph("4. Enterprise UI Standards & Design Architecture", h1_style))
    story.append(Paragraph(
        "INDEX inherits and guarantees all user experience principles perfected through TAXORA and CLARIA:",
        body_style
    ))
    story.append(Paragraph(
        "• <b>Hover-Only Sidebar Actions:</b> The Edit Pencil and Delete Trashcan icons are hidden by default (<code>opacity: 0</code>) "
        "and smoothly appear only when hovering over a conversation row (<code>opacity: 1</code>).<br/>"
        "• <b>Click-to-Edit Conversation Title:</b> The header conversation title is directly clickable to rename in-place. "
        "There is NO clunky pencil icon cluttering the header bar.<br/>"
        "• <b>Single Scrollbar Viewport:</b> The entire application is locked to <code>100dvh</code> (<code>overflow: hidden</code>). "
        "Only the chat messages pane and history list scroll independently with a customized thin 6px scrollbar.<br/>"
        "• <b>Smart Response Auto-Scroll:</b> When switching conversations, the viewport starts instantly at the <b>TOP</b> (<code>top: 0</code>). "
        "When a new AI response arrives, smooth scrolling focuses directly on the <b>TOP of the AI Result Card</b>, rather than dumping the user at the footer.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # Section 5: AWS Cloud Native Architecture & Deployment
    story.append(Paragraph("5. AWS Cloud-Native Production Architecture", h1_style))
    story.append(Paragraph(
        "INDEX runs serverlessly on enterprise-grade AWS infrastructure for sub-second latency and zero idle compute costs:",
        body_style
    ))

    aws_data = [
        [Paragraph("<b>Component</b>", body_bold), Paragraph("<b>AWS Service & Resource Name</b>", body_bold), Paragraph("<b>Configuration Details</b>", body_bold)],
        [
            Paragraph("AI Reasoning Engine", body_style),
            Paragraph("Amazon Bedrock (Nova Pro)", code_style),
            Paragraph("<code>us.amazon.nova-pro-v1:0</code> via Converse API. Zero model disclosure. PCI-DSS masked.", body_style)
        ],
        [
            Paragraph("Backend API Compute", body_style),
            Paragraph("AWS Lambda (Python 3.11)", code_style),
            Paragraph("<code>index-backend-api</code> (Memory: 512MB, Timeout: 120s, Multipart support).", body_style)
        ],
        [
            Paragraph("API Gateway", body_style),
            Paragraph("HTTP API Gateway", code_style),
            Paragraph("<code>index-http-api</code>. Fully CORS-enabled, integrated with Lambda proxy.", body_style)
        ],
        [
            Paragraph("Static Hosting", body_style),
            Paragraph("Amazon S3 Bucket", code_style),
            Paragraph("<code>index-ui-984625844016</code>. Private bucket protected with Origin Access Control.", body_style)
        ],
        [
            Paragraph("Global Edge CDN", body_style),
            Paragraph("AWS CloudFront", code_style),
            Paragraph("OAC distribution routing <code>/api/*</code> to API Gateway and <code>/*</code> to S3.", body_style)
        ],
    ]
    t_aws = Table(aws_data, colWidths=[120, 150, 234])
    t_aws.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT_BG),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_aws)
    story.append(Spacer(1, 14))

    # Verification Footer Callout
    v_text = (
        "<b>Architect Verification Passed:</b> INDEX is fully initialized as a dedicated agent inside "
        "<code>c:\\Users\\ELCOT\\OneDrive\\Desktop\\Agent\\index-metadata-tagger-agent\\</code>. All enterprise guardrails, multi-dimensional schemas, "
        "UI requirements (hover-only edit/delete, click-to-edit title, smart top-scroll), and AWS deployment scripts are verified."
    )
    t_v = Table([[Paragraph(v_text, callout_style)]], colWidths=[504])
    t_v.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ECFDF5")),
        ("BOX", (0, 0), (-1, -1), 1, SUCCESS),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(t_v)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Built PDF guide: {out_path}")
    return str(out_path)


if __name__ == "__main__":
    build_pdf()

