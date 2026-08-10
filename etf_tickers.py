"""
================================================================================
 ETF_TICKERS.PY — curated real ETF list
================================================================================
There's no single clean official "list of all ETFs" dataset to pull and
verify the way us_tickers.py does for the S&P 500, so this stays a curated
list of tickers I'm confident are real, rather than padded to a round number.

Rebalanced per feedback: US trimmed to the ~35 most widely-recognized ETFs,
NSE list grown. One honest caveat that explains "some ETFs show no price":
Yahoo Finance's coverage of Indian ETFs is genuinely inconsistent — even a
correctly-spelled NSE ETF ticker sometimes has no data behind it on Yahoo.
That's a data-availability gap, not necessarily a wrong symbol. If a specific
one is consistently blank, it's worth checking its symbol directly on
finance.yahoo.com before assuming the code is broken.
================================================================================
"""

US_ETFS = [
    # Broad market
    {"symbol": "SPY", "label": "S&P 500 ETF Trust"},
    {"symbol": "VOO", "label": "Vanguard S&P 500"},
    {"symbol": "IVV", "label": "iShares Core S&P 500"},
    {"symbol": "VTI", "label": "Vanguard Total Stock Market"},
    {"symbol": "QQQ", "label": "Invesco Nasdaq 100"},
    {"symbol": "DIA", "label": "SPDR Dow Jones Industrial Average"},
    {"symbol": "IWM", "label": "iShares Russell 2000"},
    # International
    {"symbol": "EFA", "label": "iShares MSCI EAFE"},
    {"symbol": "EEM", "label": "iShares MSCI Emerging Markets"},
    {"symbol": "VWO", "label": "Vanguard FTSE Emerging Markets"},
    {"symbol": "INDA", "label": "iShares MSCI India"},
    {"symbol": "FXI", "label": "iShares China Large-Cap"},
    # Sector — SPDR Select Sector (the most widely tracked sector ETF family)
    {"symbol": "XLK", "label": "Technology Select Sector"},
    {"symbol": "XLF", "label": "Financial Select Sector"},
    {"symbol": "XLE", "label": "Energy Select Sector"},
    {"symbol": "XLV", "label": "Health Care Select Sector"},
    {"symbol": "XLY", "label": "Consumer Discretionary Select Sector"},
    {"symbol": "XLP", "label": "Consumer Staples Select Sector"},
    {"symbol": "XLI", "label": "Industrial Select Sector"},
    {"symbol": "XLU", "label": "Utilities Select Sector"},
    {"symbol": "XLC", "label": "Communication Services Select Sector"},
    # Well-known thematic / active
    {"symbol": "SMH", "label": "VanEck Semiconductor"},
    {"symbol": "SOXX", "label": "iShares Semiconductor"},
    {"symbol": "ARKK", "label": "ARK Innovation"},
    {"symbol": "ICLN", "label": "iShares Global Clean Energy"},
    # Dividend / factor
    {"symbol": "SCHD", "label": "Schwab US Dividend Equity"},
    {"symbol": "VYM", "label": "Vanguard High Dividend Yield"},
    {"symbol": "VIG", "label": "Vanguard Dividend Appreciation"},
    # Fixed income
    {"symbol": "AGG", "label": "iShares Core US Aggregate Bond"},
    {"symbol": "BND", "label": "Vanguard Total Bond Market"},
    {"symbol": "TLT", "label": "iShares 20+ Year Treasury Bond"},
    {"symbol": "HYG", "label": "iShares iBoxx High Yield Corporate Bond"},
    # Commodities
    {"symbol": "GLD", "label": "SPDR Gold Shares"},
    {"symbol": "SLV", "label": "iShares Silver Trust"},
    {"symbol": "USO", "label": "United States Oil Fund"},
]

NSE_ETFS = [
    {"symbol": "NIFTYBEES", "label": "Nippon India Nifty 50 ETF"},
    {"symbol": "BANKBEES", "label": "Nippon India Bank Nifty ETF"},
    {"symbol": "JUNIORBEES", "label": "Nippon India Nifty Next 50 ETF"},
    {"symbol": "GOLDBEES", "label": "Nippon India Gold ETF"},
    {"symbol": "SILVERBEES", "label": "Nippon India Silver ETF"},
    {"symbol": "LIQUIDBEES", "label": "Nippon India Liquid ETF"},
    {"symbol": "ITBEES", "label": "Nippon India Nifty IT ETF"},
    {"symbol": "PSUBNKBEES", "label": "Nippon India PSU Bank ETF"},
    {"symbol": "CPSEETF", "label": "CPSE ETF"},
    {"symbol": "ICICINIFTY", "label": "ICICI Prudential Nifty ETF"},
    {"symbol": "HDFCNIFETF", "label": "HDFC Nifty 50 ETF"},
    {"symbol": "SBIETFQLTY", "label": "SBI ETF Quality"},
    {"symbol": "MOM100", "label": "Motilal Oswal Nasdaq 100 ETF"},
    {"symbol": "MAFANG", "label": "Mirae Asset NYSE FANG+ ETF"},
    {"symbol": "ICICIB22", "label": "ICICI Prudential Bharat 22 ETF"},
    {"symbol": "MIDCAPETF", "label": "Nippon India Nifty Midcap 150 ETF"},
    {"symbol": "HNGSNGBEES", "label": "Nippon India Hang Seng BeES ETF"},
]

# Build the combined tracked list used by the Markets page
TRACKED_ETFS = (
    [{"symbol": e["symbol"], "exchange": "US", "label": e["label"]} for e in US_ETFS]
    + [{"symbol": e["symbol"], "exchange": "NSE", "label": e["label"]} for e in NSE_ETFS]
)
