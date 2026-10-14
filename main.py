"""Tetris desktop game entry point.

Run with:

    python main.py
"""

from __future__ import annotations

import tkinter as tk

from tetris.controller import GameController
from tetris.engine import GameEngine
from tetris.highscore import HighScoreStore


def main() -> None:
    root = tk.Tk()
    engine = GameEngine()
    store = HighScoreStore("highscore.json")
    controller = GameController(root, engine, store)
    # Keep a reference so the controller is not garbage collected while the
    # Tk event loop runs.
    root._tetris_controller = controller  # type: ignore[attr-defined]
    root.mainloop()


if __name__ == "__main__":
    main()
