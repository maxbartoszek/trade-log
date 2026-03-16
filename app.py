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

with app.app_context():
    db.create_all()

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
    query = query.order_by(Trade.created_at.desc())

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
        status = f.get('status', 'open')

        return_pct = None
        if exit_p and entry:
            if pos == 'long':
                return_pct = round(((exit_p - entry) / entry) * 100, 2)
            else:
                return_pct = round(((entry - exit_p) / entry) * 100, 2)

        trade = Trade(
            user_id=current_user.id,
            ticker=f.get('ticker', '').upper(),
            position_type=pos,
            entry_price=entry,
            exit_price=exit_p,
            position_size=float(f.get('position_size', 0)) if f.get('position_size') else None,
            entry_date=datetime.strptime(f.get('entry_date'), '%Y-%m-%d').date() if f.get('entry_date') else None,
            exit_date=datetime.strptime(f.get('exit_date'), '%Y-%m-%d').date() if f.get('exit_date') else None,
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
        trade.position_size = float(f.get('position_size', 0)) if f.get('position_size') else None
        trade.entry_date = datetime.strptime(f.get('entry_date'), '%Y-%m-%d').date() if f.get('entry_date') else None
        trade.exit_date = datetime.strptime(f.get('exit_date'), '%Y-%m-%d').date() if f.get('exit_date') else None
        trade.status = f.get('status', 'open')
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
        pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password_hash=pw_hash)
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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
