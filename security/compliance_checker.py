"""
Compliance Checker - Regulatory compliance
"""
from datetime import datetime
from typing import Dict, List
from database.models import AuditLog
from utils.logger import get_logger

logger = get_logger("compliance_checker")


class ComplianceChecker:
    """Check compliance requirements"""
    
    @staticmethod
    def log_action(
        db,
        user_id: str,
        action: str,
        details: Dict,
        status: str = "success",
        error_message: str = None
    ):
        """Log action for audit trail"""
        try:
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                details=details,
                status=status,
                error_message=error_message,
                created_at=datetime.utcnow()
            )
            db.add(audit_log)
            db.commit()
            logger.info(f"Audit log created: {action} by {user_id}")
        except Exception as e:
            logger.error(f"Error logging action: {e}")
            db.rollback()
    
    @staticmethod
    def get_audit_trail(db, user_id: str, limit: int = 100) -> List[AuditLog]:
        """Get audit trail for user"""
        return db.query(AuditLog)\
            .filter(AuditLog.user_id == user_id)\
            .order_by(AuditLog.created_at.desc())\
            .limit(limit)\
            .all()
    
    @staticmethod
    def check_transaction_limits(db, user_id: str, amount: float) -> bool:
        """Check if transaction violates limits"""
        # Query recent transactions
        recent_transactions = db.query(AuditLog)\
            .filter(AuditLog.user_id == user_id)\
            .filter(AuditLog.action == "transaction_executed")\
            .order_by(AuditLog.created_at.desc())\
            .limit(10)\
            .all()
        
        # Check limits (example: max 10 trades per hour)
        if len(recent_transactions) >= 10:
            logger.warning(f"Transaction limit exceeded for user {user_id}")
            return False
        
        return True
