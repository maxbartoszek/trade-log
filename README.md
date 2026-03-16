# TradeLog — Personal Trade Journal

A self-hosted trade journal for systematic trade logging, performance tracking, and investment thesis documentation.

---

## Deploying to Render (free, always-on)

### Step 1 — Push to GitHub
If you haven't already, create a GitHub repo and push this project to it.

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/trade-journal.git
git push -u origin main
```

### Step 2 — Create a Render account
Sign up at https://render.com (free, no credit card required for the free tier).

### Step 3 — Deploy via render.yaml (easiest)
1. In your Render dashboard, click **New → Blueprint**
2. Connect your GitHub account and select your repo
3. Render will read `render.yaml` and automatically:
   - Create the web service
   - Create a free PostgreSQL database
   - Wire them together with the correct environment variables
4. Click **Apply** and wait ~2 minutes for the first deploy

Your app will be live at: `https://trade-journal.onrender.com` (or similar)

### Step 4 — Create your account
Visit your live URL and register. That's it — your trades are stored in the
persistent Postgres database and will survive all future redeploys.

---

## Manual Render setup (alternative to render.yaml)

If you prefer to set things up manually:

1. **New → Web Service** → connect your GitHub repo
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Add environment variable: `SECRET_KEY` → click "Generate" for a random value

2. **New → PostgreSQL** → choose the free plan, name it `trade-journal-db`

3. In your Web Service settings → Environment → add:
   - `DATABASE_URL` → paste the **Internal Database URL** from your Postgres service

---

## Running locally

```bash
pip install -r requirements.txt
python app.py
# → http://localhost:5000
```

Local runs use SQLite automatically (no Postgres needed).

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

## Notes

- **Free tier caveat:** Render free web services spin down after 15 minutes of inactivity.
  The first request after idle takes ~30 seconds to wake up. Subsequent requests are instant.
  Upgrading to the $7/month "Starter" plan removes this.
- **Database:** The free Postgres instance on Render is limited to 1GB and expires after 90 days,
  after which you need to recreate it (your data will be lost unless you export it first).
  The $7/month paid Postgres plan has no expiry.
- **Secret key:** Never commit a real SECRET_KEY to GitHub. The render.yaml auto-generates one securely.
