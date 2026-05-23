# Module: Reporting & Dashboard

## Purpose
Generate performance reports and visualizations

## Functions

### REPORT.daily_summary() -> dict
**Returns:** pnl, trades_count, win_rate, best/worst_trade

### REPORT.monthly_performance() -> pd.DataFrame
**Returns:** Monthly breakdown of performance

### REPORT.export_trades(start, end, format) -> str
**Formats:** csv, json, excel
**Returns:** file_path

### DASHBOARD.update_metrics(metrics) -> bool
**Description:** Push metrics to dashboard

### DASHBOARD.generate_charts(data, chart_type) -> str
**Types:** equity_curve, drawdown, returns_distribution
**Returns:** chart_url or base64

## Config
```yaml
reporting:
  dashboard_update_freq: 60  # seconds
  export_path: "./reports/"
  chart_resolution: "1920x1080"
```

## Dependencies
- plotly/matplotlib
- pandas
