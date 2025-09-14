#!/usr/bin/env python3
"""
Stock Trading Data Fetcher
Fetch daily stock prices and VIX/fear index data
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from stock_fetcher import StockFetcher
import pandas as pd

def main():
    """Main function to demonstrate stock data fetching."""
    
    # Initialize the stock fetcher
    fetcher = StockFetcher()
    
    # Example stocks to fetch
    stocks = ["AAPL", "GOOGL", "MSFT", "TSLA", "SPY"]
    
    print("=== Stock Trading Data Fetcher ===\n")
    
    # Fetch current prices
    print("Current Stock Prices:")
    print("-" * 30)
    for stock in stocks:
        price = fetcher.get_current_price(stock)
        if price:
            print(f"{stock}: ${price:.2f}")
        else:
            print(f"{stock}: Unable to fetch price")
    
    print("\n" + "=" * 40)
    
    # Fetch VIX data
    print("\nFetching VIX (Fear Index) Data:")
    print("-" * 35)
    vix_data = fetcher.get_vix("1mo")  # Last month
    if vix_data is not None and not vix_data.empty:
        latest_vix = vix_data['Close'].iloc[-1]
        print(f"Latest VIX: {latest_vix:.2f}")
        print(f"VIX 1-month high: {vix_data['High'].max():.2f}")
        print(f"VIX 1-month low: {vix_data['Low'].min():.2f}")
    else:
        print("Unable to fetch VIX data")
    
    print("\n" + "=" * 40)
    
    # Example: Get detailed data for a specific stock
    print("\nDetailed AAPL Data (Last 5 Days):")
    print("-" * 35)
    aapl_data = fetcher.get_daily_prices("AAPL", "5d")
    if aapl_data is not None and not aapl_data.empty:
        print(aapl_data[['Open', 'High', 'Low', 'Close', 'Volume']].round(2))
    else:
        print("Unable to fetch AAPL data")

if __name__ == "__main__":
    main()