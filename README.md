# TradeLog: A Personal Trade Journal

A trade journal for logging stock trades, tracking performance, and documenting investment theses.

Developed with Claude.

## Features
- Secure multi-user authentication
- Log long/short trades with full metadata
- Investment thesis, catalyst, and risk factor documentation
- Post-trade review and lessons learned
- Automatic P&L calculation (long and short)
- Dashboard with win rate, avg return, and open positions
- Chronological trade history with thesis preview

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
python app.py
```

The app will start at **http://localhost:5000**

### 3. Create an account
Visit http://localhost:5000/register to create your account.

## Project Structure
```
trade_journal/
├── app.py              # Flask application & routes
├── models.py           # Database models
├── requirements.txt
└── templates/
    ├── base.html       # Base layout & styles
    ├── login.html
    ├── register.html
    ├── dashboard.html  # Trade list + stats
    ├── add_trade.html  # Log new trade
    ├── edit_trade.html
    └── trade_detail.html
```

## Return Calculation
- **Long**: `(exit - entry) / entry × 100`
- **Short**: `(entry - exit) / entry × 100`

## Production Notes
- Change `SECRET_KEY` in app.py before deploying
- Migrate from SQLite to PostgreSQL for production use
- Add HTTPS / reverse proxy (nginx) for public hosting
