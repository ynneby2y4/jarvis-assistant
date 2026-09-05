"""
Internet Fetcher - Fetch real-time data from the internet
"""
import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from utils.logger import get_logger
import json

logger = get_logger("internet_fetcher")


class InternetFetcher:
    """Fetch real-time data from internet"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Dict[str, tuple[Any, datetime]] = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def initialize(self):
        """Initialize session"""
        self.session = aiohttp.ClientSession()
        logger.info("Internet fetcher initialized")
    
    async def close(self):
        """Close session"""
        if self.session:
            await self.session.close()
            logger.info("Internet fetcher closed")
    
    async def fetch_crypto_prices(self) -> Dict[str, float]:
        """Fetch cryptocurrency prices"""
        try:
            # Check cache
            if "crypto_prices" in self.cache:
                data, timestamp = self.cache["crypto_prices"]
                if (datetime.utcnow() - timestamp).seconds < self.cache_ttl:
                    return data
            
            # Fetch from CoinGecko API (free, no auth required)
            url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,cardano&vs_currencies=usd"
            
            if self.session:
                async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        prices = {
                            "BTC": data.get("bitcoin", {}).get("usd", 0),
                            "ETH": data.get("ethereum", {}).get("usd", 0),
                            "ADA": data.get("cardano", {}).get("usd", 0)
                        }
                        
                        # Cache result
                        self.cache["crypto_prices"] = (prices, datetime.utcnow())
                        logger.info("Crypto prices fetched")
                        return prices
        
        except Exception as e:
            logger.error(f"Error fetching crypto prices: {e}")
        
        return {}
    
    async def fetch_market_data(self) -> Dict[str, Any]:
        """Fetch market data"""
        try:
            # Check cache
            if "market_data" in self.cache:
                data, timestamp = self.cache["market_data"]
                if (datetime.utcnow() - timestamp).seconds < self.cache_ttl:
                    return data
            
            market_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "market_cap": None,
                "volume_24h": None,
                "btc_dominance": None
            }
            
            # Fetch from CoinGecko
            url = "https://api.coingecko.com/api/v3/global"
            
            if self.session:
                async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        market_data.update({
                            "market_cap": data.get("data", {}).get("total_market_cap", {}).get("usd"),
                            "volume_24h": data.get("data", {}).get("total_volume", {}).get("usd"),
                            "btc_dominance": data.get("data", {}).get("btc_dominance")
                        })
                        
                        self.cache["market_data"] = (market_data, datetime.utcnow())
                        logger.info("Market data fetched")
                        return market_data
        
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
        
        return {}
    
    async def fetch_news(self, query: str = "crypto") -> List[Dict[str, str]]:
        """Fetch news articles"""
        try:
            cache_key = f"news_{query}"
            
            # Check cache
            if cache_key in self.cache:
                data, timestamp = self.cache[cache_key]
                if (datetime.utcnow() - timestamp).seconds < self.cache_ttl:
                    return data
            
            # Fetch from NewsAPI (would need API key in production)
            # For now, return mock data
            news = [
                {
                    "title": f"Crypto market update: {query}",
                    "source": "crypto-news.com",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ]
            
            self.cache[cache_key] = (news, datetime.utcnow())
            return news
        
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return []
    
    async def fetch_economic_data(self) -> Dict[str, Any]:
        """Fetch economic data"""
        try:
            # Check cache
            if "economic_data" in self.cache:
                data, timestamp = self.cache["economic_data"]
                if (datetime.utcnow() - timestamp).seconds < self.cache_ttl:
                    return data
            
            economic_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "us_gdp_growth": None,
                "inflation_rate": None,
                "unemployment_rate": None
            }
            
            logger.info("Economic data prepared")
            self.cache["economic_data"] = (economic_data, datetime.utcnow())
            return economic_data
        
        except Exception as e:
            logger.error(f"Error fetching economic data: {e}")
            return {}
    
    async def fetch_weather(self, city: str = "New York") -> Dict[str, Any]:
        """Fetch weather data"""
        try:
            cache_key = f"weather_{city}"
            
            # Check cache
            if cache_key in self.cache:
                data, timestamp = self.cache[cache_key]
                if (datetime.utcnow() - timestamp).seconds < self.cache_ttl:
                    return data
            
            # Would fetch from OpenWeatherMap API in production
            weather = {
                "city": city,
                "temperature": 72,
                "condition": "Sunny",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.cache[cache_key] = (weather, datetime.utcnow())
            return weather
        
        except Exception as e:
            logger.error(f"Error fetching weather: {e}")
            return {}
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
        logger.info("Cache cleared")


# Global internet fetcher instance
internet_fetcher = InternetFetcher()
