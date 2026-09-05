"""
Kill Switch Manager - Dual kill switch implementation
"""
from enum import Enum
from typing import Callable, Optional
from datetime import datetime
import asyncio
from utils.logger import get_logger

logger = get_logger("kill_switch_manager")


class KillSwitchType(Enum):
    """Kill switch types"""
    GRACEFUL_SHUTDOWN = "graceful_shutdown"
    FACTORY_RESET = "factory_reset"


class KillSwitchManager:
    """Manage kill switches"""
    
    def __init__(self):
        self.income_stopped = False
        self.system_paused = False
        self.kill_switch_type: Optional[KillSwitchType] = None
        self.stop_callbacks: list[Callable] = []
        self.reset_callbacks: list[Callable] = []
        self.last_kill_switch_time: Optional[datetime] = None
    
    def register_stop_callback(self, callback: Callable):
        """Register callback for graceful shutdown"""
        self.stop_callbacks.append(callback)
    
    def register_reset_callback(self, callback: Callable):
        """Register callback for factory reset"""
        self.reset_callbacks.append(callback)
    
    async def graceful_shutdown(self) -> bool:
        """Execute graceful shutdown - stops processes, keeps data"""
        try:
            logger.info("Executing graceful shutdown...")
            self.kill_switch_type = KillSwitchType.GRACEFUL_SHUTDOWN
            self.income_stopped = True
            self.system_paused = True
            
            # Execute all stop callbacks
            for callback in self.stop_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback()
                    else:
                        callback()
                except Exception as e:
                    logger.error(f"Error in stop callback: {e}")
            
            self.last_kill_switch_time = datetime.utcnow()
            logger.info("Graceful shutdown completed successfully")
            return True
        
        except Exception as e:
            logger.error(f"Error during graceful shutdown: {e}")
            return False
    
    async def factory_reset(self) -> bool:
        """Execute factory reset - complete wipe of data"""
        try:
            logger.warning("Executing factory reset - this will delete all data!")
            self.kill_switch_type = KillSwitchType.FACTORY_RESET
            self.income_stopped = True
            self.system_paused = True
            
            # Execute all reset callbacks
            for callback in self.reset_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback()
                    else:
                        callback()
                except Exception as e:
                    logger.error(f"Error in reset callback: {e}")
            
            self.last_kill_switch_time = datetime.utcnow()
            logger.warning("Factory reset completed successfully")
            return True
        
        except Exception as e:
            logger.error(f"Error during factory reset: {e}")
            return False
    
    async def resume_operations(self) -> bool:
        """Resume operations after graceful shutdown"""
        if self.kill_switch_type == KillSwitchType.GRACEFUL_SHUTDOWN:
            try:
                logger.info("Resuming operations...")
                self.income_stopped = False
                self.system_paused = False
                self.kill_switch_type = None
                logger.info("Operations resumed successfully")
                return True
            except Exception as e:
                logger.error(f"Error resuming operations: {e}")
                return False
        else:
            logger.warning("Cannot resume after factory reset")
            return False
    
    def is_income_stopped(self) -> bool:
        """Check if income generation is stopped"""
        return self.income_stopped
    
    def is_system_paused(self) -> bool:
        """Check if system is paused"""
        return self.system_paused
    
    def get_status(self) -> dict:
        """Get kill switch status"""
        return {
            "income_stopped": self.income_stopped,
            "system_paused": self.system_paused,
            "kill_switch_type": self.kill_switch_type.value if self.kill_switch_type else None,
            "last_activation": self.last_kill_switch_time.isoformat() if self.last_kill_switch_time else None
        }


# Global kill switch manager instance
kill_switch_manager = KillSwitchManager()
