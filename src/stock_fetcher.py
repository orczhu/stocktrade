import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import os
import ccxt
import numpy as np

class StockFetcher:
    """Fetch stock price data using yfinance."""
    
    def __init__(self):
        self.cache = {}
        # Initialize Binance for buy/sell volume data
        try:
            self.binance = ccxt.binance({
                'sandbox': False,
                'rateLimit': 1200,
                'enableRateLimit': True,
            })
        except Exception as e:
            print(f"Warning: Binance API not available: {e}")
            self.binance = None
    
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
    
    def get_crypto_data(self, crypto_symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """
        Fetch cryptocurrency data for a given symbol.
        
        Args:
            crypto_symbol: Crypto symbol (e.g., 'BTC', 'ETH', 'ADA')
            period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
        
        Returns:
            DataFrame with OHLCV data or None if error
        """
        try:
            # Convert crypto symbol to Yahoo Finance format
            yf_symbol = f"{crypto_symbol.upper()}-USD"
            ticker = yf.Ticker(yf_symbol)
            data = ticker.history(period=period)
            return data
        except Exception as e:
            print(f"Error fetching crypto data for {crypto_symbol}: {e}")
            return None
    
    def get_crypto_current_price(self, crypto_symbol: str) -> Optional[float]:
        """
        Get current cryptocurrency price.
        
        Args:
            crypto_symbol: Crypto symbol (e.g., 'BTC', 'ETH')
            
        Returns:
            Current price in USD or None if error
        """
        try:
            yf_symbol = f"{crypto_symbol.upper()}-USD"
            ticker = yf.Ticker(yf_symbol)
            info = ticker.info
            return info.get('regularMarketPrice') or info.get('currentPrice')
        except Exception as e:
            print(f"Error getting current price for {crypto_symbol}: {e}")
            return None
    
    def create_crypto_chart(self, crypto_symbol: str, period: str = "1y", save_path: str = None) -> bool:
        """
        Create a cryptocurrency price chart.
        
        Args:
            crypto_symbol: Crypto symbol (e.g., 'BTC', 'ETH')
            period: Time period for data
            save_path: Optional path to save chart (saves to data/ if None)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            data = self.get_crypto_data(crypto_symbol, period)
            if data is None or data.empty:
                print(f"No data available for {crypto_symbol}")
                return False
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), height_ratios=[3, 1])
            
            # Price chart with crypto-specific styling
            ax1.plot(data.index, data['Close'], label=f'{crypto_symbol.upper()} Price', linewidth=2.5, color='#f7931a')  # Bitcoin orange
            ax1.fill_between(data.index, data['Low'], data['High'], alpha=0.2, color='#f7931a', label='Daily Range')
            ax1.set_title(f'{crypto_symbol.upper()}/USD Price - {period.upper()}', fontsize=16, fontweight='bold')
            ax1.set_ylabel('Price (USD)', fontsize=12)
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Format price with appropriate decimals
            current_price = data['Close'].iloc[-1]
            if current_price < 1:
                ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:.4f}'))
            elif current_price < 100:
                ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:.2f}'))
            else:
                ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            
            # Volume chart
            ax2.bar(data.index, data['Volume'], alpha=0.7, color='#627eea')  # Ethereum blue
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
                save_path = f'data/{crypto_symbol.upper()}_chart_{period}.png'
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"Crypto chart saved: {save_path}")
            return True
            
        except Exception as e:
            print(f"Error creating crypto chart for {crypto_symbol}: {e}")
            return False
    
    def create_crypto_comparison_chart(self, crypto_symbols: List[str], period: str = "1y", save_path: str = None) -> bool:
        """
        Create a comparison chart for multiple cryptocurrencies (normalized).
        
        Args:
            crypto_symbols: List of crypto symbols to compare (e.g., ['BTC', 'ETH', 'ADA'])
            period: Time period for data
            save_path: Optional path to save chart (saves to data/ if None)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Crypto-specific colors
            crypto_colors = {
                'BTC': '#f7931a',    # Bitcoin orange
                'ETH': '#627eea',    # Ethereum blue
                'ADA': '#0033ad',    # Cardano blue
                'DOT': '#e6007a',    # Polkadot magenta
                'LINK': '#375bd2',   # Chainlink blue
                'SOL': '#9945ff',    # Solana purple
                'DOGE': '#c2a633',   # Dogecoin yellow
                'LTC': '#bfbbbb',    # Litecoin silver
            }
            
            default_colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24', '#f0932b', '#eb4d4b', '#6c5ce7', '#a29bfe']
            
            for i, crypto_symbol in enumerate(crypto_symbols):
                data = self.get_crypto_data(crypto_symbol, period)
                if data is not None and not data.empty:
                    # Normalize to starting price (percentage change)
                    normalized = (data['Close'] / data['Close'].iloc[0] - 1) * 100
                    color = crypto_colors.get(crypto_symbol.upper(), default_colors[i % len(default_colors)])
                    ax.plot(data.index, normalized, label=f"{crypto_symbol.upper()}/USD", linewidth=2.5, color=color)
            
            ax.set_title(f'Cryptocurrency Comparison - {period.upper()} (Normalized % Change)', fontsize=16, fontweight='bold')
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
                symbols_str = '_'.join([s.upper() for s in crypto_symbols])
                save_path = f'data/crypto_comparison_{symbols_str}_{period}.png'
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"Crypto comparison chart saved: {save_path}")
            return True
            
        except Exception as e:
            print(f"Error creating crypto comparison chart: {e}")
            return False
    
    def get_crypto_buy_sell_data(self, crypto_symbol: str, timeframe: str = '1d', limit: int = 100) -> Optional[pd.DataFrame]:
        """
        Get crypto data with buy/sell volume analysis using Binance API.
        
        Args:
            crypto_symbol: Crypto symbol (e.g., 'BTC', 'ETH')
            timeframe: Timeframe ('1h', '4h', '1d')
            limit: Number of candles to fetch
            
        Returns:
            DataFrame with OHLCV data plus buy/sell volume analysis
        """
        if not self.binance:
            return None
            
        try:
            # Convert symbol format for Binance
            binance_symbol = f"{crypto_symbol.upper()}/USDT"
            
            # Fetch OHLCV data
            ohlcv = self.binance.fetch_ohlcv(binance_symbol, timeframe, limit=limit)
            
            if not ohlcv:
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Fetch recent trades to calculate buy/sell volume
            trades = self.binance.fetch_trades(binance_symbol, limit=1000)
            
            # Analyze buy/sell pressure based on trade data
            # Approximation: trades at ask price = buys, trades at bid price = sells
            buy_volume = []
            sell_volume = []
            
            for i, row in df.iterrows():
                period_start = i
                period_end = i + pd.Timedelta(hours=24 if timeframe == '1d' else 1)
                
                # Filter trades for this period
                period_trades = [t for t in trades if period_start <= pd.to_datetime(t['datetime']) < period_end]
                
                if period_trades:
                    # Simple heuristic: if trade price > mid-price, it's likely a buy
                    mid_price = (row['high'] + row['low']) / 2
                    period_buy_vol = sum(t['amount'] for t in period_trades if t['price'] >= mid_price)
                    period_sell_vol = sum(t['amount'] for t in period_trades if t['price'] < mid_price)
                else:
                    # Fallback: estimate based on price movement
                    price_change = (row['close'] - row['open']) / row['open']
                    if price_change > 0:
                        # Price went up - more buying pressure
                        period_buy_vol = row['volume'] * 0.6
                        period_sell_vol = row['volume'] * 0.4
                    else:
                        # Price went down - more selling pressure
                        period_buy_vol = row['volume'] * 0.4
                        period_sell_vol = row['volume'] * 0.6
                
                buy_volume.append(period_buy_vol)
                sell_volume.append(period_sell_vol)
            
            df['buy_volume'] = buy_volume
            df['sell_volume'] = sell_volume
            df['buy_sell_ratio'] = df['buy_volume'] / df['sell_volume']
            df['net_volume'] = df['buy_volume'] - df['sell_volume']
            
            # Rename columns to match yfinance format
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'BuyVolume', 'SellVolume', 'BuySellRatio', 'NetVolume']
            
            return df
            
        except Exception as e:
            print(f"Error fetching buy/sell data for {crypto_symbol}: {e}")
            return None
    
    def create_crypto_chart_with_buysell(self, crypto_symbol: str, period: str = "1y", save_path: str = None) -> bool:
        """
        Create a cryptocurrency chart with buy/sell volume analysis.
        
        Args:
            crypto_symbol: Crypto symbol (e.g., 'BTC', 'ETH')
            period: Time period for data
            save_path: Optional path to save chart (saves to data/ if None)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Try to get buy/sell data first
            timeframe_map = {
                '5d': ('1h', 120),
                '1mo': ('4h', 180),
                '3mo': ('1d', 90),
                '6mo': ('1d', 180),
                '1y': ('1d', 365),
                '2y': ('1d', 730)
            }
            
            timeframe, limit = timeframe_map.get(period, ('1d', 100))
            data = self.get_crypto_buy_sell_data(crypto_symbol, timeframe, limit)
            
            # Fallback to regular data if buy/sell data not available
            if data is None or data.empty:
                print(f"Buy/sell data not available, using regular volume data for {crypto_symbol}")
                data = self.get_crypto_data(crypto_symbol, period)
                if data is None or data.empty:
                    print(f"No data available for {crypto_symbol}")
                    return False
                has_buysell = False
            else:
                has_buysell = True
            
            fig, axes = plt.subplots(3 if has_buysell else 2, 1, figsize=(12, 12 if has_buysell else 10))
            if not has_buysell:
                axes = [axes[0], axes[1]]
            else:
                axes = [axes[0], axes[1], axes[2]]
            
            # Price chart
            axes[0].plot(data.index, data['Close'], label=f'{crypto_symbol.upper()}/USD Price', linewidth=2.5, color='#f7931a')
            axes[0].fill_between(data.index, data['Low'], data['High'], alpha=0.2, color='#f7931a', label='Daily Range')
            axes[0].set_title(f'{crypto_symbol.upper()}/USD Price - {period.upper()}', fontsize=16, fontweight='bold')
            axes[0].set_ylabel('Price (USD)', fontsize=12)
            axes[0].legend()
            axes[0].grid(True, alpha=0.3)
            
            # Format price
            current_price = data['Close'].iloc[-1]
            if current_price < 1:
                axes[0].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:.4f}'))
            elif current_price < 100:
                axes[0].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:.2f}'))
            else:
                axes[0].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            
            if has_buysell:
                # Buy/Sell Volume chart
                buy_bars = axes[1].bar(data.index, data['BuyVolume'], alpha=0.8, color='#00ff88', label='Buy Volume', width=0.8)
                sell_bars = axes[1].bar(data.index, -data['SellVolume'], alpha=0.8, color='#ff4444', label='Sell Volume', width=0.8)
                axes[1].set_title('Buy/Sell Volume Analysis', fontsize=14, fontweight='bold')
                axes[1].set_ylabel('Volume', fontsize=12)
                axes[1].legend()
                axes[1].grid(True, alpha=0.3)
                axes[1].axhline(y=0, color='black', linestyle='-', alpha=0.5)
                
                # Add buy/sell ratio as text
                avg_ratio = data['BuySellRatio'].mean()
                ratio_color = '#00ff88' if avg_ratio > 1 else '#ff4444'
                axes[1].text(0.02, 0.95, f'Avg Buy/Sell Ratio: {avg_ratio:.2f}', 
                           transform=axes[1].transAxes, fontsize=12, fontweight='bold',
                           bbox=dict(boxstyle='round', facecolor=ratio_color, alpha=0.2))
                
                # Net Volume (Buy - Sell) chart
                net_positive = data['NetVolume'] >= 0
                axes[2].bar(data.index[net_positive], data['NetVolume'][net_positive], 
                           alpha=0.8, color='#00ff88', label='Net Buying', width=0.8)
                axes[2].bar(data.index[~net_positive], data['NetVolume'][~net_positive], 
                           alpha=0.8, color='#ff4444', label='Net Selling', width=0.8)
                axes[2].set_title('Net Volume (Buy - Sell)', fontsize=14, fontweight='bold')
                axes[2].set_ylabel('Net Volume', fontsize=12)
                axes[2].set_xlabel('Date', fontsize=12)
                axes[2].legend()
                axes[2].grid(True, alpha=0.3)
                axes[2].axhline(y=0, color='black', linestyle='-', alpha=0.5)
            else:
                # Regular total volume chart
                axes[1].bar(data.index, data['Volume'], alpha=0.7, color='#627eea')
                axes[1].set_title('Volume', fontsize=14)
                axes[1].set_ylabel('Volume', fontsize=12)
                axes[1].set_xlabel('Date', fontsize=12)
                axes[1].grid(True, alpha=0.3)
            
            # Format dates for all subplots
            for ax in axes:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                ax.xaxis.set_major_locator(mdates.MonthLocator())
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
            
            plt.tight_layout()
            
            # Save chart
            if save_path is None:
                os.makedirs('data', exist_ok=True)
                suffix = "_buysell" if has_buysell else ""
                save_path = f'data/{crypto_symbol.upper()}_chart_{period}{suffix}.png'
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            chart_type = "Buy/Sell analysis" if has_buysell else "regular"
            print(f"Crypto chart with {chart_type} saved: {save_path}")
            return True
            
        except Exception as e:
            print(f"Error creating crypto buy/sell chart for {crypto_symbol}: {e}")
            return False