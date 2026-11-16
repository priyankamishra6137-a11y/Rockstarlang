# Rockstarlang (v0.1)

A Rockstar Games-inspired esoteric programming language and custom transpiler built from scratch in pure Python. Designed around GTA and RDR mechanics, cheat codes, and mission-based control flow.

> **Note:** Built and tested entirely on an Android mobile workflow (**Termux + Acode + Pydroid 3**) without a PC setup.

## Current Progress (`v0.1 - Initial Lexer`)
- **Lexical Analyzer (`cal1.py`):** Tokenizes integers, floats, basic arithmetic operators (`+`, `-`, `*`, `/`), and parentheses.
- **Whitespace Handling:** Ignores spaces and tabs during scanning.
- **Custom Error Handling:** Modular `Error` base class with `IllegalCharError` detection.
- **Interactive Shell (`shell.py`):** Command-line REPL loop to test live tokenization.

## Roadmap (Target Launch: Nov 19, 2026)
- [x] **v0.1:** Core Lexer, number/operator tokenization, and error classes
- [ ] **v0.2:** Identifier and Rockstar keyword recognition (`WASTED`, `HESOYAM`, `MISSION_PASSED`, etc.)
- [ ] **v0.3:** Parser and syntax rules
- [ ] **v1.0:** Python transpilation engine and playable sample scripts

## Author
**Priyanshu Mishra** (Class 9)
