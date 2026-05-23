# MODULE: SESSION CLASSIFIER
# Version: 1.0.0 | 2026-05-23

## НАЗНАЧЕНИЕ
Определяет текущую торговую сессию: Asia / London / NY / Overlap.
Используется в module_risk_manager для session_risk_budget.

## ПРОТОКОЛ

### SESSION.get_current() → str

UTC time → session:
- 00:00–06:00 UTC = "asia" (Tokyo, Sydney)
- 07:00–14:00 UTC = "london"
- 13:00–16:00 UTC = "overlap" (London + NY)
- 16:00–22:00 UTC = "ny"
- 22:00–00:00 UTC = "late_us"

### SESSION.get_liquidity_factor()

Returns:
- asia: 0.6 (low liquidity)
- london: 1.0
- ny: 1.2
- overlap: 1.5 (highest)
- late_us: 0.4

---

## CONFIG.YAML

```yaml
session:
  risk_budgets:
    asia: 0.4
    london: 0.7
    ny: 1.0
    overlap: 1.2
    late_us: 0.3
```

## ЗАВИСИМОСТИ
- module_risk_manager.md
- config.yaml [session]

## CHANGELOG
- v1.0.0: Base session classification
