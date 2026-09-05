"""
Helper utilities for JARVIS
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
import os
import asyncio
from decimal import Decimal


def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"${amount:,.2f}"


def format_percentage(value: float) -> str:
    """Format value as percentage"""
    return f"{value:.2%}"


def calculate_profit_loss(entry_price: float, exit_price: float, quantity: float) -> float:
    """Calculate profit/loss"""
    return (exit_price - entry_price) * quantity


def calculate_profit_loss_percentage(entry_price: float, exit_price: float) -> float:
    """Calculate profit/loss percentage"""
    if entry_price == 0:
        return 0.0
    return (exit_price - entry_price) / entry_price


def get_risk_level_label(risk: float) -> str:
    """Get risk level label"""
    if risk < 0.2:
        return "Very Low"
    elif risk < 0.4:
        return "Low"
    elif risk < 0.6:
        return "Medium"
    elif risk < 0.8:
        return "High"
    else:
        return "Very High"


def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
    """Calculate Sharpe ratio"""
    if not returns or len(returns) < 2:
        return 0.0
    
    mean_return = sum(returns) / len(returns)
    variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
    std_dev = variance ** 0.5
    
    if std_dev == 0:
        return 0.0
    
    return (mean_return - risk_free_rate) / std_dev


def calculate_max_drawdown(prices: List[float]) -> float:
    """Calculate maximum drawdown"""
    if not prices:
        return 0.0
    
    max_price = prices[0]
    max_drawdown = 0.0
    
    for price in prices:
        if price > max_price:
            max_price = price
        drawdown = (max_price - price) / max_price
        if drawdown > max_drawdown:
            max_drawdown = drawdown
    
    return max_drawdown


async def run_in_background(coro):
    """Run coroutine in background"""
    task = asyncio.create_task(coro)
    return task


def ensure_directory(path: str):
    """Ensure directory exists"""
    os.makedirs(path, exist_ok=True)


def load_json(file_path: str) -> Dict[str, Any]:
    """Load JSON file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_json(file_path: str, data: Dict[str, Any]):
    """Save JSON file"""
    ensure_directory(os.path.dirname(file_path))
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


def time_ago(dt: datetime) -> str:
    """Get human-readable time ago"""
    if not dt:
        return "Never"
    
    delta = datetime.utcnow() - dt
    
    if delta.days > 365:
        return f"{delta.days // 365} years ago"
    elif delta.days > 30:
        return f"{delta.days // 30} months ago"
    elif delta.days > 0:
        return f"{delta.days} days ago"
    elif delta.seconds > 3600:
        return f"{delta.seconds // 3600} hours ago"
    elif delta.seconds > 60:
        return f"{delta.seconds // 60} minutes ago"
    else:
        return "Just now"
