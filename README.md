# The Trading Desk (An investment Website)

An AI-powered financial analytics and advisory web application built with Python, Flask, and TensorFlow/Keras. 
This project features real-time/intraday stock tracking, market data analysis, and deep learning prediction models.

---

## 📁 Repository Structure


```text
.
├── static/                         # Frontend static assets (CSS, JavaScript)
│   ├── app.js
│   └── style.css
├── templates/                      # HTML templates (Flask views)
│   ├── about.html
│   ├── base.html
│   ├── contact.html
│   ├── input.html
│   ├── landing.html
│   ├── loading.html
│   ├── login.html
│   ├── markets.html
│   ├── output.html
│   └── reports.html
├── .gitignore                      # Configured to ignore virtualenvs, cache & datasets
├── advisor_engine.py               # Core financial advisory engine logic
├── app.py                          # Main Flask application entrypoint
├── etf_tickers.py                  # ETF data configurations
├── intraday_advisor.py             # Short-term market signals and recommendations
├── intraday_engine.py              # Intraday market data processing engine
├── markets_data.py                 # Market data extraction scripts
├── reports_data.py                 # Report generation utilities
├── sp500_tickers_cache.json        # Cached tickers list
├── stock_advisor_multi_exchange.py # Multi-exchange stock data handling
├── train_model.py                  # Keras model training pipeline
├── us_tickers.py                   # US stock tickers dataset/utility
├── requirements.txt                # Required Python dependencies
└── README.md                       # Project documentation

## 📁 Repository Structure
