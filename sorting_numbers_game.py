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
    cursor.execute(
        'SELECT best_level, best_time, mistakes, last_played FROM progress_tracking WHERE username=? AND game_name=?',
        (username, game_name)
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return row
    return (0, None, 0, None)


def update_progress(username, game_name, level, time_sec, mistakes):
    conn = connect_db()
    cursor = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(
        'SELECT best_level, best_time FROM progress_tracking WHERE username=? AND game_name=?',
        (username, game_name)
    )
    existing = cursor.fetchone()
    if existing:
        best_level, best_time = existing
        if level > best_level or (level == best_level and (best_time is None or time_sec < best_time)):
            cursor.execute(
                'UPDATE progress_tracking SET best_level=?, best_time=?, mistakes=?, last_played=? WHERE username=? AND game_name=?',
                (level, time_sec, mistakes, now, username, game_name)
            )
    else:
        cursor.execute(
            'INSERT INTO progress_tracking (username, game_name, best_level, best_time, mistakes, last_played) VALUES (?, ?, ?, ?, ?, ?)',
            (username, game_name, level, time_sec, mistakes, now)
        )
    conn.commit()
    conn.close()


def sorting_hard():
    username = "player1"
    create_progress_table()
    pygame.init()
    WIDTH, HEIGHT = 800, 600
    try:
        icon = pygame.image.load('logo.png')
        pygame.display.set_icon(icon)
    except Exception:
        pass
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Number Sort Hard")
    clock = pygame.time.Clock()

    NAVY = (23, 34, 85)
    FRAME_GREEN = (136, 176, 75)
    CREAM_BG = (247, 231, 206)
    BLACK = (0, 0, 0)
    BIN_COLORS = [(136,176,75),(255,111,97),(146,168,209),(249,199,79),(147,112,219)]
    CIRCLE_COLOR = (146,168,209)
    LEVEL_RANGES = [
        [(1,5),(6,10)],
        [(1,10),(11,20),(21,30)],
        [(1,20),(21,40),(41,60),(61,80)],
        [(1,50),(51,100),(101,150),(151,200),(201,250)]
    ]
    LEVEL_THRESHOLDS = [5, 12, 20]
    MARGIN = 20
    FPS = 60
    RADIUS = 40
    BIN_HEIGHT = 120
    TIMER = 110

    bg = pygame.Surface((WIDTH, HEIGHT))
    bg.fill(FRAME_GREEN)
    content = pygame.Rect(MARGIN, MARGIN, WIDTH-2*MARGIN, HEIGHT-2*MARGIN)
    pygame.draw.rect(bg, CREAM_BG, content)

    num_font = pygame.font.SysFont(None, 48)
    hud_font = pygame.font.SysFont(None, 36)
    msg_font = pygame.font.SysFont(None, 72)

    game_name = 'NumberSortHard'
    best_level, best_time, best_mistakes, _ = get_progress(username, game_name)

    level = 0
    score = 0
    mistakes = 0
    start_time = time.time()
    game_start = datetime.now()

    class CircleObj:
        def __init__(self, lo, hi):
            self.lo, self.hi = lo, hi
            self.reset()
        def reset(self):
            self.number = random.randint(self.lo, self.hi)
            l = content.left + RADIUS
            r = content.right - RADIUS
            t = content.top + RADIUS
            b = content.top + content.height // 3
            self.x = random.randint(l, r)
            self.y = random.randint(t, b)
            self.drag = False
            self.ox = self.oy = 0
        def draw(self):
            pygame.draw.circle(screen, CIRCLE_COLOR, (self.x, self.y), RADIUS)
            pygame.draw.circle(screen, BLACK, (self.x, self.y), RADIUS, 2)
            txt = num_font.render(str(self.number), True, BLACK)
            screen.blit(txt, (self.x-txt.get_width()//2, self.y-txt.get_height()//2))
        def hover(self, pos):
            dx,dy = pos[0]-self.x, pos[1]-self.y
            return dx*dx + dy*dy <= RADIUS*RADIUS
        def start(self, pos):
            self.drag = True
            self.ox = self.x - pos[0]
            self.oy = self.y - pos[1]
        def stop(self): self.drag = False
        def update(self, pos):
            if self.drag:
                self.x, self.y = pos[0]+self.ox, pos[1]+self.oy

    class BinObj:
        def __init__(self, lo, hi, idx, total):
            self.lo, self.hi = lo, hi
            w = content.width // total
            self.rect = pygame.Rect(content.left+idx*w, content.bottom-BIN_HEIGHT, w, BIN_HEIGHT)
            self.color = BIN_COLORS[idx]
        def draw(self):
            pygame.draw.rect(screen, self.color, self.rect)
            pygame.draw.rect(screen, BLACK, self.rect, 2)
            lbl = hud_font.render(f"{self.lo}-{self.hi}", True, BLACK)
            screen.blit(lbl, (self.rect.centerx-lbl.get_width()//2, self.rect.centery-lbl.get_height()//2))
        def contains(self, c): return self.rect.collidepoint(c.x, c.y)

    bins = [BinObj(lo, hi, i, len(LEVEL_RANGES[0])) for i,(lo,hi) in enumerate(LEVEL_RANGES[0])]
    circle = CircleObj(LEVEL_RANGES[0][0][0], LEVEL_RANGES[0][-1][1])

    running = True
    while running:
        clock.tick(FPS)
        rem = max(0, TIMER - int(time.time() - start_time))

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and circle.hover(e.pos):
                circle.start(e.pos)
            elif e.type == pygame.MOUSEBUTTONUP and e.button == 1 and circle.drag:
                circle.stop()
                placed = False
                for b in bins:
                    if b.contains(circle):
                        placed = True
                        if b.lo <= circle.number <= b.hi:
                            score += 1
                            if level < len(LEVEL_THRESHOLDS) and score >= LEVEL_THRESHOLDS[level]:
                                level += 1
                                screen.blit(bg, (0,0))
                                surf = msg_font.render(f"Level {level+1}!", True, NAVY)
                                screen.blit(surf, ((WIDTH-surf.get_width())//2,(HEIGHT-surf.get_height())//2))
                                pygame.display.flip()
                                pygame.time.wait(1500)
                                bins = [BinObj(lo, hi, i, len(LEVEL_RANGES[level])) for i,(lo,hi) in enumerate(LEVEL_RANGES[level])]
                        else:
                            mistakes += 1
                        circle = CircleObj(LEVEL_RANGES[level][0][0], LEVEL_RANGES[level][-1][1])
                        break
                if not placed:
                    mistakes += 1
            elif e.type == pygame.MOUSEMOTION:
                circle.update(e.pos)

        if rem <= 0:
            running = False

        # Draw frame
        screen.blit(bg, (0,0))
        for b in bins:
            b.draw()
        circle.draw()
                # HUD: show stats
        screen.blit(hud_font.render(f"Score: {score}", True, NAVY), (content.left+10, content.top+10))
        screen.blit(hud_font.render(f"Mistakes: {mistakes}", True, NAVY), (content.left+10, content.top+40))
        screen.blit(hud_font.render(f"Best Level: {best_level+1}", True, NAVY), (content.left+10, content.top+70))
        # Time and current level on right side
        screen.blit(hud_font.render(f"Time: {rem}s", True, NAVY), (content.right-140, content.top+10))
        screen.blit(hud_font.render(f"Level: {level+1}", True, NAVY), (content.right-140, content.top+40))
        pygame.display.flip()

    screen.blit(bg, (0,0))
    over = msg_font.render("Time's Up!", True, NAVY)
    sc = hud_font.render(f"Your Score: {score}", True, NAVY)
    screen.blit(over, ((WIDTH-over.get_width())//2, HEIGHT//2-50))
    screen.blit(sc, ((WIDTH-sc.get_width())//2, HEIGHT//2+20))
    pygame.display.flip()
    pygame.time.wait(2000)

    elapsed = (datetime.now() - game_start).total_seconds()
    update_progress(username, game_name, level, elapsed, mistakes)
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    sorting_hard()