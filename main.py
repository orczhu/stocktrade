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
    
    print("\n" + "=" * 40)
    
    # Generate charts
    print("\nGenerating Charts:")
    print("-" * 20)
    
    # Individual stock chart
    print("Creating AAPL price chart...")
    fetcher.create_price_chart("AAPL", "3mo")
    
    # VIX chart
    print("Creating VIX fear index chart...")
    fetcher.create_vix_chart("3mo")
    
    # Comparison chart
    print("Creating stock comparison chart...")
    fetcher.create_comparison_chart(stocks, "3mo")
    
    print("\n" + "=" * 40)
    
    # Cryptocurrency functionality
    print("\nCryptocurrency Data:")
    print("-" * 25)
    
    # Popular cryptocurrencies
    cryptos = ["BTC", "ETH", "ADA", "DOT"]
    
    print("Current Crypto Prices:")
    print("-" * 25)
    for crypto in cryptos:
        price = fetcher.get_crypto_current_price(crypto)
        if price:
            if price < 1:
                print(f"{crypto}/USD: ${price:.4f}")
            elif price < 100:
                print(f"{crypto}/USD: ${price:.2f}")
            else:
                print(f"{crypto}/USD: ${price:,.2f}")
        else:
            print(f"{crypto}/USD: Unable to fetch price")
    
    print("\n" + "=" * 40)
    
    # Generate crypto charts
    print("\nGenerating Crypto Charts:")
    print("-" * 30)
    
    # Individual crypto chart
    print("Creating BTC price chart...")
    fetcher.create_crypto_chart("BTC", "1y")
    
    # Crypto comparison chart
    print("Creating crypto comparison chart...")
    fetcher.create_crypto_comparison_chart(cryptos, "1y")
    
    print("\nAll charts saved to 'data/' directory!")
    print("Chart files created:")
    print("- data/AAPL_chart_3mo.png")
    print("- data/VIX_chart_3mo.png") 
    print("- data/comparison_AAPL_GOOGL_MSFT_TSLA_SPY_3mo.png")
    print("- data/BTC_chart_1y.png")
    print("- data/crypto_comparison_BTC_ETH_ADA_DOT_1y.png")

if __name__ == "__main__":
    main()