import json
import random
from pathlib import Path

import pygame


pygame.init()

WIDTH = 800
HEIGHT = 600
CELL_SIZE = 20
HUD_HEIGHT = 60

COLS = WIDTH // CELL_SIZE
ROWS = HEIGHT // CELL_SIZE

SNAKE_STEP = 0.18
MOWER_STEP = 0.065
MOWER_WARNING = 1.5
MOWER_INTERVAL = (7, 11)

BG = "#0B1220"
GRID = "#132131"
SNAKE_COLOR = "#2DD4BF"
HEAD_COLOR = "#A7F3D0"
FOOD_COLOR = "#FB923C"
WARNING_COLOR = "#FACC15"
MOWER_COLOR = "#EF4444"
TEXT_COLOR = "#E2E8F0"

SCORE_DIR = Path.home() / "SnakeMowerMayhem"
SCORE_FILE = SCORE_DIR / "scores.json"

screen = pygame.display.set_mode((WIDTH, HEIGHT + HUD_HEIGHT))
pygame.display.set_caption("Snake: Mower Mayhem")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 26)
large_font = pygame.font.Font(None, 58)
small_font = pygame.font.Font(None, 22)


def load_high_score():
    try:
        data = json.loads(SCORE_FILE.read_text(encoding="utf-8"))

        if isinstance(data, dict):
            score = data.get("high_score", 0)

            if type(score) is int and score >= 0:
                return score

    except FileNotFoundError:
        pass
    except (OSError, ValueError) as error:
        print(f"Could not load score: {error}")

    return 0


def save_high_score(score):
    temp_file = SCORE_FILE.with_suffix(".tmp")

    try:
        SCORE_DIR.mkdir(parents=True, exist_ok=True)

        temp_file.write_text(
            json.dumps({"high_score": score}, indent=4),
            encoding="utf-8",
        )

        temp_file.replace(SCORE_FILE)
        return True

    except OSError as error:
        print(f"Could not save score: {error}")
        return False


def cell_rect(position, inset=0):
    x, y = position

    return pygame.Rect(
        x * CELL_SIZE + inset,
        HUD_HEIGHT + y * CELL_SIZE + inset,
        CELL_SIZE - inset * 2,
        CELL_SIZE - inset * 2,
    )


def draw_text(text, position, color=TEXT_COLOR, text_font=None):
    text_font = text_font or font
    image = text_font.render(text, True, color)
    screen.blit(image, position)


def draw_centered(text, y, text_font, color=TEXT_COLOR):
    image = text_font.render(text, True, color)
    screen.blit(image, (WIDTH // 2 - image.get_width() // 2, y))


class Game:
    def __init__(self):
        self.high_score = load_high_score()
        self.reset()

    def reset(self):
        self.snake = [
            (10, 15),
            (9, 15),
            (8, 15),
            (7, 15),
            (6, 15),
        ]

        self.segment_ids = list(range(len(self.snake)))
        self.next_segment_id = len(self.snake)

        self.direction = (1, 0)
        self.pending_direction = self.direction
        self.turn_queued = False

        self.score = 0
        self.dead = False
        self.won = False
        self.paused = False
        self.reason = ""

        self.move_timer = 0.0
        self.mower_timer = 0.0
        self.mower_wait = random.uniform(*MOWER_INTERVAL)

        self.mower_state = "waiting"
        self.mower_position = None
        self.mower_direction = (0, 0)
        self.mower_axis = "row"
        self.mower_lane = 0
        self.warning_timer = 0.0
        self.hit_segments = set()

        self.damage_timer = 0.0
        self.damage_message = ""

        self.food = self.spawn_food()

    def update_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            save_high_score(self.high_score)

    def spawn_food(self):
        occupied = set(self.snake)

        empty = [
            (x, y)
            for y in range(ROWS)
            for x in range(COLS)
            if (x, y) not in occupied
        ]

        return random.choice(empty) if empty else None

    def end_game(self, reason):
        self.dead = True
        self.reason = reason

    def queue_turn(self, new_direction):
        if self.turn_queued:
            return

        opposite = (-self.direction[0], -self.direction[1])

        if new_direction not in (opposite, self.direction):
            self.pending_direction = new_direction
            self.turn_queued = True

    def move_snake(self):
        old_tail = self.snake[-1]

        self.direction = self.pending_direction
        self.turn_queued = False

        hx, hy = self.snake[0]
        dx, dy = self.direction
        new_head = (hx + dx, hy + dy)

        x, y = new_head

        if not (0 <= x < COLS and 0 <= y < ROWS):
            self.end_game("You hit the wall.")
            return

        growing = new_head == self.food
        collision_body = self.snake if growing else self.snake[:-1]

        if new_head in collision_body:
            self.end_game("You ran into yourself.")
            return

        self.snake = [new_head] + self.snake[:-1]

        if growing:
            self.snake.append(old_tail)
            self.segment_ids.append(self.next_segment_id)
            self.next_segment_id += 1

            self.score += 1
            self.update_high_score()

            self.food = self.spawn_food()

            if self.food is None:
                self.won = True
                self.reason = "You filled the entire board!"

    def start_warning(self):
        self.mower_axis = random.choice(("row", "column"))
        self.hit_segments.clear()

        from_start = random.choice((True, False))

        if self.mower_axis == "row":
            self.mower_lane = random.randrange(ROWS)

            self.mower_position = (
                -1 if from_start else COLS,
                self.mower_lane,
            )

            self.mower_direction = (
                1 if from_start else -1,
                0,
            )

        else:
            self.mower_lane = random.randrange(COLS)

            self.mower_position = (
                self.mower_lane,
                -1 if from_start else ROWS,
            )

            self.mower_direction = (
                0,
                1 if from_start else -1,
            )

        self.mower_state = "warning"
        self.warning_timer = MOWER_WARNING

    def check_mower_collision(self):
        if self.mower_state != "active" or self.dead:
            return

        if self.mower_position == self.snake[0]:
            self.end_game("The lawnmower hit your head!")
            return

        hit_ids = [
            segment_id
            for position, segment_id in zip(
                self.snake[1:],
                self.segment_ids[1:],
            )
            if position == self.mower_position
            and segment_id not in self.hit_segments
        ]

        if not hit_ids:
            return

        self.hit_segments.update(hit_ids)
        lost = min(len(hit_ids), len(self.snake) - 1)

        if lost:
            del self.snake[-lost:]
            del self.segment_ids[-lost:]

            self.score = max(0, self.score - lost)
            self.damage_message = f"-{lost} point / -{lost} length"
            self.damage_timer = 0.8

    def move_mower(self):
        x, y = self.mower_position
        dx, dy = self.mower_direction
        self.mower_position = (x + dx, y + dy)

        x, y = self.mower_position

        if not (0 <= x < COLS and 0 <= y < ROWS):
            self.mower_state = "waiting"
            self.mower_position = None
            self.mower_wait = random.uniform(*MOWER_INTERVAL)
            return

        self.check_mower_collision()

    def update(self, dt):
        if self.dead or self.won or self.paused:
            return

        self.damage_timer = max(0, self.damage_timer - dt)
        remaining = dt

        while remaining > 0 and not self.dead and not self.won:
            step = min(remaining, 0.01)
            remaining -= step
            self.move_timer += step

            if self.move_timer >= SNAKE_STEP:
                self.move_timer -= SNAKE_STEP
                self.move_snake()

                if self.dead or self.won:
                    return

                self.check_mower_collision()

                if self.dead:
                    return

            if self.mower_state == "waiting":
                self.mower_wait -= step

                if self.mower_wait <= 0:
                    self.start_warning()

            elif self.mower_state == "warning":
                self.warning_timer -= step

                if self.warning_timer <= 0:
                    self.mower_state = "active"
                    self.mower_timer = 0.0

            elif self.mower_state == "active":
                self.mower_timer += step

                if self.mower_timer >= MOWER_STEP:
                    self.mower_timer -= MOWER_STEP
                    self.move_mower()

    def draw_warning(self):
        if self.mower_state != "warning":
            return

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA,
        )

        alpha = 60 if int(self.warning_timer * 8) % 2 else 110

        if self.mower_axis == "row":
            lane_rect = pygame.Rect(
                0,
                self.mower_lane * CELL_SIZE,
                WIDTH,
                CELL_SIZE,
            )
        else:
            lane_rect = pygame.Rect(
                self.mower_lane * CELL_SIZE,
                0,
                CELL_SIZE,
                HEIGHT,
            )

        pygame.draw.rect(
            overlay,
            (250, 204, 21, alpha),
            lane_rect,
        )

        screen.blit(overlay, (0, HUD_HEIGHT))

    def draw_snake(self):
        for index, position in enumerate(self.snake):
            color = HEAD_COLOR if index == 0 else SNAKE_COLOR

            if self.damage_timer > 0 and index != 0:
                color = "#F87171"

            pygame.draw.rect(
                screen,
                color,
                cell_rect(position, 1),
                border_radius=5,
            )

        head = cell_rect(self.snake[0])
        cx, cy = head.center
        dx, dy = self.direction

        if dx:
            eyes = [
                (cx + dx * 5, cy - 4),
                (cx + dx * 5, cy + 4),
            ]
        else:
            eyes = [
                (cx - 4, cy + dy * 5),
                (cx + 4, cy + dy * 5),
            ]

        for eye in eyes:
            pygame.draw.circle(screen, BG, eye, 2)

    def draw_mower(self):
        if self.mower_state != "active":
            return

        if self.mower_position is None:
            return

        x, y = self.mower_position

        if not (0 <= x < COLS and 0 <= y < ROWS):
            return

        rect = cell_rect(self.mower_position)
        body = rect.inflate(-4, -4)

        pygame.draw.rect(
            screen,
            MOWER_COLOR,
            body,
            border_radius=4,
        )

        dx, dy = self.mower_direction

        if dx:
            wheels = [
                (rect.x + 3, rect.y),
                (rect.x + 12, rect.y),
                (rect.x + 3, rect.bottom - 4),
                (rect.x + 12, rect.bottom - 4),
            ]

            blade_center = (
                rect.centerx + dx * 5,
                rect.centery,
            )

        else:
            wheels = [
                (rect.x, rect.y + 3),
                (rect.right - 4, rect.y + 3),
                (rect.x, rect.y + 12),
                (rect.right - 4, rect.y + 12),
            ]

            blade_center = (
                rect.centerx,
                rect.centery + dy * 5,
            )

        for wx, wy in wheels:
            pygame.draw.rect(
                screen,
                "#64748B",
                (wx, wy, 4, 5),
            )

        pygame.draw.circle(
            screen,
            "#FDE68A",
            blade_center,
            4,
        )

    def draw_hud(self):
        pygame.draw.rect(
            screen,
            "#111C2E",
            (0, 0, WIDTH, HUD_HEIGHT),
        )

        draw_text(f"Score: {self.score}", (14, 10))
        draw_text(f"Length: {len(self.snake)}", (150, 10))

        draw_text(
            f"Best: {self.high_score}",
            (290, 10),
            WARNING_COLOR,
        )

        draw_text(
            "R: restart   P / Space: pause",
            (14, 36),
            "#94A3B8",
            small_font,
        )

        if self.mower_state == "warning":
            direction_name = {
                (1, 0): "RIGHT",
                (-1, 0): "LEFT",
                (0, 1): "DOWN",
                (0, -1): "UP",
            }[self.mower_direction]

            draw_text(
                "WARNING: MOWER INCOMING!",
                (420, 10),
                WARNING_COLOR,
                small_font,
            )

            draw_text(
                f"Direction: {direction_name}",
                (420, 34),
                WARNING_COLOR,
                small_font,
            )

        elif self.mower_state == "active":
            draw_text(
                "MOWER ACTIVE!",
                (570, 10),
                MOWER_COLOR,
                small_font,
            )

        else:
            draw_text(
                f"Next mower: {max(0, self.mower_wait):.0f}s",
                (570, 10),
                "#94A3B8",
                small_font,
            )

    def draw_overlay(self, title, subtitle):
        overlay = pygame.Surface(
            screen.get_size(),
            pygame.SRCALPHA,
        )

        overlay.fill((0, 0, 0, 185))
        screen.blit(overlay, (0, 0))

        draw_centered(title, 235, large_font)
        draw_centered(subtitle, 305, font)

        draw_centered(
            f"Score: {self.score}   Best: {self.high_score}   "
            f"Length: {len(self.snake)}",
            345,
            font,
            HEAD_COLOR,
        )

        draw_centered(
            "R: restart    Esc: quit",
            390,
            font,
        )

    def draw(self):
        screen.fill(BG)

        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(
                screen,
                GRID,
                (x, HUD_HEIGHT),
                (x, HUD_HEIGHT + HEIGHT),
            )

        for y in range(
            HUD_HEIGHT,
            HEIGHT + HUD_HEIGHT,
            CELL_SIZE,
        ):
            pygame.draw.line(
                screen,
                GRID,
                (0, y),
                (WIDTH, y),
            )

        self.draw_warning()

        if self.food is not None:
            pygame.draw.rect(
                screen,
                FOOD_COLOR,
                cell_rect(self.food, 3),
                border_radius=5,
            )

        self.draw_snake()
        self.draw_mower()
        self.draw_hud()

        if self.damage_timer > 0:
            draw_centered(
                self.damage_message,
                HUD_HEIGHT + 12,
                font,
                "#F87171",
            )

        if self.dead:
            self.draw_overlay("GAME OVER", self.reason)

        elif self.won:
            self.draw_overlay("YOU WIN!", self.reason)

        elif self.paused:
            self.draw_overlay(
                "PAUSED",
                "Press P or Space to continue",
            )

        pygame.display.flip()


def main():
    game = Game()
    running = True

    key_directions = {
        pygame.K_UP: (0, -1),
        pygame.K_w: (0, -1),
        pygame.K_DOWN: (0, 1),
        pygame.K_s: (0, 1),
        pygame.K_LEFT: (-1, 0),
        pygame.K_a: (-1, 0),
        pygame.K_RIGHT: (1, 0),
        pygame.K_d: (1, 0),
    }

    while running:
        dt = min(clock.tick(60) / 1000.0, 0.1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.WINDOWFOCUSLOST:
                if not game.dead and not game.won:
                    game.paused = True

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_r:
                    game.reset()

                elif event.key in (
                    pygame.K_p,
                    pygame.K_SPACE,
                ):
                    if not game.dead and not game.won:
                        game.paused = not game.paused

                elif (
                    event.key in key_directions
                    and not game.paused
                    and not game.dead
                    and not game.won
                ):
                    game.queue_turn(key_directions[event.key])

        if running:
            game.update(dt)
            game.draw()

    save_high_score(game.high_score)
    pygame.quit()


if __name__ == "__main__":
    main()
