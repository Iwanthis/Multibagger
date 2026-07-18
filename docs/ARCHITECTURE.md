# Architecture

## High-Level Architecture

```text
+-------------------------------------------------------------+
|                        MULTIBAGGER CLI                      |
|                         (CLI Layer)                         |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                      REPORTING ENGINE                       |
|                       (Report Layer)                        |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                        RANKING SYSTEM                       |
|                       (Ranking Layer)                       |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                       SCANNER ENGINE                        |
|                       (Scanner Layer)                       |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                      INDICATOR ENGINE                       |
|                      (Indicator Layer)                      |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                       DATA PROVIDERS                        |
|                      (Provider Layer)                       |
+-------------------------------------------------------------+
```

## Folder Responsibilities

| Directory | Responsibility |
| :--- | :--- |
| `atlas/cli/` | Manages the command-line interface, argument parsing, and orchestrating user commands. |
| `atlas/config/` | Centralizes application settings, environment variables, and external configuration files. |
| `atlas/core/` | Contains foundational abstractions, interfaces, and base classes used across the framework. |
| `atlas/indicators/` | Houses isolated, reusable technical analysis indicator logic. |
| `atlas/providers/` | Manages connections, fetching, and normalization of data from external sources. |
| `atlas/ranking/` | Contains algorithms and rules for sorting, scoring, and comparing equities. |
| `atlas/reports/` | Formats and outputs the results of scans and rankings into user-friendly formats. |
| `atlas/scanners/` | Applies filters and conditions to the universe of stocks to identify actionable setups. |

## Data Flow
1. **Request**: The user invokes a command via the **CLI Layer**.
2. **Data Acquisition**: The **Provider Layer** fetches raw historical and current market data for a given universe.
3. **Transformation**: The **Indicator Layer** processes the raw data, calculating technical metrics.
4. **Filtering**: The **Scanner Layer** evaluates the processed data against predefined rules to isolate candidates.
5. **Scoring**: The **Ranking Layer** compares the isolated candidates, assigning scores based on momentum and relative strength.
6. **Output**: The **Report Layer** aggregates the final ranked list and generates human-readable exports.

## Layer Details

### Provider Layer
Responsible for all external data I/O. It abstracts away the specific data source (e.g., Yahoo Finance) and returns standardized datasets to the rest of the framework.

### Indicator Layer
Responsible for mathematical and statistical computations on price and volume data. These are pure functions or classes that take price history and return derived metrics without understanding business context.

### Scanner Layer
Responsible for applying business logic and setup conditions (e.g., Stage Analysis, Institutional buying) to filter out equities that do not meet the criteria.

### Ranking Layer
Responsible for relative comparisons. It takes a list of screened equities and orders them by momentum strength, percentile, or other comparative metrics to surface the highest conviction setups.

### Report Layer
Responsible for presentation. It consumes the output of the ranking layer and formats it into distinct mediums like terminal tables or spreadsheet reports.

### CLI Layer
The entry point for the user. It translates terminal commands into framework orchestrations and provides user feedback and progress reporting.
