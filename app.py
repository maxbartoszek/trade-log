import os
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Trade, TradeNote
from flask_bcrypt import Bcrypt
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Render provides DATABASE_URL as postgres://, but SQLAlchemy requires postgresql://
database_url = os.environ.get('DATABASE_URL', 'sqlite:///trade_journal.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'connect_args': {'sslmode': 'require'} if 'neon.tech' in database_url else {}
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Run all migrations at module load time — must happen before any query runs
def _run_migrations():
    with app.app_context():
        with db.engine.connect() as conn:
            for sql in [
                'ALTER TABLE trades RENAME COLUMN position_size TO stop_limit',
                'ALTER TABLE users ADD COLUMN share_token VARCHAR(64) UNIQUE',
            ]:
                try:
                    conn.execute(db.text(sql))
                    conn.commit()
                except Exception:
                    pass

_run_migrations()


@app.before_request
def initialize_db():
    # Runs once on first request, not at startup — avoids blocking gunicorn boot
    if not getattr(app, '_db_initialized', False):
        db.create_all()
        with db.engine.connect() as conn:
            try:
                conn.execute(db.text(
                    'ALTER TABLE trades RENAME COLUMN position_size TO stop_limit'
                ))
                conn.commit()
            except Exception:
                pass
            try:
                conn.execute(db.text(
                    'ALTER TABLE users ADD COLUMN share_token VARCHAR(64) UNIQUE'
                ))
                conn.commit()
            except Exception:
                pass
            try:
                conn.execute(db.text(
                    'ALTER TABLE users ADD COLUMN share_enabled BOOLEAN DEFAULT FALSE'
                ))
                conn.commit()
            except Exception:
                pass
            try:
                conn.execute(db.text(
                    'ALTER TABLE trades ADD COLUMN expected_exit_price FLOAT'
                ))
                conn.commit()
            except Exception:
                pass
            try:
                conn.execute(db.text(
                    'ALTER TABLE trades ADD COLUMN expected_timeframe VARCHAR(100)'
                ))
                conn.commit()
            except Exception:
                pass
            # Backfill share_token for existing users who don't have one
            try:
                import secrets as _secrets
                from sqlalchemy import text as _text
                rows = conn.execute(_text("SELECT id FROM users WHERE share_token IS NULL")).fetchall()
                for row in rows:
                    conn.execute(_text("UPDATE users SET share_token = :t WHERE id = :id"),
                                 {'t': _secrets.token_urlsafe(32), 'id': row[0]})
                conn.commit()
            except Exception:
                pass
        app._db_initialized = True



bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = ''

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def dashboard():
    all_trades = Trade.query.filter_by(user_id=current_user.id).all()
    closed = sum(1 for t in all_trades if t.status == 'closed')
    wins   = sum(1 for t in all_trades if t.return_pct and t.return_pct > 0)
    losses = sum(1 for t in all_trades if t.return_pct and t.return_pct < 0)
    stats = {
        'total': len(all_trades),
        'wins': wins,
        'losses': losses,
        'avg_return': round(sum(t.return_pct for t in all_trades if t.return_pct) / max(len([t for t in all_trades if t.return_pct]), 1), 2),
        'open': sum(1 for t in all_trades if t.status == 'open'),
        'win_rate': round((wins / max(closed, 1)) * 100, 1),
    }
    return render_template('dashboard.html', stats=stats)

@app.route('/api/trades')
@login_required
def api_trades():
    PAGE_SIZE = 50
    page = request.args.get('page', 1, type=int)
    filter_open = request.args.get('open_only', 'false') == 'true'

    query = Trade.query.filter_by(user_id=current_user.id)
    if filter_open:
        query = query.filter_by(status='open')
    query = query.order_by(
        db.func.coalesce(Trade.exit_date, Trade.entry_date).desc().nullslast()
    )

    total = query.count()
    trades = query.offset((page - 1) * PAGE_SIZE).limit(PAGE_SIZE).all()

    def trade_dict(t):
        return {
            'id': t.id,
            'ticker': t.ticker,
            'position_type': t.position_type,
            'entry_price': t.entry_price,
            'exit_price': t.exit_price,
            'entry_date': t.entry_date.strftime('%b %d, %Y') if t.entry_date else None,
            'exit_date': t.exit_date.strftime('%b %d, %Y') if t.exit_date else None,
            'return_pct': t.return_pct,
            'status': t.status,
            'thesis': t.notes.thesis[:80] if t.notes and t.notes.thesis else None,
        }

    return jsonify({
        'trades': [trade_dict(t) for t in trades],
        'page': page,
        'total': total,
        'has_more': (page * PAGE_SIZE) < total,
        'page_size': PAGE_SIZE,
    })

@app.route('/trade/new', methods=['GET', 'POST'])
@login_required
def add_trade():
    if request.method == 'POST':
        f = request.form
        entry = float(f.get('entry_price', 0))
        exit_p = float(f.get('exit_price', 0)) if f.get('exit_price') else None
        pos = f.get('position_type', 'long')

        return_pct = None
        if exit_p and entry:
            if pos == 'long':
                return_pct = round(((exit_p - entry) / entry) * 100, 2)
            else:
                return_pct = round(((entry - exit_p) / entry) * 100, 2)

        exit_date = datetime.strptime(f.get('exit_date'), '%Y-%m-%d').date() if f.get('exit_date') else None
        status = 'closed' if (exit_p or exit_date) else 'open'

        trade = Trade(
            user_id=current_user.id,
            ticker=f.get('ticker', '').upper(),
            position_type=pos,
            entry_price=entry,
            exit_price=exit_p,
            stop_limit=float(f.get('stop_limit', 0)) if f.get('stop_limit') else None,
            expected_exit_price=float(f.get('expected_exit_price')) if f.get('expected_exit_price') else None,
            expected_timeframe=f.get('expected_timeframe', '') or None,
            entry_date=datetime.strptime(f.get('entry_date'), '%Y-%m-%d').date() if f.get('entry_date') else None,
            exit_date=exit_date,
            return_pct=return_pct,
            status=status,
            sector=f.get('sector', ''),
            strategy=f.get('strategy', ''),
        )
        db.session.add(trade)
        db.session.flush()

        note = TradeNote(
            trade_id=trade.id,
            thesis=f.get('thesis', ''),
            catalyst=f.get('catalyst', ''),
            risk_factors=f.get('risk_factors', ''),
            confidence_level=int(f.get('confidence_level', 5)),
            post_trade_review=f.get('post_trade_review', ''),
            mistakes=f.get('mistakes', ''),
            lessons=f.get('lessons', ''),
        )
        db.session.add(note)
        db.session.commit()
        flash('Trade logged successfully.', 'success')
        return redirect(url_for('trade_detail', trade_id=trade.id))

    return render_template('add_trade.html')

@app.route('/trade/<int:trade_id>')
@login_required
def trade_detail(trade_id):
    trade = Trade.query.filter_by(id=trade_id, user_id=current_user.id).first_or_404()
    return render_template('trade_detail.html', trade=trade)

@app.route('/trade/<int:trade_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_trade(trade_id):
    trade = Trade.query.filter_by(id=trade_id, user_id=current_user.id).first_or_404()
    if request.method == 'POST':
        f = request.form
        trade.ticker = f.get('ticker', '').upper()
        trade.position_type = f.get('position_type', 'long')
        trade.entry_price = float(f.get('entry_price', 0))
        trade.exit_price = float(f.get('exit_price', 0)) if f.get('exit_price') else None
        trade.stop_limit = float(f.get('stop_limit', 0)) if f.get('stop_limit') else None
        trade.entry_date = datetime.strptime(f.get('entry_date'), '%Y-%m-%d').date() if f.get('entry_date') else None
        trade.exit_date = datetime.strptime(f.get('exit_date'), '%Y-%m-%d').date() if f.get('exit_date') else None
        trade.expected_exit_price = float(f.get('expected_exit_price')) if f.get('expected_exit_price') else None
        trade.expected_timeframe = f.get('expected_timeframe', '') or None
        trade.status = 'closed' if (trade.exit_price or trade.exit_date) else 'open'
        trade.sector = f.get('sector', '')
        trade.strategy = f.get('strategy', '')

        if trade.exit_price and trade.entry_price:
            if trade.position_type == 'long':
                trade.return_pct = round(((trade.exit_price - trade.entry_price) / trade.entry_price) * 100, 2)
            else:
                trade.return_pct = round(((trade.entry_price - trade.exit_price) / trade.entry_price) * 100, 2)

        if trade.notes:
            note = trade.notes
        else:
            note = TradeNote(trade_id=trade.id)
            db.session.add(note)

        note.thesis = f.get('thesis', '')
        note.catalyst = f.get('catalyst', '')
        note.risk_factors = f.get('risk_factors', '')
        note.confidence_level = int(f.get('confidence_level', 5))
        note.post_trade_review = f.get('post_trade_review', '')
        note.mistakes = f.get('mistakes', '')
        note.lessons = f.get('lessons', '')
        db.session.commit()
        flash('Trade updated.', 'success')
        return redirect(url_for('trade_detail', trade_id=trade.id))
    return render_template('edit_trade.html', trade=trade)

@app.route('/trade/<int:trade_id>/delete', methods=['POST'])
@login_required
def delete_trade(trade_id):
    trade = Trade.query.filter_by(id=trade_id, user_id=current_user.id).first_or_404()
    db.session.delete(trade)
    db.session.commit()
    flash('Trade deleted.', 'info')
    return redirect(url_for('dashboard'))


@app.route('/analytics')
@login_required
def analytics():
    from collections import defaultdict
    trades = Trade.query.filter_by(user_id=current_user.id).all()
    closed = [t for t in trades if t.status == 'closed' and t.return_pct is not None]

    if not closed:
        return render_template('analytics.html', empty=True)

    # --- Cumulative P&L ---
    sorted_trades = sorted(closed, key=lambda t: t.exit_date or t.entry_date or datetime.min.date())
    cumulative = []
    running = 0
    for t in sorted_trades:
        running += t.return_pct
        date = t.exit_date or t.entry_date
        cumulative.append({
            'date': date.strftime('%b %d, %Y') if date else 'Unknown',
            'value': round(running, 2),
            'ticker': t.ticker,
        })

    # --- Win rate by strategy ---
    strat_data = defaultdict(lambda: {'wins': 0, 'total': 0, 'returns': []})
    for t in closed:
        key = t.strategy.strip() if t.strategy and t.strategy.strip() else 'Untagged'
        strat_data[key]['total'] += 1
        strat_data[key]['returns'].append(t.return_pct)
        if t.return_pct > 0:
            strat_data[key]['wins'] += 1
    strategies = []
    for name, d in strat_data.items():
        strategies.append({
            'name': name,
            'win_rate': round(d['wins'] / d['total'] * 100, 1),
            'avg_return': round(sum(d['returns']) / len(d['returns']), 2),
            'count': d['total'],
        })
    strategies.sort(key=lambda x: x['win_rate'], reverse=True)

    # --- Best / worst sectors ---
    sector_data = defaultdict(lambda: {'wins': 0, 'total': 0, 'returns': []})
    for t in closed:
        key = t.sector.strip() if t.sector and t.sector.strip() else 'Untagged'
        sector_data[key]['total'] += 1
        sector_data[key]['returns'].append(t.return_pct)
        if t.return_pct > 0:
            sector_data[key]['wins'] += 1
    sectors = []
    for name, d in sector_data.items():
        sectors.append({
            'name': name,
            'avg_return': round(sum(d['returns']) / len(d['returns']), 2),
            'win_rate': round(d['wins'] / d['total'] * 100, 1),
            'count': d['total'],
        })
    sectors.sort(key=lambda x: x['avg_return'], reverse=True)

    # --- Average hold time ---
    hold_times = []
    for t in closed:
        if t.entry_date and t.exit_date:
            hold_times.append((t.exit_date - t.entry_date).days)
    avg_hold = round(sum(hold_times) / len(hold_times), 1) if hold_times else None

    # --- Long vs Short breakdown ---
    long_trades = [t for t in closed if t.position_type == 'long']
    short_trades = [t for t in closed if t.position_type == 'short']
    def side_stats(ts):
        if not ts: return None
        wins = sum(1 for t in ts if t.return_pct > 0)
        return {
            'count': len(ts),
            'win_rate': round(wins / len(ts) * 100, 1),
            'avg_return': round(sum(t.return_pct for t in ts) / len(ts), 2),
        }

    # --- Best / worst trades ---
    best = max(closed, key=lambda t: t.return_pct)
    worst = min(closed, key=lambda t: t.return_pct)

    # --- Monthly returns ---
    monthly = defaultdict(list)
    for t in closed:
        date = t.exit_date or t.entry_date
        if not date:
            continue
        key = date.strftime('%b %Y')
        monthly[key].append(t.return_pct)
    monthly_data = []
    for k, v in sorted(monthly.items(), key=lambda x: datetime.strptime(x[0], '%b %Y')):
        monthly_data.append({
            'month': k,
            'avg': round(sum(v) / len(v), 2),
            'count': len(v),
        })

    return render_template('analytics.html',
        empty=False,
        total_closed=len(closed),
        avg_hold=avg_hold,
        cumulative=cumulative,
        strategies=strategies,
        sectors=sectors,
        long_stats=side_stats(long_trades),
        short_stats=side_stats(short_trades),
        best=best,
        worst=worst,
        monthly=monthly_data,
    )


@app.route('/export/csv')
@login_required
def export_csv():
    import csv
    import io
    trades = Trade.query.filter_by(user_id=current_user.id).order_by(Trade.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'Ticker', 'Position', 'Status', 'Entry Price', 'Exit Price',
        'Entry Date', 'Exit Date', 'Return %', 'Stop Limit',
        'Sector', 'Strategy', 'Confidence',
        'Thesis', 'Catalyst', 'Risk Factors',
        'Post-Trade Review', 'Mistakes', 'Lessons'
    ])

    for t in trades:
        n = t.notes
        writer.writerow([
            t.ticker,
            t.position_type,
            t.status,
            t.entry_price,
            t.exit_price or '',
            t.entry_date.strftime('%Y-%m-%d') if t.entry_date else '',
            t.exit_date.strftime('%Y-%m-%d') if t.exit_date else '',
            t.return_pct if t.return_pct is not None else '',
            t.stop_limit or '',
            t.sector or '',
            t.strategy or '',
            n.confidence_level if n else '',
            n.thesis or '' if n else '',
            n.catalyst or '' if n else '',
            n.risk_factors or '' if n else '',
            n.post_trade_review or '' if n else '',
            n.mistakes or '' if n else '',
            n.lessons or '' if n else '',
        ])

    from flask import Response
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=tradelog_export.csv'}
    )

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'error')
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('register.html')
        import secrets
        pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password_hash=pw_hash,
                    share_token=secrets.token_urlsafe(32), share_enabled=False)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials.', 'error')
    return render_template('login.html')


@app.route('/share/toggle', methods=['POST'])
@login_required
def toggle_share():
    current_user.share_enabled = not current_user.share_enabled
    db.session.commit()
    if current_user.share_enabled:
        flash('Public link enabled.', 'success')
    else:
        flash('Public link disabled.', 'info')
    return redirect(url_for('dashboard'))

@app.route('/public/<token>')
def public_journal(token):
    user = User.query.filter_by(share_token=token).first()
    if not user or not user.share_enabled:
        return render_template('link_disabled.html'), 404
    all_trades = Trade.query.filter_by(user_id=user.id).all()
    closed = sum(1 for t in all_trades if t.status == 'closed')
    wins   = sum(1 for t in all_trades if t.return_pct and t.return_pct > 0)
    losses = sum(1 for t in all_trades if t.return_pct and t.return_pct < 0)
    stats = {
        'total': len(all_trades),
        'wins': wins,
        'losses': losses,
        'avg_return': round(sum(t.return_pct for t in all_trades if t.return_pct) / max(len([t for t in all_trades if t.return_pct]), 1), 2),
        'open': sum(1 for t in all_trades if t.status == 'open'),
        'win_rate': round((wins / max(closed, 1)) * 100, 1),
    }
    return render_template('public_journal.html', user=user, stats=stats, token=token)

@app.route('/public/<token>/trades')
def public_trades(token):
    user = User.query.filter_by(share_token=token).first_or_404()
    PAGE_SIZE = 50
    page = request.args.get('page', 1, type=int)
    filter_open = request.args.get('open_only', 'false') == 'true'

    query = Trade.query.filter_by(user_id=user.id)
    if filter_open:
        query = query.filter_by(status='open')
    query = query.order_by(
        db.func.coalesce(Trade.exit_date, Trade.entry_date).desc().nullslast()
    )

    total = query.count()
    trades = query.offset((page - 1) * PAGE_SIZE).limit(PAGE_SIZE).all()

    def trade_dict(t):
        return {
            'id': t.id,
            'ticker': t.ticker,
            'position_type': t.position_type,
            'entry_price': t.entry_price,
            'exit_price': t.exit_price,
            'entry_date': t.entry_date.strftime('%b %d, %Y') if t.entry_date else None,
            'exit_date': t.exit_date.strftime('%b %d, %Y') if t.exit_date else None,
            'return_pct': t.return_pct,
            'status': t.status,
            'thesis': t.notes.thesis[:80] if t.notes and t.notes.thesis else None,
        }

    return jsonify({
        'trades': [trade_dict(t) for t in trades],
        'page': page,
        'total': total,
        'has_more': (page * PAGE_SIZE) < total,
        'page_size': PAGE_SIZE,
    })

@app.route('/public/<token>/trade/<int:trade_id>')
def public_trade_detail(token, trade_id):
    user = User.query.filter_by(share_token=token).first_or_404()
    trade = Trade.query.filter_by(id=trade_id, user_id=user.id).first_or_404()
    return render_template('public_trade_detail.html', trade=trade, token=token)

@app.route('/manifest.json')
def manifest():
    from flask import send_from_directory
    return send_from_directory('static', 'manifest.json', mimetype='application/manifest+json')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
