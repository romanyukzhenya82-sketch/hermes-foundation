# MODULE: MACRO CALENDAR
# Version: 1.0.0 | 2026-05-23

## НАЗНАЧЕНИЕ
Мониторинг важных макрособытий: CPI, FOMC, NFP, PPI, и т.д.
Автоматическое повышение min_vol_spike и снижение leverage за 30 мин. до события.

## ПРОТОКОЛ

### MACRO.check_upcoming_events(window_minutes=30) → list

Returns:
```python
[
  {"event": "CPI", "time": "14:30 UTC", "impact": "HIGH", "minutes_until": 25},
  ...
]
```

### MACRO.get_risk_adjustment()

Returns:
```python
{
  "vol_spike_mult": 1.5,  # повышение min_vol_spike
  "leverage_mult": 0.5,   # снижение leverage
  "reason": "CPI in 25 min"
}
```

---

## DATA SOURCE

### Recommended API:
1. **Trading Economics API** (https://tradingeconomics.com/analytics/api.aspx)
2. **Forex Factory Calendar** (scraping or RSS)
3. **Investing.com Economic Calendar API**

### Минимальная реализация:
Ручной YAML с расписанием:
```yaml
macro_events:
  2026-05-23:
    - {time: "14:30", event: "CPI", impact: "HIGH"}
  2026-05-27:
    - {time: "18:00", event: "FOMC", impact: "CRITICAL"}
```

---

## ПРАВИЛА

1. За 30 мин. до HIGH/CRITICAL event:
   - Increase min_vol_spike *= 1.5
   - Reduce leverage /= 2
   - Алерт в Telegram

2. За 5 мин. до CRITICAL event:
   - STOP_TRADING mode

3. Через 10 мин. после event:
   - Оценить волатильность
   - Вернуться к normal если vol стабилизировалась

---

## CONFIG.YAML

```yaml
macro_calendar:
  enabled: true
  pre_event_window_min: 30
  critical_stop_window_min: 5
  post_event_cooldown_min: 10
  high_impact_vol_mult: 1.5
  high_impact_lev_mult: 0.5
  critical_impact_stop: true
```

## ЗАВИСИМОСТИ
- module_risk_manager.md
- alert_engine.py
- config.yaml [macro_calendar]

## CHANGELOG
- v1.0.0: Base macro event monitoring
