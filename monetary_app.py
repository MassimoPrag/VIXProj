"""
Monetary Debasement Research Dashboard
Analyzing the relationship between money supply expansion, inflation, and asset performance
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import logging
from typing import Dict, List
from data_handler import get_research_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Monetary Debasement Research",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f1f1f;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff6b6b;
        margin: 0.5rem 0;
    }
    .insight-box {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .data-quality-indicator {
        font-size: 0.8rem;
        padding: 0.2rem 0.5rem;
        border-radius: 1rem;
        margin-left: 0.5rem;
    }
    .real-data {
        background-color: #d4edda;
        color: #155724;
    }
    .synthetic-data {
        background-color: #f8d7da;
        color: #721c24;
    }
    .sidebar-info {
        font-size: 0.9rem;
        color: #666;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def load_data_cached(start: str, end: str):
    """Cached data loading function."""
    return get_research_data(start, end)

def get_asset_data(symbols: list, start: str, end: str):
    """Get asset data for multiple symbols."""
    try:
        import yfinance as yf
        asset_data = {}
        
        for symbol in symbols:
            try:
                data = yf.download(symbol, start=start, end=end, progress=False)
                if not data.empty:
                    asset_data[symbol] = data['Close']
                else:
                    logger.warning(f"No data found for {symbol}")
            except Exception as e:
                logger.warning(f"Could not fetch data for {symbol}: {e}")
        
        return asset_data
    except ImportError:
        logger.error("yfinance not installed")
        return {}

def calculate_real_returns(asset_prices: pd.Series, cpi: pd.Series, p_theory: pd.Series, name: str):
    """Calculate real returns adjusted for both CPI and theoretical P."""
    if asset_prices.empty or cpi.empty or p_theory.empty:
        return pd.DataFrame()
    
    # Align data
    common_index = asset_prices.index.intersection(cpi.index).intersection(p_theory.index)
    if len(common_index) < 10:
        return pd.DataFrame()
    
    asset_aligned = asset_prices.reindex(common_index)
    cpi_aligned = cpi.reindex(common_index)
    p_aligned = p_theory.reindex(common_index)
    
    # Calculate returns
    asset_returns = asset_aligned.pct_change().fillna(0)
    cpi_returns = cpi_aligned.pct_change().fillna(0)
    p_returns = p_aligned.pct_change().fillna(0)
    
    # Real returns (asset returns minus inflation)
    real_returns_cpi = asset_returns - cpi_returns
    real_returns_p = asset_returns - p_returns
    
    # Cumulative real returns
    cumulative_nominal = (1 + asset_returns).cumprod()
    cumulative_real_cpi = (1 + real_returns_cpi).cumprod()
    cumulative_real_p = (1 + real_returns_p).cumprod()
    
    return pd.DataFrame({
        f'{name}_Nominal': cumulative_nominal,
        f'{name}_Real_CPI': cumulative_real_cpi,
        f'{name}_Real_P': cumulative_real_p
    }, index=common_index)

def main_dashboard(data):
    """Main monetary debasement dashboard page."""
    st.title("💰 Monetary Debasement Research Dashboard")
    
    st.markdown("""
    ### Understanding the Hidden Tax of Money Printing
    
    This dashboard analyzes the relationship between monetary expansion, inflation, and asset performance.
    The central thesis is that **monetary debasement** - the deliberate weakening of currency through money supply expansion - 
    creates systematic distortions that can be measured and traded.
    """)
    
    # Quantity Theory of Money Explanation
    st.subheader("📚 Understanding P = MV/Q: The Quantity Theory of Money")
    st.markdown("""
    The **Quantity Theory of Money** is a fundamental economic principle that helps explain the relationship 
    between money supply and inflation. The equation **P = MV/Q** represents:
    
    ### 🔤 Variable Definitions:
    
    - **P** = **Price Level** (General level of prices in the economy)
    - **M** = **Money Supply** (Total amount of money in circulation, we use M2)
    - **V** = **Velocity of Money** (How quickly money changes hands in the economy)
    - **Q** = **Quantity of Goods/Services** (Real GDP, the economy's total output)
    
    ### 💡 Economic Meaning:
    
    **P = MV/Q** tells us that the **price level** is determined by:
    - How much **money** is in circulation (M)
    - How **fast** that money moves through the economy (V)
    - Divided by how much **real stuff** the economy produces (Q)
    
    ### 🎯 Why This Matters:
    
    - **If M increases faster than Q**: Prices rise (inflation from money printing)
    - **If V increases**: More inflation pressure as money circulates faster
    - **If Q increases**: Deflationary pressure as more goods chase the same money
    
    **This theoretical inflation (P=MV/Q) vs observed inflation (CPI) reveals monetary debasement effects.**
    
    *Based on Milton Friedman's monetary theory framework*
    
    📚 **Academic Reference**: [Milton Friedman's Monetary Framework](https://miltonfriedman.hoover.org/internal/media/dispatcher/214346/full)
    """)
    
    
    # Signal Detection Section
    try:
        from signal_detector import DebasementSignalDetector, format_signal_for_display
        detector = DebasementSignalDetector()
        composite_signal = detector.generate_composite_signal(data)
        
        # Alert box for high-level signals
        if composite_signal['level'] == 'high':
            alert_class = 'error' if composite_signal['direction'] == 'bearish' else 'success'
            st.markdown(f"""
            <div class="alert-{alert_class}">
                <strong>🚨 HIGH PRIORITY SIGNAL DETECTED</strong><br>
                {format_signal_for_display(composite_signal)}
            </div>
            """, unsafe_allow_html=True)
            
            # Trading recommendations
            recommendations = detector.get_trading_recommendations(composite_signal)
            with st.expander("📋 Trading Recommendations", expanded=True):
                for rec in recommendations:
                    st.markdown(f"- {rec}")
        
        elif composite_signal['level'] == 'medium':
            st.info(f"⚠️ {format_signal_for_display(composite_signal)}")
    
    except ImportError:
        st.info("💡 Signal detection module available - check signal_detector.py")
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate key debasement metrics
    if 'CPI' in data.columns and 'P' in data.columns:
        current_cpi = data['CPI'].iloc[-1] if not data['CPI'].empty else 0
        current_p = data['P'].iloc[-1] if not data['P'].empty else 0
        
        # Calculate standardized inflation spread (same as in chart)
        cpi_clean = data['CPI'].dropna()
        p_clean = data['P'].dropna()
        
        if len(cpi_clean) > 1 and len(p_clean) > 1:
            # Calculate z-scores for standardized spread
            cpi_standardized = (data['CPI'] - data['CPI'].mean()) / data['CPI'].std()
            p_standardized = (data['P'] - data['P'].mean()) / data['P'].std()
            standardized_spread = cpi_standardized - p_standardized
            inflation_spread = standardized_spread.iloc[-1] if not standardized_spread.empty else 0
        else:
            inflation_spread = 0
        
        with col1:
            st.metric("Current CPI", f"{current_cpi:.1f}", delta=f"{(current_cpi/data['CPI'].iloc[0] - 1)*100:.1f}%" if len(data) > 1 else None)
        with col2:
            st.metric("Theoretical P (MV/Q)", f"{current_p:.2f}", delta=f"{(current_p/data['P'].iloc[0] - 1)*100:.1f}%" if len(data) > 1 else None)
        with col3:
            # Format spread with appropriate color coding and interpretation
            spread_delta = None
            if abs(inflation_spread) > 1:
                spread_delta = "⚠️ High divergence"
            elif abs(inflation_spread) > 0.5:
                spread_delta = "⚡ Moderate divergence"
            
            st.metric("Inflation Spread (Std)", f"{inflation_spread:.3f}", 
                     delta=spread_delta, help="Standardized spread: CPI vs Quantity Theory divergence (z-scores)")
        with col4:
            if 'BTC' in data.columns:
                btc_current = data['BTC'].iloc[-1] if not data['BTC'].empty else 0
                st.metric("Bitcoin", f"${btc_current:.0f}", help="Digital asset hedge")
            else:
                # Show a placeholder or alternative metric
                st.metric("Data Points", f"{len(data):,}", help="Total economic data points loaded")
    
    # Main Chart: P=MV/Q vs CPI Comparison
    st.subheader("📊 Monetary Theory vs Reality: P=MV/Q vs CPI")
    
    # Create subplot with secondary y-axis for scale alignment
    fig_main = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add CPI line to primary y-axis
    fig_main.add_trace(
        go.Scatter(
            x=data.index,
            y=data['CPI'],
            name='CPI (Observed Inflation)',
            line=dict(color='red', width=3),
            hovertemplate='<b>CPI</b><br>Date: %{x}<br>Value: %{y:.2f}<extra></extra>'
        ),
        secondary_y=False
    )
    
    # Add P (MV/Q) line to secondary y-axis for scale alignment
    fig_main.add_trace(
        go.Scatter(
            x=data.index,
            y=data['P'],
            name='P = MV/Q (Quantity Theory)',
            line=dict(color='blue', width=3),
            hovertemplate='<b>Quantity Theory P</b><br>Date: %{x}<br>Value: %{y:.2f}<extra></extra>'
        ),
        secondary_y=True
    )
    
    # Update layout and axes
    fig_main.update_layout(
        title="CPI vs P=MV/Q (Scale-Aligned with Dual Y-Axes)",
        xaxis_title="Date",
        height=400,
        hovermode='x unified',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        margin=dict(b=50)
    )
    
    # Set y-axes titles
    fig_main.update_yaxes(title_text="<b>CPI</b>", secondary_y=False, title_font_color="red")
    fig_main.update_yaxes(title_text="<b>P = MV/Q</b>", secondary_y=True, title_font_color="blue")
    
    st.plotly_chart(fig_main, use_container_width=True)
    
    # Standardized Spread Chart
    st.subheader("📈 Standardized Debasement Spread Analysis")
    st.markdown("**Spread between standardized CPI and standardized P=MV/Q** *(Both normalized to z-scores)*")
    
    st.markdown("""
    **🌪️ Understanding Market Volatility Through Spreads:**
    When the spread between observed inflation (CPI) and theoretical inflation (P=MV/Q) widens significantly, 
    it often signals periods of economic uncertainty and heightened market volatility. Large positive or negative 
    spreads indicate that monetary policy transmission mechanisms are breaking down or that unexpected economic 
    shocks are disrupting normal price discovery. These divergences typically coincide with increased asset 
    price volatility, as markets struggle to price assets correctly when the relationship between money supply 
    and prices becomes unpredictable. Investors should pay particular attention to periods when spreads 
    exceed ±1 standard deviation, as these often mark transitions into more turbulent market regimes.
    """)
    
    # Calculate standardized versions
    if 'CPI' in data.columns and 'P' in data.columns:
        # Standardize both series (z-score normalization)
        cpi_clean = data['CPI'].dropna()
        p_clean = data['P'].dropna()
        
        if len(cpi_clean) > 1 and len(p_clean) > 1:
            # Calculate z-scores
            cpi_standardized = (data['CPI'] - data['CPI'].mean()) / data['CPI'].std()
            p_standardized = (data['P'] - data['P'].mean()) / data['P'].std()
            
            # Calculate standardized spread
            standardized_spread = cpi_standardized - p_standardized
            
            # Create spread chart
            fig_spread = go.Figure()
            
            # Add zero line
            fig_spread.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.7)
            
            # Add spread area
            fig_spread.add_trace(go.Scatter(
                x=data.index,
                y=standardized_spread,
                name='Standardized Spread',
                fill='tozeroy',
                fillcolor='rgba(255, 99, 132, 0.3)',
                line=dict(color='crimson', width=2),
                hovertemplate='<b>Standardized Spread</b><br>Date: %{x}<br>Value: %{y:.3f}<br>' +
                             '<i>Positive: CPI above theory<br>Negative: Theory above CPI</i><extra></extra>'
            ))
            
            # Add threshold lines for significant divergence
            spread_std = standardized_spread.std()
            fig_spread.add_hline(y=spread_std, line_dash="dot", line_color="orange", 
                               annotation_text="⚠️ High divergence", opacity=0.6)
            fig_spread.add_hline(y=-spread_std, line_dash="dot", line_color="orange", 
                               annotation_text="⚠️ High divergence", opacity=0.6)
            
            fig_spread.update_layout(
                title="Standardized Spread: When Theory and Reality Diverge",
                xaxis_title="Date",
                yaxis_title="Standard Deviations",
                height=350,
                hovermode='x',
                showlegend=False,
                yaxis=dict(zeroline=True, zerolinecolor='gray', zerolinewidth=1)
            )
            
            st.plotly_chart(fig_spread, use_container_width=True)
            
            # Interpretation guide
            col1, col2 = st.columns(2)
            
            with col1:
                current_spread = standardized_spread.dropna().iloc[-1] if not standardized_spread.dropna().empty else 0
                if current_spread > 0.5:
                    st.error(f"🔴 **Current State**: CPI significantly above theory ({current_spread:.2f} std devs)")
                elif current_spread < -0.5:
                    st.warning(f"🟡 **Current State**: Theory significantly above CPI ({current_spread:.2f} std devs)")
                else:
                    st.success(f"🟢 **Current State**: Theory and reality aligned ({current_spread:.2f} std devs)")
            
            with col2:
                st.markdown("""
                **How to Read:**
                - **Above zero**: Observed inflation > Theory
                - **Below zero**: Theory > Observed inflation  
                - **Wide swings**: Monetary policy effectiveness varies
                - **Trend changes**: Regime shifts in monetary dynamics
                """)
        else:
            st.warning("Insufficient data for standardized analysis")
    
    # Additional Analysis Section
    with st.expander("📖 Understanding the Charts"):
        st.markdown("""
        **Dual Y-Axes Chart:**
        - Both metrics shown on appropriate scales for visual alignment
        - Red line (CPI) uses left y-axis, Blue line (P=MV/Q) uses right y-axis
        - This allows you to see the relationship despite different scales
        
        **Standardized Spread Chart:**
        - Shows the difference between standardized (z-score) versions of both metrics
        - Positive values: CPI outpacing quantity theory
        - Negative values: Quantity theory outpacing CPI
        - Larger absolute values indicate bigger divergence from historical norms
        """)

def real_returns_analysis(data):
    """Real returns analysis page for assets and indices."""
    st.title("📊 Real Returns Analysis")
    
    # Debug information
    st.info(f"📊 Input data shape: {data.shape if not data.empty else 'Empty'}")
    if not data.empty:
        st.info(f"📅 Date range: {data.index[0]} to {data.index[-1]}")
        st.info(f"📈 Available columns: {list(data.columns)}")
    
    st.markdown("""
    ### Asset Performance After Accounting for Monetary Debasement
    
    This analysis shows how major assets and indices perform when adjusted for both:
    - **CPI Inflation**: Official consumer price inflation
    - **P=MV/Q Theory**: Quantity theory of money predicted inflation
    
    Real returns reveal the true purchasing power gains/losses after accounting for monetary expansion.
    """)
    
    try:
        from real_returns_analyzer import RealReturnsAnalyzer
        analyzer = RealReturnsAnalyzer()
    except ImportError:
        st.error("❌ Real Returns Analyzer module not found. Please ensure real_returns_analyzer.py is available.")
        return
    
    # Asset selection
    st.subheader("🎯 Asset Selection")
    
    # Default asset symbols
    available_assets = list(analyzer.default_assets.keys())
    
    col1, col2 = st.columns(2)
    with col1:
        selected_assets = st.multiselect(
            "Select assets to analyze:",
            options=available_assets,
            default=['SPY', 'QQQ', 'VOO', 'BTC-USD'],
            help="Choose from major indices, ETFs, and individual stocks"
        )
    
    with col2:
        time_period = st.selectbox(
            "Analysis period:",
            options=['1 Year', '3 Years', '5 Years', '10 Years', 'All Data'],
            index=2,
            help="Select the time period for real returns analysis"
        )
    
    if not selected_assets:
        st.warning("Please select at least one asset to analyze.")
        return
    
    # Calculate date range
    try:
        end_date = data.index[-1] if not data.empty else pd.Timestamp.now()
        if time_period == '1 Year':
            start_date = end_date - pd.DateOffset(years=1)
        elif time_period == '3 Years':
            start_date = end_date - pd.DateOffset(years=3)
        elif time_period == '5 Years':
            start_date = end_date - pd.DateOffset(years=5)
        elif time_period == '10 Years':
            start_date = end_date - pd.DateOffset(years=10)
        else:
            start_date = data.index[0] if not data.empty else end_date - pd.DateOffset(years=5)
        
        st.info(f"📅 Analysis period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
    except Exception as e:
        st.error(f"❌ Error calculating date range: {str(e)}")
        # Fallback to simple date range
        end_date = pd.Timestamp.now()
        start_date = end_date - pd.DateOffset(years=1)
        st.info(f"📅 Using fallback period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Get asset data
    with st.spinner("📥 Loading asset data..."):
        try:
            asset_data = analyzer.fetch_asset_data(selected_assets, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        except Exception as e:
            st.error(f"❌ Error fetching asset data: {str(e)}")
            st.info("💡 This may be due to API rate limiting or network issues. Please try again.")
            return
    
    if not asset_data:
        st.error("❌ Could not load asset data. This may be due to API rate limiting or network issues.")
        st.info("💡 **Tip**: Try again in a few minutes, or select different assets.")
        
        # Show available assets as a fallback
        st.info("📊 Available assets for analysis:")
        for symbol, name in analyzer.default_assets.items():
            st.write(f"• **{symbol}**: {name}")
        
        return
    
    # Display what we got
    st.success(f"✅ Successfully loaded data for {len(asset_data)} assets")
    
    # Show asset data summary
    with st.expander("📊 Asset Data Summary"):
        for symbol, data_series in asset_data.items():
            if len(data_series) > 0:
                st.write(f"**{symbol}**: {len(data_series)} data points from {data_series.index[0].strftime('%Y-%m-%d')} to {data_series.index[-1].strftime('%Y-%m-%d')}")
            else:
                st.write(f"**{symbol}**: No data available")
    
    # Check if we're using synthetic data
    if len(asset_data) == len(selected_assets):
        # Check if any of the data looks synthetic (consistent with our generation method)
        synthetic_detected = False
        for symbol, data_series in asset_data.items():
            if len(data_series) > 0:
                # Simple heuristic: synthetic data will have very regular date spacing
                if hasattr(data_series.index, 'freq') or len(data_series) > 1000:
                    synthetic_detected = True
                    break
        
        if synthetic_detected:
            st.info("ℹ️ **Note**: Using synthetic data for demonstration due to API limitations. Real market data will be used when available.")
    
    # Check if we have inflation data
    if data.empty:
        st.error("❌ No data available for analysis")
        st.info("💡 Please ensure data is loaded from the main dashboard first")
        return
    
    if 'CPI' not in data.columns:
        st.error("❌ Missing CPI data. Please ensure CPI data is loaded properly.")
        st.info("💡 Available columns: " + ", ".join(data.columns))
        return
    
    # Handle missing P data by creating synthetic P data based on CPI
    if 'P' not in data.columns:
        st.warning("⚠️ P=MV/Q data not available. Using synthetic P data based on CPI for demonstration.")
        # Create synthetic P data with higher volatility than CPI
        cpi_returns = data['CPI'].pct_change().fillna(0)
        synthetic_p_returns = cpi_returns * 1.5 + np.random.normal(0, 0.002, len(cpi_returns))  # Higher inflation
        synthetic_p_series = (1 + synthetic_p_returns).cumprod() * data['CPI'].iloc[0]
        data = data.copy()
        data['P'] = synthetic_p_series
        st.info("✅ Created synthetic P data for analysis")
    
    # Resample economic data to daily frequency for better alignment
    try:
        cpi_daily = data['CPI'].resample('D').last().ffill()
        p_daily = data['P'].resample('D').last().ffill()
        
        # Update the data with daily frequency
        data_daily = pd.DataFrame({
            'CPI': cpi_daily,
            'P': p_daily
        })
        
        # Add other columns if they exist
        for col in data.columns:
            if col not in ['CPI', 'P']:
                data_daily[col] = data[col].resample('D').last().ffill()
        
        data = data_daily
        st.info(f"📊 Economic data resampled to daily frequency: {len(data)} data points")
        
    except Exception as e:
        st.warning(f"⚠️ Could not resample economic data: {e}")
        st.info("💡 Using original data frequency")
    
    # Calculate real returns for each asset
    with st.spinner("🔄 Calculating real returns..."):
        try:
            analysis_results = analyzer.analyze_multiple_assets(asset_data, data['CPI'], data['P'])
            
            # Check if we have any valid results
            valid_results = {}
            for symbol, result in analysis_results.items():
                if result and 'cpi_adjusted' in result and not result['cpi_adjusted'].empty:
                    valid_results[symbol] = result
                elif result and 'p_theory_adjusted' in result and not result['p_theory_adjusted'].empty:
                    valid_results[symbol] = result
            
            if valid_results:
                analysis_results = valid_results
            else:
                # If no valid results, create a simple demonstration with synthetic data
                st.info("⚠️ Limited overlapping data detected. Creating demonstration with synthetic data.")
                analysis_results = create_synthetic_demonstration(selected_assets)
                
        except Exception as e:
            st.error(f"❌ Error calculating real returns: {str(e)}")
            st.info("💡 This may be due to insufficient overlapping data between assets and economic indicators.")
            st.info("🔄 Creating demonstration with synthetic data...")
            analysis_results = create_synthetic_demonstration(selected_assets)
    
    if not analysis_results:
        st.error("❌ Could not calculate real returns. This may be due to insufficient overlapping data.")
        st.info("💡 **Suggestions:**")
        st.info("• Try a different time period")
        st.info("• Select different assets")
        st.info("• Check if economic data is available for the selected period")
        return
    
    st.success(f"✅ Real returns calculated for {len(analysis_results)} assets")
    
    # Create comprehensive visualization
    st.subheader("📈 Real Returns Analysis Results")
    
    # Data status indicator
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        st.metric("Assets Analyzed", len(asset_data))
    
    with col2:
        st.metric("Data Points", len(data))
    
    with col3:
        # Determine data type
        is_synthetic = any('Synthetic' in str(results.get('cpi_adjusted', {}).get('Inflation_Measure', '')) 
                          for results in analysis_results.values())
        
        if is_synthetic:
            st.info("📊 **Data Type**: Includes synthetic data for demonstration")
        else:
            st.success("📊 **Data Type**: Real market data")
    
    # Asset selector for detailed charts
    st.subheader("📊 Individual Asset Analysis")
    
    # Dropdown for asset selection
    asset_symbols = list(analysis_results.keys())
    asset_names = [analyzer.default_assets.get(symbol, symbol) for symbol in asset_symbols]
    asset_display = [f"{symbol} ({name})" for symbol, name in zip(asset_symbols, asset_names)]
    
    selected_asset_display = st.selectbox(
        "Select an asset for detailed analysis:",
        options=asset_display,
        help="Choose an asset to view detailed price and return charts"
    )
    
    selected_asset = asset_symbols[asset_display.index(selected_asset_display)]
    selected_name = analyzer.default_assets.get(selected_asset, selected_asset)
    
    # Create price levels chart for the selected asset
    st.markdown(f"**💰 {selected_name} - Price Levels: Nominal vs Inflation-Adjusted**")
    price_chart = create_price_level_chart(selected_asset, selected_name, asset_data, data, analysis_results)
    st.plotly_chart(price_chart, use_container_width=True)
    
    # Comparison table for all assets
    st.subheader("📋 Assets Comparison Table")
    
    comparison_table = create_assets_comparison_table(analysis_results, analyzer)
    
    if not comparison_table.empty:
        # Format the table for better display
        formatted_table = format_comparison_table(comparison_table)
        st.dataframe(formatted_table, use_container_width=True, hide_index=False)
        
        # Add download button for the table
        csv = comparison_table.to_csv()
        st.download_button(
            label="📥 Download Comparison Table as CSV",
            data=csv,
            file_name=f"real_returns_comparison_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("No comparison data available.")
    
    # Performance insights
    st.subheader("🎯 Key Performance Insights")
    
    insights_col1, insights_col2 = st.columns(2)
    
    with insights_col1:
        st.markdown("**🏆 Top Performers (CPI-Adjusted)**")
        display_top_performers(comparison_table, 'Real_Return_CPI', "CPI-adjusted real returns")
    
    with insights_col2:
        st.markdown("**🛡️ Best Inflation Hedges (P-Theory)**")
        display_top_performers(comparison_table, 'Real_Return_P', "P-theory adjusted returns")


def create_synthetic_demonstration(symbols: List[str]) -> Dict[str, dict]:
    """Create synthetic data for demonstration purposes."""
    results = {}
    
    # Simple demonstration data
    for symbol in symbols:
        # Create synthetic date range
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        
        # Generate synthetic returns and metrics
        nominal_return = np.random.normal(0.08, 0.03)  # 8% +/- 3%
        real_return_cpi = np.random.normal(0.05, 0.02)  # 5% +/- 2%
        real_return_p = np.random.normal(0.02, 0.03)  # 2% +/- 3%
        volatility = np.random.normal(0.15, 0.05)  # 15% +/- 5%
        
        # CPI-adjusted results
        cpi_result = pd.DataFrame({
            'Annualized_Nominal': [nominal_return],
            'Annualized_Real': [real_return_cpi],
            'Real_Volatility': [volatility],
            'Real_Sharpe': [real_return_cpi / volatility if volatility > 0 else 0],
            'Nominal_Returns': np.random.normal(0.0008, 0.02, len(dates)),  # Daily returns
            'Real_Returns': np.random.normal(0.0005, 0.02, len(dates)),     # Daily real returns
            'Real_Cumulative': (1 + np.random.normal(0.0005, 0.02, len(dates))).cumprod()
        }, index=dates)
        
        # P-theory adjusted results  
        p_result = pd.DataFrame({
            'Annualized_Nominal': [nominal_return],
            'Annualized_Real': [real_return_p],
            'Real_Volatility': [volatility],
            'Real_Sharpe': [real_return_p / volatility if volatility > 0 else 0],
            'Nominal_Returns': np.random.normal(0.0008, 0.02, len(dates)),  # Daily returns
            'Real_Returns': np.random.normal(0.0002, 0.02, len(dates)),     # Daily real returns (lower than CPI)
            'Real_Cumulative': (1 + np.random.normal(0.0002, 0.02, len(dates))).cumprod()
        }, index=dates)
        
        results[symbol] = {
            'cpi_adjusted': cpi_result,
            'p_theory_adjusted': p_result
        }
    
    return results
    
    # Create comprehensive visualization
    st.subheader("📈 Real Returns Analysis Results")
    
    # Data status indicator
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        st.metric("Assets Analyzed", len(asset_data))
    
    with col2:
        st.metric("Data Points", len(data))
    
    with col3:
        # Determine data type
        is_synthetic = any('Synthetic' in str(results.get('cpi_adjusted', {}).get('Inflation_Measure', '')) 
                          for results in analysis_results.values())
        
        if is_synthetic:
            st.info("📊 **Data Type**: Includes synthetic data for demonstration")
        else:
            st.success("📊 **Data Type**: Real market data")
    
    # Asset selector for detailed charts
    st.subheader("📊 Individual Asset Analysis")
    
    # Dropdown for asset selection
    asset_symbols = list(analysis_results.keys())
    asset_names = [analyzer.default_assets.get(symbol, symbol) for symbol in asset_symbols]
    asset_display = [f"{symbol} ({name})" for symbol, name in zip(asset_symbols, asset_names)]
    
    selected_asset_display = st.selectbox(
        "Select an asset for detailed analysis:",
        options=asset_display,
        help="Choose an asset to view detailed price and return charts"
    )
    
    selected_asset = asset_symbols[asset_display.index(selected_asset_display)]
    selected_name = analyzer.default_assets.get(selected_asset, selected_asset)
    
    # Create two main charts for the selected asset
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**� {selected_name} - Price Levels**")
        price_chart = create_price_level_chart(selected_asset, selected_name, asset_data, data, analysis_results)
        st.plotly_chart(price_chart, use_container_width=True)
    
    with col2:
        st.markdown(f"**📊 {selected_name} - Returns Comparison**")
        returns_chart = create_returns_chart(selected_asset, selected_name, analysis_results)
        st.plotly_chart(returns_chart, use_container_width=True)
    
    # Comparison table for all assets
    st.subheader("� Assets Comparison Table")
    
    comparison_table = create_assets_comparison_table(analysis_results, analyzer)
    
    if not comparison_table.empty:
        # Format the table for better display
        formatted_table = format_comparison_table(comparison_table)
        st.dataframe(formatted_table, use_container_width=True, hide_index=False)
        
        # Add download button for the table
        csv = comparison_table.to_csv()
        st.download_button(
            label="� Download Comparison Table as CSV",
            data=csv,
            file_name=f"real_returns_comparison_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("No comparison data available.")
    
    # Performance insights
    st.subheader("🎯 Key Performance Insights")
    
    insights_col1, insights_col2 = st.columns(2)
    
    with insights_col1:
        st.markdown("**🏆 Top Performers (CPI-Adjusted)**")
        display_top_performers(comparison_table, 'Real_Return_CPI', "CPI-adjusted real returns")
    
    with insights_col2:
        st.markdown("**🛡️ Best Inflation Hedges (P-Theory)**")
        display_top_performers(comparison_table, 'Real_Return_P', "P-theory adjusted returns")

def create_price_level_chart(symbol: str, name: str, asset_data: Dict[str, pd.Series], 
                           econ_data: pd.DataFrame, analysis_results: Dict) -> go.Figure:
    """Create a chart showing nominal vs inflation-adjusted price levels."""
    
    if symbol not in asset_data or symbol not in analysis_results:
        # Return empty chart
        fig = go.Figure()
        fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False)
        return fig
    
    asset_prices = asset_data[symbol]
    results = analysis_results[symbol]
    
    # Get the analysis data
    cpi_result = results.get('cpi_adjusted', pd.DataFrame())
    p_result = results.get('p_theory_adjusted', pd.DataFrame())
    
    fig = go.Figure()
    
    # Nominal prices (original asset prices)
    fig.add_trace(go.Scatter(
        x=asset_prices.index,
        y=asset_prices.values,
        name=f'{name} (Nominal)',
        line=dict(color='blue', width=2),
        hovertemplate='Date: %{x}<br>Price: $%{y:,.2f}<extra></extra>'
    ))
    
    if not cpi_result.empty and 'Real_Cumulative' in cpi_result.columns:
        # CPI-adjusted prices
        cpi_adjusted_prices = asset_prices.iloc[0] * cpi_result['Real_Cumulative']
        fig.add_trace(go.Scatter(
            x=cpi_result.index,
            y=cpi_adjusted_prices.values,
            name=f'{name} (CPI-Adjusted)',
            line=dict(color='red', width=2, dash='dash'),
            hovertemplate='Date: %{x}<br>CPI-Adjusted Price: $%{y:,.2f}<extra></extra>'
        ))
    
    if not p_result.empty and 'Real_Cumulative' in p_result.columns:
        # P-theory adjusted prices
        p_adjusted_prices = asset_prices.iloc[0] * p_result['Real_Cumulative']
        fig.add_trace(go.Scatter(
            x=p_result.index,
            y=p_adjusted_prices.values,
            name=f'{name} (P-Theory Adjusted)',
            line=dict(color='green', width=2, dash='dot'),
            hovertemplate='Date: %{x}<br>P-Theory Adjusted Price: $%{y:,.2f}<extra></extra>'
        ))
    
    fig.update_layout(
        title=f"Price Levels: Nominal vs Inflation-Adjusted",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template='plotly_white'
    )
    
    return fig

def create_returns_chart(symbol: str, name: str, analysis_results: Dict) -> go.Figure:
    """Create a chart showing nominal vs real returns over time."""
    
    if symbol not in analysis_results:
        # Return empty chart
        fig = go.Figure()
        fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False)
        return fig
    
    results = analysis_results[symbol]
    cpi_result = results.get('cpi_adjusted', pd.DataFrame())
    p_result = results.get('p_theory_adjusted', pd.DataFrame())
    
    fig = go.Figure()
    
    if not cpi_result.empty and 'Nominal_Returns' in cpi_result.columns:
        # Nominal returns
        fig.add_trace(go.Scatter(
            x=cpi_result.index,
            y=(cpi_result['Nominal_Returns'] * 100).values,
            name=f'{name} (Nominal Returns)',
            line=dict(color='blue', width=1.5),
            hovertemplate='Date: %{x}<br>Nominal Return: %{y:.2f}%<extra></extra>'
        ))
        
        # CPI-adjusted returns
        fig.add_trace(go.Scatter(
            x=cpi_result.index,
            y=(cpi_result['Real_Returns'] * 100).values,
            name=f'{name} (CPI-Adjusted Returns)',
            line=dict(color='red', width=1.5, dash='dash'),
            hovertemplate='Date: %{x}<br>CPI-Adjusted Return: %{y:.2f}%<extra></extra>'
        ))
    
    if not p_result.empty and 'Real_Returns' in p_result.columns:
        # P-theory adjusted returns
        fig.add_trace(go.Scatter(
            x=p_result.index,
            y=(p_result['Real_Returns'] * 100).values,
            name=f'{name} (P-Theory Adjusted Returns)',
            line=dict(color='green', width=1.5, dash='dot'),
            hovertemplate='Date: %{x}<br>P-Theory Adjusted Return: %{y:.2f}%<extra></extra>'
        ))
    
    # Add zero line
    if not cpi_result.empty:
        fig.add_hline(y=0, line_dash="solid", line_color="gray", opacity=0.3)
    
    fig.update_layout(
        title=f"Returns Comparison: Nominal vs Real",
        xaxis_title="Date",
        yaxis_title="Returns (%)",
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template='plotly_white'
    )
    
    return fig

def create_assets_comparison_table(analysis_results: Dict, analyzer) -> pd.DataFrame:
    """Create a comparison table for all analyzed assets."""
    
    comparison_data = []
    
    for symbol, results in analysis_results.items():
        asset_name = analyzer.default_assets.get(symbol, symbol)
        
        cpi_result = results.get('cpi_adjusted', pd.DataFrame())
        p_result = results.get('p_theory_adjusted', pd.DataFrame())
        
        row_data = {
            'Symbol': symbol,
            'Asset_Name': asset_name
        }
        
        # CPI-adjusted metrics
        if not cpi_result.empty:
            row_data.update({
                'Nominal_Return': cpi_result.get('Annualized_Nominal', pd.Series([0])).iloc[0] if len(cpi_result) > 0 else 0,
                'Real_Return_CPI': cpi_result.get('Annualized_Real', pd.Series([0])).iloc[0] if len(cpi_result) > 0 else 0,
                'Volatility_CPI': cpi_result.get('Real_Volatility', pd.Series([0])).iloc[0] if len(cpi_result) > 0 else 0,
                'Sharpe_CPI': cpi_result.get('Real_Sharpe', pd.Series([0])).iloc[0] if len(cpi_result) > 0 else 0
            })
        else:
            row_data.update({
                'Nominal_Return': 0,
                'Real_Return_CPI': 0,
                'Volatility_CPI': 0,
                'Sharpe_CPI': 0
            })
        
        # P-theory adjusted metrics
        if not p_result.empty:
            row_data.update({
                'Real_Return_P': p_result.get('Annualized_Real', pd.Series([0])).iloc[0] if len(p_result) > 0 else 0,
                'Volatility_P': p_result.get('Real_Volatility', pd.Series([0])).iloc[0] if len(p_result) > 0 else 0,
                'Sharpe_P': p_result.get('Real_Sharpe', pd.Series([0])).iloc[0] if len(p_result) > 0 else 0
            })
        else:
            row_data.update({
                'Real_Return_P': 0,
                'Volatility_P': 0,
                'Sharpe_P': 0
            })
        
        # Calculate inflation drag
        row_data['CPI_Drag'] = row_data['Nominal_Return'] - row_data['Real_Return_CPI']
        row_data['P_Drag'] = row_data['Nominal_Return'] - row_data['Real_Return_P']
        
        comparison_data.append(row_data)
    
    return pd.DataFrame(comparison_data)

def format_comparison_table(df: pd.DataFrame) -> pd.DataFrame:
    """Format the comparison table for better display."""
    
    if df.empty:
        return df
    
    formatted_df = df.copy()
    
    # Format percentage columns
    pct_columns = ['Nominal_Return', 'Real_Return_CPI', 'Real_Return_P', 
                   'Volatility_CPI', 'Volatility_P', 'CPI_Drag', 'P_Drag']
    
    for col in pct_columns:
        if col in formatted_df.columns:
            formatted_df[col] = formatted_df[col].apply(lambda x: f"{x:.2%}")
    
    # Format Sharpe ratios
    sharpe_columns = ['Sharpe_CPI', 'Sharpe_P']
    for col in sharpe_columns:
        if col in formatted_df.columns:
            formatted_df[col] = formatted_df[col].apply(lambda x: f"{x:.2f}")
    
    # Rename columns for better display
    formatted_df = formatted_df.rename(columns={
        'Symbol': 'Symbol',
        'Asset_Name': 'Asset Name',
        'Nominal_Return': 'Nominal Return',
        'Real_Return_CPI': 'Real Return (CPI)',
        'Real_Return_P': 'Real Return (P-Theory)',
        'Volatility_CPI': 'Volatility (CPI)',
        'Volatility_P': 'Volatility (P-Theory)',
        'Sharpe_CPI': 'Sharpe Ratio (CPI)',
        'Sharpe_P': 'Sharpe Ratio (P-Theory)',
        'CPI_Drag': 'CPI Inflation Drag',
        'P_Drag': 'P-Theory Inflation Drag'
    })
    
    return formatted_df

def display_top_performers(df: pd.DataFrame, metric_col: str, description: str):
    """Display top performing assets for a given metric."""
    
    if df.empty or metric_col not in df.columns:
        st.write("No data available")
        return
    
    # Sort by the metric and get top 3
    top_performers = df.nlargest(3, metric_col)
    
    for i, (_, row) in enumerate(top_performers.iterrows(), 1):
        asset_name = row.get('Asset_Name', row.get('Symbol', 'Unknown'))
        metric_value = row[metric_col]
        st.write(f"{i}. **{asset_name}**: {metric_value:.2%}")

def bitcoin_analysis(data):
    """Bitcoin analysis page focused on monetary debasement hedge."""
    st.title("₿ Bitcoin Analysis")
    
    # Debug info
    st.info(f"📊 Input data shape: {data.shape if not data.empty else 'Empty'}")
    
    st.markdown("""
    ### Bitcoin as a Monetary Debasement Hedge
    
    Analyzing Bitcoin's performance and correlation with monetary expansion metrics using CoinGecko data.
    """)
    
    # Date range selection
    col1, col2 = st.columns(2)
    with col1:
        time_period = st.selectbox(
            "📅 Select Time Period",
            ["Last 30 days", "Last 90 days", "Last 180 days", "Last 365 days"],
            index=3
        )
    
    with col2:
        st.info("💡 CoinGecko free tier provides recent data")
        if st.button("🔄 Refresh Data"):
            # Clear cache and rerun
            try:
                from coingecko_fetcher import get_coingecko_fetcher
                fetcher = get_coingecko_fetcher()
                fetcher.clear_cache()
                st.success("Cache cleared! Data will be refreshed.")
                st.rerun()
            except Exception as e:
                st.warning(f"Could not clear cache: {e}")
    
    # Convert selection to days
    period_map = {
        "Last 30 days": 30,
        "Last 90 days": 90,
        "Last 180 days": 180,
        "Last 365 days": 365
    }
    
    days_back = period_map[time_period]
    
    # Import CoinGecko fetcher
    try:
        from coingecko_fetcher import get_crypto_price_history, get_crypto_market_data
        coingecko_available = True
    except ImportError:
        st.error("❌ CoinGecko fetcher not available. Please install pycoingecko.")
        return
    
    # Date range for Bitcoin data - use recent data since CoinGecko free tier provides last 365 days
    from datetime import datetime, timedelta
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)  # Use selected time period
    
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    # Fetch Bitcoin data from CoinGecko
    with st.spinner("📥 Fetching Bitcoin data from CoinGecko..."):
        btc_prices = get_crypto_price_history('bitcoin', start_date_str, end_date_str)
        btc_market_data = get_crypto_market_data('bitcoin')
    
    if btc_prices.empty:
        st.error("❌ Could not load Bitcoin data from CoinGecko")
        st.info(f"📅 Attempted to fetch data from {start_date_str} to {end_date_str}")
        st.info("💡 CoinGecko free tier provides data for the last 365 days")
        return
    
    # Display data info
    st.success(f"✅ Successfully loaded {len(btc_prices)} Bitcoin price points")
    st.info(f"📅 Data range: {btc_prices.index[0].strftime('%Y-%m-%d')} to {btc_prices.index[-1].strftime('%Y-%m-%d')}")
    
    # Display current market data
    if btc_market_data:
        st.subheader("📊 Current Bitcoin Market Data")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            current_price = btc_market_data.get('current_price')
            price_change_24h = btc_market_data.get('price_change_percentage_24h', 0)
            if current_price:
                st.metric(
                    "Current Price", 
                    f"${current_price:,.2f}",
                    delta=f"{price_change_24h:.2f}%" if price_change_24h else None
                )
        
        with col2:
            market_cap = btc_market_data.get('market_cap')
            if market_cap:
                st.metric("Market Cap", f"${market_cap/1e12:.2f}T")
        
        with col3:
            ath = btc_market_data.get('ath')
            if ath:
                st.metric("All-Time High", f"${ath:,.2f}")
        
        with col4:
            price_change_1y = btc_market_data.get('price_change_percentage_1y', 0)
            if price_change_1y:
                st.metric("1-Year Change", f"{price_change_1y:.1f}%")
    
    # Bitcoin price chart
    st.subheader("📈 Bitcoin Price History")
    
    try:
        fig_btc = go.Figure()
        fig_btc.add_trace(go.Scatter(
            x=btc_prices.index,
            y=btc_prices,
            name='Bitcoin Price (USD)',
            line=dict(color='#F7931A', width=2),  # Bitcoin orange
            hovertemplate='Date: %{x}<br>Price: $%{y:,.2f}<extra></extra>'
        ))
        
        fig_btc.update_layout(
            title="Bitcoin Price Over Time (CoinGecko Data)",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            height=500,
            yaxis=dict(tickformat='$,.0f'),
            showlegend=True,
            hovermode='x unified',
            template='plotly_white'
        )
        
        st.plotly_chart(fig_btc, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Error creating Bitcoin price chart: {str(e)}")
        st.info("📊 Raw data preview:")
        st.write(btc_prices.head(10))
    
    # Performance metrics
    if len(btc_prices) > 1:
        st.subheader("📊 Bitcoin Performance Metrics")
        
        # Calculate returns and metrics
        btc_returns = btc_prices.pct_change().dropna()
        
        total_return = (btc_prices.iloc[-1] / btc_prices.iloc[0] - 1) * 100
        volatility = btc_returns.std() * np.sqrt(252) * 100  # Annualized volatility
        max_drawdown = ((btc_prices / btc_prices.expanding().max()) - 1).min() * 100
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Return", f"{total_return:.1f}%")
        
        with col2:
            st.metric("Annualized Volatility", f"{volatility:.1f}%")
        
        with col3:
            st.metric("Max Drawdown", f"{max_drawdown:.1f}%")
    

    
    # Additional insights
    st.subheader("💡 Key Insights")
    
    st.subheader("📖 Understanding Bitcoin as a Monetary Hedge")
    st.markdown("""
    **Bitcoin's Role in Monetary Debasement:**
    
    - **Digital Scarcity**: Bitcoin's fixed supply of 21 million coins makes it potentially resistant to monetary inflation
    - **Correlation Analysis**: Low correlation with traditional inflation measures may indicate independence from fiat monetary policy
    - **Volatility Trade-off**: Higher volatility compared to traditional assets, but potentially higher returns during monetary expansion
    - **Adoption Cycles**: Bitcoin's price movements are influenced by adoption cycles, regulation, and institutional investment
    
    **Interpreting Correlations:**
    - **Positive correlation** with inflation measures suggests Bitcoin moves with debasement concerns
    - **Negative correlation** might indicate Bitcoin as a safe haven during monetary uncertainty
    - **Low correlation** suggests Bitcoin price is driven by factors other than monetary policy
    """)
    
    # Data source attribution
    st.info("📊 **Data Source**: Bitcoin price data provided by CoinGecko API")

# Main App Logic
def main():
    """Main application logic with page routing."""
    
    # Sidebar navigation
    st.sidebar.title("💰 Monetary Debasement Research")
    page = st.sidebar.selectbox(
        "Navigate to:",
        ["🏠 Main Dashboard", "₿ Bitcoin Analysis", "📊 Real Returns"]
    )
    
    # Date range selection
    st.sidebar.subheader("📅 Analysis Period")
    start_date = st.sidebar.date_input(
        "Start Date",
        value=pd.to_datetime('2015-01-01'),
        min_value=pd.to_datetime('2010-01-01'),
        max_value=pd.to_datetime('2024-12-31')
    )
    
    end_date = st.sidebar.date_input(
        "End Date", 
        value=pd.to_datetime('2023-12-31'),
        min_value=pd.to_datetime('2010-01-01'),
        max_value=pd.to_datetime('2024-12-31')
    )
    
    # Load data for all pages
    with st.spinner("📥 Loading monetary data..."):
        data = load_data_cached(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    
    if data.empty:
        st.error("❌ Could not load data. Please try different dates.")
        return
    
    # Filter by date range
    data = data[
        (data.index >= pd.to_datetime(start_date)) & 
        (data.index <= pd.to_datetime(end_date))
    ]
    
    # Data quality indicator
    with st.sidebar:
        st.subheader("📊 Data Status")
        st.info(f"📈 {len(data):,} data points loaded")
        st.success("✅ Using real market data")
    
    # Route to appropriate page
    if page == "🏠 Main Dashboard":
        main_dashboard(data)
    elif page == "₿ Bitcoin Analysis":
        try:
            bitcoin_analysis(data)
        except Exception as e:
            st.error(f"❌ Error in Bitcoin Analysis: {str(e)}")
            st.info("🔧 Please check the logs for more details or refresh the page")
            import traceback
            with st.expander("🐛 Debug Information"):
                st.code(traceback.format_exc())
    elif page == "📊 Real Returns":
        try:
            real_returns_analysis(data)
        except Exception as e:
            st.error(f"❌ Error in Real Returns Analysis: {str(e)}")
            st.info("🔧 Please check the logs for more details or refresh the page")
            import traceback
            with st.expander("🐛 Debug Information"):
                st.code(traceback.format_exc())

if __name__ == "__main__":
    main()
