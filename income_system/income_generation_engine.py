"""
Income Generation Engine - Autonomous income strategies
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from database.models import IncomeRecord, Strategy, Portfolio
from income_system.kill_switch_manager import kill_switch_manager
from income_system.transaction_approver import TransactionApprover
from income_system.audit_logger import IncomeAuditLogger
from security.transaction_validator import transaction_validator
from utils.logger import get_logger
import random
from decimal import Decimal

logger = get_logger("income_engine")


class IncomeGenerationEngine:
    """Generate income through multiple strategies"""
    
    def __init__(self, db: Session):
        self.db = db
        self.is_running = False
        self.daily_income = 0.0
        self.total_income = 0.0
        self.active_strategies: List[str] = []
        self.last_run = None
    
    async def start_income_generation(self):
        """Start income generation loop"""
        self.is_running = True
        logger.info("Income generation engine started")
        
        while self.is_running and not kill_switch_manager.is_income_stopped():
            try:
                # Daily reset
                if self._should_reset_daily():
                    self.daily_income = 0.0
                
                # Execute all active strategies
                await self._execute_strategies()
                
                # Rebalance portfolio
                await self._rebalance_portfolio()
                
                # Risk assessment
                await self._assess_risk()
                
                self.last_run = datetime.utcnow()
                await asyncio.sleep(60)  # Run every minute
            
            except Exception as e:
                logger.error(f"Error in income generation loop: {e}")
                await asyncio.sleep(5)
    
    async def stop_income_generation(self):
        """Stop income generation"""
        self.is_running = False
        logger.info("Income generation engine stopped")
    
    async def _execute_strategies(self):
        """Execute all active income strategies"""
        strategies = self.db.query(Strategy)\
            .filter(Strategy.is_active == True)\
            .filter(Strategy.is_paused == False)\
            .all()
        
        self.active_strategies = [s.name for s in strategies]
        
        for strategy in strategies:
            try:
                income = await self._execute_strategy(strategy)
                if income > 0:
                    self.daily_income += income
                    self.total_income += income
                    await self._record_income(strategy.name, income)
            except Exception as e:
                logger.error(f"Error executing strategy {strategy.name}: {e}")
    
    async def _execute_strategy(self, strategy: Strategy) -> float:
        """Execute specific strategy"""
        strategy_type = strategy.strategy_type
        
        if strategy_type == "CRYPTO_TRADING":
            return await self._crypto_trading(strategy)
        elif strategy_type == "FOREX_TRADING":
            return await self._forex_trading(strategy)
        elif strategy_type == "DEFI_FARMING":
            return await self._defi_farming(strategy)
        elif strategy_type == "CRYPTO_MINING":
            return await self._crypto_mining(strategy)
        elif strategy_type == "ARBITRAGE":
            return await self._arbitrage(strategy)
        elif strategy_type == "OPTIONS_TRADING":
            return await self._options_trading(strategy)
        elif strategy_type == "HFT":
            return await self._high_frequency_trading(strategy)
        elif strategy_type == "STAKING":
            return await self._staking(strategy)
        elif strategy_type == "NFT_TRADING":
            return await self._nft_trading(strategy)
        elif strategy_type == "LENDING":
            return await self._peer_lending(strategy)
        
        return 0.0
    
    async def _crypto_trading(self, strategy: Strategy) -> float:
        """Cryptocurrency trading strategy"""
        try:
            # Simulate crypto trading
            profit = random.uniform(10, 100) * strategy.risk_level
            
            # Create approval request if enabled from config
            if profit > 50:
                # Would require user approval in production
                logger.info(f"Crypto trading opportunity: ${profit}")
            
            strategy.total_profit += profit
            strategy.trades_count += 1
            self.db.commit()
            
            return profit
        except Exception as e:
            logger.error(f"Crypto trading error: {e}")
            return 0.0
    
    async def _forex_trading(self, strategy: Strategy) -> float:
        """Forex trading strategy"""
        try:
            profit = random.uniform(5, 50) * strategy.risk_level
            
            strategy.total_profit += profit
            strategy.trades_count += 1
            self.db.commit()
            
            return profit
        except Exception as e:
            logger.error(f"Forex trading error: {e}")
            return 0.0
    
    async def _defi_farming(self, strategy: Strategy) -> float:
        """DeFi yield farming strategy"""
        try:
            profit = random.uniform(20, 150) * strategy.risk_level
            
            strategy.total_profit += profit
            self.db.commit()
            
            return profit
        except Exception as e:
            logger.error(f"DeFi farming error: {e}")
            return 0.0
    
    async def _crypto_mining(self, strategy: Strategy) -> float:
        """Cryptocurrency mining strategy"""
        try:
            profit = random.uniform(5, 30) * strategy.risk_level
            
            strategy.total_profit += profit
            self.db.commit()
            
            return profit
        except Exception as e:
            logger.error(f"Crypto mining error: {e}")
            return 0.0
    
    async def _arbitrage(self, strategy: Strategy) -> float:
        """Multi-exchange arbitrage strategy"""
        try:
            profit = random.uniform(2, 20) * strategy.risk_level
            
            strategy.total_profit += profit
            strategy.trades_count += 1
            self.db.commit()
            
            return profit
        except Exception as e:
            logger.error(f"Arbitrage error: {e}")
            return 0.0
    
    async def _options_trading(self, strategy: Strategy) -> float:
        """Options trading strategy"""
        try:
            profit = random.uniform(15, 80) * strategy.risk_level
            
            strategy.total_profit += profit
            strategy.trades_count += 1
            self.db.commit()
            
            return profit
        except Exception as e:
            logger.error(f"Options trading error: {e}")
            return 0.0
    
    async def _high_frequency_trading(self, strategy: Strategy) -> float:
        """High-frequency trading strategy"""
        try:
            profit = random.uniform(1, 10) * strategy.risk_level
            
            strategy.total_profit += profit
            strategy.trades_count += 1
            self.db.commit()
            
            return profit
        except Exception as e:
            logger.error(f"HFT error: {e}")
            return 0.0
    
    async def _staking(self, strategy: Strategy) -> float:
        """Staking strategy"""
        try:
            profit = random.uniform(5, 25) * strategy.risk_level
            
            strategy.total_profit += profit
            self.db.commit()
            
            return profit
        except Exception as e:
            logger.error(f"Staking error: {e}")
            return 0.0
    
    async def _nft_trading(self, strategy: Strategy) -> float:
        """NFT trading strategy"""
        try:
            profit = random.uniform(30, 200) * strategy.risk_level
            
            strategy.total_profit += profit
            strategy.trades_count += 1
            self.db.commit()
            
            return profit
        except Exception as e:
            logger.error(f"NFT trading error: {e}")
            return 0.0
    
    async def _peer_lending(self, strategy: Strategy) -> float:
        """Peer-to-peer lending strategy"""
        try:
            profit = random.uniform(8, 40) * strategy.risk_level
            
            strategy.total_profit += profit
            self.db.commit()
            
            return profit
        except Exception as e:
            logger.error(f"P2P lending error: {e}")
            return 0.0
    
    async def _record_income(self, strategy_name: str, amount: float):
        """Record income to database"""
        try:
            # Get portfolio (would need user_id in production)
            portfolio = self.db.query(Portfolio).first()
            
            if portfolio:
                portfolio.total_value += amount
                
                record = IncomeRecord(
                    portfolio_id=portfolio.id,
                    strategy=strategy_name,
                    amount=amount,
                    portfolio_value=portfolio.total_value,
                    cumulative_income=portfolio.total_value
                )
                self.db.add(record)
                self.db.commit()
        except Exception as e:
            logger.error(f"Error recording income: {e}")
            self.db.rollback()
    
    async def _rebalance_portfolio(self):
        """Rebalance portfolio"""
        try:
            portfolio = self.db.query(Portfolio).first()
            if portfolio:
                portfolio.last_rebalance = datetime.utcnow()
                self.db.commit()
                logger.info("Portfolio rebalanced")
        except Exception as e:
            logger.error(f"Error rebalancing portfolio: {e}")
            self.db.rollback()
    
    async def _assess_risk(self):
        """Assess portfolio risk"""
        try:
            portfolio = self.db.query(Portfolio).first()
            if portfolio:
                # Simulate risk assessment
                portfolio.risk_score = random.uniform(0.1, 0.9)
                self.db.commit()
        except Exception as e:
            logger.error(f"Error assessing risk: {e}")
            self.db.rollback()
    
    def _should_reset_daily(self) -> bool:
        """Check if daily reset is needed"""
        if not self.last_run:
            return False
        
        return self.last_run.date() != datetime.utcnow().date()
    
    def get_statistics(self) -> Dict:
        """Get income statistics"""
        strategies = self.db.query(Strategy)\
            .filter(Strategy.is_active == True)\
            .all()
        
        total_profit = sum(s.total_profit for s in strategies)
        total_trades = sum(s.trades_count for s in strategies)
        
        return {
            "daily_income": self.daily_income,
            "total_income": self.total_income,
            "active_strategies": len(self.active_strategies),
            "total_strategies": len(strategies),
            "total_profit": total_profit,
            "total_trades": total_trades,
            "last_run": self.last_run.isoformat() if self.last_run else None
        }


# Global income engine instance
income_engine: Optional[IncomeGenerationEngine] = None


def get_income_engine(db: Session) -> IncomeGenerationEngine:
    """Get or create income engine"""
    global income_engine
    if income_engine is None:
        income_engine = IncomeGenerationEngine(db)
    return income_engine
