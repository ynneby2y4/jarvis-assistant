"""
JARVIS Configuration Module
"""
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()


class Config:
    """Base configuration"""
    DEBUG = False
    TESTING = False
    
    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    
    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///./jarvis.db"
    )
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "jarvis-secret-key-change-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # API Keys (encrypted in vault in production)
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
    BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "")
    COINBASE_API_KEY = os.getenv("COINBASE_API_KEY", "")
    KRAKEN_API_KEY = os.getenv("KRAKEN_API_KEY", "")
    KRAKEN_API_SECRET = os.getenv("KRAKEN_API_SECRET", "")
    
    # Redis (for caching and real-time updates)
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Income Generation
    INCOME_ENGINE_ENABLED = os.getenv("INCOME_ENGINE_ENABLED", "True").lower() == "true"
    REQUIRE_APPROVAL = os.getenv("REQUIRE_APPROVAL", "True").lower() == "true"
    APPROVAL_TIMEOUT = int(os.getenv("APPROVAL_TIMEOUT", 300))  # 5 minutes
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_PERIOD = 60  # seconds
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/jarvis.log")
    
    # Knowledge Base
    KNOWLEDGE_BASE_PATH = os.getenv("KNOWLEDGE_BASE_PATH", "data/knowledge_base")
    INCOME_HISTORY_PATH = os.getenv("INCOME_HISTORY_PATH", "data/income_history")
    
    # Risk Management
    MAX_DAILY_LOSS = float(os.getenv("MAX_DAILY_LOSS", 1000))
    MAX_PORTFOLIO_RISK = float(os.getenv("MAX_PORTFOLIO_RISK", 0.7))
    MIN_PROFIT_TARGET = float(os.getenv("MIN_PROFIT_TARGET", 100))
    
    # Strategy Parameters
    DEFAULT_RISK_LEVEL = float(os.getenv("DEFAULT_RISK_LEVEL", 0.5))
    MIN_TRADE_AMOUNT = float(os.getenv("MIN_TRADE_AMOUNT", 10))
    MAX_TRADE_AMOUNT = float(os.getenv("MAX_TRADE_AMOUNT", 10000))


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    DATABASE_URL = "sqlite:///./jarvis_dev.db"


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/jarvis_prod")
    REQUIRE_APPROVAL = True
    INCOME_ENGINE_ENABLED = True


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_URL = "sqlite:///:memory:"
    INCOME_ENGINE_ENABLED = False
    REQUIRE_APPROVAL = True
    RATE_LIMIT_ENABLED = False


def get_config() -> Config:
    """Get configuration based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
    }
    
    return config_map.get(env, DevelopmentConfig)


config = get_config()
