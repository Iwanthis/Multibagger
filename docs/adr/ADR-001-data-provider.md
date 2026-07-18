# ADR-001

## Title

All modules must access market data exclusively through MarketDataProvider.

## Status

Accepted

## Context

Indicators, scanners and backtesting require historical data.

Direct CSV access throughout the codebase creates tight coupling and makes future storage migrations difficult.

## Decision

Introduce a MarketDataProvider as the only interface responsible for loading historical market data.

No module outside the data layer may read CSV files directly.

## Consequences

Positive

• Centralized validation

• Easier testing

• Storage backend can change without affecting business logic

• Cleaner architecture

Negative

• Slight increase in abstraction
