"""
Transaction Validator - Pre-flight transaction checks
"""
from typing import Dict, Tuple
from config import config
from utils.logger import get_logger

logger = get_logger("transaction_validator")


class TransactionValidator:
    """Validate transactions before execution"""
    
    def __init__(self):
        self.daily_loss = 0.0
        self.daily_volume = 0.0
    
    def validate_transaction(
        self,
        amount: float,
        risk_level: float,
        expected_profit: float,
        strategy: str
    ) -> Tuple[bool, str]:
        """Validate transaction"""
        # Check minimum amount
        if amount < config.MIN_TRADE_AMOUNT:
            return False, f"Amount {amount} below minimum {config.MIN_TRADE_AMOUNT}"
        
        # Check maximum amount
        if amount > config.MAX_TRADE_AMOUNT:
            return False, f"Amount {amount} exceeds maximum {config.MAX_TRADE_AMOUNT}"
        
        # Check risk level
        if risk_level > config.MAX_PORTFOLIO_RISK:
            return False, f"Risk level {risk_level} exceeds maximum {config.MAX_PORTFOLIO_RISK}"
        
        # Check daily loss limit
        if self.daily_loss + abs(expected_profit) if expected_profit < 0 else 0 > config.MAX_DAILY_LOSS:
            return False, f"Daily loss limit exceeded"
        
        # Check minimum profit
        if expected_profit < config.MIN_PROFIT_TARGET and strategy not in ["staking", "mining"]:
            return False, f"Expected profit {expected_profit} below minimum {config.MIN_PROFIT_TARGET}"
        
        logger.info(f"Transaction validated: {strategy} for ${amount}")
        return True, "Transaction valid"
    
    def update_daily_metrics(self, profit_loss: float, amount: float):
        """Update daily metrics"""
        self.daily_volume += amount
        if profit_loss < 0:
            self.daily_loss += abs(profit_loss)
    
    def reset_daily_metrics(self):
        """Reset daily metrics"""
        self.daily_loss = 0.0
        self.daily_volume = 0.0


# Global validator instance
transaction_validator = TransactionValidator()
