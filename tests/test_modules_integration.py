#!/usr/bin/env python3
"""
Интеграционный тест модулей Hermes-Foundation с реальными данными Binance
Тестирует: market_regime.py, volatility_analysis.py, risk_metrics.py
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import ccxt
except ImportError:
    print("❌ Ошибка: библиотека ccxt не установлена")
    print("Установите: pip install ccxt")
    sys.exit(1)

print("=" * 80)
print("🧪 ИНТЕГРАЦИОННЫЙ ТЕСТ МОДУЛЕЙ HERMES-FOUNDATION")
print("=" * 80)
print(f"Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# ============================================================================
# 1. ПОЛУЧЕНИЕ ДАННЫХ С BINANCE
# ============================================================================

print("📊 1. Получение данных с Binance...")
print("-" * 80)

try:
    exchange = ccxt.binance({
        'enableRateLimit': True,
        'options': {'defaultType': 'future'}
    })
    
    symbol = 'BTC/USDT'
    timeframe = '1h'
    limit = 500
    
    print(f"Символ: {symbol}")
    print(f"Таймфрейм: {timeframe}")
    print(f"Кол-во баров: {limit}")
    print()
    
    # Загрузка данных
    print("⏳ Загрузка OHLCV данных...")
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    
    # Конвертация в DataFrame
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    
    print(f"✅ Данные загружены: {len(df)} баров")
    print(f"Период: {df.index[0]} - {df.index[-1]}")
    print(f"Последняя цена: ${df['close'].iloc[-1]:,.2f}")
    print()
    
except Exception as e:
    print(f"❌ Ошибка загрузки данных: {e}")
    sys.exit(1)

# ============================================================================
# 2. ТЕСТИРОВАНИЕ MARKET REGIME DETECTION
# ============================================================================

print("🎯 2. Тестирование Market Regime Detection...")
print("-" * 80)

try:
    # Импорт модуля
    sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'analysis'))
    from market_regime import MarketRegimeDetector
    
    # Инициализация детектора
    detector = MarketRegimeDetector(
        lookback_period=100,
        adx_threshold=25,
        volatility_window=20
    )
    
    print("⏳ Анализ рыночного режима...")
    result = detector.detect(df)
    
    print(f"✅ Текущий режим: {result.regime}")
    print(f"Уверенность: {result.confidence:.2%}")
    print(f"ADX: {result.indicators.get('adx', 0):.2f}")
    print(f"ATR: {result.indicators.get('atr', 0):.2f}")
    print(f"Trend Slope: {result.indicators.get('trend_slope', 0):.4f}")
    print()
    
    # Статистика по режимам за весь период
    print("📊 Статистика режимов за весь период:")
    regimes_history = []
    for i in range(100, len(df)):
        window = df.iloc[i-100:i]
        r = detector.detect(window)
        regimes_history.append(r.regime)
    
    regime_counts = pd.Series(regimes_history).value_counts()
    for regime, count in regime_counts.items():
        pct = (count / len(regimes_history)) * 100
        print(f"  {regime}: {count} ({pct:.1f}%)")
    print()
    
    test_market_regime = True
    
except Exception as e:
    print(f"❌ Ошибка Market Regime Detection: {e}")
    import traceback
    traceback.print_exc()
    test_market_regime = False
    print()

# ============================================================================
# 3. ТЕСТИРОВАНИЕ VOLATILITY ANALYSIS
# ============================================================================

print("📈 3. Тестирование Volatility Analysis...")
print("-" * 80)

try:
    from volatility_analysis import VolatilityAnalyzer
    
    # Инициализация анализатора
    analyzer = VolatilityAnalyzer(
        window_size=20,
        annualization_factor=252
    )
    
    print("⏳ Анализ волатильности...")
    vol_result = analyzer.analyze(df)
    
    print(f"✅ Текущая волатильность: {vol_result.current_volatility:.2%}")
    print(f"Историческая волатильность (20): {vol_result.historical_volatility:.2%}")
    print(f"Реализованная волатильность: {vol_result.realized_volatility:.2%}")
    print(f"Годовая волатильность: {vol_result.annualized_volatility:.2%}")
    print(f"ATR: ${vol_result.atr:.2f}")
    print(f"ATR %: {vol_result.atr_percent:.2%}")
    print()
    
    # Статистика волатильности
    print("📊 Статистика волатильности:")
    print(f"  Минимум: {vol_result.volatility_percentile['min']:.2%}")
    print(f"  25-й процентиль: {vol_result.volatility_percentile['p25']:.2%}")
    print(f"  Медиана: {vol_result.volatility_percentile['median']:.2%}")
    print(f"  75-й процентиль: {vol_result.volatility_percentile['p75']:.2%}")
    print(f"  Максимум: {vol_result.volatility_percentile['max']:.2%}")
    print()
    
    test_volatility = True
    
except Exception as e:
    print(f"❌ Ошибка Volatility Analysis: {e}")
    import traceback
    traceback.print_exc()
    test_volatility = False
    print()

# ============================================================================
# 4. ТЕСТИРОВАНИЕ RISK METRICS
# ============================================================================

print("⚠️ 4. Тестирование Risk Metrics...")
print("-" * 80)

try:
    from risk_metrics import RiskMetricsCalculator
    
    # Инициализация калькулятора
    calculator = RiskMetricsCalculator(
        confidence_level=0.95,
        risk_free_rate=0.0
    )
    
    print("⏳ Расчет метрик риска...")
    
    # Рассчитываем доходности
    returns = df['close'].pct_change().dropna()
    
    risk_result = calculator.calculate(returns, df['close'])
    
    print(f"✅ Sharpe Ratio: {risk_result.sharpe_ratio:.3f}")
    print(f"Sortino Ratio: {risk_result.sortino_ratio:.3f}")
    print(f"Max Drawdown: {risk_result.max_drawdown:.2%}")
    print(f"VaR (95%): {risk_result.value_at_risk:.2%}")
    print(f"CVaR (95%): {risk_result.conditional_var:.2%}")
    print(f"Calmar Ratio: {risk_result.calmar_ratio:.3f}")
    print()
    
    # Дополнительная статистика
    print("📊 Статистика доходности:")
    print(f"  Средняя: {returns.mean():.4%}")
    print(f"  Медиана: {returns.median():.4%}")
    print(f"  Стандартное отклонение: {returns.std():.4%}")
    print(f"  Асимметрия: {returns.skew():.3f}")
    print(f"  Эксцесс: {returns.kurtosis():.3f}")
    print()
    
    test_risk_metrics = True
    
except Exception as e:
    print(f"❌ Ошибка Risk Metrics: {e}")
    import traceback
    traceback.print_exc()
    test_risk_metrics = False
    print()

# ============================================================================
# 5. КОМПЛЕКСНЫЙ АНАЛИЗ
# ============================================================================

print("🔄 5. Комплексный анализ (интеграция всех модулей)...")
print("-" * 80)

if test_market_regime and test_volatility and test_risk_metrics:
    print("✅ Все модули работают корректно!")
    print()
    
    print("📋 SUMMARY REPORT:")
    print("-" * 80)
    print(f"Актив: {symbol}")
    print(f"Текущая цена: ${df['close'].iloc[-1]:,.2f}")
    print()
    
    print(f"🎯 Рыночный режим: {result.regime} (уверенность: {result.confidence:.1%})")
    print(f"📈 Волатильность: {vol_result.current_volatility:.2%} (годовая: {vol_result.annualized_volatility:.2%})")
    print(f"⚠️  Sharpe Ratio: {risk_result.sharpe_ratio:.2f}")
    print(f"📉 Max Drawdown: {risk_result.max_drawdown:.2%}")
    print(f"🎲 VaR (95%): {risk_result.value_at_risk:.2%}")
    print()
    
    # Торговые рекомендации на основе анализа
    print("💡 Торговые рекомендации:")
    print("-" * 80)
    
    if result.regime == 'BULLISH_TREND' and result.confidence > 0.7:
        print("✅ Бычий тренд подтвержден - рассмотрите лонг позиции")
        print(f"   Рекомендуемый размер позиции: умеренный (волатильность: {vol_result.current_volatility:.1%})")
    elif result.regime == 'BEARISH_TREND' and result.confidence > 0.7:
        print("⚠️  Медвежий тренд - будьте осторожны с лонг позициями")
        print("   Рассмотрите шорт стратегии или выход в кэш")
    elif result.regime == 'RANGING':
        print("📊 Рынок в боковике - используйте стратегии mean-reversion")
        print("   Торгуйте от уровней поддержки/сопротивления")
    elif result.regime == 'HIGH_VOLATILITY':
        print("🔥 Высокая волатильность - снизьте размер позиций!")
        print(f"   Текущая волатильность: {vol_result.current_volatility:.1%} (выше нормы)")
        print("   Используйте более широкие стоп-лоссы")
    else:
        print("😴 Низкая волатильность - ожидайте пробой")
        print("   Подготовьтесь к увеличению активности")
    
    print()
    
    # Оценка риска
    if risk_result.sharpe_ratio > 1.5:
        risk_assessment = "Отличное"
    elif risk_result.sharpe_ratio > 1.0:
        risk_assessment = "Хорошее"
    elif risk_result.sharpe_ratio > 0.5:
        risk_assessment = "Умеренное"
    else:
        risk_assessment = "Плохое"
    
    print(f"📊 Соотношение риск/доходность: {risk_assessment}")
    print(f"   (Sharpe Ratio: {risk_result.sharpe_ratio:.2f})")
    print()
    
else:
    print("⚠️  Не все модули прошли тестирование:")
    print(f"   Market Regime: {'✅' if test_market_regime else '❌'}")
    print(f"   Volatility Analysis: {'✅' if test_volatility else '❌'}")
    print(f"   Risk Metrics: {'✅' if test_risk_metrics else '❌'}")
    print()

# ============================================================================
# 6. РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ
# ============================================================================

print("=" * 80)
print("📋 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
print("=" * 80)

tests_passed = sum([test_market_regime, test_volatility, test_risk_metrics])
tests_total = 3

print(f"Тестов пройдено: {tests_passed}/{tests_total}")
print(f"Успешность: {(tests_passed/tests_total)*100:.0f}%")
print()

if tests_passed == tests_total:
    print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    print("✅ Модули готовы к интеграции")
else:
    print("⚠️  НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
    print("Проверьте ошибки выше")

print()
print(f"Время завершения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)
