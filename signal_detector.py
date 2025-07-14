"""
Market Signal Detection for Monetary Debasement
Real-time alerts and signal generation for debasement events
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class DebasementSignalDetector:
    """Detect and generate signals for monetary debasement events."""
    
    def __init__(self):
        self.signal_thresholds = {
            'inflation_spread_high': 0.02,     # 2% spread threshold
            'inflation_spread_low': -0.01,     # -1% spread threshold  
            'btc_momentum': 0.1,               # 10% momentum threshold
            'm2_acceleration': 0.05,           # 5% acceleration
            'velocity_decline': -0.02          # -2% velocity decline
        }
    
    def detect_inflation_divergence(self, data: pd.DataFrame) -> Dict[str, any]:
        """Detect when CPI and theoretical inflation diverge significantly."""
        signals = {
            'level': 'normal',
            'direction': 'neutral',
            'strength': 0.0,
            'description': '',
            'timestamp': None
        }
        
        if 'Inflation_Spread' not in data.columns:
            return signals
        
        spread = data['Inflation_Spread'].dropna()
        if len(spread) < 2:
            return signals
        
        current_spread = spread.iloc[-1]
        recent_trend = spread.tail(5).mean() if len(spread) >= 5 else current_spread
        
        # Detect high spread (actual inflation > theoretical)
        if current_spread > self.signal_thresholds['inflation_spread_high']:
            signals.update({
                'level': 'high',
                'direction': 'bearish',
                'strength': min(current_spread / self.signal_thresholds['inflation_spread_high'], 3.0),
                'description': f'Actual inflation {current_spread:.2%} above theoretical - potential overheating',
                'timestamp': spread.index[-1]
            })
        
        # Detect low/negative spread (theoretical > actual)
        elif current_spread < self.signal_thresholds['inflation_spread_low']:
            signals.update({
                'level': 'high',
                'direction': 'bullish', 
                'strength': min(abs(current_spread) / abs(self.signal_thresholds['inflation_spread_low']), 3.0),
                'description': f'Theoretical inflation {abs(current_spread):.2%} above actual - potential catch-up coming',
                'timestamp': spread.index[-1]
            })
        
        # Check trend acceleration
        if len(spread) >= 10:
            trend_acceleration = spread.tail(5).mean() - spread.head(-5).tail(5).mean()
            if abs(trend_acceleration) > 0.01:
                signals['description'] += f' | Trend accelerating {trend_acceleration:.2%}'
        
        return signals
    
    def detect_btc_momentum(self, data: pd.DataFrame) -> Dict[str, any]:
        """Detect Bitcoin momentum relative to debasement metrics."""
        signals = {
            'level': 'normal',
            'direction': 'neutral',
            'strength': 0.0, 
            'description': '',
            'timestamp': None
        }
        
        if 'BTC' not in data.columns:
            return signals
        
        btc = data['BTC'].dropna()
        if len(btc) < 10:
            return signals
        
        # Calculate momentum (5-day vs 20-day returns)
        short_window = min(5, len(btc) // 4)
        long_window = min(20, len(btc) // 2)
        
        if len(btc) >= long_window:
            short_return = (btc.iloc[-1] / btc.iloc[-short_window] - 1) if short_window > 0 else 0
            long_return = (btc.iloc[-1] / btc.iloc[-long_window] - 1) if long_window > 0 else 0
            
            momentum = short_return - long_return
            
            if abs(momentum) > self.signal_thresholds['btc_momentum']:
                direction = 'bullish' if momentum > 0 else 'bearish'
                signals.update({
                    'level': 'medium',
                    'direction': direction,
                    'strength': min(abs(momentum) / self.signal_thresholds['btc_momentum'], 2.5),
                    'description': f'BTC momentum: {momentum:.1%} ({direction} vs debasement baseline)',
                    'timestamp': btc.index[-1]
                })
        
        return signals
    
    def detect_money_supply_acceleration(self, data: pd.DataFrame) -> Dict[str, any]:
        """Detect acceleration in money supply growth."""
        signals = {
            'level': 'normal',
            'direction': 'neutral',
            'strength': 0.0,
            'description': '',
            'timestamp': None
        }
        
        if 'M2' not in data.columns:
            return signals
        
        m2 = data['M2'].dropna()
        if len(m2) < 20:
            return signals
        
        # Calculate growth rates
        growth_rates = m2.pct_change(periods=5).dropna()  # 5-period growth
        
        if len(growth_rates) >= 10:
            recent_growth = growth_rates.tail(5).mean()
            baseline_growth = growth_rates.head(-5).tail(10).mean()
            
            acceleration = recent_growth - baseline_growth
            
            if abs(acceleration) > self.signal_thresholds['m2_acceleration']:
                direction = 'bearish' if acceleration > 0 else 'bullish'
                signals.update({
                    'level': 'high' if abs(acceleration) > 0.1 else 'medium',
                    'direction': direction,
                    'strength': min(abs(acceleration) / self.signal_thresholds['m2_acceleration'], 3.0),
                    'description': f'M2 growth {"accelerating" if acceleration > 0 else "decelerating"}: {acceleration:.2%}',
                    'timestamp': growth_rates.index[-1]
                })
        
        return signals
    
    def generate_composite_signal(self, data: pd.DataFrame) -> Dict[str, any]:
        """Generate a composite signal from all individual signals."""
        
        # Collect all individual signals
        individual_signals = {
            'inflation_divergence': self.detect_inflation_divergence(data),
            'btc_momentum': self.detect_btc_momentum(data),
            'm2_acceleration': self.detect_money_supply_acceleration(data)
        }
        
        # Calculate composite score
        total_strength = 0
        bullish_signals = 0
        bearish_signals = 0
        active_signals = []
        
        for signal_name, signal in individual_signals.items():
            if signal['level'] != 'normal':
                strength = signal['strength']
                level_multiplier = {'medium': 1.0, 'high': 2.0}.get(signal['level'], 0.5)
                weighted_strength = strength * level_multiplier
                
                total_strength += weighted_strength
                active_signals.append(signal_name)
                
                if signal['direction'] == 'bullish':
                    bullish_signals += weighted_strength
                elif signal['direction'] == 'bearish':
                    bearish_signals += weighted_strength
        
        # Determine composite direction and level
        net_signal = bullish_signals - bearish_signals
        composite_direction = 'bullish' if net_signal > 0.5 else 'bearish' if net_signal < -0.5 else 'neutral'
        
        if total_strength > 3.0:
            composite_level = 'high'
        elif total_strength > 1.5:
            composite_level = 'medium'
        else:
            composite_level = 'normal'
        
        # Generate description
        if active_signals:
            description = f"Active signals: {', '.join(active_signals)} | Net: {composite_direction}"
        else:
            description = "No significant debasement signals detected"
        
        composite = {
            'level': composite_level,
            'direction': composite_direction,
            'strength': total_strength,
            'description': description,
            'individual_signals': individual_signals,
            'active_count': len(active_signals),
            'timestamp': data.index[-1] if not data.empty else None
        }
        
        return composite
    
    def get_trading_recommendations(self, composite_signal: Dict[str, any]) -> List[str]:
        """Generate trading recommendations based on composite signal."""
        recommendations = []
        
        level = composite_signal['level']
        direction = composite_signal['direction']
        strength = composite_signal['strength']
        
        if level == 'high' and strength > 2.0:
            if direction == 'bearish':
                recommendations.extend([
                    "🔴 High debasement risk detected",
                    "💰 Consider increasing BTC allocation",
                    "📊 Look for inflation-resistant assets",
                    "🛡️ Reduce exposure to duration risk",
                    "⚖️ Rebalance towards hard assets"
                ])
            elif direction == 'bullish':
                recommendations.extend([
                    "🟢 Debasement pressures easing",
                    "📉 Consider reducing hedge positions",
                    "💵 USD may strengthen temporarily",
                    "📊 Traditional assets may outperform",
                    "🔄 Rebalance back to base allocation"
                ])
        
        elif level == 'medium':
            recommendations.extend([
                "🟡 Moderate signals detected",
                "👀 Monitor key metrics closely",
                "⚖️ Maintain current hedge ratios",
                "📊 Prepare for potential regime change"
            ])
        
        else:
            recommendations.extend([
                "🟢 No significant debasement signals",
                "📈 Focus on base case allocation",
                "💼 Regular portfolio maintenance",
                "🔍 Continue monitoring for changes"
            ])
        
        return recommendations

def format_signal_for_display(signal: Dict[str, any]) -> str:
    """Format signal information for Streamlit display."""
    
    level_colors = {
        'normal': '🟢',
        'medium': '🟡', 
        'high': '🔴'
    }
    
    direction_arrows = {
        'bullish': '⬆️',
        'bearish': '⬇️',
        'neutral': '➡️'
    }
    
    level_icon = level_colors.get(signal['level'], '⚪')
    direction_icon = direction_arrows.get(signal['direction'], '❓')
    
    return f"{level_icon} {direction_icon} {signal['description']}"

if __name__ == "__main__":
    # Test the signal detector
    detector = DebasementSignalDetector()
    
    # Create test data
    dates = pd.date_range('2023-01-01', '2024-01-01', freq='D')
    test_data = pd.DataFrame({
        'CPI': np.cumsum(np.random.normal(0.01, 0.02, len(dates))) + 100,
        'P': np.cumsum(np.random.normal(0.015, 0.025, len(dates))) + 100,
        'BTC': np.exp(np.cumsum(np.random.normal(0.001, 0.05, len(dates)))),
        'M2': np.cumsum(np.random.normal(0.008, 0.01, len(dates))) + 1000
    }, index=dates)
    
    # Add inflation spread
    test_data['Inflation_Spread'] = (test_data['CPI'] / test_data['CPI'].iloc[0] - 1) - (test_data['P'] / test_data['P'].iloc[0] - 1)
    
    # Test signal detection
    composite = detector.generate_composite_signal(test_data)
    print(f"Composite Signal: {composite['level']} {composite['direction']}")
    print(f"Description: {composite['description']}")
    
    recommendations = detector.get_trading_recommendations(composite)
    print("\nRecommendations:")
    for rec in recommendations:
        print(f"  {rec}")
