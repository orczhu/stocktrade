import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import os

class StockFetcher:
    """Fetch stock price data using yfinance."""
    
    def __init__(self):
        self.cache = {}
    
    def get_daily_prices(self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """
        Fetch daily stock prices for a given symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'GOOGL')
            period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
        
        Returns:
            DataFrame with OHLCV data or None if error
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            return data
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current stock price for a symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Current price or None if error
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return info.get('regularMarketPrice') or info.get('currentPrice')
        except Exception as e:
            print(f"Error getting current price for {symbol}: {e}")
            return None
    
    def get_stock_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive stock information.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with stock info or None if error
        """
        try:
            ticker = yf.Ticker(symbol)
            return ticker.info
        except Exception as e:
            print(f"Error getting info for {symbol}: {e}")
            return None
    
    def get_vix(self, period: str = "1y") -> Optional[pd.DataFrame]:
        """
        Fetch VIX (Volatility Index) data.
        
        Args:
            period: Time period
            
        Returns:
            DataFrame with VIX data or None if error
        """
        return self.get_daily_prices("^VIX", period)
    
    def get_fear_greed_proxy(self, period: str = "1y") -> Optional[pd.DataFrame]:
        """
        Get fear/greed indicators using market proxies.
        Returns VIX and other volatility measures.
        
        Args:
            period: Time period
            
        Returns:
            DataFrame with fear/greed proxy data
        """
        vix_data = self.get_vix(period)
        if vix_data is not None:
            vix_data.columns = [f"VIX_{col}" for col in vix_data.columns]
        return vix_data
    
    def create_price_chart(self, symbol: str, period: str = "1y", save_path: str = None) -> bool:
        """
        Create a price chart for a stock symbol.
        
        Args:
            symbol: Stock symbol
            period: Time period for data
            save_path: Optional path to save chart (saves to data/ if None)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            data = self.get_daily_prices(symbol, period)
            if data is None or data.empty:
                print(f"No data available for {symbol}")
                return False
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), height_ratios=[3, 1])
            
            # Price chart
            ax1.plot(data.index, data['Close'], label='Close Price', linewidth=2)
            ax1.fill_between(data.index, data['Low'], data['High'], alpha=0.3, label='Daily Range')
            ax1.set_title(f'{symbol} Stock Price - {period.upper()}', fontsize=16, fontweight='bold')
            ax1.set_ylabel('Price ($)', fontsize=12)
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Volume chart
            ax2.bar(data.index, data['Volume'], alpha=0.7, color='orange')
            ax2.set_title('Volume', fontsize=14)
            ax2.set_ylabel('Volume', fontsize=12)
            ax2.set_xlabel('Date', fontsize=12)
            ax2.grid(True, alpha=0.3)
            
            # Format dates
            for ax in [ax1, ax2]:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                ax.xaxis.set_major_locator(mdates.MonthLocator())
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
            
            plt.tight_layout()
            
            # Save chart
            if save_path is None:
                os.makedirs('data', exist_ok=True)
                save_path = f'data/{symbol}_chart_{period}.png'
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"Chart saved: {save_path}")
            return True
            
        except Exception as e:
            print(f"Error creating chart for {symbol}: {e}")
            return False
    
    def create_vix_chart(self, period: str = "1y", save_path: str = None) -> bool:
        """
        Create a VIX fear index chart.
        
        Args:
            period: Time period for data
            save_path: Optional path to save chart (saves to data/ if None)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            data = self.get_vix(period)
            if data is None or data.empty:
                print("No VIX data available")
                return False
            
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # VIX chart with fear/greed zones
            ax.plot(data.index, data['Close'], label='VIX Close', linewidth=2, color='red')
            ax.fill_between(data.index, data['Low'], data['High'], alpha=0.3, color='red', label='Daily Range')
            
            # Add fear/greed zones
            ax.axhspan(0, 20, alpha=0.1, color='green', label='Low Fear (0-20)')
            ax.axhspan(20, 30, alpha=0.1, color='yellow', label='Moderate Fear (20-30)')
            ax.axhspan(30, 50, alpha=0.1, color='orange', label='High Fear (30-50)')
            ax.axhspan(50, 100, alpha=0.1, color='red', label='Extreme Fear (50+)')
            
            ax.set_title(f'VIX Fear Index - {period.upper()}', fontsize=16, fontweight='bold')
            ax.set_ylabel('VIX Level', fontsize=12)
            ax.set_xlabel('Date', fontsize=12)
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Format dates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
            
            plt.tight_layout()
            
            # Save chart
            if save_path is None:
                os.makedirs('data', exist_ok=True)
                save_path = f'data/VIX_chart_{period}.png'
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"VIX chart saved: {save_path}")
            return True
            
        except Exception as e:
            print(f"Error creating VIX chart: {e}")
            return False
    
    def create_comparison_chart(self, symbols: List[str], period: str = "1y", save_path: str = None) -> bool:
        """
        Create a comparison chart for multiple stocks (normalized).
        
        Args:
            symbols: List of stock symbols to compare
            period: Time period for data
            save_path: Optional path to save chart (saves to data/ if None)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            
            colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
            
            for i, symbol in enumerate(symbols):
                data = self.get_daily_prices(symbol, period)
                if data is not None and not data.empty:
                    # Normalize to starting price (percentage change)
                    normalized = (data['Close'] / data['Close'].iloc[0] - 1) * 100
                    color = colors[i % len(colors)]
                    ax.plot(data.index, normalized, label=symbol, linewidth=2, color=color)
            
            ax.set_title(f'Stock Comparison - {period.upper()} (Normalized % Change)', fontsize=16, fontweight='bold')
            ax.set_ylabel('Percentage Change (%)', fontsize=12)
            ax.set_xlabel('Date', fontsize=12)
            ax.legend()
            ax.grid(True, alpha=0.3)
            ax.axhline(y=0, color='black', linestyle='--', alpha=0.5)
            
            # Format dates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
            
            plt.tight_layout()
            
            # Save chart
            if save_path is None:
                os.makedirs('data', exist_ok=True)
                symbols_str = '_'.join(symbols)
                save_path = f'data/comparison_{symbols_str}_{period}.png'
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"Comparison chart saved: {save_path}")
            return True
            
        except Exception as e:
            print(f"Error creating comparison chart: {e}")
            return False