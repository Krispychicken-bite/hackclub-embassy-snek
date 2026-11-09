# Snake: Mower Mayhem

A Snake game built with Python and Pygame, with a lawnmower hazard that makes surviving a little harder.

Eat food to earn points and grow your snake while avoiding the walls and your own body. Every so often, a lawnmower crosses a randomly selected row or column. A flashing yellow warning shows its path before it enters the board, giving you time to move out of the way.

If the mower hits your head, the game ends. If it hits your body, you lose a point and one segment of length.

## Download and Play

A Windows executable is available from [GitHub Releases](PASTE_RELEASE_URL_HERE).

1. Open the release page.
2. Under Assets, download `Snake-Mower-Mayhem.exe`.
3. Open the downloaded file to play.

You do not need to install Python or Pygame to run the Windows executable.

For other operating systems, follow the source-code installation instructions below.

## Features

- Classic Snake movement and food collection
- A lawnmower that travels across random rows or columns
- A flashing warning showing the mower's path
- Body-hit penalties that reduce your score and length
- Local high-score saving between sessions
- Live score, length, and best-score displays
- Pause, resume, and restart controls
- Automatic pausing when the game window loses focus
- A win condition for filling the entire board
- A downloadable Windows executable

## Preview

Gameplay screenshots will be added here.

## Controls

| Key | Action |
| --- | --- |
| Arrow keys or WASD | Move the snake |
| P or Space | Pause or resume |
| R | Restart |
| Esc | Quit |

The game also pauses automatically when you switch away from its window.

## How to Play

1. Move towards the orange food to collect it.
2. Each piece of food adds one point and one segment.
3. Avoid the walls and your own body.
4. Watch for the yellow warning marking an incoming lawnmower.
5. Move away from the marked row or column before the mower reaches you.

The snake starts with five segments. Collecting three pieces of food gives you three points and a length of eight.

### The Lawnmower

The mower waits a random 7–11 seconds before warning you about its next pass. The warning lasts 1.5 seconds and highlights the row or column it will cross. The HUD also shows its direction.

- Head hit: The game ends immediately.
- Body hit: One segment is removed from the tail, and one point is deducted.
- Your score cannot fall below zero.
- Reaching zero points does not end the game.

### Winning and Losing

The game ends if you hit a wall, run into yourself, or let the mower hit your head.

Fill the entire board with your snake to win.

## High Scores

Your best score is saved automatically whenever you reach a new record.

The save file is stored in:

```text
SnakeMowerMayhem/scores.json
```

This folder is created inside your home directory. On Windows, it will usually look like:

```text
C:\Users\YourUsername\SnakeMowerMayhem\scores.json
```

Restarting the game, closing it, or losing points to the mower does not clear your record. The Python version and executable use the same save location when run under the same user account.

## Running from Source

### Requirements

- Python 3
- Pygame

### Installation

1. Download the repository using Code → Download ZIP.
2. Extract the ZIP file.
3. Open a terminal in the extracted project folder.
4. Install Pygame:

   ```bash
   python -m pip install pygame
   ```

5. Start the game:

   ```bash
   python snek.py
   ```

On systems where Python uses the `python3` command, replace `python` with `python3`.

## Adjusting the Snake Speed

To change the speed when running from source, edit this value near the top of `snek.py`:

```python
SNAKE_STEP = 0.18
```

A larger value makes the snake slower. A smaller value makes it faster.

Changing the source code will not update an existing executable; you need to rebuild it.

## Built With

- Python
- Pygame
- PyInstaller for the Windows executable
