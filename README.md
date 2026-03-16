# TradeLog: A Personal Trade Journal

A trade journal to systematically log any investment you made, track performance, and document investment theses. 
Built as a personal analytics tool for investment decision improvement.

In coffee chats with employees at funds and AM firms, I've found that I'm always told to do one thing: track your trades. At first, I tried doing it in a paper journal, and then a Google Doc, but neither clicked for me. That's when I started looking for apps that I could use instead. However, the two big ones, TradeSync and Edgebonk, cost A LOT of money to use. As such, I decided to create my own. 

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

Created using Claude for assistance specifically in: frontend development, storing data, authorizing user profiles, and cleaning up code tremendously. 
