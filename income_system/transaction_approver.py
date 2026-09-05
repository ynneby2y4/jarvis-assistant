"""
Transaction Approver - User approval workflow
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from database.models import TransactionApproval, Transaction
from config import config
from utils.logger import get_logger
import uuid

logger = get_logger("transaction_approver")


class TransactionApprover:
    """Manage transaction approvals"""
    
    @staticmethod
    def create_approval_request(
        db: Session,
        user_id: str,
        strategy: str,
        description: str,
        expected_profit: float,
        risk_level: float,
        stop_loss: float,
        take_profit: float,
        approval_data: Dict = None
    ) -> TransactionApproval:
        """Create transaction approval request"""
        try:
            approval = TransactionApproval(
                id=str(uuid.uuid4()),
                user_id=user_id,
                strategy=strategy,
                description=description,
                expected_profit=expected_profit,
                risk_level=risk_level,
                stop_loss=stop_loss,
                take_profit=take_profit,
                status="pending",
                approval_data=approval_data or {},
                expires_at=datetime.utcnow() + timedelta(seconds=config.APPROVAL_TIMEOUT)
            )
            db.add(approval)
            db.commit()
            logger.info(f"Approval request created: {approval.id}")
            return approval
        except Exception as e:
            logger.error(f"Error creating approval request: {e}")
            db.rollback()
            raise
    
    @staticmethod
    def approve_transaction(
        db: Session,
        approval_id: str,
        user_id: str
    ) -> bool:
        """Approve transaction"""
        try:
            approval = db.query(TransactionApproval)\
                .filter(TransactionApproval.id == approval_id)\
                .filter(TransactionApproval.user_id == user_id)\
                .first()
            
            if not approval:
                logger.warning(f"Approval not found: {approval_id}")
                return False
            
            if approval.status != "pending":
                logger.warning(f"Approval not in pending status: {approval_id}")
                return False
            
            if approval.expires_at < datetime.utcnow():
                approval.status = "expired"
                db.commit()
                logger.warning(f"Approval expired: {approval_id}")
                return False
            
            approval.status = "approved"
            approval.approved_at = datetime.utcnow()
            db.commit()
            logger.info(f"Approval approved: {approval_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error approving transaction: {e}")
            db.rollback()
            return False
    
    @staticmethod
    def reject_transaction(
        db: Session,
        approval_id: str,
        user_id: str
    ) -> bool:
        """Reject transaction"""
        try:
            approval = db.query(TransactionApproval)\
                .filter(TransactionApproval.id == approval_id)\
                .filter(TransactionApproval.user_id == user_id)\
                .first()
            
            if not approval:
                logger.warning(f"Approval not found: {approval_id}")
                return False
            
            approval.status = "rejected"
            db.commit()
            logger.info(f"Approval rejected: {approval_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error rejecting transaction: {e}")
            db.rollback()
            return False
    
    @staticmethod
    def get_pending_approvals(
        db: Session,
        user_id: str
    ) -> List[TransactionApproval]:
        """Get pending approvals for user"""
        return db.query(TransactionApproval)\
            .filter(TransactionApproval.user_id == user_id)\
            .filter(TransactionApproval.status == "pending")\
            .order_by(TransactionApproval.created_at.desc())\
            .all()
    
    @staticmethod
    def cleanup_expired_approvals(db: Session):
        """Clean up expired approval requests"""
        try:
            expired = db.query(TransactionApproval)\
                .filter(TransactionApproval.status == "pending")\
                .filter(TransactionApproval.expires_at < datetime.utcnow())\
                .all()
            
            for approval in expired:
                approval.status = "expired"
            
            db.commit()
            logger.info(f"Cleaned up {len(expired)} expired approvals")
        except Exception as e:
            logger.error(f"Error cleaning up expired approvals: {e}")
            db.rollback()
