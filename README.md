# Tetris Desktop Game

A classic single-player Tetris game implemented in **Python 3 + Tkinter** with
clean separation between the pure game logic and the desktop GUI.

## Quick start

```bash
# 1. (optional) create a virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 2. install the test dependency
pip install -r requirements.txt

# 3. run the game
python main.py
```

The runtime uses only the Python standard library (`tkinter`, `json`, `random`).
`requirements.txt` only contains `pytest` for the test suite.

## Controls

| Key | Action |
|-----|--------|
| Left / Right | Move piece |
| Up | Rotate clockwise |
| Down | Soft drop |
| Space | Hard drop |
| P | Pause / resume |
| R | Restart |

## Game rules

- 10 x 20 board, seven standard tetrominoes (I, O, T, S, Z, J, L).
- Scoring: 1/2/3/4 cleared lines = 100/300/500/800 points x current level.
- Level increases every 10 cleared lines; gravity speeds up with level.
- The next piece, score, level, lines and persisted high score are shown.
- High score is stored in `highscore.json` next to the project.

## Project layout

```text
main.py                 # application entry point: python main.py
tetris/
  __init__.py
  tetromino.py          # Tetromino shapes + rotation
  engine.py             # GameEngine: board, collision, scoring, spawn
  controller.py         # GameController: input, timer, state machine
  window.py             # GameWindow: Tkinter rendering
  highscore.py          # HighScoreStore: local JSON persistence
tests/
  test_tetromino.py
  test_engine.py
  test_highscore.py
docs/
  architecture.md
requirements.txt
Dockerfile
```

## Architecture mapping

| Documentation element | Implementation file |
|-----------------------|---------------------|
| `Tetromino` | `tetris/tetromino.py` |
| `GameEngine` | `tetris/engine.py` |
| `GameController` | `tetris/controller.py` |
| `GameWindow` | `tetris/window.py` |
| `HighScoreStore` | `tetris/highscore.py` |
| Layered flow `GameWindow -> GameController -> GameEngine` | `main.py` wires `GameWindow` and `GameController` |
| State diagram (Running / Paused / GameOver) | `GameController.state` + `pause()` / `restart()` / `tick()` |
| Gravity-tick sequence | `GameController.tick()` |

More detail is available in [`docs/architecture.md`](docs/architecture.md).

## Testing

Tests are headless and cover only the domain logic (no display, input, network
or infinite loops):

```bash
python -m pytest -q
```

## Docker

The included `Dockerfile` builds a headless test image.  It does **not** start
the Tkinter GUI because a desktop display is not available in the container:

```bash
docker build -t tetris-tests .
docker run --rm tetris-tests
```

To run the GUI in Docker you would need to share the host X11/Wayland socket
and install `python3-tk`; running it natively with `python main.py` is
recommended.

## Assumptions

- "Restart" (R) is accepted in any state, not only after game over.
- Hard-drop distance is tracked but does not add bonus points (not required by
  the specification).
- The high-score JSON file uses the shape `{"high_score": <int>}`.
- Rendering is event/timer driven.  Redraws happen on gravity ticks and user
  input, keeping the per-frame draw cost comfortably within a 60 FPS budget on
  a normal laptop.
- Tetromino randomisation uses a 7-bag algorithm for fair piece distribution.
