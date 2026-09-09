import pygame
import math
import random

WIDTH, HEIGHT = 640, 480
window = pygame.display.set_mode((WIDTH,HEIGHT))
BOX_RECT = pygame.Rect(220, 200, 200, 200)
BORDER_THICKNESS = 4
INNER_BOX = BOX_RECT.inflate(-(BORDER_THICKNESS * 2), -(BORDER_THICKNESS * 2))
pygame.display.set_caption("Undertale-Type Game")

class PlayerSprite():
    def __init__(self, start_x, start_y):
        self.speed = 3
        self.size = 12
        self.hp = 100

        self.player_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(self.player_surface, (255, 0, 0), (0, 0, self.size, self.size))
        self.player_rect = self.player_surface.get_rect(center=(start_x, start_y))

        self.draw()

    def move(self, dx, dy):
        self.player_rect.x += dx * self.speed
        self.player_rect.y += dy * self.speed

    def draw(self):
        window.blit(self.player_surface, self.player_rect)

class Bullet:
        def __init__(self, target_x, target_y):
            self.speed = 3
            self.radius = 5
            self.initialize_pos()

            angle = math.atan2(target_y - self.y, target_x - self.x)
            self.vx = math.cos(angle) * self.speed
            self.vy = math.sin(angle) * self.speed

            self.bullet_surface = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(self.bullet_surface, (255, 255, 255), (self.radius,self.radius), self.radius)
            self.bullet_rect = self.bullet_surface.get_rect(center= (self.x,self.y))

            self.draw()

        def draw(self):
            window.blit(self.bullet_surface, self.bullet_rect)

        def move(self):
            self.x+=self.vx
            self.y+=self.vy
            self.bullet_rect.center = (int(self.x), int(self.y))

        def initialize_pos(self):
            side = random.choice(["top","bottom","left","right"])
            if side == "top":
                self.x, self.y = random.randint(BOX_RECT.left, BOX_RECT.right), BOX_RECT.top-12
            elif side == "bottom":
                self.x, self.y = random.randint(BOX_RECT.left, BOX_RECT.right), BOX_RECT.bottom+12
            elif side == "left":
                self.x, self.y =  BOX_RECT.left-12, random.randint(BOX_RECT.top, BOX_RECT.bottom)
            elif side == "right":
                self.x, self.y =  BOX_RECT.right+12,random.randint(BOX_RECT.top, BOX_RECT.bottom)




class game():
    def __init__(self):
        pygame.init()
        # window was here
        self.game_font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()
        self.player = PlayerSprite(BOX_RECT.centerx, BOX_RECT.centery)
        #self.bullet = Bullet(self.player.player_rect.centerx, self.player.player_rect.centery) #temp
        self.bullets = []
        self.timer = 0
        self.score = 0
        self.main_loop()


    def main_loop(self):
        while True:
            self.check_events()


            if self.player.hp > 0:
                self.draw_window()
               
            else:
           
                window.fill((0,0,0))
                game_over_text = self.game_font.render("Game Over", True, (255, 0, 0))
                window.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))
                window.blit(self.score_text, (WIDTH // 2 - self.score_text.get_width() // 2, HEIGHT // 2 - self.score_text.get_height() // 2 + 50))


                pygame.display.flip()
                #pygame.time.delay(2000)
                #texit()
            self.clock.tick(60)
    def check_events(self):
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


    def draw_window(self):
        window.fill((0,0,0))
       
        pygame.draw.rect(window, (255, 255, 255), BOX_RECT, BORDER_THICKNESS)
        self.player.player_rect.clamp_ip(INNER_BOX)
        self.player.draw()
        #self.bullet.draw()
        hp = self.game_font.render(f"HP: {self.player.hp}", True, (255, 255, 255))
        window.blit(hp,(220,400))
       
        if self.timer >= 30:
            self.bullets.append(Bullet(self.player.player_rect.centerx, self.player.player_rect.centery))
            #print(len(self.bullets))
            #print(self.player.hp)
            self.timer = 0
        self.timer+=1
        self.score += 1
        self.score_text = self.game_font.render(f"Score: {self.score}", True, (255, 255, 255))
        window.blit(self.score_text, (WIDTH - self.score_text.get_width() - 10, 10))


        remaining = []
        for b in self.bullets:
            b.move()
            b.draw()
            if (0 < b.x < WIDTH and 0 < b.y < HEIGHT) and not b.bullet_rect.colliderect(self.player.player_rect):
                remaining.append(b)
            if b.bullet_rect.colliderect(self.player.player_rect):
                self.player.hp -= 10
               
                print("HIT HP:",self.player.hp)
           
           
        self.bullets = remaining
        #self.bullet.move()


        pygame.display.flip()
   
a = game()







