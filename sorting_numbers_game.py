import pygame
import random
import sys
import time
from datetime import datetime
from utils import resource_path

from database import (
    init_db,
    ensure_user,
    get_progress,
    upsert_progress,
    get_unlocked_stickers,
    unlock_sticker
)

DB_PATH = "database.db"
GAME_NAME = "sorting_hard"
LEVEL_RANGES = [
    [(1, 5), (6, 10)],
    [(1, 10), (11, 20), (21, 30)],
    [(1, 20), (21, 40), (41, 60), (61, 80)],
    [(1, 50), (51, 100), (101, 150), (151, 200), (201, 250)]
]
LEVEL_THRESHOLDS = [5, 12, 20]
BIN_COLORS = [
    (136, 176, 75),
    (255, 111, 97),
    (146, 168, 209),
    (249, 199, 79),
    (147, 112, 219)
]
NAVY = (23, 34, 85)
FRAME_GREEN = (136, 176, 75)
CREAM_BG = (247, 231, 206)
BLACK = (0, 0, 0)

WIDTH, HEIGHT = 800, 600
FPS = 60
RADIUS = 40
BIN_HEIGHT = 120
TIMER_SECONDS = 110
MARGIN = 20

username = None
unlocked_stickers = set()

def sorting_hard(difficulty, current_username):
    global username, unlocked_stickers

    init_db(drop_existing=False)
    ensure_user(current_username)
    username = current_username
    unlocked_stickers = set(get_unlocked_stickers(username))
    progress = get_progress(username, GAME_NAME)
    best_level = progress.get("best_level", 0)

    pygame.init()
    try:
        icon = resource_path(pygame.image.load("logo.png"))
        pygame.display.set_icon(icon)
    except:
        pass

    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Number Sort - Hard")
    clock = pygame.time.Clock()

    num_font = pygame.font.SysFont(None, 48)
    hud_font = pygame.font.SysFont(None, 36)
    msg_font = pygame.font.SysFont(None, 72)

    bg_surface = pygame.Surface((WIDTH, HEIGHT))
    bg_surface.fill(FRAME_GREEN)
    content_rect = pygame.Rect(MARGIN, MARGIN, WIDTH - 2 * MARGIN, HEIGHT - 2 * MARGIN)
    pygame.draw.rect(bg_surface, CREAM_BG, content_rect)

    level = 0
    score = 0
    mistakes = 0
    start_time = time.time()
    game_start_dt = datetime.now()

    ACHIEVEMENTS = {
        LEVEL_THRESHOLDS[0]: "sorting1",
        LEVEL_THRESHOLDS[1]: "sorting2",
        LEVEL_THRESHOLDS[2]: "sorting3"
    }

    class CircleObj:
        def __init__(self, lo, hi):
            self.lo, self.hi = lo, hi
            self.reset()

        def reset(self):
            self.number = random.randint(self.lo, self.hi)
            left = content_rect.left + RADIUS
            right = content_rect.right - RADIUS
            top = content_rect.top + RADIUS
            bottom_third = content_rect.top + content_rect.height // 3
            self.x = random.randint(left, right)
            self.y = random.randint(top, bottom_third)
            self.drag = False
            self.ox = self.oy = 0

        def draw(self):
            pygame.draw.circle(screen, (146, 168, 209), (self.x, self.y), RADIUS)
            pygame.draw.circle(screen, BLACK, (self.x, self.y), RADIUS, 2)
            txt = num_font.render(str(self.number), True, BLACK)
            screen.blit(txt, (self.x - txt.get_width() // 2, self.y - txt.get_height() // 2))

        def hover(self, pos):
            dx = pos[0] - self.x
            dy = pos[1] - self.y
            return dx * dx + dy * dy <= RADIUS * RADIUS

        def start(self, pos):
            self.drag = True
            self.ox = self.x - pos[0]
            self.oy = self.y - pos[1]

        def stop(self):
            self.drag = False

        def update(self, pos):
            if self.drag:
                self.x = pos[0] + self.ox
                self.y = pos[1] + self.oy

    class BinObj:
        def __init__(self, lo, hi, idx, total):
            self.lo, self.hi = lo, hi
            w = content_rect.width // total
            self.rect = pygame.Rect(
                content_rect.left + idx * w,
                content_rect.bottom - BIN_HEIGHT,
                w,
                BIN_HEIGHT
            )
            self.color = BIN_COLORS[idx]

        def draw(self):
            pygame.draw.rect(screen, self.color, self.rect)
            pygame.draw.rect(screen, BLACK, self.rect, 2)
            lbl = hud_font.render(f"{self.lo}-{self.hi}", True, BLACK)
            screen.blit(
                lbl,
                (self.rect.centerx - lbl.get_width() // 2,
                 self.rect.centery - lbl.get_height() // 2)
            )

        def contains(self, c_obj):
            return self.rect.collidepoint(c_obj.x, c_obj.y)

    curr_ranges = LEVEL_RANGES[level]
    bins = [BinObj(lo, hi, i, len(curr_ranges)) for i, (lo, hi) in enumerate(curr_ranges)]
    circle = CircleObj(curr_ranges[0][0], curr_ranges[-1][1])

    window_closed = False
    while True:
        clock.tick(FPS)
        rem = max(0, TIMER_SECONDS - int(time.time() - start_time))

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                window_closed = True
                break
            elif e.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((e.w, e.h), pygame.RESIZABLE)
                bg_surface = pygame.Surface((e.w, e.h))
                bg_surface.fill(FRAME_GREEN)
                content_rect.width = e.w - 2 * MARGIN
                content_rect.height = e.h - 2 * MARGIN
                content_rect.left = MARGIN
                content_rect.top = MARGIN
                pygame.draw.rect(bg_surface, CREAM_BG, content_rect)
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if circle.hover(e.pos):
                    circle.start(e.pos)
            elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                if circle.drag:
                    circle.stop()
                    placed = False
                    for b in bins:
                        if b.contains(circle):
                            placed = True
                            if b.lo <= circle.number <= b.hi:
                                score += 1
                                if level < len(LEVEL_THRESHOLDS) and score >= LEVEL_THRESHOLDS[level]:
                                    level += 1
                                    thresh = LEVEL_THRESHOLDS[level - 1]
                                    sticker_key = ACHIEVEMENTS.get(thresh)
                                    if sticker_key and (sticker_key not in unlocked_stickers):
                                        unlock_sticker(username, sticker_key)
                                        unlocked_stickers.add(sticker_key)
                                    screen.blit(bg_surface, (0, 0))
                                    surf = msg_font.render(f"Level {level+1}!", True, NAVY)
                                    sw, sh = screen.get_size()
                                    screen.blit(surf, ((sw - surf.get_width()) // 2,
                                                       (sh - surf.get_height()) // 2))
                                    pygame.display.flip()
                                    pygame.time.wait(1500)
                                    curr_ranges = LEVEL_RANGES[level]
                                    bins = [
                                        BinObj(lo, hi, i, len(curr_ranges))
                                        for i, (lo, hi) in enumerate(curr_ranges)
                                    ]
                            else:
                                mistakes += 1
                            curr_ranges = LEVEL_RANGES[level]
                            circle = CircleObj(curr_ranges[0][0], curr_ranges[-1][1])
                            break
                    if not placed:
                        mistakes += 1
            elif e.type == pygame.MOUSEMOTION:
                circle.update(e.pos)
        if window_closed:
            break
        if rem <= 0:
            break

        # Recompute bins on each frame to follow resized content_rect
        curr_ranges = LEVEL_RANGES[level]
        bins = [BinObj(lo, hi, i, len(curr_ranges)) for i, (lo, hi) in enumerate(curr_ranges)]

        screen.blit(bg_surface, (0, 0))
        for b in bins:
            b.draw()
        circle.draw()

        screen.blit(hud_font.render(f"Score: {score}", True, NAVY), (content_rect.left + 10, content_rect.top + 10))
        screen.blit(hud_font.render(f"Mistakes: {mistakes}", True, NAVY), (content_rect.left + 10, content_rect.top + 40))
        screen.blit(hud_font.render(f"Best Level: {best_level+1}", True, NAVY), (content_rect.left + 10, content_rect.top + 70))
        screen.blit(hud_font.render(f"Time: {rem}s", True, NAVY), (content_rect.right - 140, content_rect.top + 10))
        screen.blit(hud_font.render(f"Level: {level+1}", True, NAVY), (content_rect.right - 140, content_rect.top + 40))

        pygame.display.flip()

    if window_closed:
        pygame.quit()
        from game_picker import game_picker
        game_picker(difficulty, username)
        return

    screen.blit(bg_surface, (0, 0))
    over_surf = msg_font.render("Time's Up!", True, NAVY)
    score_surf = hud_font.render(f"Your Score: {score}", True, NAVY)
    sw, sh = screen.get_size()
    screen.blit(over_surf, ((sw - over_surf.get_width()) // 2, sh // 2 - 50))
    screen.blit(score_surf, ((sw - score_surf.get_width()) // 2, sh // 2 + 20))
    pygame.display.flip()
    pygame.time.wait(6000)

    elapsed = (datetime.now() - game_start_dt).total_seconds()
    upsert_progress(username, GAME_NAME, level, elapsed, mistakes)

    pygame.quit()
