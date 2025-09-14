# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Stock & Crypto Chart Service

A Python Flask web application that fetches stock market and cryptocurrency data and generates interactive charts. The application supports both traditional stocks and cryptocurrencies with CLI and web service interfaces.

## Architecture

### Core Components
- **`src/stock_fetcher.py`** - Main data access layer containing `StockFetcher` class with methods for:
  - Yahoo Finance API integration via yfinance for stocks and crypto
  - Stock price retrieval (`get_current_price`, `get_daily_prices`)
  - Cryptocurrency data (`get_crypto_data`, `get_crypto_current_price`)
  - VIX volatility data (`get_vix`, `get_fear_greed_proxy`)
  - Chart generation (`create_price_chart`, `create_vix_chart`, `create_comparison_chart`)
  - Crypto chart generation (`create_crypto_chart`, `create_crypto_comparison_chart`)
  - In-memory chart creation using matplotlib with crypto-specific colors and formatting

- **`app.py`** - Flask web service that serves charts as images and provides REST API:
  - Routes for stock charts, crypto charts, VIX charts, and comparison charts
  - Crypto-specific endpoints (`/crypto/{symbol}`, `/crypto-compare`)
  - Charts generated in-memory using io.BytesIO and served directly as PNG
  - JSON API endpoints for current prices (stocks and crypto) and symbol lists
  - Production-ready with environment variable support

- **`main.py`** - CLI demonstration that fetches data and saves charts to `data/` directory

### Data Flow
1. `StockFetcher` uses yfinance to fetch raw market data as pandas DataFrames
   - Stocks: Direct symbol (e.g., `AAPL`, `GOOGL`)
   - Crypto: Symbol format `{CRYPTO}-USD` (e.g., `BTC-USD`, `ETH-USD`)
2. Chart methods process DataFrames and generate matplotlib figures with custom styling
   - Crypto charts use brand-specific colors (Bitcoin orange #f7931a, Ethereum blue #627eea)
   - Price formatting adapts to crypto price ranges (4 decimals for <$1, 2 for <$100, commas for >$100)
3. Web service serves charts as PNG images directly from memory (no file I/O)
4. CLI saves charts as files in `data/` directory

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv testenv
source testenv/bin/activate  # On Windows: testenv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Local Development
```bash
# Run CLI application (generates charts in data/)
python main.py

# Run web service (access at http://localhost:5000)
python app.py

# Production server (for deployment testing)
gunicorn app:app
```

### Key Dependencies
- `yfinance` - Yahoo Finance API for market data
- `matplotlib` - Chart generation with custom styling
- `flask` - Web framework with in-memory image serving
- `gunicorn` - Production WSGI server for deployment

## Web Service API

### Chart Endpoints (PNG Images)
- `GET /chart/{symbol}?period={period}` - Stock price/volume chart
- `GET /crypto/{symbol}?period={period}` - Cryptocurrency price/volume chart
- `GET /vix?period={period}` - VIX fear index with color-coded zones  
- `GET /compare?symbols=AAPL,GOOGL&period=3mo` - Multi-stock comparison
- `GET /crypto-compare?symbols=BTC,ETH&period=1y` - Multi-crypto comparison

### Data Endpoints (JSON)
- `GET /api/price/{symbol}` - Current stock price
- `GET /api/crypto/{symbol}` - Current cryptocurrency price
- `GET /api/stocks` - Popular stock symbols list
- `GET /api/cryptos` - Popular crypto symbols list

### Chart Features
- **Crypto Support**: BTC, ETH, ADA, DOT, LINK, SOL, DOGE, LTC, XRP, BNB
- **Crypto Colors**: Brand-specific colors (Bitcoin orange, Ethereum blue, etc.)
- **Price Formatting**: Adaptive decimals based on price range
- **VIX Fear Zones**: Color-coded backgrounds (Green: 0-20, Yellow: 20-30, Orange: 30-50, Red: 50+)
- **Comparisons**: Normalized percentage change from starting price
- **Time Periods**: 5d, 1mo, 3mo, 6mo, 1y, 2y
- **Styling**: Professional charts with grids, legends, proper date formatting

## Deployment Configuration

### Production Files
- `Procfile` - Heroku/Railway start command: `web: gunicorn app:app`
- `render.yaml` - Render platform configuration with Python environment
- `runtime.txt` - Python version specification
- `requirements.txt` - Includes gunicorn for production WSGI server

### Environment Variables
- `PORT` - Set automatically by deployment platforms
- `FLASK_ENV` - Controls debug mode (production/development)
- `PYTHONPATH` - Ensures src/ module imports work correctly

### Deployment Platforms
- **Render** - Free tier with GitHub integration
- **Railway** - Auto-detection with $5/month free credit  
- **Heroku** - Classic platform with CLI tools

### Production Considerations  
- Charts generated in-memory (no disk I/O) for scalability
- matplotlib uses 'Agg' backend for headless server environments
- Flask debug mode disabled in production via environment detection

## Development Guidelines

### Task Approach
- Always use TodoWrite tool for planning and tracking multi-step tasks
- Break down complex tasks into manageable steps  
- Mark tasks as in_progress before starting work
- Mark tasks as completed immediately after finishing
- Create follow-up tasks as they are discovered during implementation

### Code Architecture Notes
- `StockFetcher` class is the main data layer - extend here for new data sources
- Chart methods return boolean success/failure - maintain this pattern for new chart types
- Web service uses in-memory chart generation - avoid file I/O for scalability
- All matplotlib figures use `plt.close()` to prevent memory leaks
- Environment variable detection handles dev vs production automatically