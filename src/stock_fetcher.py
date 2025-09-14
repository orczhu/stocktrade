import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

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