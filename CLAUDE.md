# Stock Trading Data Fetcher

A Python application for fetching stock prices and VIX (volatility index) data using Yahoo Finance.

## Project Structure
- `main.py` - Entry point that demonstrates stock data fetching
- `src/stock_fetcher.py` - Core stock data fetching module
- `requirements.txt` - Project dependencies
- `data/` - Directory for storing data files
- `testenv/` - Test environment directory

## Development Commands

### Setup
```bash
pip install -r requirements.txt
```

### Run Application
```bash
python main.py
```

### Dependencies
- yfinance>=0.2.22 - Yahoo Finance API
- pandas>=2.0.0 - Data manipulation
- numpy>=1.24.0 - Numerical computing
- requests>=2.31.0 - HTTP requests
- python-dotenv>=1.0.0 - Environment variables
- matplotlib>=3.7.0 - Data visualization

## Features
- Fetch current stock prices for multiple symbols
- Get VIX (fear index) historical data
- Retrieve detailed daily price data with OHLCV
- Support for various time periods (5d, 1mo, etc.)

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