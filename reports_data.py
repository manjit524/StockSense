"""
================================================================================
 REPORTS_DATA.PY — growth report: how much did SYMBOL move over PERIOD
================================================================================
Uses yfinance historical downloads directly rather than the local backfilled
CSVs, because reports need arbitrary date ranges (1 week to 1 year+) and
yfinance handles that uniformly across NSE (.NS), BSE (.BO), and US tickers
without depending on how far back your local backfill happens to reach.
================================================================================
"""

import io
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

PERIOD_OPTIONS = [
    {"value": "7", "label": "1 Week"},
    {"value": "14", "label": "2 Weeks"},
    {"value": "30", "label": "1 Month"},
    {"value": "90", "label": "3 Months"},
    {"value": "180", "label": "6 Months"},
    {"value": "365", "label": "1 Year"},
]


def _to_yf_ticker(symbol, exchange):
    if exchange == "NSE":
        return f"{symbol}.NS"
    if exchange == "BSE":
        return f"{symbol}.BO"
    return symbol  # US, or already a raw yfinance ticker (crypto, commodities, etc.)


def generate_growth_report(symbol, exchange, period_days):
    """Returns a dict describing price movement over the period, or None if unavailable."""
    yf_ticker = _to_yf_ticker(symbol, exchange)
    period_days = int(period_days)

    end_date = datetime.today()
    start_date = end_date - timedelta(days=period_days + 5)  # buffer for weekends/holidays

    try:
        hist = yf.download(
            yf_ticker,
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d"),
            progress=False,
        )
    except Exception:
        hist = None

    if hist is None or hist.empty:
        return None

    hist = hist.reset_index()
    hist.columns = [c[0] if isinstance(c, tuple) else c for c in hist.columns]
    hist = hist.sort_values("Date")

    start_row = hist.iloc[0]
    end_row = hist.iloc[-1]

    start_price = float(start_row["Close"])
    end_price = float(end_row["Close"])
    abs_change = end_price - start_price
    pct_change = (abs_change / start_price) * 100 if start_price else 0.0

    # Sample down to ~30 points for a compact chart regardless of range length
    step = max(1, len(hist) // 30)
    chart_points = [
        {"date": row["Date"].strftime("%Y-%m-%d"), "price": float(row["Close"])}
        for _, row in hist.iloc[::step].iterrows()
    ]

    return {
        "symbol": symbol,
        "exchange": exchange,
        "period_days": period_days,
        "start_date": start_row["Date"].strftime("%Y-%m-%d"),
        "start_price": start_price,
        "end_date": end_row["Date"].strftime("%Y-%m-%d"),
        "end_price": end_price,
        "abs_change": abs_change,
        "pct_change": pct_change,
        "direction": "up" if pct_change >= 0 else "down",
        "currency": "$" if exchange == "US" else "₹",
        "chart_points": chart_points,
    }


# ==============================================================================
# EXPORTS — PDF and Excel versions of the same report data
# ==============================================================================

def _rows_with_change(report):
    """Turns chart_points into (date, price, change-from-previous) rows."""
    rows = []
    prev = None
    for pt in report["chart_points"]:
        change = (pt["price"] - prev) if prev is not None else None
        rows.append({"date": pt["date"], "price": pt["price"], "change": change})
        prev = pt["price"]
    return rows


def build_pdf_report(report):
    """Returns a BytesIO containing a one-page PDF summary + price table."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, title=f"{report['symbol']} Growth Report")
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"Growth Report — {report['symbol']} ({report['exchange']})", styles["Title"]))
    elements.append(Spacer(1, 8))

    direction_word = "Up" if report["direction"] == "up" else "Down"
    summary = (
        f"Period: {report['period_days']} days &nbsp;&nbsp; "
        f"{report['start_date']} to {report['end_date']}<br/>"
        f"Start price: {report['currency']}{report['start_price']:.2f} &nbsp;&nbsp; "
        f"End price: {report['currency']}{report['end_price']:.2f}<br/>"
        f"Change: {report['currency']}{report['abs_change']:.2f} "
        f"({report['pct_change']:.2f}%) — {direction_word}"
    )
    elements.append(Paragraph(summary, styles["Normal"]))
    elements.append(Spacer(1, 16))

    data = [["Date", "Price", "Change from previous"]]
    for row in _rows_with_change(report):
        change_str = "—" if row["change"] is None else f"{'+' if row['change'] >= 0 else ''}{row['change']:.2f}"
        data.append([row["date"], f"{report['currency']}{row['price']:.2f}", change_str])

    table = Table(data, colWidths=[130, 150, 150])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#141C30")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 16))
    elements.append(Paragraph(
        "Generated from historical price data for educational purposes only — not investment advice.",
        styles["Italic"],
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def build_excel_report(report):
    """Returns a BytesIO containing an .xlsx with a Summary sheet + Price History sheet."""
    buffer = io.BytesIO()

    df = pd.DataFrame(_rows_with_change(report)).rename(
        columns={"date": "Date", "price": "Price", "change": "Change from previous"}
    )
    summary_df = pd.DataFrame([{
        "Symbol": report["symbol"],
        "Exchange": report["exchange"],
        "Period (days)": report["period_days"],
        "Start Date": report["start_date"],
        "Start Price": report["start_price"],
        "End Date": report["end_date"],
        "End Price": report["end_price"],
        "Absolute Change": report["abs_change"],
        "Percent Change": report["pct_change"],
    }])

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="Summary", index=False)
        df.to_excel(writer, sheet_name="Price History", index=False)

    buffer.seek(0)
    return buffer
