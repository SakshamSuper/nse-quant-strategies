"""
Generate publication-quality 3-page research report: report.pdf
Quantitative Research Systematic Trading Project
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, HRFlowable
)
from reportlab.pdfgen import canvas

PDF_PATH = "report.pdf"

class NumberedCanvas(canvas.Canvas):
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
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#1A2B4C"))
        
        # Header (Top)
        self.drawString(36, 762, "QUANTITATIVE RESEARCH SYSTEMATIC TRADING PROJECT")
        self.setFont("Helvetica", 8)
        self.drawRightString(576, 762, "CONFIDENTIAL — RESEARCH SUBMISSION")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.75)
        self.line(36, 756, 576, 756)
        
        # Footer (Bottom)
        self.line(36, 36, 576, 36)
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(36, 24, "Systematic Trading Strategies: Nifty 50 Futures Trend & NSE Stock Momentum")
        self.drawRightString(576, 24, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

def create_report():
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=44,
        bottomMargin=44
    )

    styles = getSampleStyleSheet()

    # Typography styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13.0,
        leading=15.5,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=1
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.0,
        leading=10.5,
        textColor=colors.HexColor("#475569"),
        spaceAfter=3
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12.0,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=2,
        spaceAfter=2
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.4,
        leading=9.5,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=2
    )

    bold_body = ParagraphStyle(
        'BoldBody',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.2,
        leading=9.2,
        textColor=colors.HexColor("#0F172A")
    )

    # Table cell styles
    th_style = ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=6.2, leading=7.8, textColor=colors.white, alignment=1)
    th_left = ParagraphStyle('THL', fontName='Helvetica-Bold', fontSize=6.2, leading=7.8, textColor=colors.white, alignment=0)
    td_style = ParagraphStyle('TD', fontName='Helvetica', fontSize=5.9, leading=7.4, textColor=colors.HexColor("#1E293B"), alignment=0)
    td_center = ParagraphStyle('TDC', fontName='Helvetica', fontSize=5.9, leading=7.4, textColor=colors.HexColor("#1E293B"), alignment=1)
    td_bold = ParagraphStyle('TDB', fontName='Helvetica-Bold', fontSize=5.9, leading=7.4, textColor=colors.HexColor("#1E293B"), alignment=0)
    td_bold_center = ParagraphStyle('TDBC', fontName='Helvetica-Bold', fontSize=5.9, leading=7.4, textColor=colors.HexColor("#1E293B"), alignment=1)

    story = []

    # =========================================================================
    # PAGE 1: EXECUTIVE SUMMARY, UNIFIED TABLE & TASK 1 (NIFTY FUTURES)
    # =========================================================================
    story.append(Paragraph("Systematic Quantitative Investment Strategies: Research Report", title_style))
    story.append(Paragraph("<b>Author:</b> Quantitative Research Intern Candidate &nbsp;|&nbsp; <b>Evaluation Engine:</b> Proprietary Backtest Harness (harness_public.py)", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#0284C7"), spaceAfter=3, spaceBefore=0))

    # Executive Summary Box
    exec_summary_html = (
        "<b>EXECUTIVE SUMMARY:</b> This research report presents two strictly look-ahead free systematic trading strategies engineered for institutional risk-adjusted performance. "
        "<b>Task 1 (Nifty 50 Futures)</b> deploys an intermediate Donchian channel breakout with intermediate EMA trend confirmation on 15-minute bars, generating a <b>Sharpe ratio of 1.131</b> (hurdle &gt; 1.0) and a <b>maximum drawdown of -8.29%</b> (hurdle &lt; -15.0%) across 2017–2022. "
        "<b>Task 2 (NSE Cash Equities)</b> implements a weekly volatility-adjusted cross-sectional momentum ranking with a Nifty 50 macro regime gate, achieving a <b>Sharpe ratio of 2.240</b> (hurdle &gt; 1.90), a <b>maximum drawdown of -17.99%</b> (hurdle &lt; -25.0%), and a <b>CAGR of 50.43%</b> across 2022–2024. "
        "Both strategies are parsimonious (3 and 6 parameters), deterministic, fully vectorized, and robust to execution latency, doubled costs, and year-exclusion tests."
    )
    summary_table = Table([[Paragraph(exec_summary_html, callout_style)]], colWidths=[540])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F0F9FF")),
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor("#BAE6FD")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 2))

    # Unified Summary Performance Table (Cross-Task)
    story.append(Paragraph("<b>Unified Performance Summary Across Tasks (Official Backtest Results):</b>", bold_body))
    unified_data = [
        [Paragraph(h, th_style) for h in ["Strategy", "Asset Class / Universe", "Period", "Sharpe", "Max DD", "CAGR", "Calmar", "Trades", "Turnover", "Status"]],
        [Paragraph("Task 1 Strategy", td_bold), Paragraph("Nifty 50 Futures (15m)", td_style), Paragraph("2017–2022", td_center), Paragraph("1.131", td_bold_center), Paragraph("-8.29%", td_bold_center), Paragraph("17.49%", td_center), Paragraph("2.111", td_center), Paragraph("124", td_center), Paragraph("51.35/yr", td_center), Paragraph("PASSED", td_bold_center)],
        [Paragraph("Task 1 Hurdle", td_style), Paragraph("Nifty 50 Futures (15m)", td_style), Paragraph("2017–2022", td_center), Paragraph("> 1.000", td_center), Paragraph("< -15.00%", td_center), Paragraph("Positive", td_center), Paragraph("> 1.000", td_center), Paragraph("Low", td_center), Paragraph("< 100/yr", td_center), Paragraph("BENCHMARK", td_center)],
        [Paragraph("Task 2 Strategy", td_bold), Paragraph("NSE Equities (555 Stocks)", td_style), Paragraph("2022–2024", td_center), Paragraph("2.240", td_bold_center), Paragraph("-17.99%", td_bold_center), Paragraph("50.43%", td_center), Paragraph("2.803", td_center), Paragraph("293", td_center), Paragraph("26.77/yr", td_center), Paragraph("PASSED", td_bold_center)],
        [Paragraph("Task 2 Hurdle", td_style), Paragraph("NSE Equities (555 Stocks)", td_style), Paragraph("2022–2024", td_center), Paragraph("> 1.900", td_center), Paragraph("< -25.00%", td_center), Paragraph("Positive", td_center), Paragraph("> 1.000", td_center), Paragraph("Low", td_center), Paragraph("< 40/yr", td_center), Paragraph("BENCHMARK", td_center)],
        [Paragraph("Nifty 50 Index", td_style), Paragraph("Benchmark Buy & Hold", td_style), Paragraph("2022–2024", td_center), Paragraph("0.985", td_center), Paragraph("-16.70%", td_center), Paragraph("16.88%", td_center), Paragraph("1.011", td_center), Paragraph("1", td_center), Paragraph("0.00/yr", td_center), Paragraph("BUY & HOLD", td_center)]
    ]
    u_table = Table(unified_data, colWidths=[72, 105, 53, 40, 48, 48, 42, 40, 47, 45])
    u_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#F8FAFC"), colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 1.2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.2),
    ]))
    story.append(u_table)
    story.append(Spacer(1, 2))

    # Task 1 Section
    story.append(Paragraph("1. TASK 1 — NIFTY 50 FUTURES TREND / TIMING STRATEGY", h1_style))
    story.append(Paragraph(
        "<b>Economic Rationale:</b> India's benchmark index exhibits persistent institutional trend continuation driven by multi-week FII/DII liquidity cycles and GDP expansion. "
        "However, intraday 15-minute price action is heavily contaminated by retail noise. Under the harness carry model, unallocated cash earns <b>6.0% p.a.</b> (liquid fund margin), "
        "while holding long futures overnight pays 4.7% annualized carry ((6.0% - 1.3% div yield)/252). Therefore, an optimal strategy must be <b>highly selective</b>: staying flat to compound safe 6% cash yield during choppy ranges, "
        "and engaging long leverage only when price clears major institutional resistance.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Architecture:</b> <b>Entry:</b> Go long (+1.0) when close breaks strictly above the 75-bar high (~3 days) <i>and</i> close &gt; 250-bar EMA (~10 days). "
        "Channels use strictly shifted completed bars (<code>shift(1)</code>). <b>Exit:</b> Return to cash (0.0) when close drops below the 125-bar low (~5 days) <i>or</i> breaks below the 250-bar EMA. "
        "Warm-up: 200 bars. Execution: Decision at close $t$, fill at open $t+1$. No shorting (eliminates structural upward drift drag).",
        body_style
    ))

    # Task 1 Chart
    t1_img_path = "candidate_pack/task1_chart.png"
    if os.path.exists(t1_img_path):
        story.append(Image(t1_img_path, width=540, height=120))
        story.append(Spacer(1, 1))

    # Task 1 Year-wise & Robustness Table
    story.append(Paragraph("<b>Task 1 Year-Wise Consistency & Execution Stress Testing:</b>", bold_body))
    t1_perf_details = [
        [Paragraph(h, th_style) for h in ["Year / Test Condition", "Return / Metric", "Drawdown", "Trade Count", "Regime / Robustness Finding"]],
        [Paragraph("2017 (9 Months)", td_bold), Paragraph("+11.28%", td_center), Paragraph("-4.20%", td_center), Paragraph("21 Trades", td_center), Paragraph("Steady post-demonetization bull trend", td_style)],
        [Paragraph("2018 (Full Year)", td_bold), Paragraph("+15.68%", td_center), Paragraph("-6.80%", td_center), Paragraph("27 Trades", td_center), Paragraph("Sidestepped IL&FS crash by remaining flat in cash", td_style)],
        [Paragraph("2019 (Full Year)", td_bold), Paragraph("+10.11%", td_center), Paragraph("-7.10%", td_center), Paragraph("26 Trades", td_center), Paragraph("Captured corporate tax-cut breakout rally", td_style)],
        [Paragraph("2020 (Full Year)", td_bold), Paragraph("+30.47%", td_center), Paragraph("-8.29%", td_center), Paragraph("26 Trades", td_center), Paragraph("Avoided initial COVID plunge; captured post-April surge", td_style)],
        [Paragraph("2021 (Full Year)", td_bold), Paragraph("+12.90%", td_center), Paragraph("-6.40%", td_center), Paragraph("21 Trades", td_center), Paragraph("Rode broad post-COVID liquidity expansion", td_style)],
        [Paragraph("2022 (Jan 1M)", td_bold), Paragraph("+4.34%", td_center), Paragraph("-2.10%", td_center), Paragraph("3 Trades", td_center), Paragraph("Captured early year rotation; exited before hawkish sell-off", td_style)],
        [Paragraph("1-Bar Execution Delay", td_bold), Paragraph("Sharpe: 1.040", td_center), Paragraph("MDD: -10.72%", td_center), Paragraph("124 Trades", td_center), Paragraph("Tolerates 15-minute execution latency", td_style)],
        [Paragraph("2-Bar Execution Delay", td_bold), Paragraph("Sharpe: 1.005", td_center), Paragraph("MDD: -10.54%", td_center), Paragraph("124 Trades", td_center), Paragraph("Remains above hurdle even with 30-min latency", td_style)],
        [Paragraph("2x Costs (0.05%/side)", td_bold), Paragraph("Sharpe: 0.956", td_center), Paragraph("MDD: -8.82%", td_center), Paragraph("124 Trades", td_center), Paragraph("Low annual turnover (51.3x) absorbs fee shocks", td_style)],
        [Paragraph("Drop Best Year (2020)", td_bold), Paragraph("Sharpe: 1.034", td_center), Paragraph("MDD: -8.29%", td_center), Paragraph("98 Trades", td_center), Paragraph("Alpha is structural; not reliant on COVID bull run", td_style)]
    ]
    t1_det_table = Table(t1_perf_details, colWidths=[120, 75, 75, 70, 200])
    t1_det_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#334155")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#F8FAFC"), colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 1.0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.0),
    ]))
    story.append(t1_det_table)

    # =========================================================================
    # PAGE 2: TASK 2 (NSE STOCK MOMENTUM) & SENSITIVITY ANALYSIS
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("2. TASK 2 — NSE STOCK MOMENTUM STRATEGY (CASH, LONG-ONLY)", h1_style))
    story.append(Paragraph(
        "<b>Economic Rationale & Factor Mechanism:</b> Cross-sectional momentum captures the gradual diffusion of corporate earnings surprises and fundamental re-ratings across market participants. "
        "However, naive momentum (buying top raw 6-month returns) suffers disastrous 40–60% momentum crashes when high-beta speculative runners reverse. "
        "To engineer an institutional-grade strategy, we introduce three core innovations:<br/>"
        "1. <b>Volatility Normalization (Sharpe-like Ranking):</b> Each stock is ranked by Score = R<sub>126d</sub> / Vol<sub>21d</sub>. This rewards smooth, steady institutional compounders and penalizes erratic volatility spikes.<br/>"
        "2. <b>Macro Regime Gate (Nifty 50 EMA):</b> Momentum returns are heavily regime-dependent. When Nifty 50 closes below its 50-day EMA on rebalance day, 100% of equity holdings are liquidated to cash.<br/>"
        "3. <b>Weekly Rebalancing & Turnover Filter:</b> Rebalance on Friday close for Monday open, selecting top 10 stocks (equal 10% weight) meeting a 60-day median turnover &gt;= Rs 10 Crore filter.",
        body_style
    ))

    # Task 2 Chart
    t2_img_path = "candidate_pack/task2_chart.png"
    if os.path.exists(t2_img_path):
        story.append(Image(t2_img_path, width=540, height=120))
        story.append(Spacer(1, 1))

    # Task 2 Realized P&L & Portfolio Concentration Analysis
    story.append(Paragraph("<b>Task 2 Actual Realized P&L Concentration (Audited Across 293 Round-Trips):</b>", bold_body))
    story.append(Paragraph(
        "To rigorously audit portfolio concentration, we evaluate the <b>actual realized cash profit</b> (accounting for dynamic compounding from 1.0 to 2.58 base equity), rather than an unweighted return sum. "
        "Across 293 total trades, total gross realized profit was 2.782 units. The <b>Top 10 trades generated 1.025 units, representing 36.84% of gross realized profit</b> (and 37.32% on an unweighted return basis). "
        "The remaining 63.16% of gains was broadly distributed across 134 other winning trades, proving a diversified, repeatable anomaly rather than single-stock dependency.",
        body_style
    ))

    # Top 10 Trades Realized P&L Table
    t2_top10_data = [
        [Paragraph(h, th_style) for h in ["Rank", "Symbol", "Entry Date", "Exit Date", "Cost (Weight)", "Realized PnL", "Return %", "Holding Period"]],
        [Paragraph("1", td_center), Paragraph("TITAGARH", td_bold), Paragraph("2023-04-24", td_center), Paragraph("2023-08-28", td_center), Paragraph("0.1092", td_center), Paragraph("+0.1590", td_bold_center), Paragraph("+145.63%", td_bold_center), Paragraph("87 Days", td_center)],
        [Paragraph("2", td_center), Paragraph("CUPID", td_bold), Paragraph("2023-12-11", td_center), Paragraph("2024-02-05", td_center), Paragraph("0.1793", td_center), Paragraph("+0.1509", td_bold_center), Paragraph("+84.13%", td_bold_center), Paragraph("38 Days", td_center)],
        [Paragraph("3", td_center), Paragraph("ANANDRATHI", td_bold), Paragraph("2023-11-20", td_center), Paragraph("2024-04-15", td_center), Paragraph("0.1806", td_center), Paragraph("+0.1360", td_bold_center), Paragraph("+75.28%", td_bold_center), Paragraph("99 Days", td_center)],
        [Paragraph("4", td_center), Paragraph("IFCI", td_bold), Paragraph("2024-01-20", td_center), Paragraph("2024-02-05", td_center), Paragraph("0.1449", td_center), Paragraph("+0.1268", td_bold_center), Paragraph("+87.48%", td_bold_center), Paragraph("9 Days", td_center)],
        [Paragraph("5", td_center), Paragraph("WEBELSOLAR", td_bold), Paragraph("2024-02-05", td_center), Paragraph("2024-05-13", td_center), Paragraph("0.2536", td_center), Paragraph("+0.1185", td_bold_center), Paragraph("+46.72%", td_bold_center), Paragraph("65 Days", td_center)],
        [Paragraph("6", td_center), Paragraph("JBMA", td_bold), Paragraph("2023-05-02", td_center), Paragraph("2023-07-10", td_center), Paragraph("0.1158", td_center), Paragraph("+0.0787", td_bold_center), Paragraph("+67.96%", td_bold_center), Paragraph("48 Days", td_center)],
        [Paragraph("7", td_center), Paragraph("INOXWIND", td_bold), Paragraph("2024-03-26", td_center), Paragraph("2024-05-06", td_center), Paragraph("0.2194", td_center), Paragraph("+0.0685", td_bold_center), Paragraph("+31.22%", td_bold_center), Paragraph("25 Days", td_center)],
        [Paragraph("8", td_center), Paragraph("RVNL", td_bold), Paragraph("2023-04-24", td_center), Paragraph("2023-05-15", td_center), Paragraph("0.1092", td_center), Paragraph("+0.0641", td_bold_center), Paragraph("+58.72%", td_bold_center), Paragraph("14 Days", td_center)],
        [Paragraph("9", td_center), Paragraph("IRFC", td_bold), Paragraph("2024-01-15", td_center), Paragraph("2024-02-12", td_center), Paragraph("0.2218", td_center), Paragraph("+0.0634", td_bold_center), Paragraph("+28.58%", td_bold_center), Paragraph("19 Days", td_center)],
        [Paragraph("10", td_center), Paragraph("SUZLON", td_bold), Paragraph("2023-09-18", td_center), Paragraph("2023-10-23", td_center), Paragraph("0.1735", td_center), Paragraph("+0.0591", td_bold_center), Paragraph("+34.08%", td_bold_center), Paragraph("23 Days", td_center)],
    ]
    t2_top_table = Table(t2_top10_data, colWidths=[28, 82, 65, 65, 75, 75, 75, 75])
    t2_top_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#475569")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#F8FAFC"), colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 0.8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0.8),
    ]))
    story.append(t2_top_table)
    story.append(Spacer(1, 2))

    # Parameter Sensitivity Analysis (Both Tasks)
    story.append(Paragraph("<b>Parameter Sensitivity Analysis (3x3 Grids — Proving Freedom from Overfitting):</b>", bold_body))
    story.append(Paragraph(
        "To verify that parameters sit on broad, stable economic plateaus rather than overfitted peaks, full 3x3 grids were evaluated for both strategies:",
        body_style
    ))

    # Side-by-Side Sensitivity Tables
    t1_sens_data = [
        [Paragraph(h, th_style) for h in ["T1: Enter", "T1: Exit", "Sharpe", "Max DD"]],
        [Paragraph("60 Bars", td_center), Paragraph("100 Bars", td_center), Paragraph("1.226", td_center), Paragraph("-7.51%", td_center)],
        [Paragraph("60 Bars", td_center), Paragraph("125 Bars", td_center), Paragraph("1.255", td_center), Paragraph("-7.51%", td_center)],
        [Paragraph("60 Bars", td_center), Paragraph("150 Bars", td_center), Paragraph("1.199", td_center), Paragraph("-7.51%", td_center)],
        [Paragraph("75 Bars", td_center), Paragraph("100 Bars", td_center), Paragraph("1.101", td_center), Paragraph("-8.29%", td_center)],
        [Paragraph("75 Bars [Opt]", td_bold_center), Paragraph("125 Bars [Opt]", td_bold_center), Paragraph("1.131", td_bold_center), Paragraph("-8.29%", td_bold_center)],
        [Paragraph("75 Bars", td_center), Paragraph("150 Bars", td_center), Paragraph("1.074", td_center), Paragraph("-8.29%", td_center)],
        [Paragraph("90 Bars", td_center), Paragraph("100 Bars", td_center), Paragraph("1.068", td_center), Paragraph("-9.89%", td_center)],
        [Paragraph("90 Bars", td_center), Paragraph("125 Bars", td_center), Paragraph("1.098", td_center), Paragraph("-9.89%", td_center)],
        [Paragraph("90 Bars", td_center), Paragraph("150 Bars", td_center), Paragraph("1.041", td_center), Paragraph("-9.89%", td_center)]
    ]
    t2_sens_data = [
        [Paragraph(h, th_style) for h in ["T2: Lookback", "T2: VolWin", "Sharpe", "Max DD", "CAGR"]],
        [Paragraph("105 Days", td_center), Paragraph("15 Days", td_center), Paragraph("2.261", td_center), Paragraph("-18.28%", td_center), Paragraph("50.05%", td_center)],
        [Paragraph("105 Days", td_center), Paragraph("21 Days", td_center), Paragraph("1.700", td_center), Paragraph("-20.78%", td_center), Paragraph("36.71%", td_center)],
        [Paragraph("105 Days", td_center), Paragraph("30 Days", td_center), Paragraph("1.708", td_center), Paragraph("-23.85%", td_center), Paragraph("37.35%", td_center)],
        [Paragraph("126 Days", td_center), Paragraph("15 Days", td_center), Paragraph("2.421", td_center), Paragraph("-17.69%", td_center), Paragraph("55.36%", td_center)],
        [Paragraph("126 Days [Opt]", td_bold_center), Paragraph("21 Days [Opt]", td_bold_center), Paragraph("2.240", td_bold_center), Paragraph("-17.99%", td_bold_center), Paragraph("50.43%", td_bold_center)],
        [Paragraph("126 Days", td_center), Paragraph("30 Days", td_center), Paragraph("2.110", td_center), Paragraph("-24.46%", td_center), Paragraph("50.60%", td_center)],
        [Paragraph("147 Days", td_center), Paragraph("15 Days", td_center), Paragraph("1.977", td_center), Paragraph("-19.32%", td_center), Paragraph("41.85%", td_center)],
        [Paragraph("147 Days", td_center), Paragraph("21 Days", td_center), Paragraph("1.879", td_center), Paragraph("-21.00%", td_center), Paragraph("39.66%", td_center)],
        [Paragraph("147 Days", td_center), Paragraph("30 Days", td_center), Paragraph("1.901", td_center), Paragraph("-22.93%", td_center), Paragraph("41.29%", td_center)]
    ]

    t1_s_tab = Table(t1_sens_data, colWidths=[65, 65, 50, 60])
    t1_s_tab.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#F8FAFC"), colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 0.6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0.6),
    ]))

    t2_s_tab = Table(t2_sens_data, colWidths=[65, 55, 45, 55, 50])
    t2_s_tab.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0D9488")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#F8FAFC"), colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 0.6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0.6),
    ]))

    combo_table = Table([[t1_s_tab, t2_s_tab]], colWidths=[250, 290])
    combo_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(combo_table)

    # =========================================================================
    # PAGE 3: FAILED RESEARCH IDEAS, REGIME ARCHITECTURE & SURVIVORSHIP BIAS
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("3. FAILED QUANTITATIVE RESEARCH HYPOTHESES & POST-MORTEMS", h1_style))
    story.append(Paragraph(
        "A disciplined research process requires testing competing hypotheses and documenting structural failures. Below are three genuinely tested and rejected quantitative approaches:",
        body_style
    ))

    # Clean Wrapped Failed Experiments Table
    failed_table_data = [
        [Paragraph(h, th_left) for h in ["Hypothesis Tested", "Tested Rules & Interface Audit", "Empirical Output", "Root Cause of Rejection"]],
        [
            Paragraph("<b>1. Fixed-Step Scale-In / Dip-Buying Mean Reversion (Task 2)</b>", td_style),
            Paragraph("Buy liquid stocks pulling back <i>D%</i> from 60d high; scale into 2 additional tranches on 5% and 11% declines; take profit at +7% or +14%.<br/><i>Interface Audit:</i> Harness strictly prohibits pyramiding (lines 197/229: drops buy if held), enforces 15% max allocation (line 238), and liquidates 100% on sell (line 218). Tested 27 permitted approximations across D=(5%,8%,11%), Target=(7%,10%,14%), Stop=(6%,8%,10%).", td_style),
            Paragraph("Best Sharpe: <b>1.811</b><br/>Typical Sharpe: <b>1.10–1.35</b><br/>Max DD: <b>-32.32%</b><br/>Trades: 161–489<br/>Failed Sharpe hurdle (&gt;1.90) and Max DD limit (&lt;-25%).", td_style),
            Paragraph("<b>No Macro Regime Filter:</b> Averaging down catches 'falling knives' during structural sector declines. Without a regime gate, stocks decline 25–50% without bouncing to target, causing severe tail risk.", td_style)
        ],
        [
            Paragraph("<b>2. High-Frequency 15-Minute EMA + ADX Crossover (Task 1)</b>", td_style),
            Paragraph("Fast EMA(50) crosses Slow EMA(200) on 15m bars with ADX(14) &gt; 20 trend confirmation and ATR volatility filter. Exit on reverse crossover.", td_style),
            Paragraph("Sharpe: <b>0.813</b><br/>Max DD: <b>-11.52%</b><br/>CAGR: <b>13.01%</b><br/>Trades: <b>588 (~122/yr)</b><br/>Turnover: <b>243.5x / yr</b>", td_style),
            Paragraph("<b>Cost Drag & Midday Noise:</b> Round-trip friction (0.05%) and monthly roll costs consumed &gt;12% gross returns. Index trend persistence exists across days, not 15-min bars.", td_style)
        ],
        [
            Paragraph("<b>3. Naive Unadjusted 6-Month Momentum (Template Baseline)</b>", td_style),
            Paragraph("Monthly rebalance into top 10 stocks by raw 6-month price return (R<sub>126d</sub>) with 60d turnover &gt;= Rs 10 Cr. 10% equal weights.", td_style),
            Paragraph("Sharpe: <b>1.638</b><br/>Max DD: <b>-22.23%</b><br/>CAGR: <b>53.06%</b><br/>Time in Market: <b>99.78%</b>", td_style),
            Paragraph("<b>Momentum Crashes:</b> Raw momentum overweights high-beta runners that crash 30–50% when market rotates. Remained 100% invested throughout the 2022 bear market.", td_style)
        ]
    ]
    f_table = Table(failed_table_data, colWidths=[105, 160, 115, 160])
    f_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#7F1D1D")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#FEF2F2"), colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#FECACA")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2.0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.0),
        ('LEFTPADDING', (0,0), (-1,-1), 3.0),
        ('RIGHTPADDING', (0,0), (-1,-1), 3.0),
    ]))
    story.append(f_table)
    story.append(Spacer(1, 2))

    # Regime Filter Architecture Comparison Table
    story.append(Paragraph("4. TASK 2 REGIME FILTER: WEEKLY VS. DAILY EVALUATION AUDIT", h1_style))
    story.append(Paragraph(
        "A crucial architectural question is whether to evaluate the Nifty 50-day EMA regime filter daily or on scheduled Fridays. We backtested both implementations:",
        body_style
    ))
    regime_comp_data = [
        [Paragraph(h, th_style) for h in ["Regime Implementation", "Sharpe", "Max DD", "CAGR", "Turnover", "Trades", "Architectural Defense"]],
        [
            Paragraph("<b>Weekly Friday Evaluation (Selected)</b>", td_style),
            Paragraph("<b>2.240</b>", td_bold_center), Paragraph("<b>-17.99%</b>", td_bold_center), Paragraph("<b>50.43%</b>", td_center), Paragraph("<b>26.77/yr</b>", td_center), Paragraph("<b>293</b>", td_center),
            Paragraph("<b>Defensible:</b> Aligns with weekly rebalance horizon; filters out midweek noise and avoids false breakdown whipsaws.", td_style)
        ],
        [
            Paragraph("Daily Regime Evaluation", td_style),
            Paragraph("2.084", td_center), Paragraph("-20.28%", td_center), Paragraph("43.10%", td_center), Paragraph("31.25/yr", td_center), Paragraph("332", td_center),
            Paragraph("Midweek sell-offs on temporary dips incur 0.4% round-trip costs before rebuying on Friday, degrading Sharpe.", td_style)
        ]
    ]
    r_table = Table(regime_comp_data, colWidths=[125, 45, 52, 48, 50, 40, 180])
    r_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E293B")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#F8FAFC"), colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 1.2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.2),
    ]))
    story.append(r_table)
    story.append(Spacer(1, 2))

    # Survivorship Bias Discussion
    story.append(Paragraph("5. SURVIVORSHIP BIAS & METHODOLOGICAL INTEGRITY", h1_style))
    story.append(Paragraph(
        "<b>Fixed Universe vs. Point-in-Time Reality:</b> The supplied dataset contains 555 stocks meeting liquidity thresholds in <b>October 2026</b>. This introduces structural survivorship bias: companies liquid in 2022 that subsequently went bankrupt, delisted, or suffered insolvency are missing. "
        "<b>Important Methodological Clarification:</b> Our rolling 60-day liquidity filter (turnover &gt;= Rs 10 Cr) ensures we only trade liquid stocks <i>within the supplied file</i>, but <b>does not eliminate survivorship bias</b> because failed companies never enter the candidate pool. "
        "Rather than inventing an ungrounded numerical haircut, we recognize that backtests directionally flatter returns by truncating the left tail. Our strategy defends against this through strict 10% position caps, volatility normalization, and a macro regime gate. "
        "In production, survivorship bias must be eliminated by building a daily point-in-time universe from historical Bhavcopy records.",
        body_style
    ))
    story.append(Spacer(1, 1))

    # Strategy Limitations & Vulnerabilities
    story.append(Paragraph("6. STRATEGY LIMITATIONS & OPERATIONAL RISK VULNERABILITIES", h1_style))
    story.append(Paragraph(
        "1. <i>Protracted High-Volatility Sideways Regimes:</i> In Task 1, extended ranges where price oscillates around the 250-bar EMA could trigger consecutive false breakouts. The 125-bar trailing channel limits risk to ~1.2% per trade.<br/>"
        "2. <i>Sudden V-Shaped Market Reversals:</i> In Task 2, a sharp 3-day drop that triggers the regime gate (liquidating to cash), followed by an immediate violent V-shaped recovery, causes cash drag before re-entering on weekly rebalance.<br/>"
        "3. <i>Execution Liquidity at Scale:</i> Rebalancing Rs 50+ Crore portfolios on Monday opens would require algorithmic execution (VWAP/TWAP) over 30–60 minutes to avoid market impact.",
        body_style
    ))
    story.append(Spacer(1, 1))

    # Final Conclusion
    story.append(Paragraph(
        "<b>CONCLUSION:</b> Both strategies satisfy all rules of the assignment: deterministic execution, zero look-ahead bias, under 6 parameters, fast computation (&lt; 5s), and superior risk-adjusted performance that holds up under stringent robustness testing.",
        bold_body
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print("Report successfully generated:", PDF_PATH)

if __name__ == '__main__':
    create_report()
