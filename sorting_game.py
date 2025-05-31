import pygame
import random
import sys
import time
from datetime import datetime
import os

from database import init_db, ensure_user, get_progress, upsert_progress, get_unlocked_stickers, unlock_sticker

DB_PATH = "database.db"
GAME_NAME = "sorting_easy"
LEVEL_THRESHOLDS = [5, 12, 20]
MAX_TIERS = len(LEVEL_THRESHOLDS)
COLORS = ["red", "green", "blue", "yellow", "purple", "orange"]

FPS = 60
CIRCLE_RADIUS = 32
BIN_HEIGHT = 120
TIMER_SECONDS = 110
MARGIN = 20

username = None
unlocked_stickers = set()

def sorting_easy(user):
    global username, unlocked_stickers

    init_db(drop_existing=False)
    ensure_user(user)
    username = user
    unlocked_stickers = set(get_unlocked_stickers(username))

    pygame.init()

    info = pygame.display.Info()
    desktop_w, desktop_h = info.current_w, info.current_h

    screen = pygame.display.set_mode((desktop_w, desktop_h), pygame.RESIZABLE)
    pygame.display.set_caption("Color Sort")
    try:
        icon = pygame.image.load('logo.png')
        pygame.display.set_icon(icon)
    except:
        pass
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    big_font = pygame.font.SysFont(None, 72)

    prog = get_progress(username, GAME_NAME)
    best_score = prog.get("best_level", 0)

    game_start_time = datetime.now()

    class Circle:
        def __init__(self, colors, rect):
            self.colors = colors
            self.color = random.choice(colors)
            self.rect = rect
            self.reset()

        def reset(self):
            left = self.rect.left + CIRCLE_RADIUS
            right = self.rect.right - CIRCLE_RADIUS
            top = self.rect.top + CIRCLE_RADIUS
            bottom_third = self.rect.top + self.rect.height // 3
            self.x = random.randint(left, right)
            self.y = random.randint(top, bottom_third)
            self.dragging = False
            self.offset = (0, 0)

        def draw(self, surf):
            pygame.draw.circle(surf, self.color, (self.x, self.y), CIRCLE_RADIUS)
            pygame.draw.circle(surf, (0, 0, 0), (self.x, self.y), CIRCLE_RADIUS, 2)

        def over(self, pos):
            return (pos[0] - self.x)**2 + (pos[1] - self.y)**2 <= CIRCLE_RADIUS**2

        def start(self, pos):
            self.dragging = True
            self.offset = (self.x - pos[0], self.y - pos[1])

        def stop(self):
            self.dragging = False

        def move(self, pos):
            if self.dragging:
                self.x = pos[0] + self.offset[0]
                self.y = pos[1] + self.offset[1]

    class Bin:
        def __init__(self, color, idx, total, rect):
            w = rect.width // total
            self.color = color
            self.rect = pygame.Rect(
                rect.left + idx * w,
                rect.bottom - BIN_HEIGHT,
                w,
                BIN_HEIGHT
            )

        def draw(self, surf):
            pygame.draw.rect(surf, self.color, self.rect)
            pygame.draw.rect(surf, (0, 0, 0), self.rect, 4)

        def contains(self, c):
            return self.rect.collidepoint(c.x, c.y)

    def run_game():
        nonlocal screen

        score = 0
        mistakes = 0
        start_time = time.time()
        current_tier = 0
        circle = None

        while True:
            clock.tick(FPS)
            elapsed = time.time() - start_time
            remaining = max(0, int(TIMER_SECONDS - elapsed))

            w, h = screen.get_size()
            bg = pygame.Surface((w, h))
            bg.fill((136, 176, 75))
            content_rect = pygame.Rect(MARGIN, MARGIN, w - 2 * MARGIN, h - 2 * MARGIN)
            pygame.draw.rect(bg, (247, 231, 206), content_rect)
            screen.blit(bg, (0, 0))

            if remaining <= 0:
                break

            if circle is None:
                tier_colors = COLORS[:current_tier + 2]
                circle = Circle(tier_colors, content_rect)

            bins = [
                Bin(col, i, len(COLORS[:current_tier + 2]), content_rect)
                for i, col in enumerate(COLORS[:current_tier + 2])
            ]

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return None

                if e.type == pygame.VIDEORESIZE:
                    screen = pygame.display.set_mode((e.w, e.h), pygame.RESIZABLE)

                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if circle.over(e.pos):
                        circle.start(e.pos)

                if e.type == pygame.MOUSEBUTTONUP and e.button == 1 and circle.dragging:
                    circle.stop()
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

                    tier_colors = COLORS[:current_tier + 2]
                    circle = Circle(tier_colors, content_rect)

                    if correct and score >= LEVEL_THRESHOLDS[current_tier] and current_tier < MAX_TIERS - 1:
                        current_tier += 1

                if e.type == pygame.MOUSEMOTION:
                    circle.move(e.pos)

            for b in bins:
                b.draw(screen)
            circle.draw(screen)

            hud = [
                (f"Score: {score}", content_rect.left + 10, content_rect.top + 10),
                (f"Time: {remaining}s", content_rect.right - 140, content_rect.top + 10),
                (f"Mistakes: {mistakes}", content_rect.left + 10, content_rect.top + 50),
                (f"Level: {current_tier + 1}", content_rect.right - 140, content_rect.top + 50),
                (f"Best: {best_score}", content_rect.left + 10, content_rect.top + 90),
            ]
            for txt, x, y in hud:
                screen.blit(font.render(txt, True, (23, 34, 85)), (x, y))

            pygame.display.flip()

        return {"score": score, "mistakes": mistakes, "duration": time.time() - start_time}

    result = run_game()
    if result is None:
        pygame.quit()
        return

    score = result["score"]
    mistakes = result["mistakes"]
    duration = result["duration"]

    w, h = screen.get_size()
    screen.fill((247, 231, 206))
    txt = big_font.render(f"Time's up! Your score: {score}", True, (23, 34, 85))
    txt_rect = txt.get_rect(center=(w // 2, h // 2 - 50))
    screen.blit(txt, txt_rect)

    btn_w, btn_h = 200, 60
    btn_rect = pygame.Rect((w - btn_w) // 2, txt_rect.bottom + 30, btn_w, btn_h)
    pygame.draw.rect(screen, (44, 129, 2), btn_rect, border_radius=8)
    lbl = font.render("Try Again", True, (255, 255, 255))
    lbl_rect = lbl.get_rect(center=btn_rect.center)
    screen.blit(lbl, lbl_rect)
    pygame.display.flip()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                return
            if e.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((e.w, e.h), pygame.RESIZABLE)
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if btn_rect.collidepoint(e.pos):
                    upsert_progress(username, GAME_NAME, score, duration, mistakes)
                    _unlock_sorting_stickers(score)
                    pygame.quit()
                    return sorting_easy(username)

        clock.tick(FPS)

def _unlock_sorting_stickers(score):
    ACH = {
        LEVEL_THRESHOLDS[0]: "sorting1",
        LEVEL_THRESHOLDS[1]: "sorting2",
        LEVEL_THRESHOLDS[2]: "sorting3"
    }
    for thresh, st in ACH.items():
        if score >= thresh and st not in unlocked_stickers:
            unlock_sticker(username, st)
