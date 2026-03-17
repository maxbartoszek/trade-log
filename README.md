# TradeLog: A Personal Trade Journal

A trade journal to systematically log any investment you made, track performance, and document investment theses. 

Every coffee chat I've ever had with employees at funds and AM firms end with the same advice: track your trades. I tried a paper journal first, then a Google Doc, but neither really stuck with me. So I went looking for an app instead, and quickly found out that the two main options (TradeSync and Edgebonk) cost A LOT of money. 

So I just built my own.

Site: https://trade-log.onrender.com

The server automatically shuts down after 15 minutes of inactivity. If the app hasn't been visited recently, the first load may take around a minute while the server wakes up. This is completely normal. Just wait and the page will load.

Although free, Trade Log has enough storage to keep 250,000 logs across all accounts so don't worry too much about the site collapsing. If you want more security, I'd recommend running it locally (more on that below).

---

## Features
- **Trade logging:** Record entry/exit prices, stop limits, dates, sector, and strategy for every trade
- **Investment thesis tracking:** Document your thesis, expected catalysts, and risk factors before entering a trade
- **Post-trade review:** Reflect on what went right, what went wrong, and what you learned after closing
- **Performance dashboard:** Win rate, average return, wins/losses, and open position count
- **Analytical dashboard:** Displays more detailed metrics than Performance Dashboard (avg hold time, cumulative return, avg monthly returns, win rate by strategy, performance by sector, long vs short performance, etc.)
- **Open positions filter:** One click to isolate all currently open trades
- **Light / dark mode:** Toggle between themes with your preference saved across sessions
- **Secure authentication:** Personal accounts with bcrypt password hashing

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
---

## Project structure

```
trade_journal/
├── app.py                  
├── models.py               
├── requirements.txt
├── Procfile                
├── static/
│   └── favicon.svg
└── templates/
    ├── base.html           
    ├── login.html
    ├── register.html
    ├── dashboard.html      
    ├── add_trade.html      
    ├── edit_trade.html     
    └── trade_detail.html   
```

---
## Running Locally (Recommended)
1. Clone the repo
2. Install the necessary dependencies
 (bashpip install -r requirements.txt)
3. Start the app
 (bashpython app.py)

Visit http://localhost:5000, register an account, and start logging trades. Running locally uses SQLite automatically meaning there is no database setup needed.

---

## Acknowledgement

Created using Claude. Specifically used in: frontend development, storing data, authorizing user profiles, and cleaning up a tremendous amount of code. Definitely would not have been able to do this project without it.
