import pygame, random, sys, time

def sorting_hard():
    NAVY        = (23,  34,  85)
    FRAME_GREEN = (136, 176,  75)
    CREAM_BG    = (247, 231, 206)
    BLACK       = (0,    0,    0)

    BIN_COLORS  = [
        (136,176,75), (255,111,97), (146,168,209),
        (249,199,79), (147,112,219)
    ]
    CIRCLE_COLOR = (146,168,209)

    LEVEL_RANGES    = [
        [(1,5),(6,10)],
        [(1,10),(11,20),(21,30)],
        [(1,20),(21,40),(41,60),(61,80)],
        [(1,50),(51,100),(101,150),(151,200),(201,250)]
    ]
    LEVEL_THRESHOLDS = [5, 12, 20]

    WIDTH, HEIGHT = 800, 600
    MARGIN        = 20
    FPS           = 60
    CIRCLE_RADIUS = 40
    BIN_HEIGHT    = 120
    TIMER_SECONDS = 110

    class Circle:
        def __init__(self, lo, hi, area):
            self.min, self.max = lo, hi
            self.area = area
            self.reset()

        def reset(self):
            self.number = random.randint(self.min, self.max)
            left  = self.area.left + CIRCLE_RADIUS
            right = self.area.right - CIRCLE_RADIUS
            top   = self.area.top + CIRCLE_RADIUS
            bottom= self.area.top + self.area.height // 3
            self.x = random.randint(left, right)
            self.y = random.randint(top, bottom)
            self.dragging = False
            self.offset_x = self.offset_y = 0

        def draw(self, surf, font):
            pygame.draw.circle(surf, CIRCLE_COLOR, (self.x, self.y), CIRCLE_RADIUS)
            pygame.draw.circle(surf, BLACK, (self.x, self.y), CIRCLE_RADIUS, 2)
            txt = font.render(str(self.number), True, BLACK)
            surf.blit(txt, (self.x - txt.get_width()//2, self.y - txt.get_height()//2))

        def hover(self, pos):
            dx, dy = pos[0]-self.x, pos[1]-self.y
            return dx*dx + dy*dy <= CIRCLE_RADIUS*CIRCLE_RADIUS

        def start(self, pos):
            self.dragging = True
            self.offset_x = self.x - pos[0]
            self.offset_y = self.y - pos[1]

        def stop(self):
            self.dragging = False

        def update(self, pos):
            if self.dragging:
                self.x = pos[0] + self.offset_x
                self.y = pos[1] + self.offset_y

    class Bin:
        def __init__(self, lo, hi, idx, total, area):
            self.lo, self.hi = lo, hi
            width = area.width // total
            self.rect = pygame.Rect(
                area.left + idx*width,
                area.bottom - BIN_HEIGHT,
                width, BIN_HEIGHT
            )
            self.color = BIN_COLORS[idx]

        def draw(self, surf, font):
            pygame.draw.rect(surf, self.color, self.rect)
            pygame.draw.rect(surf, BLACK, self.rect, 2)
            lbl = font.render(f"{self.lo}-{self.hi}", True, BLACK)
            surf.blit(lbl, (
                self.rect.centerx - lbl.get_width()//2,
                self.rect.centery - lbl.get_height()//2
            ))

        def contains(self, circle):
            return self.rect.collidepoint(circle.x, circle.y)


    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Number Sort")
    clock = pygame.time.Clock()
    try:
        icon = pygame.image.load('logo.png')
        pygame.display.set_icon(icon)
    except:
        pass


    bg = pygame.Surface((WIDTH, HEIGHT))
    bg.fill(FRAME_GREEN)
    content = pygame.Rect(MARGIN, MARGIN, WIDTH-2*MARGIN, HEIGHT-2*MARGIN)
    pygame.draw.rect(bg, CREAM_BG, content)


    num_font = pygame.font.SysFont(None, 48)
    hud_font = pygame.font.SysFont(None, 36)
    msg_font = pygame.font.SysFont(None, 72)

    level = 0
    bins = [Bin(lo, hi, i, len(LEVEL_RANGES[0]), content)
            for i, (lo, hi) in enumerate(LEVEL_RANGES[0])]
    circle = Circle(
        LEVEL_RANGES[0][0][0], LEVEL_RANGES[0][-1][1], content
    )

    score = 0
    start_time = time.time()

    running = True
    while running:
        clock.tick(FPS)
        remaining = max(0, TIMER_SECONDS - int(time.time() - start_time))

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and circle.hover(e.pos):
                circle.start(e.pos)
            elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                if circle.dragging:
                    circle.stop()
                    for b in bins:
                        if b.contains(circle):
                            if b.lo <= circle.number <= b.hi:
                                score += 1
                                if level < len(LEVEL_THRESHOLDS) and score >= LEVEL_THRESHOLDS[level]:
                                    level += 1

                                    screen.fill(CREAM_BG)
                                    lvl_surf = msg_font.render(f"Level {level+1}!", True, NAVY)
                                    screen.blit(
                                        lvl_surf,
                                        ((WIDTH-lvl_surf.get_width())//2,
                                         (HEIGHT-lvl_surf.get_height())//2)
                                    )
                                    pygame.display.flip()
                                    pygame.time.wait(1500)

                                    bins = [
                                        Bin(lo, hi, i, len(LEVEL_RANGES[level]), content)
                                        for i, (lo, hi) in enumerate(LEVEL_RANGES[level])
                                    ]

                            circle = Circle(
                                LEVEL_RANGES[level][0][0],
                                LEVEL_RANGES[level][-1][1],
                                content
                            )
                            break
            elif e.type == pygame.MOUSEMOTION:
                circle.update(e.pos)

        if remaining <= 0:
            running = False

        screen.blit(bg, (0, 0))
        for b in bins:
            b.draw(screen, hud_font)
        circle.draw(screen, num_font)
        screen.blit(hud_font.render(f"Score: {score}", True, NAVY), (content.left+10, content.top+10))
        screen.blit(hud_font.render(f"Time: {remaining}s", True, NAVY), (content.right-140, content.top+10))
        pygame.display.flip()

    screen.blit(bg, (0, 0))
    over_surf = msg_font.render("Time's Up!", True, NAVY)
    score_surf = hud_font.render(f"Your Score: {score}", True, NAVY)
    screen.blit(over_surf, ((WIDTH-over_surf.get_width())//2, HEIGHT//2-50))
    screen.blit(score_surf, ((WIDTH-score_surf.get_width())//2, HEIGHT//2+20))
    pygame.display.flip()
    pygame.time.wait(2000)
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    sorting_hard()