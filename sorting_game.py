import pygame
import random
import sys
import time
from datetime import datetime
import sqlite3

DB_PATH = "database.db"



def connect_db():
    return sqlite3.connect(DB_PATH)


def create_progress_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS progress_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            game_name TEXT NOT NULL,
            best_level INTEGER DEFAULT 0,
            best_time REAL,
            mistakes INTEGER DEFAULT 0,
            last_played DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(username, game_name)
        )
    ''')
    conn.commit()
    conn.close()


def get_progress(username, game_name):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT best_level, best_time, mistakes, last_played
        FROM progress_tracking
        WHERE username=? AND game_name=?
    ''', (username, game_name))
    row = cursor.fetchone()
    conn.close()
    return row


def update_progress(username, game_name, level, time_sec, mistakes):
    conn = connect_db()
    cursor = conn.cursor()
    now = datetime.now()
    cursor.execute(
        'SELECT best_level, best_time FROM progress_tracking WHERE username=? AND game_name=?',
        (username, game_name)
    )
    existing = cursor.fetchone()
    if existing:
        best_level, best_time = existing
        if level > best_level or (level == best_level and (best_time is None or time_sec < best_time)):
            cursor.execute('''
                UPDATE progress_tracking
                SET best_level=?, best_time=?, mistakes=?, last_played=?
                WHERE username=? AND game_name=?
            ''', (level, time_sec, mistakes, now, username, game_name))
    else:
        cursor.execute(
            '''
            INSERT INTO progress_tracking (username, game_name, best_level, best_time, mistakes)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (username, game_name, level, time_sec, mistakes)
        )
    conn.commit()
    conn.close()


def sorting_easy(current_username):
    # Colors and constants
    NAVY = (23, 34, 85)
    FRAME_GREEN = (136, 176, 75)
    CREAM_BG = (247, 231, 206)
    BLACK = (0, 0, 0)
    CORAL_RED = (255, 111, 97)
    PALETTE_GREEN = (136, 176, 75)
    PERIWINKLE = (146, 141, 209)
    YELLOW = (249, 199, 79)
    PURPLE = (247, 202, 201)

    LEVEL_COLORS = [
        [CORAL_RED, PALETTE_GREEN],
        [CORAL_RED, PALETTE_GREEN, PERIWINKLE],
        [CORAL_RED, PALETTE_GREEN, PERIWINKLE, YELLOW],
        [CORAL_RED, PALETTE_GREEN, PERIWINKLE, YELLOW, PURPLE]
    ]
    LEVEL_THRESHOLDS = [5, 12, 20]
    WIDTH, HEIGHT = 800, 600
    CONTENT_MARGIN = 20
    FPS = 60
    CIRCLE_RADIUS = 32
    BIN_HEIGHT = 120
    TIMER_SECONDS = 110

    # Setup DB
    create_progress_table()

    # Init Pygam
    pygame.init()
    try:
        icon = pygame.image.load('logo.png')
        pygame.display.set_icon(icon)
    except Exception:
        pass
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Color Sort")
    clock = pygame.time.Clock()

    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill(FRAME_GREEN)
    content_rect = pygame.Rect(
        CONTENT_MARGIN,
        CONTENT_MARGIN,
        WIDTH - 2 * CONTENT_MARGIN,
        HEIGHT - 2 * CONTENT_MARGIN
    )
    pygame.draw.rect(background, CREAM_BG, content_rect)

    font = pygame.font.SysFont(None, 36)
    big_font = pygame.font.SysFont(None, 72)

    # Progress tracking
    username = current_username
    game_name = 'color_sort_easy'
    progress = get_progress(username, game_name)
    if progress:
        best_level, best_time, total_mistakes, last_played = progress
        print(f"Welcome back! Best level: {best_level + 1}, Last played: {last_played}")
    else:
        best_level = 0
        total_mistakes = 0
        print("First time playing! Good luck!")

    current_level = 0
    score = 0
    mistakes = 0
    start_time = time.time()
    game_start_time = datetime.now()

    class Circle:
        def __init__(self, colors, content_rect):
            self.colors = colors
            self.color = random.choice(colors)
            self.content_rect = content_rect
            self.reset_position()

        def reset_position(self):
            left = self.content_rect.left + CIRCLE_RADIUS
            right = self.content_rect.right - CIRCLE_RADIUS
            top = self.content_rect.top + CIRCLE_RADIUS
            bottom_third = self.content_rect.top + self.content_rect.height // 3
            self.x = random.randint(left, right)
            self.y = random.randint(top, bottom_third)
            self.dragging = False
            self.offset_x = self.offset_y = 0

        def draw(self, surface):
            pygame.draw.circle(surface, self.color, (self.x, self.y), CIRCLE_RADIUS)
            pygame.draw.circle(surface, BLACK, (self.x, self.y), CIRCLE_RADIUS, 2)

        def is_mouse_over(self, pos):
            return (pos[0] - self.x) ** 2 + (pos[1] - self.y) ** 2 <= CIRCLE_RADIUS ** 2

        def start_drag(self, pos):
            self.dragging = True
            self.offset_x = self.x - pos[0]
            self.offset_y = self.y - pos[1]

        def stop_drag(self):
            self.dragging = False

        def update_position(self, pos):
            if self.dragging:
                self.x = pos[0] + self.offset_x
                self.y = pos[1] + self.offset_y

    class Bin:
        def __init__(self, color, idx, total, content_rect):
            self.color = color
            width = content_rect.width // total
            self.rect = pygame.Rect(
                content_rect.left + idx * width,
                content_rect.bottom - BIN_HEIGHT,
                width,
                BIN_HEIGHT
            )

        def draw(self, surface):
            pygame.draw.rect(surface, self.color, self.rect)
            pygame.draw.rect(surface, BLACK, self.rect, 4)

        def contains(self, circle):
            return self.rect.collidepoint(circle.x, circle.y)

    bins = [Bin(col, i, len(LEVEL_COLORS[current_level]), content_rect)
            for i, col in enumerate(LEVEL_COLORS[current_level])]
    circle = Circle(LEVEL_COLORS[current_level], content_rect)

    running = True
    while running:
        clock.tick(FPS)
        elapsed = time.time() - start_time
        remaining = max(0, int(TIMER_SECONDS - elapsed))

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if circle.is_mouse_over(e.pos):
                    circle.start_drag(e.pos)
            elif e.type == pygame.MOUSEBUTTONUP and e.button == 1 and circle.dragging:
                circle.stop_drag()
                placed = False
                correct = False
                for b in bins:
                    if b.contains(circle):
                        placed = True
                        if b.color == circle.color:
                            score += 1
                            correct = True
                        else:
                            mistakes += 1
                        break
                if not placed:
                    mistakes += 1
                if correct and current_level < len(LEVEL_THRESHOLDS) and score >= LEVEL_THRESHOLDS[current_level]:
                    current_level += 1
                    screen.blit(background, (0, 0))
                    lvl_text = big_font.render(f"Level {current_level + 1}", True, NAVY)
                    screen.blit(lvl_text, ((WIDTH - lvl_text.get_width()) // 2, HEIGHT // 2 - 50))
                    pygame.display.flip()
                    pygame.time.wait(1500)
                    bins = [Bin(col, i, len(LEVEL_COLORS[current_level]), content_rect) for i, col in enumerate(LEVEL_COLORS[current_level])]
                circle = Circle(LEVEL_COLORS[current_level], content_rect)
            elif e.type == pygame.MOUSEMOTION:
                circle.update_position(e.pos)

        if remaining <= 0:
            running = False

        screen.blit(background, (0, 0))
        for b in bins:
            b.draw(screen)
        circle.draw(screen)

        # HUD with best level
        screen.blit(font.render(f"Score: {score}", True, NAVY), (content_rect.left + 10, content_rect.top + 10))
        screen.blit(font.render(f"Time: {remaining}s", True, NAVY), (content_rect.right - 140, content_rect.top + 10))
        screen.blit(font.render(f"Mistakes: {mistakes}", True, NAVY), (content_rect.left + 10, content_rect.top + 50))
        screen.blit(font.render(f"Level: {current_level + 1}", True, NAVY), (content_rect.right - 140, content_rect.top + 50))
        screen.blit(font.render(f"Best Lv: {best_level + 1}", True, NAVY), (content_rect.left + 10, content_rect.top + 90))
        pygame.display.flip()

    
    duration = (datetime.now() - game_start_time).total_seconds()
    update_progress(username, game_name, current_level, duration, mistakes)

    screen.blit(background, (0, 0))
    screen.blit(big_font.render("Game Over!", True, NAVY), (WIDTH // 2 - 150, HEIGHT // 2 - 80))
    screen.blit(font.render(f"Your Score: {score}", True, NAVY), (WIDTH // 2 - 100, HEIGHT // 2 - 20))
    screen.blit(font.render(f"Reached Lv: {current_level + 1}", True, NAVY), (WIDTH // 2 - 100, HEIGHT // 2 + 10))
    screen.blit(font.render(f"Mistakes: {mistakes}", True, NAVY), (WIDTH // 2 - 100, HEIGHT // 2 + 40))
    screen.blit(font.render(f"Time: {duration:.1f}s", True, NAVY), (WIDTH // 2 - 100, HEIGHT // 2 + 70))
    screen.blit(font.render(f"Best Lv: {best_level + 1}", True, CORAL_RED), (WIDTH // 2 - 100, HEIGHT // 2 + 100))
    pygame.display.flip()
    pygame.time.wait(4000)
    pygame.quit()
    sys.exit()