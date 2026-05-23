# MODULE: ORDER FLOW ANALYZER
# Version: 1.0.0 | 2026-05-23
# Hermes Foundation — Анализ ордерфлоу для скальпинга

## НАЗНАЧЕНИЕ
Отслеживание реального ордерфлоу: Delta (buy aggression - sell aggression),
CVD (cumulative volume delta), imbalance на bid/ask, footprint-структура свечей.
Ключевой модуль для scalp-режима.

## КОГДА АКТИВИРОВАТЬ
- В scalp режиме (каждый сигнал)
- На критических уровнях (support/resistance)
- При high vol_spike (> 1.5)
- При London/NY overlap

---

## ПРОТОКОЛ: АНАЛИЗ ОРДЕРФЛОУ

### 1. DELTA ANALYSIS (per candle)
```
Delta = buy_volume - sell_volume
Delta_normalized = Delta / total_volume
```
**Интерпретация:**
- Delta > +0.6 → сильный buy pressure, вероятность LONG возрастает
- Delta < -0.6 → сильный sell pressure, SHORT
- Delta −00 на резком движении вверх → bearish divergence (ловушка быков)

### 2. CVD (Cumulative Volume Delta)
```
CVD = sum(Delta) over lookback_period (default: 20 candles)
```
**Сигналы:**
- CVD rising + price rising → подтверждённый тренд
- CVD falling + price rising → bearish divergence, разворотная точка
- CVD flat на breakout → ложный пробой, не входить

### 3. BID/ASK IMBALANCE
```
imbalance_ratio = bid_volume / ask_volume
```
- ratio > 1.5 → strong bid support, вероятность отскока вверх
- ratio < 0.67 → strong ask resistance, вероятность отскока вниз
- ratio −1.0 → balanced, нейтральная зона

### 4. ABSORPTION DETECTION
```
Определяется когда:
  - Большой объём (top 10% за сессию)
  - Малый range (цена не изменилась > 0.2% ATR)
  - Delta против направления свечи
```
**Интерпретация:**
- Absorption на минимуме → institutional buying, сигнал LONG
- Absorption на максимуме → institutional selling, сигнал SHORT

### 5. FOOTPRINT CLUSTERS
```
Просмотр последних 5 свечей:
  - Если 3+ свечи с Delta > +0.4 → bullish cluster
  - Если 3+ свечи с Delta < -0.4 → bearish cluster
```
**Действие:**
- Cluster + breakout в направлении → high probability
- Cluster против breakout → divergence, пропустить

---

## ФУНКЦИИ ДЛЯ АГЕНТА

### `ORDERFLOW.analyze_entry(symbol, direction, timeframe)`
```
Returns:
  {
    delta_current: float,
    cvd_trend: "rising" | "falling" | "flat",
    imbalance_ratio: float,
    absorption_detected: bool,
    cluster_alignment: "aligned" | "divergent" | "neutral",
    confidence_score: 0-100
  }
```
**Confidence logic:**
```
score = 50  # baseline
if delta_aligned_with_direction: score += 20
if cvd_confirms_trend: score += 15
if imbalance_favors_direction: score += 10
if absorption_detected_at_level: score += 10
if cluster_aligned: score += 10
if divergence_detected: score -= 30
return max(0, min(100, score))
```

### `ORDERFLOW.check_divergence(symbol, timeframe)`
```
Returns:
  - "bullish_divergence": price down, CVD up
  - "bearish_divergence": price up, CVD down
  - "none": нет дивергенции
```

---

## ИНТЕГРАЦИЯ С BINANCE API

### Data sources:
1. **Trades stream** (wss://stream.binance.com/ws/{symbol}@aggTrade)
   - Классифицируются как buy если maker=False, sell если maker=True
   - Агрегируются по 1m / 5m свечам

2. **Order book depth** (wss://stream.binance.com/ws/{symbol}@depth20)
   - Расчёт bid_volume (sum 5 levels) vs ask_volume
   - Обновление каждые 250ms

### Ограничения:
- Binance не предоставляет footprint data через API
- Delta рассчитывается аппроксимативно по aggTrades
- Точность ~85% (vs institutional footprint tools)

---

## CONFIG.YAML ДОБАВЛЕНИЯ

```yaml
orderflow:
  enabled: true
  cvd_lookback_candles: 20
  delta_strong_threshold: 0.6
  imbalance_strong_threshold: 1.5
  absorption_volume_percentile: 90
  absorption_range_max_pct: 0.002  # 0.2% of ATR
  cluster_lookback: 5
  cluster_min_aligned: 3
  min_confidence_scalp: 70  # минимальная уверенность для scalp
```

---

## ПРАВИЛА ПОВЕДЕНИЯ

1. В scalp-режиме — **обязательно** вызывать `ORDERFLOW.analyze_entry()`
2. Если confidence < min_confidence_scalp — отклонить сигнал
3. При divergence — не входить даже если другие модули говорят "GO"
4. Логировать каждый анализ в metrics_history.jsonl
5. При absorption — явно указать в trade_brief

---

## ЗАВИСИМОСТИ
- Binance WebSocket API (aggTrades, depth)
- `exchange_prices.py` → ATR для absorption range
- `config.yaml` → [orderflow] секция
- `metrics_history.jsonl` → логирование

---

## CHANGELOG
- v1.0.0 (2026-05-23): Первичное создание. Delta, CVD, imbalance,
  absorption, cluster analysis, confidence scoring.
