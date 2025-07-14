"""
Data Handler for Monetary Debasement Research Dashboard
Fetches and processes data for monetary expansion analysis
"""
import pandas as pd
import numpy as np
import yfinance as yf
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import warnings
import time
import random
from functools import lru_cache
from yfinance_optimizer import fetch_symbol_optimized
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class MonetaryDataHandler:
    """Handle data loading and processing for monetary debasement analysis."""
    
    def __init__(self):
        self.fred_data_cache = {}
        self.yfinance_data_cache = {}
    
    def get_fred_data(self, symbol: str, start: str, end: str) -> pd.Series:
        """Fetch data from FRED API (Federal Reserve Economic Data)."""
        try:
            # Try fredapi first (most reliable)
            try:
                from fredapi import Fred
                fred = Fred()  # No API key needed for public data
                data = fred.get_series(symbol, start, end)
                
                if not data.empty:
                    # Clean and process data
                    data = data.dropna()
                    
                    # Cache the result
                    cache_key = f"{symbol}_{start}_{end}"
                    self.fred_data_cache[cache_key] = data
                    
                    logger.info(f"Successfully fetched {len(data)} data points for {symbol} from FRED via fredapi")
                    return data
                    
            except (ImportError, Exception) as e:
                logger.debug(f"fredapi failed: {e}, trying pandas_datareader")
                
                # Fallback to pandas_datareader
                try:
                    import pandas_datareader.data as web
                    
                    # Cache key
                    cache_key = f"{symbol}_{start}_{end}"
                    
                    if cache_key in self.fred_data_cache:
                        return self.fred_data_cache[cache_key]
                    
                    # Fetch data
                    data = web.get_data_fred(symbol, start, end)
                    
                    if not data.empty:
                        # Clean and process data
                        data = data.dropna()
                        data = data[data.index >= pd.to_datetime(start)]
                        data = data[data.index <= pd.to_datetime(end)]
                        
                        # Cache the result
                        self.fred_data_cache[cache_key] = data.squeeze()
                        
                        logger.info(f"Successfully fetched {len(data)} data points for {symbol} from FRED")
                        return data.squeeze()
                        
                except Exception as e2:
                    logger.debug(f"pandas_datareader failed: {e2}, trying direct HTTP")
                    
                    # Final fallback: direct HTTP request to FRED
                    try:
                        import requests
                        
                        # FRED provides JSON API without requiring API key for some data
                        url = f"https://api.stlouisfed.org/fred/series/observations"
                        params = {
                            'series_id': symbol,
                            'api_key': 'demo',  # Demo key for public data
                            'file_type': 'json',
                            'observation_start': start,
                            'observation_end': end
                        }
                        
                        response = requests.get(url, params=params, timeout=10)
                        
                        if response.status_code == 200:
                            json_data = response.json()
                            if 'observations' in json_data:
                                observations = json_data['observations']
                                
                                # Convert to pandas Series
                                dates = []
                                values = []
                                
                                for obs in observations:
                                    if obs['value'] != '.':  # FRED uses '.' for missing values
                                        dates.append(pd.to_datetime(obs['date']))
                                        values.append(float(obs['value']))
                                
                                if dates and values:
                                    data = pd.Series(values, index=dates)
                                    
                                    # Cache the result
                                    cache_key = f"{symbol}_{start}_{end}"
                                    self.fred_data_cache[cache_key] = data
                                    
                                    logger.info(f"Successfully fetched {len(data)} data points for {symbol} from FRED via HTTP")
                                    return data
                                    
                    except Exception as e3:
                        logger.debug(f"HTTP request failed: {e3}")
                
            logger.warning(f"All FRED data fetching methods failed for {symbol}")
            return pd.Series()
                
        except Exception as e:
            logger.error(f"Error fetching FRED data for {symbol}: {e}")
            return pd.Series()
    
    def get_yfinance_data(self, symbol: str, start: str, end: str) -> pd.Series:
        """Fetch data from Yahoo Finance using optimized methods."""
        try:
            cache_key = f"{symbol}_{start}_{end}"
            
            if cache_key in self.yfinance_data_cache:
                return self.yfinance_data_cache[cache_key]
            
            # Use the optimized fetcher
            data = fetch_symbol_optimized(symbol, start, end)
            
            if not data.empty:
                # Cache the result
                self.yfinance_data_cache[cache_key] = data
                logger.info(f"Successfully fetched {len(data)} data points for {symbol} from Yahoo Finance")
                return data
            else:
                logger.warning(f"No data found for {symbol} from Yahoo Finance")
                return pd.Series()
                
        except Exception as e:
            logger.error(f"Error fetching Yahoo Finance data for {symbol}: {e}")
            return pd.Series()
    
    def calculate_p_theory(self, money_supply: pd.Series, velocity: pd.Series, 
                          real_gdp: pd.Series) -> pd.Series:
        """Calculate P from the quantity theory of money: P = MV/Q."""
        try:
            # Align all series to common dates
            common_dates = money_supply.index.intersection(velocity.index).intersection(real_gdp.index)
            
            if len(common_dates) < 10:
                logger.warning("Insufficient overlapping data for P=MV/Q calculation")
                return pd.Series()
            
            # Align data
            M = money_supply.reindex(common_dates).fillna(method='ffill')
            V = velocity.reindex(common_dates).fillna(method='ffill')
            Q = real_gdp.reindex(common_dates).fillna(method='ffill')
            
            # Calculate P = MV/Q
            P = (M * V) / Q
            
            # Normalize to base period (first value = 100)
            P = (P / P.iloc[0]) * 100
            
            logger.info(f"Successfully calculated P=MV/Q for {len(P)} data points")
            return P
            
        except Exception as e:
            logger.error(f"Error calculating P=MV/Q: {e}")
            return pd.Series()
    
    def get_synthetic_data(self, start: str, end: str) -> pd.DataFrame:
        """Generate synthetic data for demonstration when real data is not available."""
        try:
            # Create date range
            dates = pd.date_range(start=start, end=end, freq='D')
            
            # Generate synthetic CPI (trending upward with volatility)
            np.random.seed(42)
            cpi_trend = np.linspace(200, 280, len(dates))
            cpi_noise = np.random.normal(0, 2, len(dates))
            cpi = cpi_trend + cpi_noise
            
            # Generate synthetic P=MV/Q (similar trend but different volatility)
            np.random.seed(43)
            p_trend = np.linspace(180, 300, len(dates))
            p_noise = np.random.normal(0, 5, len(dates))
            p_theory = p_trend + p_noise
            
            # Generate synthetic money supply (exponential growth)
            np.random.seed(44)
            money_supply_base = 15000
            money_supply_growth = np.exp(np.linspace(0, 0.8, len(dates)))
            money_supply = money_supply_base * money_supply_growth
            
            # Generate synthetic Bitcoin price (volatile but trending up)
            np.random.seed(45)
            btc_base = 30000
            btc_trend = np.exp(np.linspace(0, 1.2, len(dates)))
            btc_volatility = np.random.normal(1, 0.3, len(dates))
            btc_price = btc_base * btc_trend * btc_volatility
            btc_price = np.maximum(btc_price, 1000)  # Floor price
            
            # Create DataFrame
            data = pd.DataFrame({
                'CPI': cpi,
                'P': p_theory,
                'M2SL': money_supply,
                'BTC-USD': btc_price
            }, index=dates)
            
            logger.info(f"Generated synthetic data for {len(data)} data points")
            return data
            
        except Exception as e:
            logger.error(f"Error generating synthetic data: {e}")
            return pd.DataFrame()

def get_research_data(start: str, end: str) -> pd.DataFrame:
    """
    Main function to get research data for monetary debasement analysis.
    
    Args:
        start: Start date in YYYY-MM-DD format
        end: End date in YYYY-MM-DD format
    
    Returns:
        DataFrame with CPI, P=MV/Q, Money Supply, and Bitcoin data
    """
    handler = MonetaryDataHandler()
    
    logger.info(f"Fetching data from {start} to {end}")
    
    # Try to get real data first
    try:
        # FRED data symbols
        fred_symbols = {
            'CPI': 'CPIAUCSL',         # Consumer Price Index
            'M2SL': 'M2SL',            # M2 Money Supply
            'GDPC1': 'GDPC1',          # Real GDP
            'M2V': 'M2V'               # M2 Velocity
        }
        
        data_dict = {}
        
        # Fetch FRED data
        for name, symbol in fred_symbols.items():
            series = handler.get_fred_data(symbol, start, end)
            if not series.empty:
                data_dict[name] = series
        
        # Fetch Bitcoin data from Yahoo Finance
        btc_data = handler.get_yfinance_data('BTC-USD', start, end)
        if not btc_data.empty:
            data_dict['BTC-USD'] = btc_data
        
        # Calculate P=MV/Q if we have the required data
        if all(key in data_dict for key in ['M2SL', 'M2V', 'GDPC1']):
            p_theory = handler.calculate_p_theory(
                data_dict['M2SL'], 
                data_dict['M2V'], 
                data_dict['GDPC1']
            )
            if not p_theory.empty:
                data_dict['P'] = p_theory            # Create DataFrame with common dates
            if data_dict:
                # Find common date range and normalize timezones
                all_dates = set()
                for series in data_dict.values():
                    # Convert timezone-aware dates to timezone-naive
                    if hasattr(series.index, 'tz') and series.index.tz is not None:
                        dates = series.index.tz_localize(None)
                    else:
                        dates = series.index
                    all_dates.update(dates)
                
                # Create DataFrame
                df = pd.DataFrame(index=sorted(all_dates))
                
                for name, series in data_dict.items():
                    # Normalize timezone for series index
                    if hasattr(series.index, 'tz') and series.index.tz is not None:
                        series = series.copy()
                        series.index = series.index.tz_localize(None)
                    df[name] = series
                
                # Forward fill missing values
                df = df.fillna(method='ffill')
                
                # Filter by date range (ensure timezone-naive comparison)
                start_dt = pd.to_datetime(start).tz_localize(None) if pd.to_datetime(start).tz else pd.to_datetime(start)
                end_dt = pd.to_datetime(end).tz_localize(None) if pd.to_datetime(end).tz else pd.to_datetime(end)
                
                df = df[(df.index >= start_dt) & (df.index <= end_dt)]
                
                if len(df) >= 10:
                    logger.info(f"Successfully loaded real data with {len(df)} data points")
                    return df
                else:
                    logger.warning("Insufficient real data points, falling back to synthetic data")
                
    except Exception as e:
        logger.error(f"Error loading real data: {e}")
    
    # Fallback to synthetic data
    logger.info("Using synthetic data for demonstration")
    return handler.get_synthetic_data(start, end)

def get_asset_data(symbols: list, start: str, end: str) -> Dict[str, pd.Series]:
    """Get asset data for multiple symbols using optimized methods."""
    from yfinance_optimizer import fetch_symbols_optimized
    
    try:
        asset_data = fetch_symbols_optimized(symbols, start, end)
        return asset_data
    except Exception as e:
        logger.error(f"Error fetching asset data: {e}")
        return {}

# For backward compatibility
def load_data_cached(start: str, end: str) -> pd.DataFrame:
    """Cached data loading function."""
    return get_research_data(start, end)
