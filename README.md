# 🔫 Rockstarlang (`v0.5`)

**Rockstarlang** is a Grand Theft Auto & Red Dead Redemption-inspired esoteric programming language built from scratch in Python. Designed with a game-development-first architecture, it combines a custom three-stage interpreter pipeline (**Lexer $\rightarrow$ Recursive Descent Parser $\rightarrow$ Scoped Tree-Walk Interpreter**) with full Object-Oriented Programming (`gang`, `blueprint`, `recruit`, `boss`), multithreading, and built-in standard libraries (`math`, `time`, `thread`, `json`, `os`, `sys`).

---

## 🚀 What's New in `v0.5`

- **Full Object-Oriented Programming (`gang`, `boss`, `spawn`, `recruit`)**: Define entity classes (`gang`), initialize instances with `spawn(boss, ...)`, access properties/methods via `.`, and instantiate objects with `recruit`.
- **Lightweight Data Structs (`blueprint`)**: Declare fast game entities like `blueprint Bullet(x, y, speed)` without boilerplate constructors.
- **Module & File Imports (`hire`)**: Import built-in game-dev libraries (`hire math`, `hire time`, `hire thread`, `hire json`, `hire os`, `hire sys`) or external `.rsl` mission scripts (`hire "weapons.rsl"`).
- **Multithreading (`thread.run`)**: Spawn background `new_mission` workers concurrently alongside the main game loop.
- **Game Math, Frame Pacing & Save/Load**: Built-in `math.dist`, `math.rand`, `math.clamp`, `time.fps(60)`, and `json.save` / `json.load` for persistent savegames.

---

## 📖 Language Syntax Reference

### Core Language Keywords

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
| **Function / Method** | `new_mission` | `new_mission calc_cut(total, crew):` |
| **Return Value** | `loot` | `loot total / crew` |
| **Class / Struct** | `gang` / `blueprint` | `gang Player:` / `blueprint Bullet(x, y, speed)` |
| **Constructor / Self** | `spawn` / `boss` | `new_mission spawn(boss, name, hp):` |
| **Instantiate Object** | `recruit` | `heist cj = recruit Player("CJ", 100)` |
| **Import Module / File** | `hire` | `hire math` / `hire "utils.rsl"` |

---

### Standard Library Modules (`hire <module>`)

| Module | Available Methods & Constants | Description |
| :--- | :--- | :--- |
| **`math`** | `pi`, `sin(x)`, `cos(x)`, `sqrt(x)`, `abs(x)`, `floor(x)`, `ceil(x)`, `dist(x1, y1, x2, y2)`, `rand(min, max)`, `clamp(val, lo, hi)` | Trigonometry, distance checks, RNG spawns, and boundary clamping |
| **`time`** | `now()`, `wait(sec)`, `fps(target)` | High-precision timestamps, delays, and delta-time FPS limiter |
| **`thread`** | `run(mission_fn, *args)`, `sleep(sec)` | Asynchronous daemon threads for background timers and events |
| **`json`** | `save(path, data)`, `load(path)`, `encode(data)`, `decode(str)` | Persistent savegame serialization and JSON parsing |
| **`os`** | `exists(path)`, `mkdir(path)`, `remove(path)`, `clear()`, `cwd()` | File system helpers and terminal screen clearing |
| **`sys`** | `args()`, `exit(code)`, `platform` | CLI argument access and clean process termination |

---

## 💻 Game-Dev Showcase (`Test.rsl`)

```text
GTA52013
    hire math
    hire time
    hire json
    hire thread

    RDR2 Background police scanner running on a separate thread
    new_mission police_scanner():
        heist count = 0
        on_the_run count < 2:
            time.wait(0.6)
            call_CJ ("[LSPD RADIO] Helicopter tracking suspect...")
            heist count = count + 1

    thread.run(police_scanner)

    RDR2 Game Entity using OOP 'gang'
    gang Driver:
        new_mission spawn(boss, name, x, y):
            heist boss.name = name
            heist boss.x = x
            heist boss.y = y

        new_mission move_toward(boss, tx, ty):
            heist dx = math.rand(10, 25)
            heist boss.x = math.clamp(boss.x + dx, 0, tx)
            heist d = math.dist(boss.x, boss.y, tx, ty)
            call_CJ (boss.name, "at X =", boss.x, "| Distance to Safe House:", math.floor(d))

    heist franklin = recruit Driver("Franklin", 0, 0)

    on_the_run franklin.x < 60:
        franklin.move_toward(60, 0)
        time.wait(0.4)

    RDR2 Save mission progress to JSON file
    heist save_data = dossier{"player": franklin.name, "x": franklin.x, "status": "SAFE"}
    json.save("savegame.json", save_data)
    heist loaded = json.load("savegame.json")
    call_CJ ("Game Saved & Verified:", loaded)
GTA62026
