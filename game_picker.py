import pygame
import os
import sys
import ctypes

from math_game_easy import math_easy
from math_game_hard import math_hard
from sequence_game import sequence_easy
from SequenceGameHard import sequence_hard
from sorting_game import sorting_easy
from sorting_numbers_game import sorting_hard

def game_picker(difficulty, current_username):
    def on_math():
        if difficulty == "easy":
            math_easy()
        else:
            math_hard()

    def on_sorting():
        if difficulty == "easy":
            sorting_easy(current_username)
        else:
            sorting_hard(current_username)

    def on_sequence():
        if difficulty == "easy":
            sequence_easy(current_username)
        else:
            sequence_hard(current_username)

    def on_memory():
        if difficulty == "easy":
            print("-")
            #print("memory_easy")
        else:
            print("-")
            #print("memory_hard")

    def on_cloud_sync():
        print("cloud sync")

    pygame.init()
    info = pygame.display.Info()
    screen_width, screen_height = info.current_w, info.current_h - 60
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    pygame.display.set_caption("Smart Sprouts - Game Picker")

    if sys.platform == 'win32':
        hwnd = pygame.display.get_wm_info()['window']
        ctypes.windll.user32.SetForegroundWindow(hwnd)
        ctypes.windll.user32.SetActiveWindow(hwnd)

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
    logo_path = os.path.join("assets", "logoSelma.png")
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
