# 🔫 Rockstarlang (`v0.4`)

**Rockstarlang** is a Grand Theft Auto & Red Dead Redemption-inspired esoteric programming language built from scratch in Python. Designed around iconic Rockstar Games mechanics, it features a custom three-stage interpreter pipeline (**Lexer $\rightarrow$ Recursive Descent Parser $\rightarrow$ Tree-Walk Interpreter**) with scoped memory, control flow, data structures, and functions.

---

## 🚀 What's New in `v0.4`

- **Variables (`heist`) & User Input (`ask_Lester`)**: Store, update, and prompt dynamic values with automatic numeric type parsing.
- **Conditional Branching (`wanted` / `heat_up` / `lay_low`)**: Multi-level `if / elif / else` logic with arbitrary block indentation (`4 spaces` or `1 tab` per level).
- **Loops & Chase Controls (`on_the_run`, `busted`, `evade`)**: Full `while` loop execution supporting `break` (`busted`) and `continue` (`evade`).
- **Data Structures (`stash` & `dossier`)**: Zero-indexed lists (`stash[...]`) and key-value dictionaries (`dossier{...}`) with element mutation support.
- **Scoped Functions (`new_mission` & `loot`)**: User-defined functions with isolated call-stack frames, parameters, recursion, and `return` (`loot`) values.
- **Single-Line Comments (`RDR2`)**: Full-line and inline comment support.
- **Comparison & Arithmetic Operators**: Full BODMAS precedence (`+`, `-`, `*`, `/`, unary `+/-`) and relational operators (`==`, `!=`, `<`, `>`, `<=`, `>=`).

---

## 📖 Language Syntax Reference

| Standard Concept | Rockstarlang Keyword | Example |
| :--- | :--- | :--- |
| **Program Start / End** | `GTA52013` ... `GTA62026` | Mandatory entry and exit block markers |
| **Print Output** | `call_CJ (...)` | `call_CJ ("Mission Passed!", cash)` |
| **Variable Declaration** | `heist` | `heist stars = 3` |
| **User Input** | `ask_Lester(...)` | `heist name = ask_Lester("Enter alias: ")` |
| **Single-Line Comment** | `RDR2` | `RDR2 Plan the getaway route` |
| **If / Elif / Else** | `wanted` / `heat_up` / `lay_low` | `wanted stars >= 5:` / `heat_up stars > 0:` / `lay_low:` |
| **While Loop** | `on_the_run` | `on_the_run stars > 0:` |
| **Break / Continue** | `busted` / `evade` | `busted` (break) / `evade` (continue) |
| **List (Array)** | `stash[...]` | `heist guns = stash["Pistol", "AK-47", "RPG"]` |
| **Dictionary (Map)** | `dossier{...}` | `heist stats = dossier{"health": 100, "cash": 5000}` |
| **Function Definition** | `new_mission` | `new_mission calc_cut(total, crew):` |
| **Return Value** | `loot` | `loot total / crew` |

---

## 💻 Example Script (`Test.rsl`)

```text
GTA52013
    RDR2 Define payout calculation mission
    new_mission split_payout(total_loot, crew_count):
        wanted crew_count <= 0:
            loot 0
        loot total_loot / crew_count

    heist crew = stash["Michael", "Franklin", "Trevor"] RDR2 Main heist crew
    heist vault = dossier{"target": "Union Depository", "gold": 1500000, "heat": 3}

    call_CJ ("Target:", vault["target"])
    heist vault["gold"] = vault["gold"] + 300000

    on_the_run vault["heat"] > 0:
        call_CJ ("Evading cops... Stars left:", vault["heat"])
        heist vault["heat"] = vault["heat"] - 1

    heist cut = split_payout(vault["gold"], 3)
    call_CJ ("Mission Passed! Each member gets:", cut)
    call_CJ ("Lead Driver:", crew[1])
GTA62026
