# Contributing

## Coding Standards

- Python 3.12+
- Type hints required
- Use pathlib instead of os.path
- Follow PEP 8
- Keep functions short and focused

## Design Principles

- One class = One responsibility
- No business logic inside CLI
- Prefer composition over inheritance
- Write readable code

## Testing

Every new module should include tests.

Tests belong in:

tests/

## Commit Messages

Examples:

Added EMA indicator

Implemented MarketDataProvider

Fixed downloader retry logic

Added Momentum Scanner

Avoid generic commits like:

update

changes

fix

## Documentation

Update documentation whenever functionality changes.