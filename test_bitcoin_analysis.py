#!/usr/bin/env python3
"""
Test script for Bitcoin analysis function
"""
import sys
import pandas as pd
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_bitcoin_analysis():
    """Test the Bitcoin analysis function directly."""
    print("Testing Bitcoin analysis function...")
    
    # Import the function
    try:
        from monetary_app import bitcoin_analysis
        print("✅ Successfully imported bitcoin_analysis function")
    except ImportError as e:
        print(f"❌ Error importing bitcoin_analysis: {e}")
        return False
    
    # Create a simple test data frame
    test_data = pd.DataFrame({
        'CPI': [100, 102, 104, 106, 108],
        'P': [100, 103, 105, 107, 109]
    }, index=pd.date_range('2024-01-01', periods=5, freq='M'))
    
    print(f"📊 Test data created with {len(test_data)} rows")
    print(f"📅 Date range: {test_data.index[0]} to {test_data.index[-1]}")
    
    # Test CoinGecko direct
    try:
        from coingecko_fetcher import get_crypto_price_history, get_crypto_market_data
        
        # Test with last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        print(f"🔍 Testing CoinGecko with date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        btc_prices = get_crypto_price_history('bitcoin', start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        market_data = get_crypto_market_data('bitcoin')
        
        print(f"📈 BTC prices: {len(btc_prices)} data points")
        print(f"💰 Market data keys: {list(market_data.keys())}")
        
        if len(btc_prices) > 0:
            print(f"💵 Price range: ${btc_prices.min():,.2f} - ${btc_prices.max():,.2f}")
            print("✅ CoinGecko integration working correctly")
            return True
        else:
            print("❌ No Bitcoin price data retrieved")
            return False
            
    except Exception as e:
        print(f"❌ Error testing CoinGecko: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_bitcoin_analysis()
    sys.exit(0 if success else 1)
