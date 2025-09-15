#!/usr/bin/env python3
"""
Price Alert Management System
Handles alert storage, notification sending, and price monitoring.
"""

import sqlite3
import smtplib
import threading
import time
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import logging
from stock_fetcher import StockFetcher

# Email functionality - simplified for compatibility
import email.message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PriceAlert:
    """Represents a price alert configuration."""
    id: Optional[int] = None
    symbol: str = ""
    asset_type: str = "stock"  # "stock" or "crypto"
    alert_type: str = "above"  # "above" or "below"
    target_price: float = 0.0
    email: str = ""
    phone: Optional[str] = None
    is_active: bool = True
    created_at: Optional[str] = None
    triggered_at: Optional[str] = None
    message: Optional[str] = None

class AlertManager:
    """Manages price alerts and notifications."""
    
    def __init__(self, db_path: str = "alerts.db"):
        """Initialize AlertManager with database path."""
        self.db_path = db_path
        self.fetcher = StockFetcher()
        self.monitoring = False
        self.monitor_thread = None
        
        # Email configuration from environment variables (Render.com compatible)
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_address = os.getenv('EMAIL', os.getenv('EMAIL_ADDRESS', ''))
        self.email_password = os.getenv('APP_KEY', os.getenv('EMAIL_PASSWORD', ''))
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with alerts table."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        asset_type TEXT NOT NULL DEFAULT 'stock',
                        alert_type TEXT NOT NULL,
                        target_price REAL NOT NULL,
                        email TEXT NOT NULL,
                        phone TEXT,
                        is_active BOOLEAN NOT NULL DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        triggered_at TIMESTAMP,
                        message TEXT
                    )
                ''')
                conn.commit()
                logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def create_alert(self, alert: PriceAlert) -> int:
        """Create a new price alert."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    INSERT INTO alerts (symbol, asset_type, alert_type, target_price, 
                                      email, phone, message)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    alert.symbol.upper(),
                    alert.asset_type,
                    alert.alert_type,
                    alert.target_price,
                    alert.email,
                    alert.phone,
                    alert.message
                ))
                alert_id = cursor.lastrowid
                conn.commit()
                logger.info(f"Created alert {alert_id} for {alert.symbol} at ${alert.target_price}")
                return alert_id
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
            raise
    
    def get_alerts(self, email: Optional[str] = None, active_only: bool = False) -> List[PriceAlert]:
        """Get alerts, optionally filtered by email or active status."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = "SELECT * FROM alerts"
                params = []
                
                conditions = []
                if email:
                    conditions.append("email = ?")
                    params.append(email)
                if active_only:
                    conditions.append("is_active = 1")
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                
                query += " ORDER BY created_at DESC"
                
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                alerts = []
                for row in rows:
                    alert = PriceAlert(
                        id=row[0],
                        symbol=row[1],
                        asset_type=row[2],
                        alert_type=row[3],
                        target_price=row[4],
                        email=row[5],
                        phone=row[6],
                        is_active=bool(row[7]),
                        created_at=row[8],
                        triggered_at=row[9],
                        message=row[10]
                    )
                    alerts.append(alert)
                
                return alerts
        except Exception as e:
            logger.error(f"Failed to get alerts: {e}")
            return []
    
    def update_alert(self, alert_id: int, **kwargs) -> bool:
        """Update an existing alert."""
        try:
            if not kwargs:
                return True
            
            # Build dynamic update query
            fields = []
            values = []
            for key, value in kwargs.items():
                if key in ['symbol', 'asset_type', 'alert_type', 'target_price', 
                          'email', 'phone', 'is_active', 'message', 'triggered_at']:
                    fields.append(f"{key} = ?")
                    values.append(value)
            
            if not fields:
                return True
            
            values.append(alert_id)
            query = f"UPDATE alerts SET {', '.join(fields)} WHERE id = ?"
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(query, values)
                conn.commit()
                logger.info(f"Updated alert {alert_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to update alert {alert_id}: {e}")
            return False
    
    def delete_alert(self, alert_id: int) -> bool:
        """Delete an alert."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM alerts WHERE id = ?", (alert_id,))
                conn.commit()
                logger.info(f"Deleted alert {alert_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to delete alert {alert_id}: {e}")
            return False
    
    def send_email_notification(self, alert: PriceAlert, current_price: float) -> bool:
        """Send email notification for triggered alert."""
        if not self.email_address or not self.email_password:
            logger.warning("Email credentials not configured")
            return False
        
        try:
            # Create email message
            msg = email.message.EmailMessage()
            msg['From'] = self.email_address
            msg['To'] = alert.email
            msg['Subject'] = f"🚨 Price Alert: {alert.symbol} - ${current_price:.4f}"
            
            # Email body
            asset_name = "cryptocurrency" if alert.asset_type == "crypto" else "stock"
            direction = "above" if alert.alert_type == "above" else "below"
            
            body = f"""
🎯 Price Alert Triggered!

📊 Symbol: {alert.symbol} ({asset_name})
💰 Current Price: ${current_price:.4f}
🎯 Target Price: ${alert.target_price:.4f}
📈 Condition: Price went {direction} target

💬 Message: {alert.message or 'No additional message.'}

⏰ Alert created: {alert.created_at}
🔔 Triggered: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is an automated notification from your Stock Chart Service.
View charts at: http://localhost:5000/crypto/{alert.symbol.lower()} (if crypto)
            """
            
            msg.set_content(body)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            
            logger.info(f"Email sent to {alert.email} for {alert.symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False
    
    
    def check_alert(self, alert: PriceAlert) -> bool:
        """Check if an alert should be triggered."""
        try:
            # Get current price
            if alert.asset_type == "crypto":
                current_price = self.fetcher.get_crypto_current_price(alert.symbol)
            else:
                current_price = self.fetcher.get_current_price(alert.symbol)
            
            if current_price is None:
                logger.warning(f"Could not fetch price for {alert.symbol}")
                return False

            # Check if alert condition is met
            should_trigger = False
            if alert.alert_type == "above" and current_price >= alert.target_price:
                should_trigger = True
            elif alert.alert_type == "below" and current_price <= alert.target_price:
                should_trigger = True
            if should_trigger:
                logger.info(f"Alert triggered for {alert.symbol}: ${current_price:.4f} {alert.alert_type} ${alert.target_price:.4f}")
                
                # Send email notification
                email_sent = self.send_email_notification(alert, current_price)
                
                if email_sent:
                    # Mark alert as triggered and deactivate
                    self.update_alert(
                        alert.id,
                        is_active=False,
                        triggered_at=datetime.now().isoformat()
                    )
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking alert for {alert.symbol}: {e}")
            return False
    
    def start_monitoring(self, interval_minutes: int = 5):
        """Start background monitoring of price alerts."""
        if self.monitoring:
            logger.info("Monitoring already started")
            return
        
        self.monitoring = True
        
        def monitor_loop():
            logger.info(f"Started price monitoring (interval: {interval_minutes} minutes)")
            
            while self.monitoring:
                try:
                    # Get all active alerts
                    active_alerts = self.get_alerts(active_only=True)
                    
                    if active_alerts:
                        logger.info(f"Checking {len(active_alerts)} active alerts")
                        
                        for alert in active_alerts:
                            if not self.monitoring:  # Check if we should stop
                                break
                            self.check_alert(alert)
                            time.sleep(1)  # Small delay between checks to avoid rate limits
                    
                    # Wait for next check
                    time.sleep(interval_minutes * 60)
                    
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    time.sleep(60)  # Wait 1 minute before retrying
            
            logger.info("Price monitoring stopped")
        
        # Start monitoring in background thread
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop background monitoring."""
        if self.monitoring:
            self.monitoring = False
            logger.info("Stopping price monitoring...")
            if self.monitor_thread:
                self.monitor_thread.join(timeout=10)
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get statistics about alerts."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                stats = {}
                
                # Total alerts
                cursor = conn.execute("SELECT COUNT(*) FROM alerts")
                stats['total_alerts'] = cursor.fetchone()[0]
                
                # Active alerts
                cursor = conn.execute("SELECT COUNT(*) FROM alerts WHERE is_active = 1")
                stats['active_alerts'] = cursor.fetchone()[0]
                
                # Triggered alerts
                cursor = conn.execute("SELECT COUNT(*) FROM alerts WHERE triggered_at IS NOT NULL")
                stats['triggered_alerts'] = cursor.fetchone()[0]
                
                # Alerts by asset type
                cursor = conn.execute("SELECT asset_type, COUNT(*) FROM alerts GROUP BY asset_type")
                stats['by_asset_type'] = dict(cursor.fetchall())
                
                # Recent alerts (last 7 days)
                week_ago = (datetime.now() - timedelta(days=7)).isoformat()
                cursor = conn.execute("SELECT COUNT(*) FROM alerts WHERE created_at >= ?", (week_ago,))
                stats['recent_alerts'] = cursor.fetchone()[0]
                
                return stats
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}