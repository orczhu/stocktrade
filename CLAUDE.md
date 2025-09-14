# Stock Trading Data Fetcher & Chart Service

A Python application for fetching stock prices and VIX (volatility index) data using Yahoo Finance, with a web service for displaying interactive charts.

## Project Structure
- `main.py` - Entry point that demonstrates stock data fetching and chart generation
- `app.py` - Flask web service for displaying charts in browser
- `src/stock_fetcher.py` - Core stock data fetching and chart generation module
- `templates/index.html` - Web interface for chart service
- `requirements.txt` - Project dependencies
- `data/` - Directory for storing chart files
- `testenv/` - Test environment directory

## Development Commands

### Setup
```bash
pip install -r requirements.txt
```

### Run Command Line Application
```bash
python main.py
```

### Run Web Service
```bash
python app.py
```
Then open http://localhost:5000 in your browser

### Dependencies
- yfinance>=0.2.22 - Yahoo Finance API
- pandas>=2.0.0 - Data manipulation
- numpy>=1.24.0 - Numerical computing
- requests>=2.31.0 - HTTP requests
- python-dotenv>=1.0.0 - Environment variables
- matplotlib>=3.7.0 - Data visualization
- flask>=2.3.0 - Web framework for chart service

## Features

### Command Line Application
- Fetch current stock prices for multiple symbols
- Get VIX (fear index) historical data
- Retrieve detailed daily price data with OHLCV
- Generate and save charts as PNG files
- Support for various time periods (5d, 1mo, 3mo, 6mo, 1y, 2y)

### Web Service Features
- **Interactive Web Interface**: Beautiful web UI for generating charts
- **Individual Stock Charts**: Price trends with volume, customizable time periods
- **VIX Fear Index Charts**: Color-coded fear/greed zones (Low/Moderate/High/Extreme Fear)
- **Stock Comparison Charts**: Compare multiple stocks with normalized percentage changes
- **REST API Endpoints**: Programmatic access to charts and data
- **Real-time Chart Generation**: Charts generated on-demand in memory
- **Popular Stock Quick Access**: One-click access to major stocks (AAPL, GOOGL, etc.)

### API Endpoints
- `GET /` - Main web interface
- `GET /chart/{symbol}?period={period}` - Individual stock chart (PNG)
- `GET /vix?period={period}` - VIX fear index chart (PNG)
- `GET /compare?symbols={symbols}&period={period}` - Stock comparison chart (PNG)
- `GET /api/price/{symbol}` - Current stock price (JSON)
- `GET /api/stocks` - List of popular stock symbols (JSON)

## Development Guidelines

### Task Approach
- Always use TodoWrite tool for planning and tracking multi-step tasks
- Break down complex tasks into manageable steps
- Mark tasks as in_progress before starting work
- Mark tasks as completed immediately after finishing
- Create follow-up tasks as they are discovered during implementation

### Code Standards
- Follow existing code conventions and patterns
- Check imports and dependencies before adding new libraries
- Ensure all changes maintain security best practices
- Never commit secrets or API keys to the repository
- to memorize