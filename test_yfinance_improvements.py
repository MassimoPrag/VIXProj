#!/usr/bin/env python3
"""
Test the improved yfinance rate limiting strategies
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_yfinance_optimizer():
    """Test the new yfinance optimizer."""
    print("🧪 Testing YFinance Optimizer...")
    
    try:
        from yfinance_optimizer import fetch_symbols_optimized, get_rate_limit_status
        
        # Test symbols
        symbols = ['SPY', 'QQQ', 'AAPL']
        start_date = '2023-01-01'
        end_date = '2023-12-31'
        
        print(f"   🔄 Fetching data for {symbols}")
        print(f"   📅 Period: {start_date} to {end_date}")
        
        # Fetch data
        data = fetch_symbols_optimized(symbols, start_date, end_date)
        
        if data:
            print(f"   ✅ Successfully fetched data for {len(data)} symbols")
            for symbol, series in data.items():
                print(f"   📊 {symbol}: {len(series)} data points")
        else:
            print("   ❌ No data fetched")
            return False
        
        # Check rate limit status
        status = get_rate_limit_status()
        print(f"   📈 Rate limit status: {status}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_real_returns_with_optimizer():
    """Test real returns analyzer with optimizer."""
    print("\n🧪 Testing Real Returns with Optimizer...")
    
    try:
        from real_returns_analyzer import RealReturnsAnalyzer
        
        analyzer = RealReturnsAnalyzer()
        
        # Test with small set of symbols
        symbols = ['SPY', 'QQQ']
        start_date = '2023-01-01'
        end_date = '2023-12-31'
        
        print(f"   🔄 Testing analyzer with {symbols}")
        asset_data = analyzer.fetch_asset_data(symbols, start_date, end_date)
        
        if asset_data:
            print(f"   ✅ Analyzer successfully fetched {len(asset_data)} assets")
            for symbol, data in asset_data.items():
                print(f"   📊 {symbol}: {len(data)} data points")
        else:
            print("   ❌ No asset data returned")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_data_handler_with_optimizer():
    """Test data handler with optimizer."""
    print("\n🧪 Testing Data Handler with Optimizer...")
    
    try:
        from data_handler import get_asset_data
        
        symbols = ['BTC-USD', 'GLD']
        start_date = '2023-01-01'
        end_date = '2023-12-31'
        
        print(f"   🔄 Testing data handler with {symbols}")
        asset_data = get_asset_data(symbols, start_date, end_date)
        
        if asset_data:
            print(f"   ✅ Data handler successfully fetched {len(asset_data)} assets")
            for symbol, data in asset_data.items():
                print(f"   📊 {symbol}: {len(data)} data points")
        else:
            print("   ❌ No asset data returned")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Run all optimizer tests."""
    print("🚀 Testing YFinance Rate Limiting Improvements")
    print("=" * 60)
    
    tests = [
        ("YFinance Optimizer", test_yfinance_optimizer),
        ("Real Returns with Optimizer", test_real_returns_with_optimizer),
        ("Data Handler with Optimizer", test_data_handler_with_optimizer)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✅ {test_name} - PASSED")
            else:
                print(f"\n❌ {test_name} - FAILED")
        except Exception as e:
            print(f"\n💥 {test_name} - ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 TEST SUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All rate limiting improvements are working!")
        print("📈 YFinance should now be more reliable with better rate limiting")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
