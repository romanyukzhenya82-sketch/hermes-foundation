"""Risk Metrics Module

Calculates portfolio risk metrics: VaR, CVaR, Sharpe, Sortino, Max Drawdown, Beta.
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional
import logging
from exchange_prices import get_ohlcv_data

logger = logging.getLogger(__name__)

class RiskMetrics:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {
            'var_confidence': 0.95,
            'risk_free_rate': 0.05
        }
    
    def var(self, returns: pd.Series, confidence: float = 0.95) -> float:
        """Value at Risk - worst expected loss at confidence level"""
        if len(returns) < 10:
            return 0.0
        return float(np.percentile(returns, (1 - confidence) * 100))
    
    def cvar(self, returns: pd.Series, confidence: float = 0.95) -> float:
        """Conditional VaR (Expected Shortfall) - average loss beyond VaR"""
        var_threshold = self.var(returns, confidence)
        losses = returns[returns <= var_threshold]
        return float(losses.mean()) if len(losses) > 0 else 0.0
    
    def sharpe_ratio(self, returns: pd.Series, risk_free: float = 0.05) -> float:
        """Sharpe Ratio - risk-adjusted return"""
        excess_returns = returns - (risk_free / 252)  # Daily risk-free
        if excess_returns.std() == 0:
            return 0.0
        return float((excess_returns.mean() / excess_returns.std()) * np.sqrt(252))
    
    def sortino_ratio(self, returns: pd.Series, target: float = 0.0) -> float:
        """Sortino Ratio - downside risk-adjusted return"""
        excess = returns - target
        downside = excess[excess < 0]
        if len(downside) == 0 or downside.std() == 0:
            return 0.0
        return float((excess.mean() / downside.std()) * np.sqrt(252))
    
    def max_drawdown(self, equity_curve: pd.Series) -> Dict:
        """Maximum Drawdown analysis"""
        cummax = equity_curve.cummax()
        drawdown = (equity_curve - cummax) / cummax
        max_dd = float(drawdown.min())
        
        # Find drawdown duration
        dd_start = drawdown[drawdown == max_dd].index[0] if max_dd < 0 else None
        recovery = equity_curve[equity_curve >= cummax.loc[dd_start]].index[0] if dd_start and len(equity_curve[equity_curve >= cummax.loc[dd_start]]) > 0 else None
        duration = (recovery - dd_start).days if dd_start and recovery else 0
        
        return {
            'max_dd': max_dd,
            'duration_days': duration,
            'recovery_time': recovery
        }
    
    def beta(self, asset_returns: pd.Series, market_returns: pd.Series) -> float:
        """Beta coefficient - systematic risk vs market"""
        if len(asset_returns) != len(market_returns) or market_returns.std() == 0:
            return 0.0
        covariance = np.cov(asset_returns, market_returns)[0][1]
        market_variance = market_returns.var()
        return float(covariance / market_variance) if market_variance != 0 else 0.0
    
    def calculate_all(self, symbol: str, timeframe: str = '1d', period: int = 90) -> Dict:
        """Calculate all risk metrics for a symbol"""
        try:
            df = get_ohlcv_data(symbol, timeframe, limit=period)
            returns = np.log(df['close'] / df['close'].shift(1)).dropna()
            equity = (1 + returns).cumprod()
            
            return {
                'var_95': self.var(returns, 0.95),
                'cvar_95': self.cvar(returns, 0.95),
                'sharpe': self.sharpe_ratio(returns),
                'sortino': self.sortino_ratio(returns),
                'max_dd': self.max_drawdown(equity)['max_dd'],
                'volatility': float(returns.std() * np.sqrt(252))
            }
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {e}")
            return {'var_95': 0, 'cvar_95': 0, 'sharpe': 0, 'sortino': 0, 'max_dd': 0, 'volatility': 0}

def calculate_sharpe(returns: pd.Series, rf: float = 0.05) -> float:
    """Quick Sharpe Ratio"""
    rm = RiskMetrics()
    return rm.sharpe_ratio(returns, rf)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    rm = RiskMetrics()
    metrics = rm.calculate_all('BTCUSDT', '1d', 90)
    print(f"VaR (95%): {metrics['var_95']:.4f}")
    print(f"CVaR (95%): {metrics['cvar_95']:.4f}")
    print(f"Sharpe: {metrics['sharpe']:.2f}")
    print(f"Sortino: {metrics['sortino']:.2f}")
    print(f"Max DD: {metrics['max_dd']:.2%}")
