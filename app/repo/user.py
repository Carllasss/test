from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    """Пользователь ТГ"""
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)

    bitrix_data = relationship("BitrixLead", back_populates="user", uselist=False,cascade="all, delete-orphan")
    form_history = relationship("FormHistory", back_populates="user", cascade="all, delete-orphan")
    admin_data = relationship("Admin", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User>(user_id={self.id}, telegram_id={self.telegram_id})"


class BitrixLead(Base):
    """Данные по лидам битрикса"""
    __tablename__ = 'bitrix_lead'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), unique=True, nullable=False)
    lead_id = Column(Integer, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="bitrix_lead")

    def __repr__(self):
        return f"<BitrixLead>(user_id={self.user_id}, lead_id={self.lead_id})"



class FormHistory(Base):
    """История заполнений"""
    __tablename__ = 'form_history'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), unique=True, nullable=False)

    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)

    via_bot = Column(Boolean, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="form_history")

    def __repr__(self):
        return f"<FormHistory>(user_id={self.user_id}, name={self.name}, phone={self.phone})"


class Admin(Base):
    """Админские права"""
    __tablename__ = 'admin'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), unique=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="admin")

    def __repr__(self):
        return f"<Admin>(user_id={self.user_id})"
