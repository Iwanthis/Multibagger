# ADR-001: Rename Python Package to Atlas

## Status
Accepted

## Context
The project originally used the package name `multibagger`.
This created ambiguity in the codebase and discussions between:
- The repository
- The end-user product
- The internal Python package

## Decision
- Rename the core internal Python package to `atlas`.
- Retain the overarching product name as `Multibagger`.

## Consequences
- All Python imports must be updated to use the `atlas.*` namespace.
- The CLI command will remain `multibagger` to reflect the product name.
- Results in a clearer architectural boundary where Multibagger (the product) is powered by Atlas (the internal framework).