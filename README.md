# TradeLog: A Personal Trade Journal

A trade journal to systematically log any investment you made, track performance, and document investment theses. 

Every coffee chat I've ever had with employees at funds and AM firms end the same way: track your trades. I tried a paper journal first, then a Google Doc, but neither really stuck with me. So I went looking for an app instead, and quickly found out that the two big options (TradeSync and Edgebonk) cost A LOT of money. 

So I just built my own.

Site: https://trade-log.onrender.com

The server automatically shuts down after 15 minutes of inactivity. If the app hasn't been visited recently, the first load may take 20–30 seconds while the server wakes up. This is completely normal. Just wait a moment and the page will load.

---

## Features
- Trade Logging: Record entry/exit prices, position size, dates, sector, and strategy for every trade
- Investment thesis tracking: Document your thesis, expected catalysts, and risk factors before entering a trade
- Post-trade review: Reflect on what went right, what went wrong, and what you learned after closing
- A Performance dashboard: Win rate, average return, wins/losses, and open position count
- Open positions filter: One click to isolate all currently open trades
- Light / dark mode: Toggle between themes with your preference saved across sessions
- Secure authentication — Per-user accounts with bcrypt password hashing

---
## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Database ORM | SQLAlchemy |
| Authentication | Flask-Login, Flask-Bcrypt |
| Frontend | Jinja2, Vanilla JS, CSS Variables |
| Database (prod) | PostgreSQL via Neon |
| Database (local) | SQLite |
| Hosting | Render |
| Fonts | Space Mono, DM Sans |
---

## Project structure

```
trade_journal/
├── app.py                  # Flask application, routes, and API endpoints
├── models.py               # SQLAlchemy database models
├── requirements.txt        # Python dependencies
├── Procfile                # Render/Gunicorn start command
├── static/
│   └── favicon.svg
└── templates/
    ├── base.html           # Base layout, global styles, theme toggle
    ├── login.html
    ├── register.html
    ├── dashboard.html      # Infinite scroll trade list with filter
    ├── add_trade.html      # New trade form
    ├── edit_trade.html     # Edit existing trade
    └── trade_detail.html   # Full trade view with all notes
```

---

## Acknowledgement

Created using Claude for assistance specifically in: frontend development, storing data, authorizing user profiles, and cleaning up code tremendously. Definitely would not be able to do this project without it.
