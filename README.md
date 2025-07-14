# 💰 Monetary Debasement Research Dashboard

A comprehensive Streamlit dashboard analyzing the relationship between monetary expansion, inflation, and asset performance.

## 🎯 Features

- **CPI vs P=MV/Q Analysis**: Compare observed inflation vs quantity theory predictions
- **Real Returns Analysis**: Multi-asset performance adjusted for inflation
- **Bitcoin Analysis**: Bitcoin as a monetary debasement hedge
- **Signal Detection**: Automated detection of monetary debasement events
- **Interactive Visualizations**: Professional charts with Plotly

## 📊 Data Sources

- **FRED (Federal Reserve)**: CPI, M2 Money Supply, GDP, Velocity
- **Yahoo Finance**: Asset prices (stocks, ETFs, Bitcoin, commodities)
- **CoinGecko**: Bitcoin market data

*All APIs are free and require no API keys!*

## 🚀 Quick Start

### Local Development
```bash
pip install -r requirements.txt
streamlit run monetary_app.py
```

### Live Demo
[View the deployed dashboard →](https://your-app-url.streamlit.app)

## 🧠 Research Thesis

This dashboard explores how **monetary debasement** - the deliberate weakening of currency through money supply expansion - creates systematic distortions that can be measured and traded.

### Key Hypotheses:
- Monetary expansion creates measurable price distortions
- These distortions can be detected by comparing CPI vs P=MV/Q
- Asset prices reflect monetary distortions over time
- Bitcoin and other assets serve as hedges against debasement

## 📈 Dashboard Sections

### 1. 🏠 Main Dashboard
- Core monetary debasement analysis
- Standardized spread analysis
- Real-time signal detection
- Key economic metrics

### 2. ₿ Bitcoin Analysis
- Bitcoin price and performance tracking
- Correlation with monetary metrics
- Market data from CoinGecko
- Performance during different regimes

### 3. 📊 Real Returns Analysis
- Multi-asset selection (SPY, QQQ, VOO, BTC, etc.)
- CPI and P=MV/Q inflation adjustments
- Performance comparison tables
- Inflation drag analysis

### 4. 📄 Research & Methodology
- Theoretical framework explanation
- Data sources and calculations
- Research notes and observations

## 🔧 Technical Features

- **Robust Data Pipeline**: Multiple APIs with fallback strategies
- **Error Handling**: Graceful failures with synthetic data
- **Caching**: Optimized performance with data caching
- **Rate Limiting**: Respectful API usage
- **Responsive Design**: Works on desktop and mobile

## 📚 Educational Value

- **Monetary Theory**: Practical application of quantity theory of money
- **Real Returns**: Understanding purchasing power vs nominal returns
- **Signal Detection**: Identifying monetary regime changes
- **Financial Analysis**: Professional-grade metrics and visualizations

## 🛠 Development

### Project Structure
```
├── monetary_app.py          # Main Streamlit application
├── data_handler.py         # Data fetching and processing
├── real_returns_analyzer.py # Real returns calculations
├── yfinance_optimizer.py   # Optimized Yahoo Finance API
├── coingecko_fetcher.py    # Bitcoin data from CoinGecko
├── signal_detector.py      # Signal detection algorithms
└── helpingfunctions.py     # Utility functions
```

### Key Dependencies
- **Streamlit**: Web application framework
- **Pandas/NumPy**: Data manipulation
- **Plotly**: Interactive visualizations
- **yfinance**: Yahoo Finance API
- **pandas-datareader**: FRED API access
- **pycoingecko**: CoinGecko API

## 📊 Performance

- **Live Data**: Real-time fetching from multiple APIs
- **Fallback Systems**: Synthetic data when APIs are unavailable
- **Caching**: Optimized loading times
- **Error Recovery**: Robust error handling

## 🎯 Use Cases

### Investment Analysis
- Asset allocation for inflation protection
- Timing decisions based on monetary signals
- Risk assessment with real volatility measures

### Academic Research
- Testing quantity theory of money
- Analyzing monetary policy effectiveness
- Studying asset price relationships

### Policy Analysis
- Understanding monetary expansion effects
- Inflation targeting effectiveness
- Early warning system for monetary distortions

## 🚀 Deployment

This application is designed for easy deployment:
- ✅ No API keys required
- ✅ All dependencies in requirements.txt
- ✅ Streamlit Cloud ready
- ✅ Heroku compatible
- ✅ Docker support available

## 📖 Documentation

- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Complete deployment instructions
- [User Guide](USER_GUIDE.md) - How to use the dashboard
- [Project Summary](PROJECT_SUMMARY.md) - Technical overview

## 🤝 Contributing

This project is designed to be educational and extensible. Feel free to:
- Add new assets to the analysis
- Implement additional monetary indicators
- Enhance visualizations
- Improve signal detection algorithms

## ⚠️ Disclaimer

This dashboard is for educational and research purposes only. It is not financial advice. Past performance does not guarantee future results. Always consult with qualified financial professionals before making investment decisions.

---

**Understanding monetary debasement is the key to preserving purchasing power in an era of endless money printing.**
