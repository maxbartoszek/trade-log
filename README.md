# TradeLog: A Personal Trade Journal

A trade journal to systematically log any investment you made, track performance, and document investment theses.

---

## Project structure

```
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

---

## Acknowledgement

Created using Claude for assistance specifically in: frontend development, storing data, authorizing user profiles, and cleaning up code tremendously. 
