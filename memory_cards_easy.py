import pygame
import random
import os
import math
from utils import resource_path
from database import (
    upsert_progress,
    unlock_sticker,
    get_progress,
    get_unlocked_stickers,
    ensure_user,
    init_db,
    connect_db
)


MAX_LEVEL = 10
pygame.init()
WIDTH, HEIGHT = 1300, 780

script_dir = os.path.dirname(os.path.abspath(__file__))
image_folder = resource_path(os.path.join(script_dir, "assets"))
font_path = resource_path("assets/Pixellettersful.ttf")
font = pygame.font.Font(font_path, 46)

BUTTON_WIDTH, BUTTON_HEIGHT = 200, 50
BUTTON_GAP = 40
HEADER_HEIGHT = 150
BUTTONS_HEIGHT = 100
PADDING = 20
GREEN = (44, 129, 2)
BORDER_THICKNESS = 12
CARD_WIDTH, CARD_HEIGHT = 280, 220
MARGIN = 10
total_images = 7


class Button:
    def __init__(self, text, x, y, width=300, height=100):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = (0, 200, 0)
        self.hover_color = (0, 255, 0)

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        surface.blit(text_surf, text_rect)

def get_level_images(level, used_images):
    if level < 2:
        pairs = 2
    elif level < 6:
        pairs = 3
    else:
        pairs = 6
    available = list(set(range(1, total_images + 1)) - used_images)
    if len(available) < pairs:
        used_images.clear()
        available = list(range(1, total_images + 1))
    selected = random.sample(available, pairs)
    used_images.update(selected)
    return [pygame.image.load(os.path.join(image_folder, f"memory_easy{i}.png")).convert_alpha() for i in selected]

def calculate_centered_grid(card_count, current_width, current_height, card_width, card_height, margin=10, min_card_size=20):
    options = []
    for cols in range(1, card_count + 1):
        rows = math.ceil(card_count / cols)
        grid_w = cols * (card_width + margin) - margin
        grid_h = rows * (card_height + margin) - margin
        if grid_w <= current_width and grid_h <= current_height:
            options.append((rows, cols, grid_w, grid_h, card_width, card_height))
    if options:
        rows, cols, grid_w, grid_h, card_w, card_h = min(options, key=lambda x: (abs(x[0] - x[1]), -x[1]))
    else:
        best = None
        for cols in range(1, card_count + 1):
            rows = math.ceil(card_count / cols)
            scale_w = (current_width - margin * (cols - 1)) / cols
            scale_h = (current_height - margin * (rows - 1)) / rows
            scale = min(scale_w / card_width, scale_h / card_height, 1.0)
            new_card_w = max(int(card_width * scale), min_card_size)
            new_card_h = max(int(card_height * scale), min_card_size)
            grid_w = cols * (new_card_w + margin) - margin
            grid_h = rows * (new_card_h + margin) - margin
            if grid_w <= current_width and grid_h <= current_height:
                if best is None or abs(rows - cols) < abs(best[0] - best[1]):
                    best = (rows, cols, grid_w, grid_h, new_card_w, new_card_h)
        if best:
            rows, cols, grid_w, grid_h, card_w, card_h = best
        else:
            cols = max(1, min(card_count, current_width // (min_card_size + margin)))
            rows = math.ceil(card_count / cols)
            card_w = card_h = min_card_size
            grid_w = cols * (card_w + margin) - margin
            grid_h = rows * (card_h + margin) - margin
    start_x = (current_width - grid_w) // 2
    start_y = (current_height - grid_h) // 2
    return rows, cols, start_x, start_y, card_w, card_h, grid_w, grid_h

def memory_cards_easy(current_difficulty, username):
    GAME_NAME = "memory_easy"
    MAX_LEVEL = 10
    difficulty = current_difficulty
    progress = get_progress(username, GAME_NAME)
    unlocked_stickers = set(get_unlocked_stickers(username))

    if progress['best_level'] >= MAX_LEVEL:
        game_completed = True
        current_level = MAX_LEVEL
    elif progress['best_level'] > 0:
        current_level = progress['best_level']
        game_completed = False
    else:
        current_level = 1
        game_completed = False

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    logo_original = pygame.image.load(os.path.join(image_folder, 'logo.png')).convert_alpha()
    logo_icon = pygame.transform.smoothscale(logo_original, (32, 32))
    pygame.display.set_caption("Memory Card Game")
    pygame.display.set_icon(logo_icon)
    clock = pygame.time.Clock()

    used_images = set()
    running = True
    level_completed = False
    cards = []
    card_states = []
    flipped_indices = []
    wait_time = 0
    card_back = pygame.image.load(os.path.join(image_folder, 'memory_back.png'))
    total_mistakes = 0

    achievements = {
        "finish_1_level": "memory1",
        "finish_3_levels": "memory2",
        "finish_all_levels": "memory3"
    }
    achievement_popups = []
    ACHIEVEMENT_POPUP_DURATION = 2000

    def unlock_sticker_achievement(achievement_key):
        sticker_name = achievements[achievement_key]
        if sticker_name not in unlocked_stickers:
            unlock_sticker(username, sticker_name)
            unlocked_stickers.add(sticker_name)
            achievement_popups.append((sticker_name, pygame.time.get_ticks()))
            print(f"Sticker unlocked for achievement: {sticker_name}")

    def check_achievements(level):
        if level == 1:
            unlock_sticker_achievement("finish_1_level")
        if level == 3:
            unlock_sticker_achievement("finish_3_levels")
        if level == MAX_LEVEL:
            unlock_sticker_achievement("finish_all_levels")

    def initialize_level():
        nonlocal cards, card_states, flipped_indices, wait_time, level_completed, rows, cols, start_x, start_y, card_w, card_h, grid_width, grid_height
        images = get_level_images(current_level, used_images)
        cards = images * 2
        random.shuffle(cards)
        current_width, current_height = screen.get_width(), screen.get_height()
        available_height = current_height - HEADER_HEIGHT - BUTTONS_HEIGHT - PADDING
        rows, cols, start_x, start_y, card_w, card_h, grid_width, grid_height = calculate_centered_grid(
            card_count=len(cards),
            current_width=current_width,
            current_height=available_height,
            card_width=CARD_WIDTH,
            card_height=CARD_HEIGHT,
            margin=MARGIN,
            min_card_size=60
        )
        start_y += HEADER_HEIGHT
        card_states = ["hidden"] * len(cards)
        flipped_indices = []
        wait_time = 0
        level_completed = False
        return rows, cols, start_x, start_y, card_w, card_h, grid_width, grid_height

    rows, cols, start_x, start_y, card_w, card_h, grid_width, grid_height = initialize_level()
    wait_time = 0
    wait_indices = []

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                current_width, current_height = event.w, event.h
                available_height = current_height - HEADER_HEIGHT - BUTTONS_HEIGHT - PADDING
                rows, cols, start_x, start_y, card_w, card_h, grid_width, grid_height = calculate_centered_grid(
                    card_count=len(cards),
                    current_width=current_width,
                    current_height=available_height,
                    card_width=CARD_WIDTH,
                    card_height=CARD_HEIGHT,
                    margin=MARGIN,
                    min_card_size=60
                )
                start_y += HEADER_HEIGHT

            if not game_completed and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if level_completed:
                    current_width, current_height = screen.get_width(), screen.get_height()
                    buttons_y = start_y + grid_height + 30
                    total_buttons_width = BUTTON_WIDTH * 2 + BUTTON_GAP
                    buttons_start_x = (current_width - total_buttons_width) // 2
                    prev_level_button = Button("Previous", buttons_start_x, buttons_y, BUTTON_WIDTH, BUTTON_HEIGHT)
                    next_level_button = Button("Next", buttons_start_x + BUTTON_WIDTH + BUTTON_GAP, buttons_y, BUTTON_WIDTH, BUTTON_HEIGHT)
                    if current_level < MAX_LEVEL and next_level_button.rect.collidepoint(event.pos):
                        current_level += 1
                        rows, cols, start_x, start_y, card_w, card_h, grid_width, grid_height = initialize_level()
                        level_completed = False
                        total_mistakes = 0
                    elif current_level > 1 and prev_level_button.rect.collidepoint(event.pos):
                        current_level -= 1
                        used_images.clear()
                        rows, cols, start_x, start_y, card_w, card_h, grid_width, grid_height = initialize_level()
                        level_completed = False
                        total_mistakes = 0
                else:
                    mouse_pos = event.pos
                    for idx in range(len(cards)):
                        row = idx // cols
                        col = idx % cols
                        x = start_x + col * (card_w + MARGIN)
                        y = start_y + row * (card_h + MARGIN)
                        rect = pygame.Rect(x, y, card_w, card_h)
                        if rect.collidepoint(mouse_pos):
                            if card_states[idx] == "hidden" and len(flipped_indices) < 2 and wait_time == 0:
                                card_states[idx] = "flipped"
                                flipped_indices.append(idx)
                            break

        if not level_completed and len(flipped_indices) == 2 and wait_time == 0:
            i1, i2 = flipped_indices
            if cards[i1] == cards[i2]:
                card_states[i1] = card_states[i2] = "matched"
                flipped_indices.clear()
            else:
                wait_time = pygame.time.get_ticks()
                wait_indices = [i1, i2]
                total_mistakes += 1

        if wait_time and pygame.time.get_ticks() - wait_time > 1000:
            for idx in wait_indices:
                if card_states[idx] != "matched":
                    card_states[idx] = "hidden"
            flipped_indices.clear()
            wait_time = 0
            wait_indices = []

        current_width, current_height = screen.get_width(), screen.get_height()
        available_height = current_height - HEADER_HEIGHT - BUTTONS_HEIGHT - PADDING

        logo_height = int(HEADER_HEIGHT * 0.8)
        logo_width = int(logo_original.get_width() * (logo_height / logo_original.get_height()))
        logo_resized = pygame.transform.smoothscale(logo_original, (logo_width, logo_height))

        screen.fill((247, 231, 206))
        pygame.draw.rect(screen, GREEN, (0, 0, current_width, current_height), BORDER_THICKNESS)

        screen.blit(logo_resized, (10, 10))
        level_text = font.render(f"Level {current_level}", True, (23, 34, 85))
        screen.blit(level_text, (logo_width + 30, 40))

        for idx, card_img in enumerate(cards):
            row = idx // cols
            col = idx % cols
            x = start_x + col * (card_w + MARGIN)
            y = start_y + row * (card_h + MARGIN)
            rect = pygame.Rect(x, y, card_w, card_h)
            if card_states[idx] in ["matched", "flipped"]:
                screen.blit(pygame.transform.smoothscale(card_img, (card_w, card_h)), rect.topleft)
            else:
                screen.blit(pygame.transform.smoothscale(card_back, (card_w, card_h)), rect.topleft)

        if not level_completed and all(state == "matched" for state in card_states):
            level_completed = True
            check_achievements(current_level)
            upsert_progress(
                username=username,
                game_name=GAME_NAME,
                best_level=max(current_level, progress['best_level']),
                best_time=None, 
                mistakes=total_mistakes
            )
            if current_level >= MAX_LEVEL:
                game_completed = True

        if level_completed and not game_completed:
            buttons_y = start_y + grid_height + 30
            total_buttons_width = BUTTON_WIDTH * 2 + BUTTON_GAP
            buttons_start_x = (current_width - total_buttons_width) // 2
            prev_level_button = Button("Previous", buttons_start_x, buttons_y, BUTTON_WIDTH, BUTTON_HEIGHT)
            next_level_button = Button("Next", buttons_start_x + BUTTON_WIDTH + BUTTON_GAP, buttons_y, BUTTON_WIDTH, BUTTON_HEIGHT)
            if current_level > 1:
                prev_level_button.draw(screen)
            if current_level < MAX_LEVEL:
                next_level_button.draw(screen)

        if game_completed:
            screen.fill((247, 231, 206))
            congrats_text = font.render("Congratulations! You finished all levels!", True, (23, 34, 85))
            text_rect = congrats_text.get_rect(center=(current_width // 2, current_height // 2 - 40))
            screen.blit(congrats_text, text_rect)

            play_again_w, play_again_h = 260, 80
            play_again_x = (current_width - play_again_w) // 2
            play_again_y = text_rect.bottom + 30
            play_again_button_rect = pygame.Rect(play_again_x, play_again_y, play_again_w, play_again_h)
            pygame.draw.rect(screen, (70, 130, 180), play_again_button_rect, border_radius=10)
            btn_label = font.render("Play Again", True, (255, 255, 255))
            btn_label_rect = btn_label.get_rect(center=play_again_button_rect.center)
            screen.blit(btn_label, btn_label_rect)
            pygame.display.flip()

            play_again_handled = False
            while not play_again_handled:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        play_again_handled = True
                    elif event.type == pygame.VIDEORESIZE:
                        screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                        current_width, current_height = event.w, event.h
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if play_again_button_rect.collidepoint(event.pos):
                            upsert_progress(username, GAME_NAME, 1, None, 0)
                            current_level = 1
                            used_images.clear()
                            rows, cols, start_x, start_y, card_w, card_h, grid_width, grid_height = initialize_level()
                            play_again_handled = True
                            game_completed = False
                clock.tick(60)
            continue

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    from game_picker import game_picker
    game_picker(difficulty, username) 

   