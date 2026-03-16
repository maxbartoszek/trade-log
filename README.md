# TradeLog: A Personal Trade Journal

A stock trading journal to log trades, track performance, and document investment theses.

In my chats with people working at funds and AM firms, they always tell me to track my trades/investments. Doing it in a paper journal or Google Doc felt weird so I looked for specific software, but the big ones (TraderSync and Edgewonk) cost a LOT of money. As such, I decided to develop my own.

---
trade_journal/
├── app.py                  # Flask app & routes
├── models.py               # Database models
├── requirements.txt        # Python dependencies
├── Procfile                # Tells Render/Heroku how to start the app
├── render.yaml             # One-click Render deploy config
└── templates/
    ├── base.html           # Base layout, styles, theme toggle
    ├── login.html
    ├── register.html
    ├── dashboard.html      # Infinite-scroll trade list
    ├── add_trade.html
    ├── edit_trade.html
    └── trade_detail.html
```
# Acknowledgement

Created with the assistance of Claude, specifically in frontend development, storing data, authenticating user profiles, and cleaning up code. 
---
