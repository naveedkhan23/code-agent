# Tetris Desktop Game - Architecture Documentation

## 1. Overview
A classic single-player Tetris game delivered as a desktop application written in Python with Tkinter.
The player must be able to move, rotate and drop falling tetrominoes on a 10x20 board.

## 2. Functional Requirements
- The game shall support the seven standard tetrominoes (I, O, T, S, Z, J, L).
- The player must be able to move left/right, rotate, soft-drop and hard-drop pieces with the keyboard.
- Completed lines shall be cleared and scored (1/2/3/4 lines = 100/300/500/800 points x level).
- The game should speed up every 10 cleared lines (level up).
- The game shall show the next piece, score, level and lines cleared.
- The player should be able to pause and restart the game.
- A high score must be persisted in a local JSON file.

## 3. Architecture
Layered design: `GameWindow` (Tkinter view) -> `GameController` (input and timer) -> `GameEngine` (pure logic, no UI).
Domain logic must be unit-testable without a display.

| Component | Responsibility |
|-----------|----------------|
| GameEngine | Board state, collision, line clearing, scoring |
| Tetromino | Shape definitions and rotation |
| GameController | Gravity timer, key bindings, state transitions |
| GameWindow | Rendering the board and side panel |
| HighScoreStore | Load/save the high score JSON |

## 4. Non-functional Requirements
- Must start with a single command: `python main.py`.
- Should run at a steady 60 FPS rendering budget on a normal laptop.
