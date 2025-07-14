# Monetary Debasement Research Dashboard - User Guide

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- Internet connection for data fetching
- Web browser for dashboard access

### Installation & Setup
1. **Install Dependencies**:
   ```bash
   pip install streamlit pandas numpy plotly yfinance pandas-datareader
   ```

2. **Run the Dashboard**:
   ```bash
   cd /path/to/VIXProj
   streamlit run monetary_app.py
   ```

3. **Access the Dashboard**:
   - Open your browser to `http://localhost:8501`
   - The dashboard will automatically load with default settings

## 📊 Dashboard Navigation

### Main Sections

#### 🏠 Main Dashboard
- **Primary Analysis**: Core monetary debasement research
- **Key Charts**: CPI vs P=MV/Q comparison, standardized spread analysis
- **Signal Detection**: Automated detection of monetary debasement signals
- **Insights**: Research observations and key findings

#### ₿ Bitcoin Analysis
- **Bitcoin Focus**: Specific analysis of Bitcoin as a monetary debasement hedge
- **Correlation Analysis**: Bitcoin vs traditional assets and inflation measures
- **Performance Metrics**: Bitcoin returns adjusted for inflation

#### 📊 Real Returns Analysis
- **Asset Selection**: Choose from 16+ major assets (SPY, QQQ, VOO, BTC, Gold, etc.)
- **Time Periods**: 1Y, 3Y, 5Y, 10Y, or All Data
- **Inflation Adjustment**: Compare CPI vs P=MV/Q adjusted returns
- **Performance Ranking**: Best performing assets after inflation adjustment

#### 📄 Thesis & About
- **Research Methodology**: Explanation of theoretical framework
- **Data Sources**: Information about data providers and calculations
- **Limitations**: Understanding the scope and limitations of the analysis

## 🎛️ Dashboard Controls

### Date Range Selection
- **Located**: Left sidebar under "📅 Analysis Period"
- **Default**: 2015-2023 (8 years of data)
- **Range**: 2010-2024 (adjustable based on data availability)
- **Impact**: Affects all analyses and visualizations

### Asset Selection (Real Returns Page)
- **Multi-Select**: Choose multiple assets for comparison
- **Default Selection**: SPY, QQQ, VOO, BTC-USD
- **Available Assets**: 16 major indices, ETFs, and individual stocks
- **Custom Analysis**: Select specific assets for focused analysis

### Time Period Selection
- **Quick Select**: 1Y, 3Y, 5Y, 10Y, All Data
- **Dynamic**: Automatically calculates from the end date backwards
- **Analysis Impact**: Affects annualized returns and volatility calculations

## 📈 Understanding the Charts

### CPI vs P=MV/Q Chart
- **Red Line**: Official CPI inflation (Consumer Price Index)
- **Blue Line**: P=MV/Q theoretical inflation (Quantity Theory of Money)
- **Dual Y-Axis**: Each measure on its own scale for comparison
- **Interpretation**: Divergence indicates monetary policy effects

### Standardized Spread Chart
- **Z-Score Normalized**: Both measures converted to standard deviations
- **Spread Line**: Difference between standardized CPI and P=MV/Q
- **Significance**: Large spreads indicate monetary debasement periods

### Real Returns Performance Chart
- **Solid Lines**: Nominal returns (not inflation-adjusted)
- **Dashed Lines**: CPI-adjusted real returns
- **Dotted Lines**: P=MV/Q-adjusted real returns
- **Color Coding**: Each asset has a unique color across all metrics

### Correlation Heatmap
- **Color Scale**: Red (negative) to Blue (positive) correlations
- **Values**: -1 (perfect negative) to +1 (perfect positive)
- **Interpretation**: Understanding asset relationships during monetary expansion

## 🔍 Key Metrics Explained

### Real Returns
- **Calculation**: Nominal Return - Inflation Rate
- **CPI Adjusted**: Using official consumer price inflation
- **P=MV/Q Adjusted**: Using quantity theory predicted inflation
- **Annualized**: Converted to annual percentage for comparison

### Volatility
- **Calculation**: Standard deviation of returns, annualized
- **Real Volatility**: Volatility after inflation adjustment
- **Interpretation**: Higher values indicate more price instability

### Sharpe Ratio
- **Calculation**: (Return - Risk-free rate) / Volatility
- **Real Sharpe**: Using inflation-adjusted returns
- **Interpretation**: Higher values indicate better risk-adjusted performance

### Performance Rankings
- **Best Real Returns**: Assets with highest inflation-adjusted returns
- **Dual Rankings**: Separate rankings for CPI and P=MV/Q adjustments
- **Hedge Analysis**: Which assets perform best against different inflation measures

## 💡 Pro Tips

### Data Quality
- **Live Data**: Dashboard fetches real-time data from FRED and Yahoo Finance
- **Rate Limits**: Yahoo Finance may rate limit; synthetic data available as fallback
- **Data Gaps**: Some assets may have limited historical data

### Analysis Best Practices
- **Longer Periods**: Use 5+ year periods for more stable analysis
- **Multiple Assets**: Compare at least 3-5 assets for meaningful insights
- **Both Measures**: Always compare CPI and P=MV/Q adjustments
- **Context**: Consider macroeconomic context when interpreting results

### Troubleshooting
- **Loading Issues**: Refresh the page if data doesn't load
- **API Errors**: Rate limiting is normal; try again after a few minutes
- **Missing Data**: Some assets may not have data for all time periods

## 🎯 Research Applications

### Investment Analysis
- **Asset Allocation**: Identify best inflation hedges
- **Timing Decisions**: Use signal detection for entry/exit timing
- **Risk Management**: Understand real volatility vs nominal volatility

### Academic Research
- **Monetary Theory**: Test quantity theory of money predictions
- **Inflation Analysis**: Compare official vs theoretical inflation measures
- **Asset Pricing**: Study how monetary policy affects asset prices

### Policy Analysis
- **Monetary Policy**: Understand effects of money supply expansion
- **Inflation Targeting**: Compare policy effectiveness across measures
- **Economic Indicators**: Use as early warning system for monetary distortions

## 📞 Support

### Technical Issues
- Check the terminal output for error messages
- Verify internet connection for data fetching
- Ensure all Python dependencies are installed

### Data Questions
- FRED data is official Federal Reserve economic data
- Yahoo Finance data is market-sourced price information
- P=MV/Q calculations follow standard economic methodology

### Feature Requests
- The dashboard is designed to be extensible
- Additional assets and analysis methods can be added
- Consider contributing to the open-source project

---

**Happy Researching! 🎉**

*Understanding monetary debasement is the key to preserving purchasing power in an era of endless money printing.*
