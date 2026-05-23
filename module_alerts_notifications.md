# Module: Alerts & Notifications

## Purpose
Send alerts via Telegram, Email, Discord

## Functions

### ALERTS.send(message, priority, channels) -> bool
**Priorities:** low, medium, high, critical
**Channels:** telegram, email, discord, webhook

### ALERTS.price_alert(symbol, condition, price) -> str
**Conditions:** above, below, crosses
**Returns:** alert_id

### ALERTS.indicator_alert(symbol, indicator, condition) -> str
**Example:** RSI crosses above 70

### ALERTS.cancel(alert_id) -> bool

## Config
```yaml
alerts:
  telegram_token: "..."
  telegram_chat_id: "..."
  email_smtp: "smtp.gmail.com"
  discord_webhook: "..."
```

## Dependencies
- python-telegram-bot
- smtplib
