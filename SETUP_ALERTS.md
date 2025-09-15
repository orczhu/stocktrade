# 🔔 Price Alert System Setup Guide

Your price alert system has been successfully implemented! Here's how to set it up and use it.

## 📋 What Was Added

### 1. Core Alert System (`src/alert_manager.py`)
- **SQLite Database**: Stores alert configurations 
- **Email Notifications**: Sends rich alerts via SMTP (Gmail)
- **Background Monitoring**: Checks prices every 5 minutes
- **Alert Management**: Create, update, delete, and trigger alerts

### 2. API Endpoints (added to `app.py`)
- `POST /api/alerts` - Create new alert
- `GET /api/alerts?email={email}` - Get user's alerts
- `PUT /api/alerts/{id}` - Update alert
- `DELETE /api/alerts/{id}` - Delete alert
- `POST /api/alerts/check/{id}` - Manually check alert
- `GET /api/alerts/stats` - Get statistics
- `POST /api/alerts/monitoring` - Start monitoring
- `DELETE /api/alerts/monitoring` - Stop monitoring

### 3. Web Interface (`/alerts`)
- Clean, responsive UI for managing alerts
- Real-time statistics dashboard
- Create alerts for stocks or crypto (including CRO)
- View, edit, delete, and manually trigger alerts

## 🚀 Setup Instructions

### 1. Install Dependencies
```bash
# Activate your virtual environment
source testenv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 2. Configure Email (Required for notifications)
Set up environment variables for Gmail SMTP:

```bash
# Option 1: Export in terminal (temporary)
export EMAIL_ADDRESS="your-gmail@gmail.com"
export EMAIL_PASSWORD="your-app-password"

# Option 2: Add to ~/.bashrc or ~/.zshrc (permanent)
echo 'export EMAIL_ADDRESS="your-gmail@gmail.com"' >> ~/.bashrc
echo 'export EMAIL_PASSWORD="your-app-password"' >> ~/.bashrc

# Option 3: Create .env file (recommended for development)
echo 'EMAIL_ADDRESS=your-gmail@gmail.com' > .env
echo 'EMAIL_PASSWORD=your-app-password' >> .env
```

**Getting Gmail App Password:**
1. Go to Google Account settings
2. Security → 2-Step Verification → App passwords
3. Generate password for "Mail"
4. Use that password (not your regular Gmail password)

### 3. Start the Application
```bash
python app.py
```

The app will automatically:
- Initialize the alerts database
- Start background price monitoring (every 5 minutes)
- Serve the web interface

## 📱 How to Use

### Via Web Interface (Recommended)
1. Open http://localhost:5000/alerts
2. Fill out the alert form:
   - **Symbol**: CRO (or any crypto/stock)
   - **Asset Type**: Cryptocurrency
   - **Alert Type**: Above/Below
   - **Target Price**: e.g., 0.15
   - **Email**: wangzhuyunabc@gmail.com (pre-filled)
   - **Phone**: 858-882-7642 (pre-filled for T-Mobile SMS)
3. Click "Create Alert"
4. Monitor your alerts in the dashboard

### Via API (for automation)
```bash
# Create CRO alert
curl -X POST http://localhost:5000/api/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "CRO",
    "asset_type": "crypto",
    "alert_type": "above",
    "target_price": 0.15,
    "email": "wangzhuyunabc@gmail.com",
    "phone": "858-882-7642",
    "message": "CRO hit my target!"
  }'

# Get your alerts
curl "http://localhost:5000/api/alerts?email=wangzhuyunabc@gmail.com"
```

## 🧪 Testing

### 1. Test Basic Functionality
```bash

```

### 2. Test with Real Alert
1. Check current CRO price: http://localhost:5000/api/crypto/CRO
2. Create alert slightly below current price (should trigger)
3. Wait for email/SMS notification

### 3. Manual Testing
- Create alert via web interface
- Use "Check Now" button to manually trigger
- Monitor console logs for debugging

## 📊 Features

### Alert Types
- **Above**: Notify when price goes above target
- **Below**: Notify when price goes below target

### Supported Assets
- **Cryptocurrencies**: BTC, ETH, CRO, ADA, DOT, LINK, SOL, DOGE, LTC, XRP, BNB
- **Stocks**: AAPL, GOOGL, MSFT, TSLA, etc.

### Notifications
- **Email**: Rich notifications with price details, emojis, and chart links
- **Auto-deactivation**: Alerts turn off after triggering
- **Push notifications**: Via Gmail app on mobile devices

### Monitoring
- **Background Process**: Checks every 5 minutes automatically  
- **Rate Limiting**: Small delays between checks to avoid API limits
- **Error Handling**: Continues monitoring even if individual checks fail

## 🎯 Example: CRO Alert

Create a CRO alert for $0.15:

```json
{
  "symbol": "CRO",
  "asset_type": "crypto", 
  "alert_type": "above",
  "target_price": 0.15,
  "email": "wangzhuyunabc@gmail.com",
  "phone": "858-882-7642",
  "message": "CRO reached my target price!"
}
```

When CRO hits $0.15, you'll receive:
- 📧 **Email**: Rich notification with current price, target, chart link, and custom message
- 📱 **Mobile Push**: Via Gmail app notifications (if installed)

## 🔧 Troubleshooting

### No Notifications Received
1. Check environment variables: `echo $EMAIL_ADDRESS`
2. Verify Gmail app password is correct
3. Check console logs for SMTP errors
4. Test with manual alert check

### Database Issues
- Database file: `alerts.db` (created automatically)
- Reset: Delete `alerts.db` and restart app
- Backup: Copy `alerts.db` file

### API Errors
- Check if Flask app is running
- Verify JSON format in requests
- Check console logs for detailed errors

### Price Fetching Issues
- Uses Yahoo Finance API (same as existing charts)
- Network connection required
- Some symbols may have different formats

## 🚀 Next Steps

1. **Set up email credentials** and test notifications
2. **Create your first CRO alert** via the web interface  
3. **Monitor the background process** in console logs
4. **Customize alert messages** for different scenarios
5. **Set up multiple alerts** for portfolio management

Your price alert system is ready to use! Visit http://localhost:5000/alerts to get started.