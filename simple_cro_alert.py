#!/usr/bin/env python3
"""
Simple CRO Price Alert - No Database Required
Hardcoded to alert when CRO reaches $0.26
"""

import sys
import os
import time
import threading
import smtplib
import email.message
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from src.stock_fetcher import StockFetcher

class SimpleCROAlert:
    """Simple CRO price monitor - no database, just email when target hit."""
    
    def __init__(self):
        self.fetcher = StockFetcher()
        self.target_price = 0.26  # Hardcoded target
        # Read from Render.com environment variables
        self.email_address = os.getenv('EMAIL', 'wangzhuyunabc@gmail.com')
        self.email_password = os.getenv('APP_KEY', '')
        self.alert_sent = False  # Track if we already sent the alert
        self.monitoring = False
        
    def send_alert_email(self, current_price: float) -> bool:
        """Send CRO alert email."""
        try:
            msg = email.message.EmailMessage()
            msg['From'] = self.email_address
            msg['To'] = 'wangzhuyunabc@gmail.com'
            msg['Subject'] = f"🚨 CRO ALERT: ${current_price:.4f} - Target Reached!"
            
            body = f"""
🎉 CRO Price Alert!

📊 Symbol: CRO (Cryptocurrency)
💰 Current Price: ${current_price:.4f}
🎯 Target Price: ${self.target_price:.2f}
📈 Status: TARGET REACHED!

⏰ Alert Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔗 View CRO Chart: http://localhost:5000/crypto/cro

This alert will only be sent once until the system is restarted.
Happy trading! 🚀
            """
            
            msg.set_content(body)
            
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            
            print(f"✅ CRO Alert email sent! ${current_price:.4f}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    def check_cro_price(self) -> bool:
        """Check CRO price and send alert if target reached."""
        try:
            current_price = self.fetcher.get_crypto_current_price("CRO")
            
            if current_price is None:
                print("⚠️  Could not fetch CRO price")
                return False
            
            print(f"📊 CRO: ${current_price:.4f} (target: ${self.target_price:.2f})")
            
            # Check if target reached and we haven't sent alert yet
            if current_price >= self.target_price and not self.alert_sent:
                print(f"🎯 TARGET HIT! CRO reached ${current_price:.4f}")
                
                if self.send_alert_email(current_price):
                    self.alert_sent = True
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error checking CRO price: {e}")
            return False
    
    def start_monitoring(self, interval_minutes: int = 2):
        """Start monitoring CRO price."""
        def monitor_loop():
            print(f"🔍 Starting CRO monitoring (checking every {interval_minutes} minutes)")
            print(f"🎯 Will alert when CRO >= ${self.target_price:.2f}")
            
            while self.monitoring and not self.alert_sent:
                try:
                    self.check_cro_price()
                    
                    if self.alert_sent:
                        print("✅ Alert sent! Monitoring stopped.")
                        break
                        
                    # Wait for next check
                    time.sleep(interval_minutes * 60)
                    
                except Exception as e:
                    print(f"❌ Monitoring error: {e}")
                    time.sleep(60)  # Wait 1 minute before retrying
            
            print("🛑 CRO monitoring stopped")
        
        self.monitoring = True
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        return monitor_thread
    
    def stop_monitoring(self):
        """Stop monitoring."""
        self.monitoring = False

def main():
    """Main function to run CRO alert."""
    print("🚀 Simple CRO Price Alert System")
    print("=" * 40)
    
    # Create alert system
    cro_alert = SimpleCROAlert()
    
    # Show configuration
    email_configured = "✅" if cro_alert.email_password else "❌"
    print(f"📧 Email: {cro_alert.email_address}")
    print(f"🔑 App Key: {email_configured} {'Configured' if cro_alert.email_password else 'Missing (set APP_KEY env var)'}")
    print(f"🎯 Target: ${cro_alert.target_price:.2f}")
    print()
    
    # Check current price first
    print("📊 Checking current CRO price...")
    cro_alert.check_cro_price()
    
    if cro_alert.alert_sent:
        print("🎉 Target already reached! Alert sent.")
        return
    
    # Start monitoring
    monitor_thread = cro_alert.start_monitoring(interval_minutes=2)
    
    try:
        print("\n⌨️  Press Ctrl+C to stop monitoring")
        # Keep main thread alive
        while cro_alert.monitoring and not cro_alert.alert_sent:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping CRO monitoring...")
        cro_alert.stop_monitoring()
        monitor_thread.join(timeout=5)
        print("✅ Stopped.")

if __name__ == "__main__":
    main()