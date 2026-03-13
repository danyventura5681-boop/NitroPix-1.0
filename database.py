from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import random
import string
from config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String)
    first_name = Column(String)
    language = Column(String, default='en')
    diamonds = Column(Float, default=5.0)
    referred_by = Column(Integer, nullable=True)
    referral_code = Column(String, unique=True)
    last_daily = Column(DateTime, nullable=True)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_admin = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)

def get_user(telegram_id):
    session = SessionLocal()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    session.close()
    return user

def get_user_by_referral_code(code):
    session = SessionLocal()
    user = session.query(User).filter_by(referral_code=code).first()
    session.close()
    return user

def get_user_by_id(user_id):
    session = SessionLocal()
    user = session.query(User).filter_by(telegram_id=user_id).first()
    session.close()
    return user

def get_all_users():
    session = SessionLocal()
    users = session.query(User).all()
    session.close()
    return users

def create_user(telegram_id, username, first_name, referred_by=None):
    session = SessionLocal()
    ref_code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    user = User(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        referral_code=ref_code,
        diamonds=5.0
    )
    if referred_by:
        referrer = session.query(User).filter_by(telegram_id=referred_by).first()
        if referrer:
            user.referred_by = referred_by
            referrer.diamonds += 3
            user.diamonds += 3
    session.add(user)
    session.commit()
    session.refresh(user)
    session.close()
    return user

def update_user_language(telegram_id, language):
    session = SessionLocal()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if user:
        user.language = language
        session.commit()
    session.close()

def add_diamonds(telegram_id, amount):
    session = SessionLocal()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if user:
        user.diamonds += amount
        session.commit()
        new_balance = user.diamonds
    session.close()
    return new_balance

def deduct_diamond(telegram_id):
    session = SessionLocal()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if user and user.diamonds >= 1:
        user.diamonds -= 1
        session.commit()
        return True
    session.close()
    return False

def can_claim_daily(telegram_id):
    session = SessionLocal()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if not user or not user.last_daily:
        return True, 0
    time_diff = datetime.utcnow() - user.last_daily
    if time_diff.total_seconds() >= 86400:
        return True, 0
    else:
        remaining = 86400 - time_diff.total_seconds()
        hours = int(remaining // 3600)
        return False, hours

def set_daily_claimed(telegram_id):
    session = SessionLocal()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if user:
        user.last_daily = datetime.utcnow()
        session.commit()
    session.close()

def is_admin(telegram_id):
    session = SessionLocal()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    result = user.is_admin if user else False
    session.close()
    return result

def make_admin(telegram_id):
    session = SessionLocal()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if user and not user.is_admin:
        user.is_admin = True
        session.commit()
        session.close()
        return True
    session.close()
    return False

def is_banned(telegram_id):
    session = SessionLocal()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    result = user.is_banned if user else False
    session.close()
    return result

def ban_user(telegram_id):
    session = SessionLocal()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if user and not user.is_banned:
        user.is_banned = True
        session.commit()
        session.close()
        return True
    session.close()
    return False

def unban_user(telegram_id):
    session = SessionLocal()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if user and user.is_banned:
        user.is_banned = False
        session.commit()
        session.close()
        return True
    session.close()
    return False

def update_last_active(telegram_id):
    """Actualiza la última actividad del usuario"""
    session = SessionLocal()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if user:
        user.last_active = datetime.utcnow()
        session.commit()
    session.close()

def get_user_stats():
    """Obtiene estadísticas de usuarios"""
    session = SessionLocal()
    
    total_users = session.query(User).count()
    
    now = datetime.utcnow()
    last_month = now - timedelta(days=30)
    last_week = now - timedelta(days=7)
    last_48h = now - timedelta(hours=48)
    
    month_users = session.query(User).filter(User.created_at >= last_month).count()
    week_users = session.query(User).filter(User.created_at >= last_week).count()
    last_48h_users = session.query(User).filter(User.created_at >= last_48h).count()
    
    # Usuarios activos en las últimas 48h (los que han hecho algo)
    active_48h = session.query(User).filter(User.last_active >= last_48h).count()
    
    session.close()
    
    return {
        "total": total_users,
        "last_month": month_users,
        "last_week": week_users,
        "last_48h": last_48h_users,
        "active_48h": active_48h
    }