# Hermes Foundation

Мультиагентная система сканирования рынка и генерации торговых сигналов для перпетуальных контрактов (Bybit USDT-M).

## Агенты

| Агент | Назначение |
|-------|-----------|
| **Long** | Направленные лонги (perps) с ATR-стопами и 3 TP |
| **Short** | Направленные шорты (perps) |
| **Spot** | Спотовые покупки (swing) |
| **Arb** | Арбитраж между биржами (slippage + fee aware) |
| **Moonshot** | Низкокапы с потенциалом x2-x4 |
| **Options** | Скелет для опционных алертов (BTC/ETH) |

## Торговые режимы

- **Scalp** — 5m ATR, leverage 15x, risk 0.5%
- **Intraday** — 15m ATR, leverage 8x, risk 1%
- **Swing** — 4h ATR, leverage 5x, risk 1.5%

## Структура

```
├── directional_binance_agents.py  # Главный движок (6 агентов)
├── deep_binance_analysis.py       # Сканер + скоринг рынка
├── bot.py                         # Telegram-бот
├── api.py                         # FastAPI endpoint
├── config.yaml                    # Вся конфигурация
├── config_loader.py               # Загрузчик конфига
├── claude_client.py               # Claude API для анализа
├── exchange_prices.py             # Цены, orderbook, slippage
├── market_regime.py               # Определение режима рынка
├── evaluate_signals.py            # Оценка качества сигналов
├── backtest_directional.py        # Бэктест направленных сигналов
├── backtest_moonshot.py           # Бэктест moonshot
├── docs/                          # Спецификации модулей
├── scripts/                       # Батники и скрипты запуска
├── tasks/                         # Windows Task Scheduler XML
└── tests/                         # pytest тесты
```

## Быстрый старт

```bash
# 1. Установка
python -m pip install -r requirements.txt

# 2. Настройка
cp .env.example .env
# Заполни BYBIT_API_KEY, BYBIT_API_SECRET, ANTHROPIC_API_KEY

# 3. Запуск сканера + агентов
python directional_binance_agents.py

# 4. Тесты
pytest tests/ -q
```

## Конфигурация

Вся настройка в `config.yaml`:
- `exchange` — биржа (bybit/binance), тип рынка
- `scanner` — параметры скана (объём, OI, спред)
- `scoring` — веса скоринговой модели
- `agents` — пороги и параметры каждого агента
- `risk` — размер депо, риск на сделку, левериджи
- `trading_modes` — пресеты scalp/intraday/swing

## Стек

- Python 3.11+
- ccxt (Bybit API)
- Anthropic Claude (AI-анализ)
- FastAPI (API-слой)
- pytest (тесты)

## Статус

🟡 В разработке. Сканер и агенты работают. Нужна адаптация под Bybit API.

## Лицензия

Private / Personal use only.
