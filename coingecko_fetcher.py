"""
CoinGecko API Data Fetcher
Reliable cryptocurrency data fetching using CoinGecko API
"""
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
import time
import requests
from typing import Dict, List, Optional, Tuple

try:
    from pycoingecko import CoinGeckoAPI
    COINGECKO_AVAILABLE = True
except ImportError:
    COINGECKO_AVAILABLE = False
    logging.warning("PyCoinGecko not available. Install with: pip install pycoingecko")

logger = logging.getLogger(__name__)

class CoinGeckoDataFetcher:
    """Fetch cryptocurrency data from CoinGecko API."""
    
    def __init__(self):
        if COINGECKO_AVAILABLE:
            self.cg = CoinGeckoAPI()
        else:
            self.cg = None
        
        self.cache = {}
        self.last_request_time = 0
        self.min_request_interval = 1.0  # CoinGecko free tier: 10-30 requests/minute
        
        # Common cryptocurrency mappings
        self.crypto_map = {
            'BTC-USD': 'bitcoin',
            'ETH-USD': 'ethereum',
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'BITCOIN': 'bitcoin',
            'ETHEREUM': 'ethereum'
        }
    
    def _rate_limit(self):
        """Apply rate limiting for CoinGecko API."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _get_coin_id(self, symbol: str) -> str:
        """Get CoinGecko coin ID from symbol."""
        symbol_upper = symbol.upper()
        
        # Check our mapping first
        if symbol_upper in self.crypto_map:
            return self.crypto_map[symbol_upper]
        
        # Default mappings
        if symbol_upper.startswith('BTC'):
            return 'bitcoin'
        elif symbol_upper.startswith('ETH'):
            return 'ethereum'
        
        return symbol.lower()
    
    def get_price_history(self, symbol: str, start_date: str, end_date: str) -> pd.Series:
        """
        Get historical price data from CoinGecko.
        
        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC-USD', 'bitcoin')
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            pandas Series with date index and price values
        """
        if not COINGECKO_AVAILABLE or self.cg is None:
            logger.error("CoinGecko API not available")
            return pd.Series()
        
        cache_key = f"{symbol}_{start_date}_{end_date}"
        
        if cache_key in self.cache:
            logger.info(f"Using cached data for {symbol}")
            return self.cache[cache_key]
        
        try:
            coin_id = self._get_coin_id(symbol)
            logger.info(f"Fetching {symbol} ({coin_id}) data from {start_date} to {end_date}")
            
            # Convert dates to timestamps
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            
            # Calculate days difference
            days_diff = (end_dt - start_dt).days
            
            self._rate_limit()
            
            # For periods <= 365 days, use market_chart with days parameter
            # For longer periods, limit to 365 days (CoinGecko free tier)
            days_to_fetch = min(days_diff, 365)
            
            logger.info(f"Fetching {days_to_fetch} days of data for {coin_id}")
            
            data = self.cg.get_coin_market_chart_by_id(
                id=coin_id,
                vs_currency='usd',
                days=days_to_fetch
            )
            
            if 'prices' in data and data['prices']:
                # Convert to DataFrame
                prices_data = data['prices']
                df = pd.DataFrame(prices_data, columns=['timestamp', 'price'])
                
                # Convert timestamp to datetime
                df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
                df = df.set_index('date')
                
                # Sort by date
                df = df.sort_index()
                
                # For API calls with 'days' parameter, the data comes in reverse chronological order
                # and might extend beyond our requested date range
                # Only filter if we have a reasonable date range
                if days_diff <= 365:
                    # Be more flexible with date filtering - allow some buffer
                    start_buffer = start_dt - pd.Timedelta(days=1)
                    end_buffer = end_dt + pd.Timedelta(days=1)
                    df = df[(df.index >= start_buffer) & (df.index <= end_buffer)]
                
                # Create price series
                price_series = df['price']
                
                # Remove any duplicates and ensure ascending order
                price_series = price_series[~price_series.index.duplicated(keep='first')]
                price_series = price_series.sort_index()
                
                # Final filtering to exact date range if we have data
                if len(price_series) > 0 and days_diff <= 365:
                    price_series = price_series[(price_series.index >= start_dt) & (price_series.index <= end_dt)]
                
                # Cache the result
                self.cache[cache_key] = price_series
                
                logger.info(f"Successfully fetched {len(price_series)} data points for {symbol}")
                return price_series
            else:
                logger.warning(f"No price data found for {symbol}")
                return pd.Series()
                
        except Exception as e:
            logger.error(f"Error fetching {symbol} from CoinGecko: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return pd.Series()
    
    def get_multiple_prices(self, symbols: List[str], start_date: str, end_date: str) -> Dict[str, pd.Series]:
        """Get price data for multiple cryptocurrencies."""
        results = {}
        
        for symbol in symbols:
            try:
                price_data = self.get_price_history(symbol, start_date, end_date)
                if not price_data.empty:
                    results[symbol] = price_data
                
                # Rate limiting between requests
                time.sleep(1.5)  # Be conservative with free tier
                
            except Exception as e:
                logger.error(f"Error fetching {symbol}: {e}")
        
        return results
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for a cryptocurrency."""
        if not COINGECKO_AVAILABLE or self.cg is None:
            return None
        
        try:
            coin_id = self._get_coin_id(symbol)
            
            self._rate_limit()
            
            data = self.cg.get_price(ids=coin_id, vs_currencies='usd')
            
            if coin_id in data and 'usd' in data[coin_id]:
                return data[coin_id]['usd']
            
        except Exception as e:
            logger.error(f"Error fetching current price for {symbol}: {e}")
        
        return None
    
    def get_market_data(self, symbol: str) -> Dict[str, any]:
        """Get comprehensive market data for a cryptocurrency."""
        if not COINGECKO_AVAILABLE or self.cg is None:
            return {}
        
        try:
            coin_id = self._get_coin_id(symbol)
            
            self._rate_limit()
            
            data = self.cg.get_coin_by_id(coin_id, localization=False, tickers=False, 
                                        market_data=True, community_data=False, 
                                        developer_data=False, sparkline=False)
            
            if 'market_data' in data:
                market_data = data['market_data']
                
                return {
                    'current_price': market_data.get('current_price', {}).get('usd'),
                    'market_cap': market_data.get('market_cap', {}).get('usd'),
                    'total_volume': market_data.get('total_volume', {}).get('usd'),
                    'price_change_24h': market_data.get('price_change_24h'),
                    'price_change_percentage_24h': market_data.get('price_change_percentage_24h'),
                    'price_change_percentage_7d': market_data.get('price_change_percentage_7d'),
                    'price_change_percentage_30d': market_data.get('price_change_percentage_30d'),
                    'price_change_percentage_1y': market_data.get('price_change_percentage_1y'),
                    'ath': market_data.get('ath', {}).get('usd'),
                    'ath_date': market_data.get('ath_date', {}).get('usd'),
                    'atl': market_data.get('atl', {}).get('usd'),
                    'atl_date': market_data.get('atl_date', {}).get('usd')
                }
            
        except Exception as e:
            logger.error(f"Error fetching market data for {symbol}: {e}")
        
        return {}
    
    def get_status(self) -> Dict[str, any]:
        """Get API status information."""
        return {
            'api_available': COINGECKO_AVAILABLE,
            'cache_size': len(self.cache),
            'last_request_time': self.last_request_time,
            'min_interval': self.min_request_interval
        }
    
    def clear_cache(self):
        """Clear the cache."""
        self.cache.clear()
        logger.info("CoinGecko cache cleared")

# Global instance
_coingecko_fetcher = None

def get_coingecko_fetcher() -> CoinGeckoDataFetcher:
    """Get the global CoinGecko fetcher instance."""
    global _coingecko_fetcher
    if _coingecko_fetcher is None:
        _coingecko_fetcher = CoinGeckoDataFetcher()
    return _coingecko_fetcher

def get_crypto_price_history(symbol: str, start_date: str, end_date: str) -> pd.Series:
    """Convenience function to get crypto price history."""
    fetcher = get_coingecko_fetcher()
    return fetcher.get_price_history(symbol, start_date, end_date)

def get_crypto_market_data(symbol: str) -> Dict[str, any]:
    """Convenience function to get crypto market data."""
    fetcher = get_coingecko_fetcher()
    return fetcher.get_market_data(symbol)

def get_multiple_crypto_prices(symbols: List[str], start_date: str, end_date: str) -> Dict[str, pd.Series]:
    """Convenience function to get multiple crypto prices."""
    fetcher = get_coingecko_fetcher()
    return fetcher.get_multiple_prices(symbols, start_date, end_date)
