import pygame
import os
import sys
import ctypes
import tkinter as tk
from tkinter import messagebox
from utils import resource_path

from math_game_easy import math_easy
from math_game_hard import math_hard
from sequence_game import sequence_easy
from SequenceGameHard import sequence_hard
from sorting_game import sorting_easy
from sorting_numbers_game import sorting_hard
from memory_cards_easy import memory_cards_easy
from memory_cards_hard import memory_cards_hard

#imports for sync functionality
from database import init_db
from database import connect_db
from cloud_api import connect_cloud
from sync import cloud_sync
from net_util import is_internet_available
init_db()

def game_picker(difficulty, current_username):
    pygame.init()
    def on_math():
        if difficulty == "easy":
            math_easy(difficulty, current_username)
        else:
            math_hard(difficulty, current_username)

    def on_sorting():
        if difficulty == "easy":
            sorting_easy(difficulty, current_username)
        else:
            sorting_hard(difficulty, current_username)

    def on_sequence():
        if difficulty == "easy":
            sequence_easy(difficulty, current_username)
        else:
            sequence_hard(difficulty, current_username)

    def on_memory():
        if difficulty == "easy":
            memory_cards_easy(difficulty, current_username)
        else:
            memory_cards_hard(difficulty, current_username)

    def on_cloud_sync():
        root = tk.Tk()
        root.withdraw()

        if not is_internet_available():
            messagebox.showerror("No Connection", "No internet connection.\nPlease connect to Wi-Fi and try again.")
            root.destroy()
            return

        # If user is online:
        cloud_conn_str = "sqlitecloud://cz0s4hgxnz.g6.sqlite.cloud:8860/database.db?apikey=w1Q0wgb3dEbBL9iiUtDIO8uh29bg3Trn8b9pLmt9Qvg"
        tables = ["login_info", "progress_tracking", "rewards"]
        sync_manager_ready = True

        try:
            local_conn = connect_db()
            cloud_conn = connect_cloud(cloud_conn_str)

            success = cloud_sync(current_username, local_conn, cloud_conn, tables, sync_manager_ready)

            if success:
                messagebox.showinfo("Sync Status", "Cloud sync completed successfully!")
            else:
                messagebox.showerror("Sync Status", "Cloud sync failed. Try again later.")

            local_conn.close()
            cloud_conn.close()

        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error during sync:\n{e}")

        root.destroy()

    info = pygame.display.Info()
    screen_width, screen_height = info.current_w, info.current_h - 40
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    pygame.display.set_caption("Smart Sprouts - Game Picker")

    if sys.platform == 'win32':
        hwnd = pygame.display.get_wm_info()['window']
        ctypes.windll.user32.SetForegroundWindow(hwnd)
        ctypes.windll.user32.SetActiveWindow(hwnd)

    pygame.event.clear()

    BG_COLOR = (44, 129, 2)
    FRAME_COLOR = (247, 231, 206)
    TEXT_COLOR = (23, 34, 85)
    LABEL_FONT = pygame.font.SysFont("Arial", 14, bold=True)
    TITLE_FONT = pygame.font.SysFont("Arial", 36, bold=True)


    cloud_icon_path = resource_path(os.path.join("assets", "cloud_sync_btn.png"))
    if os.path.exists(cloud_icon_path):
        cloud_img = pygame.image.load(cloud_icon_path).convert_alpha()
        cloud_img = pygame.transform.smoothscale(cloud_img, (80, 80))
    else:
        cloud_img = None
        cloud_text = LABEL_FONT.render("Cloud Sync", True, TEXT_COLOR)

    logo_path = resource_path(os.path.join("assets", "logo.png"))
    logo_img = pygame.image.load(logo_path).convert_alpha()
    logo_img = pygame.transform.smoothscale(logo_img, (480, 280))


    btn_info = [
        {"img": "math_btn.png", "label": "Math Game", "callback": on_math},
        {"img": "sorting_btn.png", "label": "Sorting", "callback": on_sorting},
        {"img": "sequence_btn.png", "label": "Sequences", "callback": on_sequence},
        {"img": "memory_btn.png", "label": "Memory Cards", "callback": on_memory},
    ]
    btn_w, btn_h = 140, 140
    btn_gap_x, btn_gap_y = 60, 80
    btn_surfaces = []
    for info in btn_info:
        surf = pygame.image.load(resource_path(os.path.join("assets", info["img"])))
        surf = pygame.transform.smoothscale(surf, (btn_w, btn_h))
        btn_surfaces.append(surf)

    running = True
    while running:
        screen.fill(BG_COLOR)
        width, height = screen.get_size()
        pygame.draw.rect(screen, FRAME_COLOR, (10, 10, width - 20, height - 20))

        screen.blit(TITLE_FONT.render("Select a Game", True, TEXT_COLOR),
                    TITLE_FONT.render("Select a Game", True, TEXT_COLOR).get_rect(center=(width // 2, 50)))
        screen.blit(logo_img, logo_img.get_rect(center=(width // 2, 150)))

    
        if cloud_img:
            c_rect = cloud_img.get_rect(topright=(width - 20, 20))
            screen.blit(cloud_img, c_rect)
        else:
            c_rect = cloud_text.get_rect(topright=(width - 20, 40))
            screen.blit(cloud_text, c_rect)

    
        start_y = 250
        total_w = btn_w * 2 + btn_gap_x
        start_x = (width - total_w) // 2
        btn_rects = []
        for idx, surf in enumerate(btn_surfaces):
            r, c = divmod(idx, 2)
            x = start_x + c * (btn_w + btn_gap_x)
            y = start_y + r * (btn_h + btn_gap_y)
            rect = pygame.Rect(x, y, btn_w, btn_h)
            btn_rects.append(rect)
            screen.blit(surf, (x, y))
            screen.blit(
                LABEL_FONT.render(btn_info[idx]["label"], True, TEXT_COLOR),
                LABEL_FONT.render(btn_info[idx]["label"], True, TEXT_COLOR).get_rect(
                    center=(x + btn_w // 2, y + btn_h + 20))
            )

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
                from age_picker import age_pkr 
                age_pkr(current_username)
                return
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                # Cloud button click
                if c_rect.collidepoint(pos):
                    on_cloud_sync()
                # Game button click
                for idx, rect in enumerate(btn_rects):
                    if rect.collidepoint(pos):
                        btn_info[idx]["callback"]()
                        running = False
                        break
