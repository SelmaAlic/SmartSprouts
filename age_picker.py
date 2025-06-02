import pygame
import os
import sys
import ctypes

from utils import resource_path
from game_picker import game_picker

def age_pkr(current_username, on_select=None):
    if on_select is None:
        on_select = game_picker

    print("Hello from age_picker!")
    info = pygame.display.Info()
    screen_width, screen_height = info.current_w, info.current_h - 40
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)

    pygame.display.set_caption("Smart Sprouts - Age picker")
    logo_path = resource_path(os.path.join("assets", "logo2.ico"))
    if os.path.exists(logo_path):
        try:
            pygame.display.set_icon(pygame.image.load(logo_path))
        except Exception:
            pass

    BG_COLOR = (44, 129, 2)
    FRAME_COLOR = (247, 231, 206)
    TEXT_COLOR = (23, 34, 85)
    LABEL_COLOR = (23, 34, 85)
    FONT = pygame.font.SysFont("Arial", 36, bold=True)
    LABEL_FONT = pygame.font.SysFont("Arial", 24, bold=True)

    btn_info = [
        {
            "img": "easy_btn.png",
            "label": "Age 3–5",
            "difficulty": "easy"
        },
        {
            "img": "difficult_btn.png",
            "label": "Age 6–8",
            "difficulty": "hard"
        }
    ]

    btn_w, btn_h = 180, 180
    btn_gap = 120

    btn_imgs = []
    for info in btn_info:
        img_path = resource_path(os.path.join("assets", info["img"]))
        img = pygame.image.load(img_path).convert_alpha()
        img = pygame.transform.smoothscale(img, (btn_w, btn_h))
        btn_imgs.append(img)

    running = True
    selected = None

    try:
        hand_cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_HAND)
        arrow_cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW)
    except Exception:
        hand_cursor = arrow_cursor = None

    current_cursor = None

    while running:
        width, height = screen.get_size()
        total_btns_w = btn_w * 2 + btn_gap
        start_x = (width - total_btns_w) // 2
        btn_y = height // 2 - btn_h // 2

        btn_rects = []
        labels = []
        label_rects = []

        for i, info in enumerate(btn_info):
            btn_x = start_x + i * (btn_w + btn_gap)
            btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
            btn_rects.append(btn_rect)
            label_surface = LABEL_FONT.render(info["label"], True, LABEL_COLOR)
            label_rect = label_surface.get_rect(center=(btn_x + btn_w // 2, btn_y + btn_h + 40))
            labels.append(label_surface)
            label_rects.append(label_rect)

        title_surface = FONT.render("Select Your Age", True, TEXT_COLOR)
        title_rect = title_surface.get_rect(center=(width // 2, height // 4))

        screen.fill(BG_COLOR)
        frame_rect = pygame.Rect(15, 15, width - 30, height - 30)
        pygame.draw.rect(screen, FRAME_COLOR, frame_rect, width=0)

        screen.blit(title_surface, title_rect)
        for i in range(2):
            screen.blit(btn_imgs[i], btn_rects[i].topleft)
            screen.blit(labels[i], label_rects[i].topleft)

        pygame.display.flip()

        mouse_pos = pygame.mouse.get_pos()
        over_button = any(rect.collidepoint(mouse_pos) for rect in btn_rects)
        if hand_cursor and arrow_cursor:
            if over_button and current_cursor != "hand":
                pygame.mouse.set_cursor(hand_cursor)
                current_cursor = "hand"
            elif not over_button and current_cursor != "arrow":
                pygame.mouse.set_cursor(arrow_cursor)
                current_cursor = "arrow"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                from landing_page import landing_page_pygame 
                landing_page_pygame()
                return
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(btn_rects):
                    if rect.collidepoint(event.pos):
                        selected = btn_info[i]["difficulty"]
                        running = False

    if on_select and selected:
        if sys.platform == 'win32':
            try:
                hwnd = pygame.display.get_wm_info()['window']
                ctypes.windll.user32.SetForegroundWindow(hwnd)
                ctypes.windll.user32.SetActiveWindow(hwnd)
            except KeyError:
                pass
        on_select(selected, current_username)
