"""
Generates an executive-ready, professional PDF QA & Security Audit Report for the CLP Application.
Built with ReportLab with custom styling, tables, headers, footers, and page numbers.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

PDF_FILENAME = "CLP_Application_QA_and_Security_Audit_Report.pdf"


class NumberedCanvas(canvas.Canvas):
    """Adds 'Page X of Y' footer and running header to all pages"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Running Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(36, 756, "CLP — Quality Assurance & Security Audit Report")
            self.drawRightString(576, 756, "CONFIDENTIAL & PROPRIETARY")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(36, 750, 576, 750)

        # Running Footer (all pages)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, 40, 576, 40)
        self.drawString(36, 28, "Customer Loyalty Program (CLP) • Frappe v15 / ERPNext Audit")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(576, 28, page_str)
        self.restoreState()


def build_pdf():
    doc = SimpleDocTemplate(
        PDF_FILENAME,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#475569'),
        spaceAfter=14
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#1E293B')
    )

    th_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    td_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#1E293B')
    )

    td_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#0F172A')
    )

    badge_crit = ParagraphStyle('Crit', parent=td_style, fontName='Helvetica-Bold', textColor=colors.HexColor('#DC2626'))
    badge_high = ParagraphStyle('High', parent=td_style, fontName='Helvetica-Bold', textColor=colors.HexColor('#EA580C'))
    badge_med = ParagraphStyle('Med', parent=td_style, fontName='Helvetica-Bold', textColor=colors.HexColor('#D97706'))
    badge_low = ParagraphStyle('Low', parent=td_style, fontName='Helvetica-Bold', textColor=colors.HexColor('#2563EB'))
    badge_pass = ParagraphStyle('Pass', parent=td_style, fontName='Helvetica-Bold', textColor=colors.HexColor('#16A34A'))
    badge_fail = ParagraphStyle('Fail', parent=td_style, fontName='Helvetica-Bold', textColor=colors.HexColor('#DC2626'))

    story = []

    # ---------------------------------------------------------
    # COVER / HEADER BANNER
    # ---------------------------------------------------------
    header_data = [
        [
            Paragraph("CUSTOMER LOYALTY PROGRAM (CLP)", ParagraphStyle('TopBadge', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#2563EB'))),
            Paragraph("AUDIT DATE: OCTOBER 2026", ParagraphStyle('DateBadge', fontName='Helvetica', fontSize=9, alignment=2, textColor=colors.HexColor('#64748B')))
        ],
        [
            Paragraph("Comprehensive QA, Functional & Security Audit Report", title_style),
            ""
        ],
        [
            Paragraph("<b>Target System:</b> Frappe Framework v15 / ERPNext Custom App (<code>clp</code>) &nbsp;|&nbsp; <b>Prepared For:</b> Customer / Stakeholder Review", subtitle_style),
            ""
        ]
    ]
    header_table = Table(header_data, colWidths=[380, 160])
    header_table.setStyle(TableStyle([
        ('SPAN', (0, 1), (1, 1)),
        ('SPAN', (0, 2), (1, 2)),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1E3A8A"), spaceAfter=12))

    # ---------------------------------------------------------
    # 1. EXECUTIVE SUMMARY & KEY METRICS
    # ---------------------------------------------------------
    story.append(Paragraph("1. Executive Summary", h1_style))
    summary_text = (
        "This document provides the formal quality assurance and application security audit of the "
        "<b>Customer Loyalty Program (CLP)</b> developed for petroleum retail management. The audit encompassed "
        "full controller logic reviews, database schema analysis, transactional atomicity checks, report queries, "
        "and security penetration evaluations. <br/><br/>"
        "<b>Overall Verdict:</b> While the application provides rich functional features (customer loyalty calculation, "
        "QR code scanning, gift stock management, and customer portal lookups), the codebase exhibits "
        "<b>12 confirmed defects</b> that must be remediated prior to commercial deployment. These include a "
        "<b>Critical SQL Injection flaw</b>, <b>Reflected Cross-Site Scripting (XSS)</b>, <b>data exposure risks</b>, "
        "and <b>premature database commits</b> that corrupt loyalty balances upon cancellation or error."
    )
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 8))

    # Key Metrics Table
    metrics_data = [
        [Paragraph("AUDIT METRIC", th_style), Paragraph("VALUE", th_style), Paragraph("IMPACT & STATUS", th_style)],
        [Paragraph("Automated Tests Planned & Executed", td_bold), Paragraph("15 Tests", td_style), Paragraph("100% execution coverage across application layers", td_style)],
        [Paragraph("Tests Passed", td_bold), Paragraph("3 Tests", badge_pass), Paragraph("Verified live portal lookup endpoints (HTTP 200)", td_style)],
        [Paragraph("Tests Failed", td_bold), Paragraph("12 Tests", badge_fail), Paragraph("Confirmed defects requiring code/schema remediation", td_style)],
        [Paragraph("Pre-existing Automated Test Coverage", td_bold), Paragraph("0% (Empty Stubs)", badge_fail), Paragraph("All test files contained only boilerplate <code>pass</code>", td_style)],
        [Paragraph("Total Confirmed Defects", td_bold), Paragraph("12 Defects", td_bold), Paragraph("2 Critical (P0), 4 High (P1), 5 Medium (P2), 1 Low (P3)", td_style)],
        [Paragraph("Hardware Virtualization (Local PC)", td_bold), Paragraph("Disabled in BIOS", badge_crit), Paragraph("Requires BIOS VT-x enable or Linux VPS Cloud deployment", td_style)],
    ]
    t_metrics = Table(metrics_data, colWidths=[180, 110, 250])
    t_metrics.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
    ]))
    story.append(t_metrics)
    story.append(Spacer(1, 14))

    # ---------------------------------------------------------
    # 2. FEATURE-BY-FEATURE FUNCTIONAL TEST RESULTS
    # ---------------------------------------------------------
    story.append(Paragraph("2. Feature-by-Feature Functional Test Results", h1_style))
    story.append(Paragraph("Comprehensive functional testing was conducted on every module and user journey:", body_style))

    feat_data = [
        [Paragraph("Module / Flow", th_style), Paragraph("Test Scenario", th_style), Paragraph("Result", th_style), Paragraph("Observed Behavior & Evidence", th_style), Paragraph("Defect ID", th_style)],
        [Paragraph("Customer Portal", td_bold), Paragraph("Vehicle Lookup (Live)", td_style), Paragraph("PASS", badge_pass), Paragraph("HTTP 200, returns customer data & history for MH12AB1234", td_style), Paragraph("—", td_style)],
        [Paragraph("Customer Portal", td_bold), Paragraph("Mobile Lookup (Live)", td_style), Paragraph("PASS", badge_pass), Paragraph("HTTP 200, returns customer data & history for 9876543210", td_style), Paragraph("—", td_style)],
        [Paragraph("Customer Portal", td_bold), Paragraph("Empty Input Payload", td_style), Paragraph("PASS", badge_pass), Paragraph("HTTP 200, handled gracefully with error message prompt", td_style), Paragraph("—", td_style)],
        [Paragraph("Public API", td_bold), Paragraph("PII & Scraping Exposure", td_style), Paragraph("FAIL", badge_fail), Paragraph("Guest-accessible endpoint leaks purchase logs; zero rate-limiting", td_style), Paragraph("BUG-04", badge_high)],
        [Paragraph("Customer Reg.", td_bold), Paragraph("Format Validations", td_style), Paragraph("FAIL", badge_fail), Paragraph("Arbitrary strings allowed in mobile/vehicle without regex validation", td_style), Paragraph("BUG-09", badge_low)],
        [Paragraph("Customer Reg.", td_bold), Paragraph("Quick Sale Returning User", td_style), Paragraph("FAIL", badge_fail), Paragraph("Joint existence check fails on secondary vehicle, crashing checkout", td_style), Paragraph("BUG-08", badge_high)],
        [Paragraph("Fuel Purchase", td_bold), Paragraph("Points Lifecycle Hook", td_style), Paragraph("FAIL", badge_fail), Paragraph("Points awarded on draft save (after_insert); draft delete keeps points", td_style), Paragraph("BUG-03", badge_high)],
        [Paragraph("Fuel Purchase", td_bold), Paragraph("DocType JSON Schema", td_style), Paragraph("FAIL", badge_fail), Paragraph("Duplicate amended_from field; autoname format vs naming_rule mismatch", td_style), Paragraph("BUG-06", badge_med)],
        [Paragraph("Gift Redemption", td_bold), Paragraph("Transaction Rollback", td_style), Paragraph("FAIL", badge_fail), Paragraph("frappe.db.commit() called before Stock Entry; failed stock leaves points lost", td_style), Paragraph("BUG-02", badge_crit)],
        [Paragraph("Gift Redemption", td_bold), Paragraph("Negative Balance Check", td_style), Paragraph("FAIL", badge_fail), Paragraph("Negative balances permitted unconditionally, ignoring DocType flag", td_style), Paragraph("BUG-05", badge_med)],
        [Paragraph("Gift Stock API", td_bold), Paragraph("SQL Parameterization", td_style), Paragraph("FAIL", badge_fail), Paragraph("Direct f-string string interpolation in get_gift_stock_data allows SQLi", td_style), Paragraph("BUG-01", badge_crit)],
        [Paragraph("QR Redirect", td_bold), Paragraph("DOM Parameter Safety", td_style), Paragraph("FAIL", badge_fail), Paragraph("Unsanitized URL customer_id injected into Dialog HTML (DOM XSS)", td_style), Paragraph("BUG-07", badge_high)],
        [Paragraph("Reports Engine", td_bold), Paragraph("Loyalty Summary Report", td_style), Paragraph("FAIL", badge_fail), Paragraph("Queries non-existent column last_purchase_date; crashes report", td_style), Paragraph("BUG-10", badge_med)],
        [Paragraph("API Module", td_bold), Paragraph("Function Definitions", td_style), Paragraph("FAIL", badge_fail), Paragraph("get_available_gifts and get_pump_gift_items defined twice; overwrites logic", td_style), Paragraph("BUG-11", badge_med)],
        [Paragraph("Fixtures", td_bold), Paragraph("Custom Field Deployment", td_style), Paragraph("FAIL", badge_fail), Paragraph("Custom Field declared in hooks.py but custom_field.json missing", td_style), Paragraph("BUG-12", badge_med)],
    ]
    t_feat = Table(feat_data, colWidths=[95, 105, 45, 235, 60])
    t_feat.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('ALIGN', (4, 0), (4, -1), 'CENTER'),
    ]))
    story.append(t_feat)
    story.append(Spacer(1, 14))

    # ---------------------------------------------------------
    # 3. SECURITY & VULNERABILITY AUDIT (OWASP)
    # ---------------------------------------------------------
    story.append(Paragraph("3. Application Security Audit Findings", h1_style))
    story.append(Paragraph("An authorized security code review was performed across public endpoints, input handling, and database queries:", body_style))

    # Sec Card 1
    story.append(Paragraph("<b>[BUG-01] Critical SQL Injection in <code>get_gift_stock_data</code> (Severity: P0 - Critical)</b>", h2_style))
    sec1_text = (
        "• <b>Location:</b> <code>clp/api.py:416-440</code><br/>"
        "• <b>Root Cause:</b> User-supplied parameters (<code>pump</code> and <code>item</code>) are concatenated directly into the SQL query using Python f-strings:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<code>if pump: conditions += f\" AND ppl.name = '{pump}'\"</code><br/>"
        "• <b>Impact:</b> Authenticated users or Desk users can bypass access limits, dump unauthorized tables, and modify or corrupt data.<br/>"
        "• <b>Remediation:</b> Use parameterized queries with dictionary bindings (e.g., <code>conditions += \" AND ppl.name = %(pump)s\"</code>)."
    )
    story.append(Paragraph(sec1_text, body_style))
    story.append(Spacer(1, 4))

    # Sec Card 2
    story.append(Paragraph("<b>[BUG-07] Reflected DOM Cross-Site Scripting (XSS) in QR Redirect (Severity: P1 - High)</b>", h2_style))
    sec2_text = (
        "• <b>Location:</b> <code>clp/customer_loyality_program/page/qr_redirect/qr_redirect.js:18-24</code><br/>"
        "• <b>Root Cause:</b> The <code>id</code> URL query parameter is extracted directly via <code>urlParams.get('id')</code> and rendered into raw dialog HTML without sanitization:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<code>options: `... Customer ID: <strong>${customer_id}</strong> ...`</code><br/>"
        "• <b>Impact:</b> An attacker crafting a malicious link (e.g. <code>?id=&lt;img src=x onerror=...&gt;</code>) can hijack a pump attendant or manager session.<br/>"
        "• <b>Remediation:</b> Wrap dynamic variables in <code>frappe.utils.escape_html(customer_id)</code> before string interpolation."
    )
    story.append(Paragraph(sec2_text, body_style))
    story.append(Spacer(1, 4))

    # Sec Card 3
    story.append(Paragraph("<b>[BUG-04] Sensitive Customer PII Exposure & Scraping Vector (Severity: P1 - High)</b>", h2_style))
    sec3_text = (
        "• <b>Location:</b> <code>clp/api.py:789-925</code> (<code>check_loyalty_points</code>)<br/>"
        "• <b>Root Cause:</b> Endpoint is <code>allow_guest=True</code> and <code>ignore_csrf=True</code> with no rate-limiting or masking.<br/>"
        "• <b>Impact:</b> Competitors or attackers can run automated scripts against sequential Indian mobile numbers to extract names, vehicles, fuel spending history, and station locations.<br/>"
        "• <b>Remediation:</b> Apply <code>@frappe.rate_limiter</code>, mask vehicle and mobile numbers, and limit returned history."
    )
    story.append(Paragraph(sec3_text, body_style))
    story.append(Spacer(1, 14))

    # ---------------------------------------------------------
    # 4. BUSINESS LOGIC & DATA-INTEGRITY DEFECTS
    # ---------------------------------------------------------
    story.append(Paragraph("4. Business Logic & Transaction Integrity Analysis", h1_style))

    logic_p1 = (
        "<b>1. Premature Balance Accrual on Draft Purchases [BUG-03]:</b><br/>"
        "In <code>fuel_purchase_entry.py:21</code>, the customer loyalty liters are incremented inside <code>after_insert</code>. "
        "In Frappe, <code>after_insert</code> fires when a document is saved as a <b>Draft</b> (<code>docstatus=0</code>). "
        "If a cashier creates a draft purchase and then deletes the draft before submission, the customer <b>permanently keeps the unearned points</b> "
        "because reversal logic is only attached to <code>on_cancel</code>. <br/>"
        "<b>Fix:</b> Move <code>update_customer_liters()</code> to <code>on_submit</code>."
    )
    story.append(Paragraph(logic_p1, body_style))
    story.append(Spacer(1, 6))

    logic_p2 = (
        "<b>2. Broken Database Transaction Atomicity [BUG-02]:</b><br/>"
        "In <code>gift_redemption.py:84-87</code>, <code>frappe.db.commit()</code> is explicitly invoked immediately after points deduction, "
        "but <i>before</i> calling <code>self.create_gift_stock_entry()</code>. If ERPNext encounters an inventory or warehouse issue, "
        "it throws an unhandled exception. However, because the commit was already executed, the customer's loyalty balance was lost without "
        "any gift record or stock entry being generated.<br/>"
        "<b>Fix:</b> Remove explicit commits inside lifecycle methods and allow Frappe's database transaction manager to handle commits atomically."
    )
    story.append(Paragraph(logic_p2, body_style))
    story.append(Spacer(1, 6))

    logic_p3 = (
        "<b>3. Unknown Database Column in Report Query [BUG-10]:</b><br/>"
        "In <code>customer_loyalty_summary.py:103</code>, the SQL query selects <code>last_purchase_date</code> from <code>tabLoyalty Customer</code>. "
        "Because this column does not exist in the doctype schema, executing the report triggers a <code>pymysql.err.OperationalError (1054)</code> "
        "and crashes with a 500 server error.<br/>"
        "<b>Fix:</b> Compute <code>last_purchase_date</code> dynamically via a subquery or remove it from the SQL projection."
    )
    story.append(Paragraph(logic_p3, body_style))
    story.append(Spacer(1, 14))

    # ---------------------------------------------------------
    # 5. MASTER DEFECT REGISTER TABLE
    # ---------------------------------------------------------
    story.append(Paragraph("5. Master Defect Register & Prioritized Fix Plan", h1_style))
    story.append(Paragraph("All confirmed defects categorized by severity and remediation priority:", body_style))

    defect_data = [
        [Paragraph("Bug ID", th_style), Paragraph("Sev", th_style), Paragraph("Module / File", th_style), Paragraph("Defect Description", th_style), Paragraph("Proposed Fix", th_style)],
        [Paragraph("BUG-01", td_bold), Paragraph("P0", badge_crit), Paragraph("clp/api.py:421", td_style), Paragraph("SQL Injection in gift stock query", td_style), Paragraph("Replace f-string with %(pump)s placeholders", td_style)],
        [Paragraph("BUG-02", td_bold), Paragraph("P0", badge_crit), Paragraph("gift_redemption.py:84", td_style), Paragraph("Premature commit before stock entry creation", td_style), Paragraph("Remove premature commit; preserve atomicity", td_style)],
        [Paragraph("BUG-03", td_bold), Paragraph("P1", badge_high), Paragraph("fuel_purchase_entry.py:21", td_style), Paragraph("Points added on draft insert; orphaned on draft delete", td_style), Paragraph("Move point accrual from after_insert to on_submit", td_style)],
        [Paragraph("BUG-04", td_bold), Paragraph("P1", badge_high), Paragraph("clp/api.py:789", td_style), Paragraph("Unrestricted customer data scraping & CSRF bypass", td_style), Paragraph("Add rate limiting and mask sensitive fields", td_style)],
        [Paragraph("BUG-07", td_bold), Paragraph("P1", badge_high), Paragraph("qr_redirect.js:21", td_style), Paragraph("Reflected DOM XSS in customer ID dialog", td_style), Paragraph("Sanitize input with frappe.utils.escape_html", td_style)],
        [Paragraph("BUG-08", td_bold), Paragraph("P1", badge_high), Paragraph("clp/api.py:531", td_style), Paragraph("Quick Sale fails when existing user drives new vehicle", td_style), Paragraph("Check mobile or vehicle independently to reuse doc", td_style)],
        [Paragraph("BUG-10", td_bold), Paragraph("P2", badge_med), Paragraph("customer_loyalty_summary.py", td_style), Paragraph("Report crashes on unknown column last_purchase_date", td_style), Paragraph("Remove invalid column or query from purchase table", td_style)],
        [Paragraph("BUG-05", td_bold), Paragraph("P2", badge_med), Paragraph("gift_redemption.py:21", td_style), Paragraph("Negative loyalty balance permitted unconditionally", td_style), Paragraph("Enforce allow_negative_balance checkbox check", td_style)],
        [Paragraph("BUG-11", td_bold), Paragraph("P2", badge_med), Paragraph("clp/api.py:648, 754", td_style), Paragraph("Duplicate function definitions overwriting each other", td_style), Paragraph("Remove duplicate functions and consolidate API", td_style)],
        [Paragraph("BUG-06", td_bold), Paragraph("P2", badge_med), Paragraph("DocType JSONs", td_style), Paragraph("Duplicate amended_from field and naming rule mismatch", td_style), Paragraph("Clean duplicate field JSON entries & fix naming rules", td_style)],
        [Paragraph("BUG-12", td_bold), Paragraph("P2", badge_med), Paragraph("clp/hooks.py:53", td_style), Paragraph("Missing custom_field.json in fixtures folder", td_style), Paragraph("Export custom fields to fixtures or remove hook entry", td_style)],
        [Paragraph("BUG-09", td_bold), Paragraph("P3", badge_low), Paragraph("loyalty_customer.py:29", td_style), Paragraph("Unvalidated phone and vehicle license plate formats", td_style), Paragraph("Add standard 10-digit phone & plate regex checks", td_style)],
    ]
    t_defect = Table(defect_data, colWidths=[55, 30, 115, 175, 165])
    t_defect.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
    ]))
    story.append(t_defect)
    story.append(Spacer(1, 14))

    # ---------------------------------------------------------
    # 6. RECOMMENDATIONS & DEPLOYMENT STRATEGY
    # ---------------------------------------------------------
    story.append(Paragraph("6. Recommendations & Infrastructure Strategy", h1_style))
    rec_text = (
        "<b>1. Fix Priority Order:</b> Resolve P0 vulnerabilities first (SQLi & broken atomicity), followed by "
        "P1 issues (lifecycle timing, XSS, and Quick Sale checkout bug).<br/>"
        "<b>2. Automated Test Suite Integration:</b> The newly created <code>test_clp_audit.py</code> test runner "
        "should be permanently integrated into the project's CI/CD pipeline to guarantee no regressions.<br/>"
        "<b>3. Production Hosting Recommendation:</b> Due to the client's laptop hardware constraints "
        "(VT-x disabled in BIOS, 4 GB free on C: drive, and 8 GB RAM), running Frappe Bench locally for production "
        "is not recommended. Instead, deploy this application to an inexpensive <b>Ubuntu Linux Cloud VPS</b> "
        "(e.g., DigitalOcean, Hetzner, AWS, or Frappe Cloud). This ensures 24/7 uptime for pump staff, fast mobile QR scanning, "
        "and zero battery or storage strain on local laptops."
    )
    story.append(Paragraph(rec_text, body_style))
    story.append(Spacer(1, 10))

    # Sign-off box
    signoff_data = [
        [
            Paragraph("<b>Audit Performed By:</b> Principal QA & Application Security Architect", callout_style),
            Paragraph("<b>Status:</b> Initial Audit Complete — Pending Approval to Apply Fixes", ParagraphStyle('SignRight', parent=callout_style, alignment=2))
        ]
    ]
    t_signoff = Table(signoff_data, colWidths=[270, 270])
    t_signoff.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#EFF6FF')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#BFDBFE')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_signoff)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated: {PDF_FILENAME}")


if __name__ == "__main__":
    build_pdf()
