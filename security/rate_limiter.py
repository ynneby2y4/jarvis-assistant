"""
Rate Limiter - Prevent API abuse
"""
from datetime import datetime, timedelta
from typing import Dict
from collections import deque
import threading
from config import config
from utils.logger import get_logger

logger = get_logger("rate_limiter")


class RateLimiter:
    """Rate limiter using sliding window"""
    
    def __init__(
        self,
        requests: int = config.RATE_LIMIT_REQUESTS,
        period: int = config.RATE_LIMIT_PERIOD
    ):
        self.requests = requests
        self.period = period
        self.requests_log: Dict[str, deque] = {}
        self.lock = threading.Lock()
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed"""
        if not config.RATE_LIMIT_ENABLED:
            return True
        
        with self.lock:
            now = datetime.utcnow()
            cutoff = now - timedelta(seconds=self.period)
            
            if client_id not in self.requests_log:
                self.requests_log[client_id] = deque()
            
            # Remove old requests outside the window
            while self.requests_log[client_id] and self.requests_log[client_id][0] < cutoff:
                self.requests_log[client_id].popleft()
            
            # Check if limit exceeded
            if len(self.requests_log[client_id]) >= self.requests:
                logger.warning(f"Rate limit exceeded for client {client_id}")
                return False
            
            # Add current request
            self.requests_log[client_id].append(now)
            return True
    
    def get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for client"""
        if client_id not in self.requests_log:
            return self.requests
        
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.period)
        
        # Count requests in window
        count = sum(1 for req_time in self.requests_log[client_id] if req_time >= cutoff)
        return max(0, self.requests - count)


# Global rate limiter instance
rate_limiter = RateLimiter()
