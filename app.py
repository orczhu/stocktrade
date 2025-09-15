#!/usr/bin/env python3
"""
Stock Chart Web Service
Flask web application to display stock charts
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask, render_template, request, send_file, jsonify
from stock_fetcher import StockFetcher
from alert_manager import AlertManager, PriceAlert
from simple_cro_alert import SimpleCROAlert
from datetime import datetime
import io
import base64
import logging
import sys
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

app = Flask(__name__)
fetcher = StockFetcher()
alert_manager = AlertManager()
cro_alert = SimpleCROAlert()

@app.route('/')
def index():
    """Home page with chart options."""
    return render_template('index.html')

@app.route('/alerts')
def alerts_page():
    """Price alerts management page."""
    return render_template('alerts.html')

@app.route('/chart/<symbol>')
def stock_chart(symbol):
    """Display individual stock chart."""
    period = request.args.get('period', '3mo')
    
    # Generate chart in memory
    data = fetcher.get_daily_prices(symbol, period)
    if data is None or data.empty:
        return jsonify({'error': f'No data available for {symbol}'}), 404
    
    # Create chart
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), height_ratios=[3, 1])
    
    # Price chart
    ax1.plot(data.index, data['Close'], label='Close Price', linewidth=2)
    ax1.fill_between(data.index, data['Low'], data['High'], alpha=0.3, label='Daily Range')
    ax1.set_title(f'{symbol.upper()} Stock Price - {period.upper()}', fontsize=16, fontweight='bold')
    ax1.set_ylabel('Price ($)', fontsize=12)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Volume chart
    ax2.bar(data.index, data['Volume'], alpha=0.7, color='orange')
    ax2.set_title('Volume', fontsize=14)
    ax2.set_ylabel('Volume', fontsize=12)
    ax2.set_xlabel('Date', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save to memory buffer
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()
    
    return send_file(img_buffer, mimetype='image/png')

@app.route('/vix')
def vix_chart():
    """Display VIX fear index chart."""
    period = request.args.get('period', '3mo')
    
    data = fetcher.get_vix(period)
    if data is None or data.empty:
        return jsonify({'error': 'No VIX data available'}), 404
    
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
    
    plt.tight_layout()
    
    # Save to memory buffer
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()
    
    return send_file(img_buffer, mimetype='image/png')

@app.route('/compare')
def comparison_chart():
    """Display stock comparison chart."""
    symbols_param = request.args.get('symbols', 'AAPL,GOOGL,MSFT,TSLA,SPY')
    period = request.args.get('period', '3mo')
    
    symbols = [s.strip().upper() for s in symbols_param.split(',')]
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
    
    for i, symbol in enumerate(symbols):
        data = fetcher.get_daily_prices(symbol, period)
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
    
    plt.tight_layout()
    
    # Save to memory buffer
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()
    
    return send_file(img_buffer, mimetype='image/png')

@app.route('/api/price/<symbol>')
def get_current_price(symbol):
    """API endpoint to get current stock price."""
    price = fetcher.get_current_price(symbol)
    if price:
        return jsonify({'symbol': symbol.upper(), 'price': price})
    else:
        return jsonify({'error': f'Unable to fetch price for {symbol}'}), 404

@app.route('/api/stocks')
def get_stock_list():
    """API endpoint to get popular stock symbols."""
    popular_stocks = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NVDA", "SPY", "QQQ", "IWM"]
    return jsonify({'stocks': popular_stocks})

@app.route('/crypto/<symbol>')
def crypto_chart(symbol):
    """Display individual cryptocurrency chart with buy/sell analysis."""
    period = request.args.get('period', '1y')
    
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
    data = fetcher.get_crypto_buy_sell_data(symbol, timeframe, limit)
    
    # Fallback to regular data if buy/sell data not available
    if data is None or data.empty:
        data = fetcher.get_crypto_data(symbol, period)
        if data is None or data.empty:
            return jsonify({'error': f'No crypto data available for {symbol}'}), 404
        has_buysell = False
    else:
        has_buysell = True
    
    # Create chart with appropriate number of subplots
    fig, axes = plt.subplots(3 if has_buysell else 2, 1, figsize=(12, 12 if has_buysell else 10))
    if not has_buysell:
        axes = [axes[0], axes[1]]
    else:
        axes = [axes[0], axes[1], axes[2]]
    
    # Price chart
    axes[0].plot(data.index, data['Close'], label=f'{symbol.upper()}/USD Price', linewidth=2.5, color='#f7931a')
    axes[0].fill_between(data.index, data['Low'], data['High'], alpha=0.2, color='#f7931a', label='Daily Range')
    axes[0].set_title(f'{symbol.upper()}/USD Price - {period.upper()}', fontsize=16, fontweight='bold')
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
        axes[1].bar(data.index, data['BuyVolume'], alpha=0.8, color='#00ff88', label='Buy Volume', width=0.8)
        axes[1].bar(data.index, -data['SellVolume'], alpha=0.8, color='#ff4444', label='Sell Volume', width=0.8)
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
    
    # Save to memory buffer
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()
    
    return send_file(img_buffer, mimetype='image/png')

@app.route('/crypto-compare')
def crypto_comparison_chart():
    """Display cryptocurrency comparison chart."""
    symbols_param = request.args.get('symbols', 'BTC,ETH,ADA,DOT')
    period = request.args.get('period', '1y')
    
    symbols = [s.strip().upper() for s in symbols_param.split(',')]
    
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
    
    default_colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24', '#f0932b', '#eb4d4b']
    
    for i, symbol in enumerate(symbols):
        data = fetcher.get_crypto_data(symbol, period)
        if data is not None and not data.empty:
            # Normalize to starting price (percentage change)
            normalized = (data['Close'] / data['Close'].iloc[0] - 1) * 100
            color = crypto_colors.get(symbol.upper(), default_colors[i % len(default_colors)])
            ax.plot(data.index, normalized, label=f"{symbol}/USD", linewidth=2.5, color=color)
    
    ax.set_title(f'Cryptocurrency Comparison - {period.upper()} (Normalized % Change)', fontsize=16, fontweight='bold')
    ax.set_ylabel('Percentage Change (%)', fontsize=12)
    ax.set_xlabel('Date', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    
    # Save to memory buffer
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()
    
    return send_file(img_buffer, mimetype='image/png')

@app.route('/api/crypto/<symbol>')
def get_crypto_price(symbol):
    """API endpoint to get current cryptocurrency price."""
    price = fetcher.get_crypto_current_price(symbol)
    if price:
        return jsonify({'symbol': f'{symbol.upper()}/USD', 'price': price})
    else:
        return jsonify({'error': f'Unable to fetch price for {symbol}'}), 404

@app.route('/api/cryptos')
def get_crypto_list():
    """API endpoint to get popular cryptocurrency symbols."""
    popular_cryptos = ["BTC", "ETH", "ADA", "DOT", "LINK", "SOL", "DOGE", "LTC", "XRP", "BNB", "CRO"]
    return jsonify({'cryptos': popular_cryptos})

# Price Alert API Endpoints

@app.route('/api/alerts', methods=['POST'])
def create_alert():
    """Create a new price alert."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['symbol', 'target_price', 'alert_type', 'email']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create alert object
        alert = PriceAlert(
            symbol=data['symbol'].upper(),
            asset_type=data.get('asset_type', 'stock'),
            alert_type=data['alert_type'],
            target_price=float(data['target_price']),
            email=data['email'],
            phone=data.get('phone'),
            message=data.get('message', '')
        )
        
        # Validate alert_type
        if alert.alert_type not in ['above', 'below']:
            return jsonify({'error': 'alert_type must be "above" or "below"'}), 400
        
        # Validate asset_type
        if alert.asset_type not in ['stock', 'crypto']:
            return jsonify({'error': 'asset_type must be "stock" or "crypto"'}), 400
        
        # Create the alert
        alert_id = alert_manager.create_alert(alert)
        
        return jsonify({
            'success': True,
            'alert_id': alert_id,
            'message': f'Alert created for {alert.symbol} at ${alert.target_price}'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': f'Invalid target_price: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to create alert: {str(e)}'}), 500

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get alerts for a specific email."""
    email = request.args.get('email')
    active_only = request.args.get('active_only', 'false').lower() == 'true'
    
    try:
        alerts = alert_manager.get_alerts(email=email, active_only=active_only)
        
        # Convert alerts to JSON-serializable format
        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                'id': alert.id,
                'symbol': alert.symbol,
                'asset_type': alert.asset_type,
                'alert_type': alert.alert_type,
                'target_price': alert.target_price,
                'email': alert.email,
                'phone': alert.phone,
                'is_active': alert.is_active,
                'created_at': alert.created_at,
                'triggered_at': alert.triggered_at,
                'message': alert.message
            })
        
        return jsonify({
            'success': True,
            'alerts': alerts_data,
            'count': len(alerts_data)
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get alerts: {str(e)}'}), 500

@app.route('/api/alerts/<int:alert_id>', methods=['DELETE'])
def delete_alert(alert_id):
    """Delete a specific alert."""
    try:
        success = alert_manager.delete_alert(alert_id)
        if success:
            return jsonify({
                'success': True,
                'message': f'Alert {alert_id} deleted successfully'
            })
        else:
            return jsonify({'error': 'Alert not found'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Failed to delete alert: {str(e)}'}), 500

@app.route('/api/alerts/<int:alert_id>', methods=['PUT'])
def update_alert(alert_id):
    """Update a specific alert."""
    try:
        data = request.get_json()
        
        # Remove fields that shouldn't be updated via API
        allowed_fields = ['target_price', 'alert_type', 'is_active', 'message', 'phone']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # Validate types
        if 'target_price' in update_data:
            update_data['target_price'] = float(update_data['target_price'])
        
        if 'alert_type' in update_data and update_data['alert_type'] not in ['above', 'below']:
            return jsonify({'error': 'alert_type must be "above" or "below"'}), 400
        
        success = alert_manager.update_alert(alert_id, **update_data)
        if success:
            return jsonify({
                'success': True,
                'message': f'Alert {alert_id} updated successfully'
            })
        else:
            return jsonify({'error': 'Alert not found'}), 404
            
    except ValueError as e:
        return jsonify({'error': f'Invalid data: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to update alert: {str(e)}'}), 500

@app.route('/api/alerts/check/<int:alert_id>', methods=['POST'])
def check_alert_now(alert_id):
    """Manually trigger a check for a specific alert."""
    try:
        alerts = alert_manager.get_alerts()
        alert = next((a for a in alerts if a.id == alert_id), None)
        
        if not alert:
            return jsonify({'error': 'Alert not found'}), 404
        
        if not alert.is_active:
            return jsonify({'error': 'Alert is not active'}), 400
        
        triggered = alert_manager.check_alert(alert)
        
        return jsonify({
            'success': True,
            'triggered': triggered,
            'message': 'Alert triggered and notifications sent' if triggered else 'Alert checked but not triggered'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to check alert: {str(e)}'}), 500

@app.route('/api/alerts/stats')
def get_alert_stats():
    """Get alert statistics."""
    try:
        stats = alert_manager.get_alert_statistics()
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get statistics: {str(e)}'}), 500

@app.route('/api/alerts/monitoring', methods=['POST'])
def start_monitoring():
    """Start alert monitoring."""
    try:
        interval = request.get_json().get('interval_minutes', 5)
        alert_manager.start_monitoring(interval)
        return jsonify({
            'success': True,
            'message': f'Alert monitoring started (checking every {interval} minutes)'
        })
    except Exception as e:
        return jsonify({'error': f'Failed to start monitoring: {str(e)}'}), 500

@app.route('/api/alerts/monitoring', methods=['DELETE'])
def stop_monitoring():
    """Stop alert monitoring."""
    try:
        alert_manager.stop_monitoring()
        return jsonify({
            'success': True,
            'message': 'Alert monitoring stopped'
        })
    except Exception as e:
        return jsonify({'error': f'Failed to stop monitoring: {str(e)}'}), 500

@app.route('/keep-alive')
def keep_alive():
    """Keep-alive endpoint to prevent Render from sleeping."""
    return jsonify({
        'status': 'alive',
        'timestamp': datetime.now().isoformat(),
        'cro_monitoring': not cro_alert.alert_sent,
        'next_check': '30 minutes'
    })

if __name__ == '__main__':
    # Configure logging for web service
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)  # Ensure logs go to stdout for Render
        ]
    )
    logger = logging.getLogger(__name__)
    
    # Log configuration status at startup
    logger.info("🚀 CRO Alert System Starting...")
    logger.info(f"📧 Email: {cro_alert.email_address}")
    if cro_alert.email_password:
        logger.info("✅ APP_KEY is configured - Email notifications enabled")
    else:
        logger.warning("❌ APP_KEY is missing - Email notifications disabled")
    logger.info(f"🎯 Target Price: ${cro_alert.target_price:.2f}")
    
    # Start CRO alert monitoring
    logger.info("🔍 Starting CRO alert monitoring...")
    cro_alert.start_monitoring(interval_minutes=2)

    # Get port from environment variable for deployment
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    try:
        logger.info(f"🌐 Starting Flask web service on port {port}")
        app.run(debug=debug_mode, host='0.0.0.0', port=port)
    except KeyboardInterrupt:
        logger.info("⛔ Shutting down...")
        cro_alert.stop_monitoring()
        logger.info("🛑 CRO alert monitoring stopped.")