# 🚀 Monetary Debasement Dashboard - Deployment Guide

## 📋 Overview

This Streamlit application analyzes monetary debasement through CPI vs P=MV/Q analysis, real returns calculation, and Bitcoin correlation analysis. The app uses only **free APIs with no API keys required**, making deployment straightforward.

## 🔧 APIs Used (All Free, No Keys Required)

- **FRED (Federal Reserve)**: Economic data via pandas_datareader
- **Yahoo Finance**: Stock/ETF prices via yfinance
- **CoinGecko**: Bitcoin data via pycoingecko (free tier)

## 🌐 Deployment Options

### Option 1: Streamlit Community Cloud (Recommended)

**✅ Pros**: Free, easy, automatic deployments from GitHub
**❌ Cons**: Public repository required, some resource limits

#### Steps:

1. **Prepare Repository**:
```bash
# Create a new GitHub repository
git init
git add .
git commit -m "Initial commit: Monetary Debasement Dashboard"
git branch -M main
git remote add origin https://github.com/yourusername/monetary-debasement-dashboard.git
git push -u origin main
```

2. **Deploy to Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your repository
   - Set main file: `monetary_app.py`
   - Click "Deploy"

3. **Configuration** (if needed):
   - No environment variables required
   - All APIs are free and don't need keys

#### Repository Structure for Streamlit Cloud:
```
├── monetary_app.py          # Main Streamlit app
├── requirements.txt         # Python dependencies
├── data_handler.py         # Data fetching logic
├── real_returns_analyzer.py # Real returns calculations
├── yfinance_optimizer.py   # Optimized Yahoo Finance fetching
├── coingecko_fetcher.py    # Bitcoin data fetching
├── signal_detector.py      # Signal detection logic
├── helpingfunctions.py     # Utility functions
└── README.md              # Project documentation
```

### Option 2: Heroku

**✅ Pros**: More control, custom domain support
**❌ Cons**: No free tier anymore, requires credit card

#### Files needed for Heroku:

1. **Procfile**:
```
web: streamlit run monetary_app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
```

2. **runtime.txt**:
```
python-3.11.0
```

3. **Deploy**:
```bash
# Install Heroku CLI
brew install heroku/brew/heroku  # macOS
# or download from heroku.com

# Login and create app
heroku login
heroku create your-app-name

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

### Option 3: Railway

**✅ Pros**: Simple deployment, generous free tier
**❌ Cons**: Newer platform

#### Steps:
1. Connect GitHub to [Railway](https://railway.app)
2. Import your repository
3. Railway auto-detects Streamlit
4. Add start command: `streamlit run monetary_app.py --server.port=$PORT --server.address=0.0.0.0`

### Option 4: Render

**✅ Pros**: Free tier available, easy setup
**❌ Cons**: Cold starts on free tier

#### Build Command:
```bash
pip install -r requirements.txt
```

#### Start Command:
```bash
streamlit run monetary_app.py --server.port=$PORT --server.address=0.0.0.0
```

### Option 5: DigitalOcean App Platform

**✅ Pros**: Professional hosting, scalable
**❌ Cons**: Not free, more complex

## 📦 Pre-Deployment Checklist

### 1. **Optimize requirements.txt**:
```txt
streamlit>=1.28.0
pandas>=1.5.0,<2.0.0
numpy>=1.24.0
plotly>=5.15.0
yfinance>=0.2.18
pandas-datareader==0.10.0
pycoingecko>=3.1.0
requests>=2.31.0
setuptools>=65.0.0
fredapi>=0.5.0
```

**Note**: `setuptools` and `fredapi` are included to fix the "No module named 'distutils'" error that can occur with FRED data fetching in Python 3.12+.

### 2. **Add Error Handling**:
Your app already has good error handling with synthetic data fallbacks.

### 3. **Performance Optimizations**:
- ✅ Data caching implemented
- ✅ Rate limiting for APIs
- ✅ Synthetic data fallbacks

### 4. **Security Considerations**:
- ✅ No API keys to secure
- ✅ No sensitive data stored
- ✅ Uses only public APIs

## 🔒 API Rate Limiting & Best Practices

### Yahoo Finance (yfinance)
- **Rate Limit**: ~100 requests/hour per IP
- **Your Implementation**: ✅ Built-in rate limiting
- **Fallback**: ✅ Synthetic data generation

### CoinGecko Free Tier
- **Rate Limit**: 50 calls/minute
- **Your Implementation**: ✅ Caching implemented
- **Fallback**: ✅ Error handling with user feedback

### FRED (pandas_datareader)
- **Rate Limit**: Very generous, rarely hit
- **Your Implementation**: ✅ Caching and error handling
- **Fallback**: ✅ Synthetic data generation

## 🚀 Quick Deploy to Streamlit Cloud

### Step-by-Step:

1. **Create GitHub Repository**:
```bash
cd /Users/massimoprag/Downloads/FinResearch/VIXProj
git init
git add .
git commit -m "Monetary Debasement Dashboard"
```

2. **Push to GitHub**:
```bash
# Create repository on github.com first, then:
git remote add origin https://github.com/yourusername/monetary-debasement-dashboard.git
git branch -M main
git push -u origin main
```

3. **Deploy to Streamlit**:
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Connect GitHub
   - Select repository: `monetary-debasement-dashboard`
   - Main file path: `monetary_app.py`
   - Click "Deploy!"

4. **Access Your App**:
   - URL: `https://yourusername-monetary-debasement-dashboard.streamlit.app`
   - Updates automatically when you push to GitHub

## 🔧 Environment Variables (Optional)

Even though no API keys are required, you might want to set optional configurations:

```bash
# Optional: Disable debug mode in production
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

## 📊 Monitoring & Analytics

### Built-in Monitoring:
- Streamlit provides basic usage analytics
- Error logs available in deployment dashboard

### Optional Analytics:
```python
# Add to monetary_app.py if desired
import streamlit as st

# Simple usage tracking
if 'page_views' not in st.session_state:
    st.session_state.page_views = 0
st.session_state.page_views += 1
```

## 🐛 Troubleshooting Common Issues

### 1. **Module Import Errors**:
- Ensure all files are in repository root
- Check `requirements.txt` includes all dependencies

### 2. **"No module named 'distutils'" Error**:
- **Problem**: FRED data fetching fails with distutils error
- **Solution**: The updated `requirements.txt` includes `setuptools>=65.0.0` and `fredapi>=0.5.0`
- **Symptoms**: CPI vs P=MV/Q charts show only synthetic data
- **Fix**: Redeploy with the updated requirements.txt

### 3. **API Rate Limiting**:
- Your app handles this gracefully with synthetic data
- Consider adding user feedback for rate limit status

### 3. **Memory Issues**:
- Streamlit Cloud: 1GB RAM limit
- Use `@st.cache_data` for expensive operations (already implemented)

### 4. **Slow Loading**:
- Cold starts are normal on free tiers
- Consider paid hosting for better performance

## Troubleshooting Deployment Issues

### Common Build Errors

#### 1. "Could not build wheels for pandas" Error

If you encounter the error `ERROR: Could not build wheels for pandas`, try these solutions:

**Solution 1: Use the main requirements.txt**
The current `requirements.txt` uses tested, compatible versions:
- pandas==2.0.3
- numpy==1.24.3  
- Python 3.9.18 (specified in runtime.txt)

**Solution 2: Use fallback requirements**
If the main requirements still fail, rename `requirements-fallback.txt` to `requirements.txt`:
```bash
mv requirements.txt requirements-main.txt
mv requirements-fallback.txt requirements.txt
```

**Solution 3: Check system dependencies**
The `packages.txt` file includes necessary build tools:
- build-essential
- gcc, g++
- python3-dev
- libatlas-base-dev

#### 2. Memory or Timeout Issues
- Streamlit Community Cloud has resource limits
- Consider reducing the number of assets analyzed simultaneously
- The app includes optimized data fetching to minimize API calls

#### 3. FRED API Issues
- FRED data fetching has multiple fallback methods
- No API key required for public data
- If FRED fails, the app shows clear error messages instead of synthetic data

## 🚨 Emergency Deployment Fixes

### If the installer still returns non-zero exit code:

#### Option 1: Use Minimal Requirements
Copy the contents of `requirements-minimal.txt` to `requirements.txt`:
```bash
streamlit==1.28.1
pandas==1.5.3
numpy==1.21.6
plotly==5.11.0
yfinance==0.2.18
requests==2.28.2
fredapi==0.5.0
```

#### Option 2: Remove packages.txt entirely
Delete the `packages.txt` file if system dependencies are causing issues.

#### Option 3: Use even older pandas
Update requirements.txt to use pandas==1.3.5:
```
streamlit==1.28.1
pandas==1.3.5
numpy==1.21.6
plotly==5.11.0
yfinance==0.2.18
requests==2.28.2
fredapi==0.5.0
```

#### Option 4: Alternative Python version
Try Python 3.8.18 in runtime.txt:
```
python-3.8.18
```
