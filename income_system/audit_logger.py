"""
Audit Logger - Income system audit trail
"""
from datetime import datetime
from sqlalchemy.orm import Session
from database.models import AuditLog
from typing import Dict
from utils.logger import get_logger

logger = get_logger("audit_logger")


class IncomeAuditLogger:
    """Log income system activities"""
    
    @staticmethod
    def log_income(
        db: Session,
        user_id: str,
        strategy: str,
        amount: float,
        details: Dict = None
    ):
        """Log income generation"""
        try:
            details = details or {}
            details["strategy"] = strategy
            details["amount"] = amount
            
            AuditLog.log_action(
                db=db,
                user_id=user_id,
                action="income_generated",
                details=details,
                status="success"
            )
        except Exception as e:
            logger.error(f"Error logging income: {e}")
    
    @staticmethod
    def log_transaction(
        db: Session,
        user_id: str,
        transaction_id: str,
        strategy: str,
        action: str,
        amount: float,
        status: str,
        details: Dict = None
    ):
        """Log transaction"""
        try:
            details = details or {}
            details["transaction_id"] = transaction_id
            details["strategy"] = strategy
            details["action"] = action
            details["amount"] = amount
            
            AuditLog.log_action(
                db=db,
                user_id=user_id,
                action="transaction_executed",
                details=details,
                status=status
            )
        except Exception as e:
            logger.error(f"Error logging transaction: {e}")
    
    @staticmethod
    def log_strategy_update(
        db: Session,
        user_id: str,
        strategy: str,
        changes: Dict
    ):
        """Log strategy update"""
        try:
            AuditLog.log_action(
                db=db,
                user_id=user_id,
                action="strategy_updated",
                details={
                    "strategy": strategy,
                    "changes": changes
                },
                status="success"
            )
        except Exception as e:
            logger.error(f"Error logging strategy update: {e}")
    
    @staticmethod
    def log_kill_switch(
        db: Session,
        user_id: str,
        kill_switch_type: str,
        details: Dict = None
    ):
        """Log kill switch activation"""
        try:
            AuditLog.log_action(
                db=db,
                user_id=user_id,
                action="kill_switch_activated",
                details={
                    "type": kill_switch_type,
                    **(details or {})
                },
                status="success"
            )
        except Exception as e:
            logger.error(f"Error logging kill switch: {e}")
