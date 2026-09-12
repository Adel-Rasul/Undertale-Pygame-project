import pygame
import math
import random

WIDTH, HEIGHT = 640*1.5, 480*1.5
BOX_RECT = pygame.Rect(0, 0, 200, 200)

BORDER_THICKNESS = 6
INNER_BOX = BOX_RECT.inflate(-(BORDER_THICKNESS * 2), -(BORDER_THICKNESS * 2))

class PlayerSprite():
    def __init__(self, start_x, start_y):
        self.speed = 3
        self.size = 12
        self.hp = 100

        self.surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(self.surface, (255, 0, 0), (0, 0, self.size, self.size))
        self.rect = self.surface.get_rect(center=(start_x, start_y))

    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

    def draw(self, surface):
        surface.blit(self.surface, self.rect)

class Bullet:
        def __init__(self, target_x, target_y, tier):
            self.speed = 3
            self.radius = 5
            self.tier = tier
            self.initialize_pos(target_x, target_y)

            self.surface = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(self.surface, (255, 255, 255), (self.radius,self.radius), self.radius)
            self.rect = self.surface.get_rect(center= (self.x,self.y))

        def draw(self, surface):
            surface.blit(self.surface, self.rect)

        def move(self):
            self.x+=self.vx
            self.y+=self.vy
            self.rect.center = (int(self.x), int(self.y))

        def initialize_pos(self, target_x, target_y):
            side = random.choice(["top","bottom","left","right"])
            if side == "top":
                self.x, self.y = random.randint(BOX_RECT.left, BOX_RECT.right), BOX_RECT.top-12
            elif side == "bottom":
                self.x, self.y = random.randint(BOX_RECT.left, BOX_RECT.right), BOX_RECT.bottom+12
            elif side == "left":
                self.x, self.y =  BOX_RECT.left-12, random.randint(BOX_RECT.top, BOX_RECT.bottom)
            elif side == "right":
                self.x, self.y =  BOX_RECT.right+12,random.randint(BOX_RECT.top, BOX_RECT.bottom)

            if self.tier == 1:
                self.wave_attack(side)
            elif self.tier == 2:
                self.tier2()
            elif self.tier == 3:
                self.homing_attack(target_x, target_y)
        
        def wave_attack(self, side):
            if side == "top":
                
                self.vx = 0 
                self.vy = self.speed
            elif side == "bottom":
                
                self.vx = 0 
                self.vy = -self.speed
            elif side == "left":
                
                self.vx = self.speed 
                self.vy = 0
            elif side == "right":
                
                self.vx = -self.speed 
                self.vy = 0

        def tier2(self):
            pass

        def homing_attack(self, target_x, target_y):
            angle = math.atan2(target_y - self.y, target_x - self.x)
            self.vx = math.cos(angle) * self.speed
            self.vy = math.sin(angle) * self.speed

class Enemy:
    def __init__(self):
        pass

    def bullet_attacks(self):
        def wave():
            pass
        
        def homing():
            pass

class Game():
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Undertale-Type Game")
        self.clock = pygame.time.Clock()

        self.window = pygame.display.set_mode((WIDTH,HEIGHT))
        window_rect = pygame.Rect(0,0,self.window.get_width(),self.window.get_height())
        BOX_RECT.center = (window_rect.center[0], window_rect.center[1]+75)
        self.box_rect = BOX_RECT
        self.inner_box = BOX_RECT.inflate(-(BORDER_THICKNESS * 2), -(BORDER_THICKNESS * 2))
        self.game_font = pygame.font.Font(None, 36)

        self.player = PlayerSprite(self.box_rect.centerx, self.box_rect.centery)
        self.bullets = []
        self.bullet_tier = 0
        self.timer = 0
        self.score = 0
        
        self.main_loop()

    def main_loop(self):
        while True:
            self.handle_events()

            if self.player.hp > 0:
                self.render()
                self.update()

            else:
                self.render_game_over()

            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move(-1,0)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move(1,0)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.player.move(0,-1)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.player.move(0,1)

        self.player.rect.clamp_ip(self.inner_box)

    def update(self):
        self.timer+=1
        self.score += 1
        
        if self.score < 1800:
            self.bullet_tier = 1
        elif self.score >= 1800 and self.score <3600:
            self.bullet_tier = 3
        elif self.score >= 3600:
            self.bullet_tier = 3

        if self.timer >= 30:
            self.bullets.append(Bullet(self.player.rect.centerx, self.player.rect.centery, self.bullet_tier))
            self.timer = 0

        # Dealing with Bullets
        remaining_bullets = []
        for b in self.bullets:
            b.move()

            if b.rect.colliderect(self.player.rect):
                self.player.hp -= 10
                print("HIT HP:",self.player.hp)

            elif (0 < b.x < WIDTH and 0 < b.y < HEIGHT):
                remaining_bullets.append(b)
                
        self.bullets = remaining_bullets
        

    def render(self):
        self.window.fill((0,0,0))
       
        #Player and Borders/Box
        pygame.draw.rect(self.window, (255, 255, 255), BOX_RECT, BORDER_THICKNESS)
        self.player.draw(self.window)

        #Other Sprite Rendering
        for b in self.bullets:
            b.draw(self.window)

        #UI Text
        hp = self.game_font.render(f"HP: {self.player.hp}", True, (255, 255, 255))
        self.window.blit(hp,(220,400))

        self.score_text = self.game_font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.window.blit(self.score_text, (WIDTH - self.score_text.get_width() - 10, 10))

        pygame.display.flip()

    def render_game_over(self):
        self.window.fill((0,0,0))
        game_over_text = self.game_font.render("Game Over", True, (255, 0, 0))
        self.window.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))
        self.window.blit(self.score_text, (WIDTH // 2 - self.score_text.get_width() // 2, HEIGHT // 2 - self.score_text.get_height() // 2 + 50))
        
        pygame.display.flip()
        #pygame.time.delay(2000)
        #texit()
   
a = Game()







