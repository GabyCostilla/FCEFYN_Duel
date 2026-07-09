from flask import Blueprint, request, jsonify, render_template
from app import db
from models import User, StudySession, ActiveTimer, Goal, Bet, UserBadge
from datetime import datetime, date, timedelta
from collections import defaultdict

main = Blueprint('main', __name__)

# ── Badge definitions ─────────────────────────────────
BADGES = {
    'first_session':  {'label': 'Primera sesión',       'icon': '🎯'},
    'streak_3':       {'label': '3 días seguidos',       'icon': '🔥'},
    'streak_7':       {'label': '7 días seguidos',       'icon': '⚡'},
    'streak_30':      {'label': '30 días seguidos',      'icon': '🏅'},
    'week_10h':       {'label': '10 hs en una semana',   'icon': '📚'},
    'week_20h':       {'label': '20 hs en una semana',   'icon': '🚀'},
    'total_50h':      {'label': '50 hs totales',         'icon': '💎'},
    'total_100h':     {'label': '100 hs totales',        'icon': '👑'},
    'sessions_10':    {'label': '10 sesiones',           'icon': '✅'},
    'sessions_50':    {'label': '50 sesiones',           'icon': '🌟'},
}

def check_and_award_badges(user):
    earned = {b.badge_key for b in user.badges}
    new_badges = []
    completed = [s for s in user.sessions if s.ended_at]
    total_secs = sum(s.duration_seconds for s in completed)

    def award(key):
        if key not in earned:
            db.session.add(UserBadge(user_id=user.id, badge_key=key))
            new_badges.append(key)

    if len(completed) >= 1:    award('first_session')
    if len(completed) >= 10:   award('sessions_10')
    if len(completed) >= 50:   award('sessions_50')
    if total_secs >= 50*3600:  award('total_50h')
    if total_secs >= 100*3600: award('total_100h')

    week_start = date.today() - timedelta(days=date.today().weekday())
    week_secs = sum(s.duration_seconds for s in completed
                    if s.started_at.date() >= week_start)
    if week_secs >= 10*3600: award('week_10h')
    if week_secs >= 20*3600: award('week_20h')

    study_days = sorted({s.started_at.date() for s in completed}, reverse=True)
    streak = 0
    if study_days:
        check = date.today()
        for d in study_days:
            if d == check or d == check - timedelta(days=1):
                streak += 1
                check = d
            else:
                break
    if streak >= 3:  award('streak_3')
    if streak >= 7:  award('streak_7')
    if streak >= 30: award('streak_30')

    db.session.commit()
    return streak, new_badges

# ── Pages ─────────────────────────────────────────────
@main.route('/')
def index():
    return render_template('index.html')

# ── Users ─────────────────────────────────────────────
@main.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username', '').strip()
    if not username:
        return jsonify({'error': 'Nombre requerido'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Usuario ya existe'}), 409
    user = User(username=username)
    db.session.add(user)
    db.session.commit()
    return jsonify({'id': user.id, 'username': user.username}), 201

@main.route('/users/<username>/login')
def login(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    return jsonify({'id': user.id, 'username': user.username})

# ── Timer ─────────────────────────────────────────────
@main.route('/timer/start', methods=['POST'])
def start_timer():
    data = request.get_json()
    user_id = data.get('user_id')
    if ActiveTimer.query.get(user_id):
        return jsonify({'error': 'Cronómetro ya corriendo'}), 400
    now = datetime.utcnow()
    db.session.add(ActiveTimer(user_id=user_id, started_at=now, accumulated_seconds=0))
    db.session.add(StudySession(user_id=user_id, started_at=now))
    db.session.commit()
    return jsonify({'started_at': now.isoformat()})

@main.route('/timer/pause', methods=['POST'])
def pause_timer():
    data = request.get_json()
    user_id = data.get('user_id')
    timer = ActiveTimer.query.get(user_id)
    if not timer:
        return jsonify({'error': 'No hay cronómetro activo'}), 400
    if timer.paused_at:
        return jsonify({'error': 'Ya está pausado'}), 400
    now = datetime.utcnow()
    timer.accumulated_seconds += int((now - timer.started_at).total_seconds())
    timer.paused_at = now
    db.session.commit()
    return jsonify({'accumulated_seconds': timer.accumulated_seconds})

@main.route('/timer/resume', methods=['POST'])
def resume_timer():
    data = request.get_json()
    user_id = data.get('user_id')
    timer = ActiveTimer.query.get(user_id)
    if not timer or not timer.paused_at:
        return jsonify({'error': 'No hay cronómetro pausado'}), 400
    now = datetime.utcnow()
    timer.started_at = now
    timer.paused_at = None
    db.session.commit()
    return jsonify({'resumed_at': now.isoformat()})

@main.route('/timer/stop', methods=['POST'])
def stop_timer():
    data = request.get_json()
    user_id = data.get('user_id')
    subject = data.get('subject', '').strip() or None
    timer = ActiveTimer.query.get(user_id)
    if not timer:
        return jsonify({'error': 'No hay cronómetro activo'}), 400
    now = datetime.utcnow()
    if timer.paused_at:
        duration = timer.accumulated_seconds
    else:
        duration = timer.accumulated_seconds + int((now - timer.started_at).total_seconds())
    session = (StudySession.query
               .filter_by(user_id=user_id, ended_at=None)
               .order_by(StudySession.id.desc()).first())
    if session:
        session.ended_at = now
        session.duration_seconds = duration
        session.subject = subject
    db.session.delete(timer)
    db.session.commit()
    user = User.query.get(user_id)
    streak, _ = check_and_award_badges(user)
    return jsonify({'duration_seconds': duration, 'streak': streak})

# ── Goals ─────────────────────────────────────────────
@main.route('/goals', methods=['POST'])
def set_goal():
    data = request.get_json()
    user_id = data.get('user_id')
    goal = Goal.query.filter_by(user_id=user_id).first()
    if not goal:
        goal = Goal(user_id=user_id)
        db.session.add(goal)
    goal.daily_hours  = float(data.get('daily_hours', 2))
    goal.weekly_hours = float(data.get('weekly_hours', 10))
    db.session.commit()
    return jsonify({'ok': True})

# ── Bets ──────────────────────────────────────────────
@main.route('/bets', methods=['GET'])
def get_bets():
    bets = Bet.query.order_by(Bet.created_at.desc()).limit(10).all()
    return jsonify([{
        'id': b.id, 'description': b.description,
        'week_start': str(b.week_start), 'resolved': b.resolved,
        'winner_id': b.winner_id, 'created_by': b.created_by
    } for b in bets])

@main.route('/bets', methods=['POST'])
def create_bet():
    data = request.get_json()
    week_start = date.today() - timedelta(days=date.today().weekday())
    bet = Bet(
        description=data.get('description', ''),
        created_by=data.get('user_id'),
        week_start=week_start
    )
    db.session.add(bet)
    db.session.commit()
    return jsonify({'id': bet.id, 'description': bet.description})

@main.route('/bets/<int:bet_id>/resolve', methods=['POST'])
def resolve_bet(bet_id):
    data = request.get_json()
    bet = Bet.query.get_or_404(bet_id)
    bet.winner_id = data.get('winner_id')
    bet.resolved = True
    db.session.commit()
    return jsonify({'ok': True})

# ── Sessions history ──────────────────────────────────
@main.route('/sessions/<int:user_id>')
def get_sessions(user_id):
    sessions = (StudySession.query
                .filter_by(user_id=user_id)
                .filter(StudySession.ended_at.isnot(None))
                .order_by(StudySession.started_at.desc())
                .limit(50).all())
    return jsonify([{
        'id': s.id,
        'started_at': s.started_at.strftime('%d/%m/%Y %H:%M'),
        'duration_seconds': s.duration_seconds,
        'subject': s.subject or '—'
    } for s in sessions])

# ── Stats ─────────────────────────────────────────────
@main.route('/stats')
def get_stats():
    users = User.query.all()
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    result = []

    for u in users:
        completed = [s for s in u.sessions if s.ended_at]
        total      = sum(s.duration_seconds for s in completed)
        today_secs = sum(s.duration_seconds for s in completed if s.started_at.date() == today)
        week_secs  = sum(s.duration_seconds for s in completed if s.started_at.date() >= week_start)

        active_elapsed = None
        active_paused  = False
        if u.timer:
            if u.timer.paused_at:
                active_elapsed = u.timer.accumulated_seconds
                active_paused  = True
            else:
                active_elapsed = u.timer.accumulated_seconds + int((datetime.utcnow() - u.timer.started_at).total_seconds())

        # streak
        study_days = sorted({s.started_at.date() for s in completed}, reverse=True)
        streak = 0
        if study_days:
            check = today
            for d in study_days:
                if d == check or d == check - timedelta(days=1):
                    streak += 1; check = d
                else: break

        # last 7 days
        day_map = defaultdict(int)
        for s in completed:
            day_map[str(s.started_at.date())] += s.duration_seconds
        history = [{'day': d, 'seconds': secs} for d, secs in sorted(day_map.items())][-7:]

        # goal
        goal = {'daily_hours': 2.0, 'weekly_hours': 10.0}
        if u.goal:
            goal = {'daily_hours': u.goal.daily_hours, 'weekly_hours': u.goal.weekly_hours}

        # badges
        badges = [{'key': b.badge_key, **BADGES.get(b.badge_key, {})} for b in u.badges]

        result.append({
            'id': u.id, 'username': u.username,
            'total_seconds': total,
            'total_sessions': len(completed),
            'today_seconds': today_secs,
            'week_seconds': week_secs,
            'active_elapsed': active_elapsed,
            'active_paused': active_paused,
            'streak': streak,
            'history': history,
            'goal': goal,
            'badges': badges,
        })

    result.sort(key=lambda x: x['total_seconds'], reverse=True)
    return jsonify(result)

@main.route('/health')
def health():
    return jsonify({'ok': True})