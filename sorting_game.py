import pygame
import random
import sys
import time

NAVY          = (23,  34,  85)
FRAME_GREEN   = (136, 176,  75)
CREAM_BG      = (247, 231, 206)
BLACK         = (  0,   0,   0)

CORAL_RED     = (255, 111,  97)
PALETTE_GREEN = (136, 176,  75)
PERIWINKLE    = (146, 141, 209)
YELLOW        = (249, 199,  79)
PURPLE        = (247, 202, 201)

LEVEL_COLORS  = [
    [CORAL_RED,      PALETTE_GREEN],
    [CORAL_RED,      PALETTE_GREEN, PERIWINKLE],
    [CORAL_RED,      PALETTE_GREEN, PERIWINKLE, YELLOW],
    [CORAL_RED,      PALETTE_GREEN, PERIWINKLE, YELLOW, PURPLE]
]
LEVEL_THRESHOLDS = [5, 12, 20]

WIDTH, HEIGHT    = 800, 600
CONTENT_MARGIN   = 20
FPS              = 60
CIRCLE_RADIUS    = 32
BIN_HEIGHT       = 120
TIMER_SECONDS    = 110

class Circle:
    def __init__(self, colors, content_rect):
        self.colors       = colors
        self.color        = random.choice(colors)
        self.content_rect = content_rect
        self.reset_position()

    def reset_position(self):
        left  = self.content_rect.left + CIRCLE_RADIUS
        right = self.content_rect.right - CIRCLE_RADIUS
        top   = self.content_rect.top + CIRCLE_RADIUS
        bottom_third = self.content_rect.top + self.content_rect.height // 3
        self.x = random.randint(left, right)
        self.y = random.randint(top, bottom_third)
        self.dragging = False
        self.offset_x = self.offset_y = 0

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), CIRCLE_RADIUS)
        pygame.draw.circle(surface, BLACK, (self.x, self.y), CIRCLE_RADIUS, 2)

    def is_mouse_over(self, pos):
        dx, dy = pos[0] - self.x, pos[1] - self.y
        return dx*dx + dy*dy <= CIRCLE_RADIUS**2

    def start_drag(self, pos):
        self.dragging = True
        self.offset_x = self.x - pos[0]
        self.offset_y = self.y - pos[1]

    def stop_drag(self):
        self.dragging = False

    def update_position(self, pos):
        if self.dragging:
            self.x = pos[0] + self.offset_x
            self.y = pos[1] + self.offset_y

class Bin:
    def __init__(self, color, idx, total, content_rect):
        self.color = color
        width = content_rect.width // total
        self.rect  = pygame.Rect(
            content_rect.left + idx*width,
            content_rect.bottom - BIN_HEIGHT,
            width,
            BIN_HEIGHT
        )

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 4)

    def contains(self, circle):
        return self.rect.collidepoint(circle.x, circle.y)

# ---------------------------------------------------------------------------#
# Main game function
# ---------------------------------------------------------------------------#
def run_game():
    pygame.init()

    try:
        icon = pygame.image.load('logo.png')
        pygame.display.set_icon(icon)
    except:
        pass

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Color Sort")
    clock = pygame.time.Clock()


    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill(FRAME_GREEN)
    content_rect = pygame.Rect(CONTENT_MARGIN, CONTENT_MARGIN,
                               WIDTH - 2*CONTENT_MARGIN,
                               HEIGHT - 2*CONTENT_MARGIN)
    pygame.draw.rect(background, CREAM_BG, content_rect)

    font     = pygame.font.SysFont(None, 36)
    big_font = pygame.font.SysFont(None, 72)


    current_level = 0
    bins = [Bin(col, i, len(LEVEL_COLORS[0]), content_rect)
            for i, col in enumerate(LEVEL_COLORS[0])]
    circle = Circle(LEVEL_COLORS[0], content_rect)

    score = 0
    start_time = time.time()
    running = True

    while running:
        clock.tick(FPS)
        elapsed = time.time() - start_time
        remaining = max(0, int(TIMER_SECONDS - elapsed))

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if circle.is_mouse_over(e.pos):
                    circle.start_drag(e.pos)
            elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                if circle.dragging:
                    circle.stop_drag()
                    placed = False
                    for b in bins:
                        if b.contains(circle):
                            if b.color == circle.color:
                                score += 1
                                placed = True
                            break
                    # Level-up
                    if placed and current_level < len(LEVEL_THRESHOLDS) and score >= LEVEL_THRESHOLDS[current_level]:
                        current_level += 1
                        screen.blit(background, (0,0))
                        lvl_text = big_font.render(f"Level {current_level+1}", True, NAVY)
                        screen.blit(lvl_text, ((WIDTH - lvl_text.get_width())//2,
                                               HEIGHT//2 - 50))
                        pygame.display.flip()
                        pygame.time.wait(1500)
                        # rebuild bins
                        cols = LEVEL_COLORS[current_level]
                        bins = [Bin(col, i, len(cols), content_rect) for i, col in enumerate(cols)]
                    circle = Circle(LEVEL_COLORS[current_level], content_rect)
            elif e.type == pygame.MOUSEMOTION:
                circle.update_position(e.pos)

        if remaining <= 0:
            running = False


        screen.blit(background, (0, 0))
        for b in bins:
            b.draw(screen)
        circle.draw(screen)


        score_surf = font.render(f"Score: {score}", True, NAVY)
        timer_surf = font.render(f"Time: {remaining}s", True, NAVY)
        screen.blit(score_surf, (content_rect.left + 10, content_rect.top + 10))
        screen.blit(timer_surf, (content_rect.right - timer_surf.get_width() - 10,
                                 content_rect.top + 10))

        pygame.display.flip()


    screen.blit(background, (0, 0))
    over_text = big_font.render("Time's Up!", True, NAVY)
    final_text = font.render(f"Your Score: {score}", True, NAVY)
    screen.blit(over_text, ((WIDTH - over_text.get_width())//2, HEIGHT//2 - 50))
    screen.blit(final_text, ((WIDTH - final_text.get_width())//2, HEIGHT//2 + 20))
    pygame.display.flip()
    pygame.time.wait(3000)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    run_game()
