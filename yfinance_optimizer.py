"""
Yahoo Finance Optimization Utilities
Advanced strategies to work around rate limits and improve data fetching reliability
"""
import yfinance as yf
import pandas as pd
import numpy as np
import time
import random
import logging
from typing import Dict, List, Optional
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from functools import lru_cache

logger = logging.getLogger(__name__)

class YFinanceOptimizer:
    """Optimized Yahoo Finance data fetching with rate limiting strategies."""
    
    def __init__(self):
        self.session = self._create_optimized_session()
        self.cache = {}
        self.request_count = 0
        self.last_request_time = 0
        self.min_request_interval = 0.5  # Minimum seconds between requests
        
    def _create_optimized_session(self) -> requests.Session:
        """Create an optimized session with proper headers."""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        return session
    
    def _rate_limit(self):
        """Apply rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
        
        # Add extra delay every 10 requests
        if self.request_count % 10 == 0:
            time.sleep(random.uniform(2, 5))
            logger.info(f"Rate limit pause after {self.request_count} requests")
    
    def fetch_single_symbol(self, symbol: str, start: str, end: str) -> pd.Series:
        """Fetch data for a single symbol with multiple strategies."""
        cache_key = f"{symbol}_{start}_{end}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        strategies = [
            self._fetch_with_optimized_session,
            self._fetch_with_standard_method,
            self._fetch_with_download,
            self._fetch_with_period_method
        ]
        
        for i, strategy in enumerate(strategies):
            try:
                self._rate_limit()
                logger.info(f"Trying strategy {i+1} for {symbol}")
                
                data = strategy(symbol, start, end)
                
                if not data.empty:
                    self.cache[cache_key] = data
                    logger.info(f"Successfully fetched {len(data)} data points for {symbol} using strategy {i+1}")
                    return data
                    
            except Exception as e:
                logger.warning(f"Strategy {i+1} failed for {symbol}: {e}")
                if i < len(strategies) - 1:
                    time.sleep(random.uniform(1, 3))
        
        logger.error(f"All strategies failed for {symbol}")
        return pd.Series()
    
    def _fetch_with_optimized_session(self, symbol: str, start: str, end: str) -> pd.Series:
        """Fetch using optimized session - adjusted for yfinance 0.2.65+."""
        # For yfinance 0.2.65+, let yfinance handle the session internally
        ticker = yf.Ticker(symbol)
        data = ticker.history(
            start=start, 
            end=end,
            auto_adjust=True,
            prepost=True,
            actions=False
        )
        
        if not data.empty:
            return data['Close'].dropna()
        return pd.Series()
    
    def _fetch_with_standard_method(self, symbol: str, start: str, end: str) -> pd.Series:
        """Fetch using standard yfinance method."""
        ticker = yf.Ticker(symbol)
        data = ticker.history(start=start, end=end)
        
        if not data.empty:
            return data['Close'].dropna()
        return pd.Series()
    
    def _fetch_with_download(self, symbol: str, start: str, end: str) -> pd.Series:
        """Fetch using yf.download."""
        data = yf.download(
            symbol, 
            start=start, 
            end=end,
            auto_adjust=True,
            prepost=True,
            show_errors=False,
            threads=False
        )
        
        if not data.empty:
            if 'Close' in data.columns:
                return data['Close'].dropna()
            elif len(data.columns) > 0:
                return data.iloc[:, 0].dropna()
        
        return pd.Series()
    
    def _fetch_with_period_method(self, symbol: str, start: str, end: str) -> pd.Series:
        """Fetch using period parameter."""
        try:
            start_dt = pd.to_datetime(start)
            end_dt = pd.to_datetime(end)
            days_diff = (end_dt - start_dt).days
            
            # Map days to periods
            if days_diff <= 7:
                period = "7d"
            elif days_diff <= 30:
                period = "1mo"
            elif days_diff <= 90:
                period = "3mo"
            elif days_diff <= 180:
                period = "6mo"
            elif days_diff <= 365:
                period = "1y"
            elif days_diff <= 730:
                period = "2y"
            elif days_diff <= 1825:
                period = "5y"
            else:
                period = "10y"
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, auto_adjust=True, prepost=True)
            
            if not data.empty:
                # Filter to requested date range
                data = data[data.index >= start_dt]
                data = data[data.index <= end_dt]
                return data['Close'].dropna()
        
        except Exception as e:
            logger.warning(f"Period method failed for {symbol}: {e}")
        
        return pd.Series()
    
    def fetch_multiple_symbols(self, symbols: List[str], start: str, end: str, 
                              max_workers: int = 3) -> Dict[str, pd.Series]:
        """Fetch multiple symbols with controlled threading."""
        results = {}
        
        # Process in batches to avoid overwhelming the API
        batch_size = 5
        symbol_batches = [symbols[i:i + batch_size] for i in range(0, len(symbols), batch_size)]
        
        for batch_idx, batch in enumerate(symbol_batches):
            logger.info(f"Processing batch {batch_idx + 1}/{len(symbol_batches)}: {batch}")
            
            batch_results = {}
            
            # Use ThreadPoolExecutor for controlled concurrency
            with ThreadPoolExecutor(max_workers=min(max_workers, len(batch))) as executor:
                future_to_symbol = {
                    executor.submit(self.fetch_single_symbol, symbol, start, end): symbol
                    for symbol in batch
                }
                
                for future in as_completed(future_to_symbol):
                    symbol = future_to_symbol[future]
                    try:
                        data = future.result()
                        if not data.empty:
                            batch_results[symbol] = data
                    except Exception as e:
                        logger.error(f"Error fetching {symbol}: {e}")
            
            results.update(batch_results)
            
            # Pause between batches
            if batch_idx < len(symbol_batches) - 1:
                pause_time = random.uniform(3, 6)
                logger.info(f"Pausing {pause_time:.1f}s between batches")
                time.sleep(pause_time)
        
        return results
    
    def get_rate_limit_status(self) -> Dict[str, any]:
        """Get current rate limiting status."""
        return {
            'total_requests': self.request_count,
            'cache_size': len(self.cache),
            'last_request_time': self.last_request_time,
            'min_interval': self.min_request_interval
        }
    
    def clear_cache(self):
        """Clear the internal cache."""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def adjust_rate_limit(self, new_interval: float):
        """Adjust the minimum request interval."""
        self.min_request_interval = new_interval
        logger.info(f"Rate limit interval adjusted to {new_interval}s")

# Global optimizer instance
_optimizer = None

def get_optimizer() -> YFinanceOptimizer:
    """Get the global optimizer instance."""
    global _optimizer
    if _optimizer is None:
        _optimizer = YFinanceOptimizer()
    return _optimizer

def fetch_symbols_optimized(symbols: List[str], start: str, end: str) -> Dict[str, pd.Series]:
    """Convenience function to fetch multiple symbols with optimization."""
    optimizer = get_optimizer()
    return optimizer.fetch_multiple_symbols(symbols, start, end)

def fetch_symbol_optimized(symbol: str, start: str, end: str) -> pd.Series:
    """Convenience function to fetch a single symbol with optimization."""
    optimizer = get_optimizer()
    return optimizer.fetch_single_symbol(symbol, start, end)

def get_rate_limit_status() -> Dict[str, any]:
    """Get current rate limiting status."""
    optimizer = get_optimizer()
    return optimizer.get_rate_limit_status()

def clear_cache():
    """Clear the global cache."""
    optimizer = get_optimizer()
    optimizer.clear_cache()

def adjust_rate_limit(interval: float):
    """Adjust the global rate limit interval."""
    optimizer = get_optimizer()
    optimizer.adjust_rate_limit(interval)
