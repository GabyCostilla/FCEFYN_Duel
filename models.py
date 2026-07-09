from datetime import datetime
from app import db

class User(db.Model):
    __tablename__ = 'users'
    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sessions   = db.relationship('StudySession', backref='user', lazy=True)
    timer      = db.relationship('ActiveTimer', backref='user', uselist=False)
    goal       = db.relationship('Goal', backref='user', uselist=False)
    badges     = db.relationship('UserBadge', backref='user', lazy=True)

class StudySession(db.Model):
    __tablename__ = 'sessions'
    id               = db.Column(db.Integer, primary_key=True)
    user_id          = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    started_at       = db.Column(db.DateTime, nullable=False)
    ended_at         = db.Column(db.DateTime, nullable=True)
    duration_seconds = db.Column(db.Integer, default=0)
    subject          = db.Column(db.String(100), nullable=True)

class ActiveTimer(db.Model):
    __tablename__ = 'active_timers'
    user_id             = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    started_at          = db.Column(db.DateTime, nullable=False)
    paused_at           = db.Column(db.DateTime, nullable=True) 
    accumulated_seconds = db.Column(db.Integer, default=0)

class Goal(db.Model):
    __tablename__ = 'goals'
    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    daily_hours    = db.Column(db.Float, default=2.0)
    weekly_hours   = db.Column(db.Float, default=10.0)

class Bet(db.Model):
    __tablename__ = 'bets'
    id          = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    created_by  = db.Column(db.Integer, db.ForeignKey('users.id'))
    week_start  = db.Column(db.Date, nullable=False)
    winner_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    resolved    = db.Column(db.Boolean, default=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

class UserBadge(db.Model):
    __tablename__ = 'user_badges'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'))
    badge_key  = db.Column(db.String(50), nullable=False)
    earned_at  = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'badge_key'),)