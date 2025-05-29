import pygame
import sys
import os

from login import show_login_window
from age_picker import age_picker
from inventory import show_inventory
from progress_tracking_page import progress_tracker

BG_OUTER= (0x2C, 0x81, 0x02)
BG_INNER= (0xF7, 0xE7, 0xCE)
TEXT_COLOR= (0x17, 0x22, 0x55)

BTN_SIZE= (150, 150)
BTN_GAP= 40
LOGO_SIZE= (630, 400)
PADDING_TOP= 30

def landing_page_pygame():
    #Opens login window
    current_username = show_login_window()
    if not current_username:
        sys.exit(0)

    pygame.init()

    info = pygame.display.Info()
    screen_w, screen_h = info.current_w, info.current_h
    # left room for white bar at the top
    win_h = screen_h-40

    screen = pygame.display.set_mode((screen_w, win_h), pygame.RESIZABLE)
    pygame.display.set_caption("Smart Sprouts - Home")

    logo_path = os.path.join("assets", "logo2.ico")
    if os.path.exists(logo_path):
        try:
            ico = pygame.image.load(logo_path)
            pygame.display.set_icon(ico)
        except Exception:
            pass

    logo_surf = pygame.image.load(os.path.join("assets", "logo.png")).convert_alpha()
    logo_surf = pygame.transform.smoothscale(logo_surf, LOGO_SIZE)

    btn_files = [ "progress.png", "login.png", "stickers.png" ]
    btn_labels= [ "Progress Tracking", "Play", "Sticker Collection" ]
    btn_funcs = [ lambda: progress_tracker(current_username),
                  lambda: age_picker(current_username),
                  lambda: show_inventory(current_username) ]

    btn_surfs = []
    for fn in btn_files:
        path = os.path.join("assets", fn)
        img  = pygame.image.load(path).convert_alpha()
        img  = pygame.transform.smoothscale(img, BTN_SIZE)
        btn_surfs.append(img)

    label_font = pygame.font.SysFont("Arial", 13, bold=True)

    clock = pygame.time.Clock()
    running = True

    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                running = False
            elif ev.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((ev.w, ev.h), pygame.RESIZABLE)
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mx, my = ev.pos
                # test each button rect
                for rect, func in button_rects:
                    if rect.collidepoint(mx, my):
                        func()
                        break

        screen.fill(BG_OUTER)

        W, H = screen.get_size()
        inner_rect = pygame.Rect(10, 10, W-20, H-20)
        pygame.draw.rect(screen, BG_INNER, inner_rect)

        logo_rect = logo_surf.get_rect()
        logo_rect.centerx = W // 2
        logo_rect.top     = inner_rect.top + PADDING_TOP
        screen.blit(logo_surf, logo_rect)

        total_w = BTN_SIZE[0]*3 + BTN_GAP*2
        start_x = (W - total_w)//2
        btn_y   = logo_rect.bottom + PADDING_TOP

        button_rects = []
        for i, surf in enumerate(btn_surfs):
            x = start_x + i*(BTN_SIZE[0] + BTN_GAP)
            rect = pygame.Rect(x, btn_y, *BTN_SIZE)
            screen.blit(surf, rect.topleft)
            button_rects.append((rect, btn_funcs[i]))

            lbl_s = label_font.render(btn_labels[i], True, TEXT_COLOR)
            lbl_r = lbl_s.get_rect(center=(x + BTN_SIZE[0]//2,
                                           btn_y + BTN_SIZE[1] + 16))
            screen.blit(lbl_s, lbl_r)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    landing_page_pygame()
