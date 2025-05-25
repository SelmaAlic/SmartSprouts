#WORKING GAME PICKER

import pygame
import os
import sys
import ctypes  # For window focus on Windows

def game_picker(difficulty):
    """
    Pygame-based Game Picker.
    difficulty: "easy" or "hard"
    """
    # Callbacks
    def on_math():
        if difficulty == "easy":
            print("math_easy")
        else:
            print("math_hard")

    def on_sorting():
        if difficulty == "easy":
            print("sorting_easy")
        else:
            print("sorting_hard")

    def on_sequence():
        if difficulty == "easy":
            print("sequence_easy")
        else:
            print("sequence_hard")

    def on_memory():
        if difficulty == "easy":
            print("memory_easy")
        else:
            print("memory_hard")

    def on_cloud_sync():
        print("cloud sync")

    pygame.init()
    info = pygame.display.Info()
    screen_width, screen_height = info.current_w, info.current_h - 60
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    pygame.display.set_caption("Smart Sprouts - Game Picker")

    # ▶ ADDED: force window to foreground (Windows)
    if sys.platform == 'win32':
        hwnd = pygame.display.get_wm_info()['window']
        ctypes.windll.user32.SetForegroundWindow(hwnd)
        ctypes.windll.user32.SetActiveWindow(hwnd)

    # ▶ ADDED: clear any focus-stealing events
    pygame.event.clear()

    # Colors & fonts
    BG_COLOR    = (44, 129, 2)
    FRAME_COLOR = (247, 231, 206)
    TEXT_COLOR  = (23, 34, 85)
    LABEL_FONT  = pygame.font.SysFont("Arial", 14, bold=True)
    TITLE_FONT  = pygame.font.SysFont("Arial", 36, bold=True)

    # Cloud icon/text
    cloud_icon_path = os.path.join("assets", "cloud_sync_btn.png")
    if os.path.exists(cloud_icon_path):
        cloud_img = pygame.image.load(cloud_icon_path).convert_alpha()
        cloud_img = pygame.transform.smoothscale(cloud_img, (80, 80))
    else:
        cloud_img = None
        cloud_text = LABEL_FONT.render("Cloud Sync", True, TEXT_COLOR)

    # Logo
    logo_path = os.path.join("assets", "logo.png")
    logo_img = pygame.image.load(logo_path).convert_alpha()
    logo_img = pygame.transform.smoothscale(logo_img, (480, 280))

    # Button setup
    btn_info = [
        {"img": "math_btn.png",     "label": "Math Game",    "callback": on_math},
        {"img": "sorting_btn.png",  "label": "Sorting",      "callback": on_sorting},
        {"img": "sequence_btn.png", "label": "Sequences",    "callback": on_sequence},
        {"img": "memory_btn.png",   "label": "Memory Cards", "callback": on_memory},
    ]
    btn_w, btn_h = 140, 140
    btn_gap_x, btn_gap_y = 60, 80
    btn_surfaces = []
    for info in btn_info:
        surf = pygame.image.load(os.path.join("assets", info["img"]))
        surf = pygame.transform.smoothscale(surf, (btn_w, btn_h))
        btn_surfaces.append(surf)

    running = True
    while running:
        screen.fill(BG_COLOR)
        width, height = screen.get_size()
        pygame.draw.rect(screen, FRAME_COLOR, (10, 10, width-20, height-20))

        # Title & logo
        screen.blit(TITLE_FONT.render("Select a Game", True, TEXT_COLOR), TITLE_FONT.render("Select a Game", True, TEXT_COLOR).get_rect(center=(width//2,50)))
        screen.blit(logo_img, logo_img.get_rect(center=(width//2,150)))

        # Cloud
        if cloud_img:
            c_rect = cloud_img.get_rect(topright=(width-20,20)); screen.blit(cloud_img, c_rect)
        else:
            c_rect = cloud_text.get_rect(topright=(width-20,40)); screen.blit(cloud_text, c_rect)

        # Buttons
        start_y = 250
        total_w = btn_w*2 + btn_gap_x
        start_x = (width-total_w)//2
        btn_rects = []
        for idx, surf in enumerate(btn_surfaces):
            r, c = divmod(idx,2)
            x = start_x + c*(btn_w+btn_gap_x)
            y = start_y + r*(btn_h+btn_gap_y)
            rect = pygame.Rect(x, y, btn_w, btn_h)
            btn_rects.append(rect)
            screen.blit(surf, (x,y))
            screen.blit(LABEL_FONT.render(btn_info[idx]["label"], True, TEXT_COLOR), LABEL_FONT.render(btn_info[idx]["label"], True, TEXT_COLOR).get_rect(center=(x+btn_w//2,y+btn_h+20)))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w,event.h), pygame.RESIZABLE)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                # Cloud
                if cloud_img and c_rect.collidepoint(pos) or (not cloud_img and c_rect.collidepoint(pos)):
                    on_cloud_sync(); running=False; break
                # Buttons
                for idx, rect in enumerate(btn_rects):
                    if rect.collidepoint(pos):
                        btn_info[idx]["callback"](); running=False; break

    pygame.quit()
    sys.exit()






















# WORKING AGE PICKER
import tkinter as tk
from PIL import Image, ImageTk
import os
from game_picker import game_picker
import pygame
import sys
import ctypes  # For window focus on Windows

def age_picker(on_select=None):
    if on_select is None:
        on_select = game_picker

    pygame.init()

    info = pygame.display.Info()
    screen_width, screen_height = info.current_w, info.current_h - 60
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)

    pygame.display.set_caption("Smart Sprouts - Age picker")
    logo_path = os.path.join("assets", "logo2.ico")
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
        img_path = os.path.join("assets", info["img"])
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
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(btn_rects):
                    if rect.collidepoint(event.pos):
                        selected = btn_info[i]["difficulty"]
                        running = False

    pygame.quit()
    if on_select and selected:
        # Reinitialize Pygame for the next window
        pygame.init()
        pygame.event.clear()
        # Force window to foreground (Windows)
        if sys.platform == 'win32':
            try:
                hwnd = pygame.display.get_wm_info()['window']
                ctypes.windll.user32.SetForegroundWindow(hwnd)
                ctypes.windll.user32.SetActiveWindow(hwnd)
            except KeyError:
                pass  # Handle the case where 'window' key is not available
        on_select(selected)

