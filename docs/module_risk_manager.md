# MODULE: RISK MANAGER
# Version: 1.0.0 | 2026-05-23
# Hermes Foundation — Динамический риск-менеджмент

## НАЗНАЧЕНИЕ
Адаптивное управление риском на основе текущей волатильности, drawdown сессии,
корреляции открытых позиций и режима рынка. Заменяет статичные параметры
config.yaml [risk] динамическими расчётами в реальном времени.

## КОГДА АКТИВИРОВАТЬ
- Перед каждым входом в позицию (scalp / intraday / swing)
- При изменении market regime (см. module_market_regime)
- При достижении drawdown-порогов
- При открытии новой сессии (Asia / London / NY)

---

## ПРОТОКОЛ: АДАПТИВНЫЙ РАСЧЁТ РИСКА

### ШАГИ ВЫПОЛНЕНИЯ:

**1. ОЦЕНИТЬ СОСТОЯНИЕ СЧЁТА**
```
Current DD% = (peak_equity - current_equity) / peak_equity * 100
```
- DD < 2%  → normal_mode: risk_pct = config.default_risk_pct
- DD 2–4%  → reduced_mode: risk_pct = config.default_risk_pct * 0.5
- DD 4–6%  → defensive_mode: risk_pct = config.default_risk_pct * 0.25, leverage /= 2
- DD > 6%  → STOP_TRADING: выход из всех позиций, пауза 2 часа
- DD > 10% → HARD_STOP: торговля запрещена до ручного сброса

**2. СКОРРЕКТИРОВАТЬ НА ВОЛАТИЛЬНОСТЬ**
```
Vol_ratio = current_ATR_1h / avg_ATR_1h_14d
```
- Vol_ratio < 0.7  → low_vol: risk_pct * 0.7 (ложные пробои)
- Vol_ratio 0.7–1.3 → normal: без изменений
- Vol_ratio 1.3–2.0 → high_vol: risk_pct * 0.8, стоп шире на 20%
- Vol_ratio > 2.0  → extreme_vol: risk_pct * 0.5, вход только на подтверждённых уровнях

**3. КОРРЕЛЯЦИОННЫЙ ФИЛЬТР ОТКРЫТЫХ ПОЗИЦИЙ**
```
Использовать: module_correlation.md
```
- Если новый сигнал коррелирует > 0.75 с уже открытой позицией:
  → Уменьшить размер новой позиции на 50%
  → Или отклонить сигнал если совокупный риск > 2 * default_risk_pct
- Максимальное количество одновременных коррелированных позиций: 2

**4. РЕЖИМ-СПЕЦИФИЧНЫЙ ЛЕВЕРИДЖ**
| Режим | Базовый leverage | DD-коррекция | Max leverage |
|-------|-----------------|--------------|-------------|
| scalp | 15 | DD * 0.3 | 20 |
| intraday | 8 | DD * 0.5 | 12 |
| swing | 5 | DD * 0.7 | 8 |
| moonshot | 3 | DD * 1.0 | 5 |

*Формула: effective_leverage = base * (1 - DD% * mode_factor)*

**5. ДНЕВНЫЕ ЛИМИТЫ**
- Max daily loss: 3% от счёта → STOP_TRADING на день
- Max daily trades (scalp): 20 сделок
- Max daily trades (intraday): 8 сделок
- Max open positions одновременно: 4
- Max exposure в одном активе: 30% от total_risk_budget

---

## ФУНКЦИИ ДЛЯ АГЕНТА

### `RISK.calculate_position_size(symbol, entry, stop, mode)`
```
Inputs:
  - symbol: торговая пара
  - entry: цена входа
  - stop: уровень стопа
  - mode: scalp | intraday | swing

Logic:
  1. risk_pct = get_adaptive_risk_pct()  # с учётом DD и волатильности
  2. risk_usd = account_usdt * risk_pct
  3. stop_distance_pct = abs(entry - stop) / entry
  4. position_size_usd = risk_usd / stop_distance_pct
  5. leverage = get_effective_leverage(mode)
  6. margin_required = position_size_usd / leverage
  return: {size_usd, leverage, margin_required, risk_usd}
```

### `RISK.check_entry_allowed(symbol, direction)`
```
Returns True если:
  - DD < HARD_STOP порога
  - daily_loss < max_daily_loss
  - daily_trades_count < max_daily_trades[mode]
  - open_positions_count < max_open_positions
  - correlation_check passed
Returns False + reason если любое условие нарушено
```

### `RISK.get_session_risk_budget()`
```
Возвращает доступный риск-бюджет на текущую сессию:
  - Asia session: 40% от daily_budget (низкая ликвидность)
  - London session: 70% от daily_budget
  - NY session: 100% от daily_budget
  - London/NY overlap: 120% от daily_budget (повышенная активность)
```

---

## ИНТЕГРАЦИЯ С CONFIG.YAML

```yaml
# Добавить в config.yaml секцию [risk_dynamic]:
risk_dynamic:
  dd_reduced_threshold: 0.02      # 2% DD → reduced mode
  dd_defensive_threshold: 0.04    # 4% DD → defensive
  dd_stop_threshold: 0.06         # 6% DD → stop trading
  dd_hard_stop_threshold: 0.10    # 10% DD → hard stop
  max_daily_loss_pct: 0.03        # 3% дневной лимит потерь
  max_open_positions: 4
  max_correlated_positions: 2
  correlation_threshold: 0.75
  vol_ratio_high: 1.3
  vol_ratio_extreme: 2.0
  session_budgets:
    asia: 0.4
    london: 0.7
    ny: 1.0
    overlap: 1.2
```

---

## ПРАВИЛА ПОВЕДЕНИЯ АГЕНТА

1. **Никогда** не входить в позицию без предварительного вызова `RISK.check_entry_allowed()`
2. При DD_MODE = STOP_TRADING — сообщить пользователю и прекратить генерацию сигналов
3. При extreme_vol — явно указывать повышенный риск в трейд-брифе
4. Логировать каждый расчёт риска в `metrics_history.jsonl` с полями:
   - timestamp, symbol, dd_pct, vol_ratio, effective_risk_pct, effective_leverage
5. При изменении DD_MODE — немедленный алерт через Telegram (см. alert_engine.py)

---

## ЗАВИСИМОСТИ
- `config.yaml` → секции [risk], [trading_modes], [risk_dynamic]
- `module_market_regime.md` → текущий режим рынка
- `module_session_classifier.md` → текущая сессия
- `module_correlation.md` → корреляция позиций
- `metrics_history.jsonl` → исторические данные для Vol_ratio
- `alert_engine.py` → уведомления при смене режима

---

## CHANGELOG
- v1.0.0 (2026-05-23): Первичное создание модуля. Базовый DD-контроль,
  адаптивный риск по волатильности, корреляционный фильтр, сессионные бюджеты.
