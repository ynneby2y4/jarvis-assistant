"""
Database Models for JARVIS
"""
from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    api_key = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    approvals = relationship("TransactionApproval", back_populates="user")
    portfolio = relationship("Portfolio", back_populates="user", uselist=False)
    knowledge_entries = relationship("KnowledgeEntry", back_populates="user")


class Conversation(Base):
    """Conversation history"""
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    context = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="conversations")


class Portfolio(Base):
    """User portfolio"""
    __tablename__ = "portfolios"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), unique=True)
    total_value = Column(Float, default=0.0)
    cash_balance = Column(Float, default=0.0)
    total_invested = Column(Float, default=0.0)
    profit_rate = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.5)
    last_rebalance = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="portfolio")
    assets = relationship("Asset", back_populates="portfolio")
    income_records = relationship("IncomeRecord", back_populates="portfolio")


class Asset(Base):
    """Asset in portfolio"""
    __tablename__ = "assets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = Column(String, ForeignKey("portfolios.id"), index=True)
    symbol = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    purchase_price = Column(Float)
    current_price = Column(Float)
    total_value = Column(Float)
    allocation_percentage = Column(Float)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="assets")


class Transaction(Base):
    """Financial transaction"""
    __tablename__ = "transactions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True)
    strategy = Column(String, nullable=False)
    action = Column(String)  # BUY, SELL, STAKE, etc.
    asset = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String, default="pending")  # pending, executed, failed, cancelled
    profit_loss = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    executed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="transactions")


class TransactionApproval(Base):
    """Transaction approval request"""
    __tablename__ = "transaction_approvals"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True)
    transaction_id = Column(String, ForeignKey("transactions.id"))
    strategy = Column(String, nullable=False)
    description = Column(Text)
    expected_profit = Column(Float)
    risk_level = Column(Float)
    stop_loss = Column(Float)
    take_profit = Column(Float)
    status = Column(String, default="pending")  # pending, approved, rejected, expired
    approval_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    approved_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="approvals")


class IncomeRecord(Base):
    """Income generation record"""
    __tablename__ = "income_records"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = Column(String, ForeignKey("portfolios.id"), index=True)
    strategy = Column(String, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    portfolio_value = Column(Float)
    cumulative_income = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="income_records")


class Strategy(Base):
    """Income generation strategy"""
    __tablename__ = "strategies"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)
    strategy_type = Column(String, nullable=False)  # CRYPTO_TRADING, FOREX, DeFi, etc.
    description = Column(Text)
    risk_level = Column(Float, default=0.5)
    expected_return = Column(Float, default=0.1)
    is_active = Column(Boolean, default=True)
    is_paused = Column(Boolean, default=False)
    pause_duration = Column(Integer)  # seconds
    performance_score = Column(Float, default=0.0)
    total_profit = Column(Float, default=0.0)
    trades_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class KnowledgeEntry(Base):
    """Knowledge base entry"""
    __tablename__ = "knowledge_entries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True)
    concept = Column(String, nullable=False, index=True)
    data = Column(JSON, nullable=False)
    weight = Column(Float, default=1.0)
    source = Column(String)  # user, internet, market_data, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_accessed = Column(DateTime)
    access_count = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="knowledge_entries")


class AuditLog(Base):
    """Audit log for compliance"""
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True)
    action = Column(String, nullable=False, index=True)
    details = Column(JSON)
    status = Column(String)  # success, failure
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class SystemStatus(Base):
    """System status tracking"""
    __tablename__ = "system_status"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    income_engine_running = Column(Boolean, default=False)
    last_income_run = Column(DateTime)
    total_daily_income = Column(Float, default=0.0)
    total_monthly_income = Column(Float, default=0.0)
    total_yearly_income = Column(Float, default=0.0)
    active_strategies_count = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
