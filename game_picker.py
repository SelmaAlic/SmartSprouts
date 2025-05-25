#Converted from Tkinter to Pygame, due to multiple instance of Tk issue
import pygame
import os
import sys

from math_game_easy import math_easy
from math_game_hard import math_hard

def game_picker(difficulty):

    def on_math():
        if difficulty == "easy":
            math_easy()
        else:
            math_hard

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
    info=pygame.display.Info()
    screen_width, screen_height = info.current_w, info.current_h
    screen = pygame.display.set_mode((screen_width,screen_height), pygame.RESIZABLE)
    pygame.display.set_caption("Smart Sprouts - Pick your game!")

    icon_path = os.path.join("assets", "logo2.ico")
    if os.path.exists(icon_path):
        try:
            pygame.display.set_icon(pygame.image.load(icon_path))
        except Exception:
            pass

    BG_COLOR     = (44, 129, 2)
    FRAME_COLOR  = (247, 231, 206)
    TEXT_COLOR   = (23, 34, 85)
    LABEL_FONT   = pygame.font.SysFont("Arial", 14, bold=True)
    TITLE_FONT   = pygame.font.SysFont("Arial", 36, bold=True)

    cloud_icon_path = os.path.join("assets", "cloud_sync_btn.png")
    if os.path.exists(cloud_icon_path):
        cloud_img = pygame.image.load(cloud_icon_path).convert_alpha()
        cloud_img = pygame.transform.smoothscale(cloud_img, (50, 50))
    else:
        cloud_img = None
        cloud_text = LABEL_FONT.render("Cloud Sync", True, TEXT_COLOR)

   
    logo_path = os.path.join("assets", "logo.png")
    logo_img = pygame.image.load(logo_path).convert_alpha()
    logo_img = pygame.transform.smoothscale(logo_img, (300, 175))

    btn_info = [
        {"img": "math_btn.png",     "label": "Math Game",    "callback": on_math},
        {"img": "sorting_btn.png",  "label": "Sorting",      "callback": on_sorting},
        {"img": "sequence_btn.png", "label": "Sequences",    "callback": on_sequence},
        {"img": "memory_btn.png",   "label": "Memory Cards", "callback": on_memory},
    ]

    btn_w, btn_h = 140, 140
    btn_gap_x = 60
    btn_gap_y = 80
    btn_surfaces = []
    for info in btn_info:
        path = os.path.join("assets", info["img"])
        surf = pygame.image.load(path).convert_alpha()
        surf = pygame.transform.smoothscale(surf, (btn_w, btn_h))
        btn_surfaces.append(surf)

    running = True
    while running:
        screen.fill(BG_COLOR)
        width, height = screen.get_size()

        pygame.draw.rect(screen, FRAME_COLOR, (10, 10, width-20, height-20))

        title_surf = TITLE_FONT.render("Select a Game", True, TEXT_COLOR)
        title_rect = title_surf.get_rect(center=(width//2, 50))
        screen.blit(title_surf, title_rect)

        logo_rect = logo_img.get_rect(center=(width//2, 150))
        screen.blit(logo_img, logo_rect)

        if cloud_img:
            cloud_rect = cloud_img.get_rect(topright=(width-20, 20))
            screen.blit(cloud_img, cloud_rect)
        else:
            cloud_rect = cloud_text.get_rect(topright=(width-20, 40))
            screen.blit(cloud_text, cloud_rect)

        start_y = 250
        total_width = btn_w*2 + btn_gap_x
        start_x = (width - total_width)//2

        btn_rects = []
        for idx, surf in enumerate(btn_surfaces):
            row = idx // 2
            col = idx % 2
            x = start_x + col * (btn_w + btn_gap_x)
            y = start_y + row * (btn_h + btn_gap_y)
            rect = pygame.Rect(x, y, btn_w, btn_h)
            btn_rects.append(rect)
            screen.blit(surf, rect.topleft)
            
            lbl_surf = LABEL_FONT.render(btn_info[idx]["label"], True, TEXT_COLOR)
            lbl_rect = lbl_surf.get_rect(center=(x+btn_w//2, y+btn_h+20))
            screen.blit(lbl_surf, lbl_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if cloud_img and cloud_rect.collidepoint(pos):
                    on_cloud_sync()
                elif not cloud_img and cloud_rect.collidepoint(pos):
                    on_cloud_sync()
                else:
                    for idx, rect in enumerate(btn_rects):
                        if rect.collidepoint(pos):
                            btn_info[idx]["callback"]()
                            break

    pygame.quit()
    sys.exit()
