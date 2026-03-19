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
- **Mobile use**: Use it seemlessly on mobile devices. You can even add the webapp to your homepage where it'll act like an app without you downloading anything!
- **Dark / pink mode:** Toggle between themes with your preference saved across sessions (pink as per my girlfriend's request)
- **Share trade data:** Click a button to enable others viewing your trades. Great for sharing with recruiters ;)
- **CSV Export**: Download your transactions off Trade Log in a CSV
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

## Running Locally 
1. Clone the repo
2. Install the necessary dependencies
 (install -r requirements.txt)
3. Start the app
 (python app.py)
4. Hop on http://localhost:5000, register an account, and start logging trades.

Running locally uses SQLite automatically meaning there is no database setup needed.

---

## Acknowledgement

Created using Claude. First wrote all code and the MVP in Python and Streamlit. Then began using Claude AI for developing a better frontend with HTML, storing data online in a Neon Tech database instead of SQLite, creating a user authentication system, cleaning up my code (optimizing efficiency of code, removing redundant comments, etc.), and creating the [Share Data] function. Definitely would not have been able to do this project without it.
