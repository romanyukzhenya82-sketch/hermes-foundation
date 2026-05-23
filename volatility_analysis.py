"""Volatility Analysis Module

Calculates historical, realized, and implied volatility.
Builds volatility cones and compares HV vs IV.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import logging
from exchange_prices import get_ohlcv_data

logger = logging.getLogger(__name__)

class VolatilityAnalysis:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {
            'default_window': 30,
            'annualization_factor': 365,
            'confidence_levels': [0.1, 0.25, 0.5, 0.75, 0.9]
        }
    
    def historical(self, symbol: str, window: int = 30, timeframe: str = '1d') -> float:
        """Calculate historical volatility (annualized)"""
        try:
            df = get_ohlcv_data(symbol, timeframe, limit=window + 10)
            returns = np.log(df['close'] / df['close'].shift(1))
            returns = returns.dropna()
            
            if len(returns) < window:
                logger.warning(f"Insufficient data for {symbol}")
                return 0.0
            
            vol = returns.std() * np.sqrt(self.config['annualization_factor'])
            return float(vol)
        except Exception as e:
            logger.error(f"Error calculating HV for {symbol}: {e}")
            return 0.0
    
    def realized(self, symbol: str, timeframe: str = '1d') -> Dict:
        """Calculate realized volatility metrics"""
        try:
            df = get_ohlcv_data(symbol, timeframe, limit=100)
            returns = np.log(df['close'] / df['close'].shift(1))
            
            # Daily realized vol
            rv_daily = returns.tail(1).std() * np.sqrt(365)
            # Weekly
            rv_weekly = returns.tail(7).std() * np.sqrt(52)
            # Monthly
            rv_monthly = returns.tail(30).std() * np.sqrt(12)
            # Parkinson estimator
            hl = np.log(df['high'] / df['low'])
            parkinson = np.sqrt(hl.tail(30).pow(2).mean() / (4 * np.log(2))) * np.sqrt(365)
            
            return {
                'rv_daily': float(rv_daily),
                'rv_weekly': float(rv_weekly),
                'rv_monthly': float(rv_monthly),
                'parkinson': float(parkinson)
            }
        except Exception as e:
            logger.error(f"Error calculating realized vol: {e}")
            return {'rv_daily': 0, 'rv_weekly': 0, 'rv_monthly': 0, 'parkinson': 0}
    
    def cone(self, symbol: str, windows: List[int] = [7, 14, 30, 60, 90]) -> Dict:
        """Generate volatility cone"""
        try:
            df = get_ohlcv_data(symbol, '1d', limit=max(windows) * 3)
            returns = np.log(df['close'] / df['close'].shift(1)).dropna()
            
            cone_data = {}
            for window in windows:
                rolling_vol = returns.rolling(window).std() * np.sqrt(365)
                percentiles = {}
                for level in self.config['confidence_levels']:
                    percentiles[f"p{int(level*100)}"] = float(rolling_vol.quantile(level))
                cone_data[window] = percentiles
            
            current_hv = self.historical(symbol, 30)
            return {'cone': cone_data, 'current_hv': current_hv}
        except Exception as e:
            logger.error(f"Error generating volatility cone: {e}")
            return {'cone': {}, 'current_hv': 0}

def calculate_historical_volatility(symbol: str, window: int = 30) -> float:
    """Quick HV calculation"""
    analyzer = VolatilityAnalysis()
    return analyzer.historical(symbol, window)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    print(f"HV: {calculate_historical_volatility('BTCUSDT', 30):.4f}")
