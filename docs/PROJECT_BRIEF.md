# Project Brief

## Project Vision
Build a professional, modular research platform that transforms raw market data into actionable investment insights through clean architecture, reusable components, and disciplined momentum investing principles for the Indian stock market.

## Goals
- Identify high-quality momentum opportunities using rule-based analysis.
- Maintain a highly modular and extensible codebase.
- Provide a robust backtesting and reporting system.
- Establish a single source of truth for technical and design decisions.

## Product Overview: Multibagger
Multibagger is the end-user application. It serves as a professional momentum investing research platform, offering features like market data management, momentum scanners, relative strength ranking, stage analysis, and reporting.

## Framework Overview: Atlas
Atlas is the internal Python framework powering Multibagger. It provides the core quantitative market research engine, abstracting away data fetching, indicators, and scoring logic from the end-user product. 

## Design Philosophy
- **Separation of Concerns**: Clear boundaries between data provisioning, technical analysis, screening, and reporting.
- **Maintainability**: Easy to read, debug, and extend.
- **Explainability**: Rule-based analysis without black-box logic.

## Engineering Principles
- **Clean Architecture**: Decoupled layers.
- **SOLID Principles**: Object-oriented design best practices.
- **Single Responsibility Principle (SRP)**: Each module and class has one purpose.
- **No Hardcoded Paths**: Dynamic file and path resolution.
- **Configuration-Driven**: Core settings are managed via central configuration (`settings.py` / `.yaml`).
- **Type Hints**: Extensive use of Python type hinting for clarity and static analysis.
- **Docstrings**: Well-documented public interfaces.
- **Unit Tests**: Comprehensive test coverage.
- **Logging**: Robust execution tracking using `loguru`.

## Folder Overview
- `atlas/`: The core internal framework.
  - `cli/`: Command-line interfaces.
  - `config/`: Application configuration.
  - `core/`: Base classes and core logic.
  - `indicators/`: Technical indicator implementations.
  - `providers/`: External data source integrations.
  - `ranking/`: Scoring and sorting logic.
  - `reports/`: Output generation (Excel, PDF, Morning reports).
  - `scanners/`: Market screening logic.
  - `utils/`: Shared helper functions.
- `data/`: Local storage for universe definitions, market data, exports, logs, and scans.
- `tests/`: Unit and integration test suites.
- `docs/`: Project documentation and ADRs.

## Current Roadmap
- **Current Phase**: Atlas framework foundation.
- **Focus Areas**: Market data management, indicator engine, scanner framework, relative strength ranking, backtesting engine, and reporting capabilities.

## Coding Standards
- Python 3.11+ syntax and features.
- Strict adherence to PEP 8.
- Use `typer` for CLI, `pandas` for data manipulation, `pytest` for testing.
