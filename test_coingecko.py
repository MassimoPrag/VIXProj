#!/usr/bin/env python3
"""
Test CoinGecko Bitcoin data fetching
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_coingecko_fetcher():
    """Test CoinGecko data fetching."""
    print("🧪 Testing CoinGecko Bitcoin Data Fetching...")
    
    try:
        from coingecko_fetcher import get_crypto_price_history, get_crypto_market_data
        
        # Test Bitcoin price history
        print("   🔄 Fetching Bitcoin price history...")
        
        # Enable debug logging
        import logging
        logging.basicConfig(level=logging.DEBUG)
        
        btc_prices = get_crypto_price_history('bitcoin', '2023-01-01', '2023-12-31')
        
        if not btc_prices.empty:
            print(f"   ✅ Successfully fetched {len(btc_prices)} Bitcoin price points")
            print(f"   📊 Price range: ${btc_prices.min():,.2f} - ${btc_prices.max():,.2f}")
            print(f"   📅 Date range: {btc_prices.index[0].date()} to {btc_prices.index[-1].date()}")
        else:
            print("   ❌ No Bitcoin price data fetched")
            
            # Try a simpler test
            print("   🔄 Trying direct API test...")
            from pycoingecko import CoinGeckoAPI
            cg = CoinGeckoAPI()
            
            # Test 30 days
            data = cg.get_coin_market_chart_by_id(id='bitcoin', vs_currency='usd', days=30)
            if 'prices' in data:
                print(f"   ✅ Direct API returned {len(data['prices'])} price points")
            else:
                print("   ❌ Direct API failed")
            
            return False
        
        # Test current market data
        print("\n   🔄 Fetching Bitcoin market data...")
        market_data = get_crypto_market_data('bitcoin')
        
        if market_data:
            print(f"   ✅ Successfully fetched market data")
            print(f"   💰 Current price: ${market_data.get('current_price', 'N/A'):,.2f}")
            print(f"   📈 24h change: {market_data.get('price_change_percentage_24h', 'N/A'):.2f}%")
            print(f"   🏆 All-time high: ${market_data.get('ath', 'N/A'):,.2f}")
        else:
            print("   ⚠️ No market data fetched (may be rate limited)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run CoinGecko test."""
    print("🚀 Testing CoinGecko Integration for Bitcoin Analysis")
    print("=" * 60)
    
    success = test_coingecko_fetcher()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 CoinGecko integration is working!")
        print("📈 Bitcoin analysis page should now have reliable data")
    else:
        print("❌ CoinGecko integration failed")
        print("💡 Check your internet connection and try again")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
