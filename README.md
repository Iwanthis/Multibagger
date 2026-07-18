# 📈 Multibagger

> Powered by the Atlas Framework

A professional momentum investing research platform for the Indian stock market.

Multibagger is designed to help identify high-quality momentum opportunities using explainable, rule-based analysis inspired by proven investing methodologies.

---

## Vision

Build a modular research platform that transforms raw market data into actionable investment insights through clean architecture, reusable components, and disciplined trading principles.

---

## Key Features (Planned)

- Market data management
- Indicator engine
- Relative Strength ranking
- Relative Volume analysis
- Stage Analysis (Stan Weinstein)
- Episodic Pivot detection (Stockbee)
- VCP detection
- Institutional buying detection
- Scanner framework
- Backtesting engine
- Morning market report
- Excel & PDF reporting

---

## Architecture

```
Providers
    ↓
Indicators
    ↓
Scanners
    ↓
Ranking
    ↓
Reports
```

The project is powered internally by the **Atlas Framework**, a modular Python engine designed for quantitative market research.

---

## Project Status

Current Sprint: **Atlas**

Current Task: **AT-001 – MarketDataProvider**

---

## Documentation

- 📄 ROADMAP.md
- 📄 CHANGELOG.md
- 📄 CONTRIBUTING.md
- 📄 ARCHITECTURE.md *(coming soon)*

---

## Technology Stack

- Python 3.13+
- Pandas
- yfinance
- Typer
- OpenPyXL
- Pytest

---

## License

Private project.