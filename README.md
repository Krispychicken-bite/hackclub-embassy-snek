# Snake: Mower Mayhem

A Snake game built with Python and Pygame, with a lawnmower hazard that makes surviving a little harder.

Eat food to earn points and grow your snake while avoiding the walls and your own body. Every so often, a lawnmower crosses a randomly selected row or column. A flashing warning shows its path before it enters the board, giving you time to move out of the way.

If the mower hits your head, the game ends. If it hits your body, you lose a point and one segment of length.

## Features

- Classic Snake movement and food collection
- A lawnmower that travels across random rows or columns
- A flashing warning showing the mower's path
- Body-hit penalties that reduce your score and length
- Local high-score saving between sessions
- Live score, length, and best-score displays
- Pause, resume, and restart controls
- A win condition for filling the entire board

## Preview

Gameplay screenshots will be added here.

Planned previews:
- The main game board
- The lawnmower warning and hazard
- The game-over screen and high score

## Requirements

To run the source code, you need:

- Python 3
- Pygame

## Installation

1. Download the repository using GitHub's Code → Download ZIP option.
2. Extract the ZIP file.
3. Open a terminal in the project folder.
4. Install Pygame:

   ```bash
   python -m pip install pygame
   ```

5. Start the game:

   ```bash
   python snake.py
   ```

On systems where Python uses the `python3` command, replace `python` with `python3`.

## Controls

| Key | Action |
| --- | --- |
| Arrow keys or WASD | Move the snake |
| P or Space | Pause or resume |
| R | Restart the game |
| Esc | Quit |

## How to Play

1. Move towards the orange food to collect it.
2. Each piece of food adds one point and one segment.
3. Avoid the walls and your own body.
4. Watch for the yellow warning marking an incoming lawnmower.
5. Move away from the marked row or column before the mower reaches you.

The snake starts with five segments, so collecting three pieces of food gives you three points and a length of eight.

A mower hitting a body segment removes one segment from the tail and deducts one point. Your score cannot fall below zero, and reaching zero points does not end the game.

The game ends if you hit a wall, run into yourself, or let the mower hit your head. Filling the entire board wins the game.

## High Scores

Your highest score is saved automatically in `scores.json` next to the Python script.

The record is saved whenever you reach a new best score. Restarting the game or losing points to the mower does not clear it.

## Executable Download

An executable has not been published yet. For now, follow the installation instructions above to run the game from source.

## Built With

- Python
- Pygame
