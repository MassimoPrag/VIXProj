"""
Real Returns Analysis Module
Calculate and analyze real returns adjusted for both CPI and P=MV/Q theory inflation
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
import logging
from typing import Dict, List, Tuple, Optional
import time
import random
from functools import lru_cache
from yfinance_optimizer import fetch_symbols_optimized, fetch_symbol_optimized

logger = logging.getLogger(__name__)

class RealReturnsAnalyzer:
    """Analyze real returns of assets adjusted for monetary debasement."""
    
    def __init__(self):
        self.default_assets = {
            'SPY': 'SPDR S&P 500 ETF',
            'QQQ': 'Invesco QQQ (Nasdaq-100)',
            'VOO': 'Vanguard S&P 500 ETF',
            'IWM': 'iShares Russell 2000 ETF',
            'VTI': 'Vanguard Total Stock Market ETF',
            'DIA': 'SPDR Dow Jones Industrial Average ETF',
            'BTC-USD': 'Bitcoin',
            'GLD': 'SPDR Gold Shares',
            'SLV': 'iShares Silver Trust',
            'TLT': 'iShares 20+ Year Treasury Bond ETF',
            'AAPL': 'Apple Inc.',
            'GOOGL': 'Alphabet Inc.',
            'MSFT': 'Microsoft Corporation',
            'AMZN': 'Amazon.com Inc.',
            'TSLA': 'Tesla Inc.',
            'NVDA': 'NVIDIA Corporation'
        }
    
    def fetch_asset_data(self, symbols: List[str], start_date: str, end_date: str) -> Dict[str, pd.Series]:
        """Fetch price data for multiple assets using optimized methods."""
        try:
            logger.info(f"Fetching data for {len(symbols)} symbols using optimizer")
            
            # Use the optimized fetcher
            asset_data = fetch_symbols_optimized(symbols, start_date, end_date)
            
            if asset_data:
                logger.info(f"Successfully fetched real data for {len(asset_data)} out of {len(symbols)} symbols")
                
                # Improve data alignment by standardizing to daily frequency
                aligned_data = {}
                for symbol, series in asset_data.items():
                    if not series.empty:
                        # Ensure datetime index
                        if not isinstance(series.index, pd.DatetimeIndex):
                            series.index = pd.to_datetime(series.index)
                        
                        # Remove timezone info to avoid conflicts
                        if series.index.tz is not None:
                            series.index = series.index.tz_localize(None)
                        
                        # Resample to daily frequency with forward fill
                        series_daily = series.resample('D').last().ffill()
                        
                        # Filter to requested date range
                        start_dt = pd.to_datetime(start_date)
                        end_dt = pd.to_datetime(end_date)
                        series_daily = series_daily[(series_daily.index >= start_dt) & (series_daily.index <= end_dt)]
                        
                        if not series_daily.empty:
                            aligned_data[symbol] = series_daily
                            logger.info(f"Aligned {symbol}: {len(series_daily)} daily points from {series_daily.index[0]} to {series_daily.index[-1]}")
                
                return aligned_data
            else:
                logger.warning("No real data fetched, falling back to synthetic data")
                
        except Exception as e:
            logger.error(f"Error in optimized fetch: {e}")
        
        # Fallback to synthetic data if needed
        logger.info("Generating synthetic data for demonstration")
        return self.generate_synthetic_asset_data(symbols, start_date, end_date)
    
    def _fetch_single_asset_robust(self, symbol: str, start_date: str, end_date: str) -> pd.Series:
        """Fetch single asset data with multiple fallback strategies."""
        strategies = [
            self._fetch_with_session,
            self._fetch_with_download,
            self._fetch_with_period
        ]
        
        for strategy_idx, strategy in enumerate(strategies):
            try:
                data = strategy(symbol, start_date, end_date)
                if not data.empty:
                    return data
            except Exception as e:
                logger.warning(f"Strategy {strategy_idx + 1} failed for {symbol}: {e}")
                if strategy_idx < len(strategies) - 1:
                    time.sleep(random.uniform(1, 2))
        
        return pd.Series()
    
    def _fetch_with_session(self, symbol: str, start_date: str, end_date: str) -> pd.Series:
        """Fetch using session with custom headers."""
        session = yf.utils.get_session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
        
        ticker = yf.Ticker(symbol, session=session)
        data = ticker.history(start=start_date, end=end_date, auto_adjust=True, prepost=True)
        
        if not data.empty:
            return data['Close'].dropna()
        return pd.Series()
    
    def _fetch_with_download(self, symbol: str, start_date: str, end_date: str) -> pd.Series:
        """Fetch using yf.download with specific parameters."""
        data = yf.download(symbol, start=start_date, end=end_date, 
                          auto_adjust=True, prepost=True, progress=False, 
                          show_errors=False, threads=False)
        
        if not data.empty:
            if 'Close' in data.columns:
                return data['Close'].dropna()
            elif len(data.columns) > 0:
                return data.iloc[:, 0].dropna()  # Use first column if Close not available
        
        return pd.Series()
    
    def _fetch_with_period(self, symbol: str, start_date: str, end_date: str) -> pd.Series:
        """Fetch using period parameter."""
        try:
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            days_diff = (end_dt - start_dt).days
            
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
                data = data[data.index >= start_dt]
                data = data[data.index <= end_dt]
                return data['Close'].dropna()
        
        except Exception as e:
            logger.warning(f"Period fetch failed for {symbol}: {e}")
        
        return pd.Series()
    
    def calculate_real_returns(self, asset_prices: pd.Series, inflation_series: pd.Series, 
                             asset_name: str, inflation_name: str) -> pd.DataFrame:
        """Calculate real returns for a single asset against an inflation measure."""
        
        # Ensure both series have datetime indices
        if not isinstance(asset_prices.index, pd.DatetimeIndex):
            asset_prices.index = pd.to_datetime(asset_prices.index)
        if not isinstance(inflation_series.index, pd.DatetimeIndex):
            inflation_series.index = pd.to_datetime(inflation_series.index)
        
        # Remove timezone info if present to avoid conflicts
        if asset_prices.index.tz is not None:
            asset_prices.index = asset_prices.index.tz_localize(None)
        if inflation_series.index.tz is not None:
            inflation_series.index = inflation_series.index.tz_localize(None)
        
        # Find common dates
        common_dates = asset_prices.index.intersection(inflation_series.index)
        
        logger.info(f"Analyzing {asset_name} vs {inflation_name}")
        logger.info(f"Asset data: {len(asset_prices)} points from {asset_prices.index[0]} to {asset_prices.index[-1]}")
        logger.info(f"Inflation data: {len(inflation_series)} points from {inflation_series.index[0]} to {inflation_series.index[-1]}")
        logger.info(f"Common dates: {len(common_dates)} points")
        
        if len(common_dates) < 5:  # Reduced threshold for more flexible analysis
            logger.warning(f"Insufficient overlapping data for {asset_name} vs {inflation_name}")
            
            # Try to create synthetic overlapping data by interpolating
            return self._create_synthetic_alignment(asset_prices, inflation_series, asset_name, inflation_name)
        
        # Align data
        asset_aligned = asset_prices.reindex(common_dates).ffill().bfill()
        inflation_aligned = inflation_series.reindex(common_dates).ffill().bfill()
        
        # Remove any remaining NaN values
        valid_mask = ~(asset_aligned.isna() | inflation_aligned.isna())
        asset_aligned = asset_aligned[valid_mask]
        inflation_aligned = inflation_aligned[valid_mask]
        common_dates = common_dates[valid_mask]
        
        if len(common_dates) < 2:
            logger.warning(f"Insufficient valid data after alignment for {asset_name} vs {inflation_name}")
            return self._create_synthetic_alignment(asset_prices, inflation_series, asset_name, inflation_name)
        
        # Calculate returns
        asset_returns = asset_aligned.pct_change().fillna(0)
        inflation_returns = inflation_aligned.pct_change().fillna(0)
        
        # Real returns = nominal returns - inflation
        real_returns = asset_returns - inflation_returns
        
        # Calculate cumulative returns
        cumulative_nominal = (1 + asset_returns).cumprod()
        cumulative_real = (1 + real_returns).cumprod()
        
        # Calculate annualized metrics
        years = len(common_dates) / 252  # Approximate trading days per year
        
        if years > 0:
            total_nominal_return = cumulative_nominal.iloc[-1] - 1
            total_real_return = cumulative_real.iloc[-1] - 1
            
            annualized_nominal = (1 + total_nominal_return) ** (1/years) - 1
            annualized_real = (1 + total_real_return) ** (1/years) - 1
            
            # Volatility (annualized)
            nominal_vol = asset_returns.std() * np.sqrt(252) if len(asset_returns) > 1 else 0
            real_vol = real_returns.std() * np.sqrt(252) if len(real_returns) > 1 else 0
            
            # Sharpe-like ratio for real returns
            real_sharpe = annualized_real / real_vol if real_vol > 0 else 0
        else:
            annualized_nominal = 0
            annualized_real = 0
            nominal_vol = 0
            real_vol = 0
            real_sharpe = 0
        
        return pd.DataFrame({
            'Date': common_dates,
            'Nominal_Cumulative': cumulative_nominal,
            'Real_Cumulative': cumulative_real,
            'Nominal_Returns': asset_returns,
            'Real_Returns': real_returns,
            'Inflation_Returns': inflation_returns,
            'Asset': asset_name,
            'Inflation_Measure': inflation_name,
            'Annualized_Nominal': annualized_nominal,
            'Annualized_Real': annualized_real,
            'Nominal_Volatility': nominal_vol,
            'Real_Volatility': real_vol,
            'Real_Sharpe': real_sharpe
        }).set_index('Date')
    
    def analyze_multiple_assets(self, asset_data: Dict[str, pd.Series], 
                              cpi_data: pd.Series, p_theory_data: pd.Series) -> Dict[str, Dict[str, pd.DataFrame]]:
        """Analyze multiple assets against both CPI and P theory inflation."""
        
        results = {}
        
        for asset_symbol, asset_prices in asset_data.items():
            asset_name = self.default_assets.get(asset_symbol, asset_symbol)
            
            results[asset_symbol] = {
                'cpi_adjusted': self.calculate_real_returns(asset_prices, cpi_data, asset_name, 'CPI'),
                'p_theory_adjusted': self.calculate_real_returns(asset_prices, p_theory_data, asset_name, 'P=MV/Q')
            }
            
            # Add comparative analysis
            if not results[asset_symbol]['cpi_adjusted'].empty and not results[asset_symbol]['p_theory_adjusted'].empty:
                cpi_real = results[asset_symbol]['cpi_adjusted']['Annualized_Real'].iloc[0]
                p_real = results[asset_symbol]['p_theory_adjusted']['Annualized_Real'].iloc[0]
                
                results[asset_symbol]['inflation_comparison'] = {
                    'cpi_real_return': cpi_real,
                    'p_theory_real_return': p_real,
                    'difference': cpi_real - p_real,
                    'better_against': 'CPI' if cpi_real > p_real else 'P Theory'
                }
        
        return results
    
    def create_performance_summary(self, analysis_results: Dict[str, Dict[str, pd.DataFrame]]) -> pd.DataFrame:
        """Create a summary table of performance metrics."""
        
        summary_data = []
        
        for asset_symbol, results in analysis_results.items():
            if 'inflation_comparison' in results:
                asset_name = self.default_assets.get(asset_symbol, asset_symbol)
                
                cpi_data = results['cpi_adjusted']
                p_data = results['p_theory_adjusted']
                comparison = results['inflation_comparison']
                
                if not cpi_data.empty and not p_data.empty:
                    summary_data.append({
                        'Asset': asset_name,
                        'Symbol': asset_symbol,
                        'Nominal_Return_Ann': cpi_data['Annualized_Nominal'].iloc[0],
                        'Real_Return_CPI_Ann': cpi_data['Annualized_Real'].iloc[0],
                        'Real_Return_P_Ann': p_data['Annualized_Real'].iloc[0],
                        'CPI_Impact': cpi_data['Annualized_Nominal'].iloc[0] - cpi_data['Annualized_Real'].iloc[0],
                        'P_Theory_Impact': p_data['Annualized_Nominal'].iloc[0] - p_data['Annualized_Real'].iloc[0],
                        'Real_Volatility_CPI': cpi_data['Real_Volatility'].iloc[0],
                        'Real_Volatility_P': p_data['Real_Volatility'].iloc[0],
                        'Real_Sharpe_CPI': cpi_data['Real_Sharpe'].iloc[0],
                        'Real_Sharpe_P': p_data['Real_Sharpe'].iloc[0],
                        'Better_Against': comparison['better_against']
                    })
        
        return pd.DataFrame(summary_data)
    
    def create_performance_chart(self, analysis_results: Dict[str, Dict[str, pd.DataFrame]], 
                               chart_type: str = 'cumulative') -> go.Figure:
        """Create performance visualization charts."""
        
        fig = go.Figure()
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
        
        for i, (asset_symbol, results) in enumerate(analysis_results.items()):
            if 'cpi_adjusted' in results and not results['cpi_adjusted'].empty:
                color = colors[i % len(colors)]
                asset_name = self.default_assets.get(asset_symbol, asset_symbol)
                
                cpi_data = results['cpi_adjusted']
                p_data = results['p_theory_adjusted']
                
                if chart_type == 'cumulative':
                    # Nominal returns
                    fig.add_trace(go.Scatter(
                        x=cpi_data.index,
                        y=cpi_data['Nominal_Cumulative'],
                        name=f'{asset_name} (Nominal)',
                        line=dict(color=color, width=2),
                        legendgroup=asset_symbol,
                        hovertemplate=f'<b>{asset_name} Nominal</b><br>Date: %{{x}}<br>Value: %{{y:.2f}}<extra></extra>'
                    ))
                    
                    # Real returns (CPI adjusted)
                    fig.add_trace(go.Scatter(
                        x=cpi_data.index,
                        y=cpi_data['Real_Cumulative'],
                        name=f'{asset_name} (Real CPI)',
                        line=dict(color=color, width=2, dash='dash'),
                        legendgroup=asset_symbol,
                        hovertemplate=f'<b>{asset_name} Real (CPI)</b><br>Date: %{{x}}<br>Value: %{{y:.2f}}<extra></extra>'
                    ))
                    
                    # Real returns (P theory adjusted)
                    if not p_data.empty:
                        fig.add_trace(go.Scatter(
                            x=p_data.index,
                            y=p_data['Real_Cumulative'],
                            name=f'{asset_name} (Real P Theory)',
                            line=dict(color=color, width=2, dash='dot'),
                            legendgroup=asset_symbol,
                            hovertemplate=f'<b>{asset_name} Real (P Theory)</b><br>Date: %{{x}}<br>Value: %{{y:.2f}}<extra></extra>'
                        ))
        
        fig.update_layout(
            title="Asset Performance: Nominal vs Real Returns",
            xaxis_title="Date",
            yaxis_title="Cumulative Return (Base = 1.0)",
            height=600,
            hovermode='x unified',
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.01
            )
        )
        
        return fig
    
    def calculate_correlation_matrix(self, analysis_results: Dict[str, Dict[str, pd.DataFrame]]) -> pd.DataFrame:
        """Calculate correlation matrix of real returns."""
        
        real_returns_data = {}
        
        for asset_symbol, results in analysis_results.items():
            if 'cpi_adjusted' in results and not results['cpi_adjusted'].empty:
                asset_name = self.default_assets.get(asset_symbol, asset_symbol)
                real_returns_data[f'{asset_name}_CPI'] = results['cpi_adjusted']['Real_Returns']
                
                if 'p_theory_adjusted' in results and not results['p_theory_adjusted'].empty:
                    real_returns_data[f'{asset_name}_P'] = results['p_theory_adjusted']['Real_Returns']
        
        if real_returns_data:
            df = pd.DataFrame(real_returns_data).dropna()
            return df.corr()
        else:
            return pd.DataFrame()
    
    def get_best_performers(self, summary_df: pd.DataFrame, metric: str = 'Real_Return_CPI_Ann', 
                          top_n: int = 5) -> List[Dict[str, any]]:
        """Get top performing assets by a specific metric."""
        
        if summary_df.empty or metric not in summary_df.columns:
            return []
        
        sorted_df = summary_df.sort_values(metric, ascending=False)
        top_performers = sorted_df.head(top_n)
        
        return [
            {
                'Asset': row['Asset'],
                'Symbol': row['Symbol'],
                'Value': row[metric],
                'Rank': i + 1
            }
            for i, (_, row) in enumerate(top_performers.iterrows())
        ]
    
    def generate_synthetic_asset_data(self, symbols: List[str], start_date: str, end_date: str) -> Dict[str, pd.Series]:
        """Generate synthetic asset data for demonstration when real data is unavailable."""
        asset_data = {}
        
        try:
            # Create date range
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
            
            # Asset-specific parameters for realistic synthetic data
            asset_params = {
                'SPY': {'base_price': 300, 'annual_return': 0.10, 'volatility': 0.15},
                'QQQ': {'base_price': 250, 'annual_return': 0.12, 'volatility': 0.20},
                'VOO': {'base_price': 280, 'annual_return': 0.09, 'volatility': 0.14},
                'IWM': {'base_price': 180, 'annual_return': 0.08, 'volatility': 0.22},
                'VTI': {'base_price': 200, 'annual_return': 0.09, 'volatility': 0.15},
                'DIA': {'base_price': 320, 'annual_return': 0.07, 'volatility': 0.16},
                'BTC-USD': {'base_price': 40000, 'annual_return': 0.30, 'volatility': 0.80},
                'GLD': {'base_price': 170, 'annual_return': 0.05, 'volatility': 0.18},
                'SLV': {'base_price': 22, 'annual_return': 0.06, 'volatility': 0.25},
                'TLT': {'base_price': 140, 'annual_return': 0.03, 'volatility': 0.12},
                'AAPL': {'base_price': 150, 'annual_return': 0.15, 'volatility': 0.25},
                'GOOGL': {'base_price': 2500, 'annual_return': 0.13, 'volatility': 0.22},
                'MSFT': {'base_price': 300, 'annual_return': 0.14, 'volatility': 0.20},
                'AMZN': {'base_price': 3200, 'annual_return': 0.12, 'volatility': 0.24},
                'TSLA': {'base_price': 800, 'annual_return': 0.20, 'volatility': 0.50},
                'NVDA': {'base_price': 220, 'annual_return': 0.25, 'volatility': 0.35}
            }
            
            for symbol in symbols:
                params = asset_params.get(symbol, {'base_price': 100, 'annual_return': 0.08, 'volatility': 0.20})
                
                # Generate realistic price series using geometric Brownian motion
                np.random.seed(hash(symbol) % 2**32)  # Consistent seed based on symbol
                
                # Daily return parameters
                daily_return = params['annual_return'] / 252
                daily_vol = params['volatility'] / np.sqrt(252)
                
                # Generate random returns
                returns = np.random.normal(daily_return, daily_vol, len(dates))
                
                # Calculate cumulative prices
                price_series = params['base_price'] * np.exp(np.cumsum(returns))
                
                # Create pandas Series
                asset_data[symbol] = pd.Series(price_series, index=dates)
                
                logger.info(f"Generated synthetic data for {symbol}: {len(dates)} data points")
            
            return asset_data
            
        except Exception as e:
            logger.error(f"Error generating synthetic asset data: {e}")
            return {}
    
    def _create_synthetic_alignment(self, asset_prices: pd.Series, inflation_series: pd.Series, 
                                  asset_name: str, inflation_name: str) -> pd.DataFrame:
        """Create synthetic alignment when there's insufficient overlapping data."""
        
        logger.info(f"Creating synthetic alignment for {asset_name} vs {inflation_name}")
        
        # Use the asset's date range but create synthetic inflation data
        asset_dates = asset_prices.index
        
        # Create synthetic inflation data based on the inflation series characteristics
        if len(inflation_series) > 1:
            # Calculate average inflation rate
            inflation_returns = inflation_series.pct_change().dropna()
            avg_inflation_rate = inflation_returns.mean() if len(inflation_returns) > 0 else 0.03 / 252  # Default 3% annual
            inflation_vol = inflation_returns.std() if len(inflation_returns) > 0 else 0.01 / np.sqrt(252)  # Default volatility
        else:
            avg_inflation_rate = 0.03 / 252  # Default 3% annual
            inflation_vol = 0.01 / np.sqrt(252)  # Default volatility
        
        # Generate synthetic inflation data
        np.random.seed(42)  # For reproducibility
        synthetic_inflation_returns = np.random.normal(avg_inflation_rate, inflation_vol, len(asset_dates))
        
        # Calculate asset returns
        asset_returns = asset_prices.pct_change().fillna(0)
        
        # Real returns = nominal returns - synthetic inflation
        real_returns = asset_returns - synthetic_inflation_returns
        
        # Calculate cumulative returns
        cumulative_nominal = (1 + asset_returns).cumprod()
        cumulative_real = (1 + real_returns).cumprod()
        
        # Calculate annualized metrics
        years = len(asset_dates) / 252
        
        if years > 0:
            total_nominal_return = cumulative_nominal.iloc[-1] - 1
            total_real_return = cumulative_real.iloc[-1] - 1
            
            annualized_nominal = (1 + total_nominal_return) ** (1/years) - 1
            annualized_real = (1 + total_real_return) ** (1/years) - 1
            
            # Volatility (annualized)
            nominal_vol = asset_returns.std() * np.sqrt(252) if len(asset_returns) > 1 else 0
            real_vol = real_returns.std() * np.sqrt(252) if len(real_returns) > 1 else 0
            
            # Sharpe-like ratio for real returns
            real_sharpe = annualized_real / real_vol if real_vol > 0 else 0
        else:
            annualized_nominal = 0
            annualized_real = 0
            nominal_vol = 0
            real_vol = 0
            real_sharpe = 0
        
        return pd.DataFrame({
            'Date': asset_dates,
            'Nominal_Cumulative': cumulative_nominal,
            'Real_Cumulative': cumulative_real,
            'Nominal_Returns': asset_returns,
            'Real_Returns': real_returns,
            'Inflation_Returns': synthetic_inflation_returns,
            'Asset': asset_name,
            'Inflation_Measure': f"{inflation_name} (Synthetic)",
            'Annualized_Nominal': annualized_nominal,
            'Annualized_Real': annualized_real,
            'Nominal_Volatility': nominal_vol,
            'Real_Volatility': real_vol,
            'Real_Sharpe': real_sharpe
        }).set_index('Date')

# Test the analyzer
if __name__ == "__main__":
    analyzer = RealReturnsAnalyzer()
    
    # Test with a few assets
    test_symbols = ['SPY', 'QQQ', 'BTC-USD']
    start_date = '2020-01-01'
    end_date = '2023-12-31'
    
    print("🧪 Testing Real Returns Analyzer")
    
    # Mock CPI and P theory data
    dates = pd.date_range(start_date, end_date, freq='D')
    mock_cpi = pd.Series(
        index=dates,
        data=250 + np.cumsum(np.random.normal(0.02, 0.1, len(dates)))
    )
    mock_p = pd.Series(
        index=dates,
        data=1.2 + np.cumsum(np.random.normal(0.001, 0.01, len(dates)))
    )
    
    # Test asset data fetching
    asset_data = analyzer.fetch_asset_data(test_symbols, start_date, end_date)
    print(f"✅ Fetched data for {len(asset_data)} assets")
    
    # Test real returns calculation
    if asset_data:
        results = analyzer.analyze_multiple_assets(asset_data, mock_cpi, mock_p)
        print(f"✅ Analyzed {len(results)} assets")
        
        # Test summary creation
        summary = analyzer.create_performance_summary(results)
        print(f"✅ Created summary with {len(summary)} rows")
        
        # Test chart creation
        chart = analyzer.create_performance_chart(results)
        print("✅ Created performance chart")
        
        print("\n🎯 Real Returns Analyzer ready for use!")
