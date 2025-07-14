#!/usr/bin/env python3
"""
Test script to verify the monetary debasement dashboard functionality
"""
import pandas as pd
import sys
import os
import warnings
warnings.filterwarnings('ignore')

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_data_handler():
    """Test the data handler functionality."""
    print("🧪 Testing Data Handler...")
    
    try:
        from data_handler import get_research_data
        
        # Test data loading
        start_date = '2020-01-01'
        end_date = '2023-12-31'
        
        print(f"   Loading data from {start_date} to {end_date}")
        data = get_research_data(start_date, end_date)
        
        if data.empty:
            print("   ❌ No data loaded")
            return False
        
        print(f"   ✅ Loaded {len(data)} data points")
        print(f"   📊 Columns: {list(data.columns)}")
        
        # Check required columns
        required_columns = ['CPI', 'P']
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            print(f"   ❌ Missing required columns: {missing_columns}")
            return False
        
        print("   ✅ All required columns present")
        
        # Check data quality
        print(f"   📈 CPI range: {data['CPI'].min():.2f} to {data['CPI'].max():.2f}")
        print(f"   📈 P=MV/Q range: {data['P'].min():.2f} to {data['P'].max():.2f}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_real_returns_analyzer():
    """Test the real returns analyzer functionality."""
    print("\n🧪 Testing Real Returns Analyzer...")
    
    try:
        from real_returns_analyzer import RealReturnsAnalyzer
        
        analyzer = RealReturnsAnalyzer()
        
        print(f"   ✅ Analyzer initialized")
        print(f"   📊 Available assets: {len(analyzer.default_assets)}")
        
        # Test synthetic data creation for asset prices
        import numpy as np
        dates = pd.date_range('2020-01-01', '2023-12-31', freq='D')
        
        # Create synthetic asset data
        np.random.seed(42)
        asset_prices = pd.Series(
            100 * np.exp(np.random.normal(0.0005, 0.02, len(dates)).cumsum()),
            index=dates
        )
        
        # Create synthetic inflation data
        inflation_data = pd.Series(
            200 + np.random.normal(0, 1, len(dates)).cumsum(),
            index=dates
        )
        
        print(f"   🔄 Testing real returns calculation...")
        results = analyzer.calculate_real_returns(
            asset_prices, inflation_data, "Test Asset", "Test Inflation"
        )
        
        if results.empty:
            print("   ❌ No results from real returns calculation")
            return False
        
        print(f"   ✅ Real returns calculated successfully")
        print(f"   📊 Results shape: {results.shape}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_app_modules():
    """Test that all app modules can be imported."""
    print("\n🧪 Testing App Module Imports...")
    
    modules_to_test = [
        'data_handler',
        'real_returns_analyzer',
        'signal_detector',
        'cross_asset_analysis'
    ]
    
    success_count = 0
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"   ✅ {module_name}")
            success_count += 1
        except ImportError as e:
            print(f"   ❌ {module_name}: {e}")
        except Exception as e:
            print(f"   ⚠️ {module_name}: {e}")
    
    print(f"\n   📊 {success_count}/{len(modules_to_test)} modules imported successfully")
    return success_count == len(modules_to_test)

def main():
    """Run all tests."""
    print("🚀 Testing Monetary Debasement Dashboard")
    print("=" * 50)
    
    tests = [
        ("Data Handler", test_data_handler),
        ("Real Returns Analyzer", test_real_returns_analyzer),
        ("App Modules", test_app_modules)
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
    
    print("\n" + "=" * 50)
    print(f"📊 TEST SUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Dashboard is ready to use.")
        print("🌐 You can now access the dashboard at: http://localhost:8501")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
