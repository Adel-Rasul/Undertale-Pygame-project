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
        def __init__(self, x, y, vx, vy, radius=5):
            #self.speed = 3
            self.x = float(x)
            self.y = float(y)
            self.vx = vx
            self.vy = vy
            self.radius = radius

            self.surface = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(self.surface, (255, 255, 255), (self.radius,self.radius), self.radius)
            self.rect = self.surface.get_rect(center= (self.x,self.y))

        def move(self):
            self.x+=self.vx
            self.y+=self.vy
            self.rect.center = (int(self.x), int(self.y))

        def draw(self, surface):
            surface.blit(self.surface, self.rect)

class OscillatingBullet(Bullet):
    def __init__(self, x, y, vx, vy, amplitude=20, frequency=0.1, radius=5):
        super().__init__(x,y,vx,vy, radius)

        self.base_x = float(x)
        self.base_y = float(y)

        self.amplitude = amplitude
        self.frequency = frequency
        self.time = 0

        self.forward_angle = math.atan2(vy,vx)
        self.perp_angle = self.forward_angle + (math.pi / 2)
    
    def move(self):
        self.time +=1
        self.base_x += self.vx
        self.base_y += self.vy

        wave_offset = math.sin(self.time * self.frequency) * self.amplitude

        self.x = self.base_x + math.cos(self.perp_angle) * wave_offset
        self.y = self.base_y + math.sin(self.perp_angle) * wave_offset

        self.rect.center = (int(self.x), int(self.y))

class Bomb:
    def __init__(self, x, y, vx, vy, fuse_frames = 120, shrapnel_count = 12, shrapnel_speed=3, radius=8):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.fuse_timer = fuse_frames
        self.shrapnel_count = shrapnel_count
        self.shrapnel_speed = shrapnel_speed 
        self.radius = radius   

        self.active = True
        self.has_exploded = False
        self.rect = pygame.Rect(x-self.radius, y-self.radius, 16, 16)
    
    def update(self, player_rect):
        if not self.active:
            return

        self.x += self.vx
        self.y += self.vy
        
        self.vx *= 0.96
        self.vy *= 0.96

        self.rect.center = (int(self.x), int(self.y))

        self.fuse_timer -= 1
        player_collide = self.rect.colliderect(player_rect)

        if self.fuse_timer <= 0 or player_collide:
            self.has_exploded = True
            self.active = False
    
    def explode(self):
        exploded_bullets = []
        angle_increment = (2*math.pi) / self.shrapnel_count

        for i in range(self.shrapnel_count):
            angle = i* angle_increment
            vx = math.cos(angle) * self.shrapnel_speed
            vy = math.sin(angle) * self.shrapnel_speed
            exploded_bullets.append(Bullet(self.x, self.y, vx, vy, radius=4))
        return exploded_bullets

    def draw(self, surface):
        pygame.draw.circle(surface, (255,255,255), (int(self.x), int(self.y)), self.radius)
        
        if self.vx <= 0.3 and self.vy <=0.3:
            flash= (255,0,0) if (self.fuse_timer // 6) % 2 == 0 else (255,165,0)
            pygame.draw.circle(surface, flash, (int(self.x), int(self.y)), self.radius)
        

class Enemy:
    def __init__(self,player, name="Boss",hp=100):
        self.name = name
        self.hp = hp
        self.timer = 0
        self.current_attack = ""
        self.player = player

    def create_straight_bullet(self, x, y, vx, vy):
        return Bullet(x, y, vx, vy)
    
    def create_targeted_bullet(self, x, y, speed=3):
        tx, ty = self.player.rect.centerx, self.player.rect.centery
        angle = math.atan2(ty - y, tx - x)
        return Bullet(x,y, math.cos(angle)*speed, math.sin(angle)*speed)
    
    def create_oscillating_bullet(self, x, y, vx, vy, amplitude=25, frequency=0.12):
        return OscillatingBullet(x, y, vx, vy, amplitude=amplitude, frequency=frequency)

    def pick_side(self):
        side = random.choice(["top","bottom","left","right"])
        if side == "top":
            return random.randint(BOX_RECT.left, BOX_RECT.right), BOX_RECT.top-12
        elif side == "bottom":
            return  random.randint(BOX_RECT.left, BOX_RECT.right), BOX_RECT.bottom+12
        elif side == "left":
            return  BOX_RECT.left-12, random.randint(BOX_RECT.top, BOX_RECT.bottom)
        elif side == "right":
            return  BOX_RECT.right+12,random.randint(BOX_RECT.top, BOX_RECT.bottom)

    def wave_barrage_attack(self):
        '''Spawn 5 waves of 4 bullets in intervals of 15 frames'''
        bullets = []

        if self.timer % 15 == 0 and self.timer <= 75:
            gap_x = random.randint(BOX_RECT.left + 40, BOX_RECT.right - 40)
            for x in range(BOX_RECT.left +20, BOX_RECT.right, 35):
                if abs(x-gap_x) > 30:
                    bullets.append(self.create_straight_bullet(x, BOX_RECT.top -10, 0, 3))
        return bullets
    
    def targeted_bursts_attack(self):
        bullets = []

        if self.timer in [10, 30, 50, 70]:
            spawn_x = random.choice([BOX_RECT.left - 10, BOX_RECT.right + 10])
            spawn_y = BOX_RECT.top - 10
            bullets.append(self.create_targeted_bullet(spawn_x, spawn_y, speed=4))
        return bullets
    
    def targeted_random_attack(self):
        bullets = []

        if self.timer % 20 == 0 and self.timer <= 260:
            spawn_x, spawn_y = self.pick_side()

            bullets.append(self.create_targeted_bullet(spawn_x, spawn_y))
        return bullets

    def triple_oscillating_attck(self):
        bullets = []
        if self.timer == 30:
            for spawn_x in [BOX_RECT.left +30, BOX_RECT.centerx, BOX_RECT.right-30]:
                bullets.append(self.create_oscillating_bullet(x = spawn_x,y = BOX_RECT.top - 10, vx = 0, vy = 1.5, amplitude=30, frequency=0.15))
        if self.timer == 90:
            for spawn_x in [BOX_RECT.left +50, BOX_RECT.right-50]:
                bullets.append(self.create_oscillating_bullet(x = spawn_x,y = BOX_RECT.top - 10, vx = 0, vy = 1.5, amplitude=30, frequency=0.15))
                
        return bullets

    def conga_oscillating_attack(self):
        bullets = []
        if self.timer == 1:
            self.current_spawn_x = random.randint(BOX_RECT.left +30,BOX_RECT.right-30)
        if self.timer%10 == 0 and self.timer <= 150:
            bullets.append(self.create_oscillating_bullet(x = self.current_spawn_x,y = BOX_RECT.top - 10, vx = 0, vy = 1.5, amplitude=30, frequency=0.15))
                
        return bullets
    
    def mine_attack(self):
        bombs = []

        if self.timer in [10,70,160]:
            x = random.randint(BOX_RECT.left+30,BOX_RECT.right-30)
            vy = random.randint(2,8)
            shrapnel_count = random.randint(8,12)
            bombs.append(Bomb(x=x,y=BOX_RECT.top - 10,vx=0,vy=vy,fuse_frames=120,shrapnel_count=shrapnel_count))
        return bombs

    def update(self):
        new_bullets = []
        new_bombs = []
        self.timer +=1
        if self.current_attack == "":
            attack_length = 120

        elif self.current_attack == "targeted_bursts_attack":
            new_bullets = self.targeted_bursts_attack()
            attack_length = 110

        elif self.current_attack == "wave_barrage_attack":
            new_bullets = self.wave_barrage_attack()
            attack_length = 120

        elif self.current_attack == "targeted_random_attack":
            new_bullets = self.targeted_random_attack()
            attack_length = 300 
        
        elif self.current_attack == "triple_oscillating_attck":
            new_bullets = self.triple_oscillating_attck()
            attack_length = 210 
        elif self.current_attack == "conga_oscillating_attack":
            new_bullets = self.conga_oscillating_attack()
            attack_length = 210 
        elif self.current_attack == "mine_attack":
            new_bombs = self.mine_attack()
            attack_length = 300 

        if self.timer >= attack_length:
            attacks = ["targeted_bursts_attack","wave_barrage_attack","targeted_random_attack","triple_oscillating_attck","conga_oscillating_attack","mine_attack"]
            self.current_attack = random.choice(attacks)
            print("RESET", self.current_attack)
            self.timer = 0

        return new_bullets, new_bombs
        
class Game():
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Undertale-Type Game")
        self.clock = pygame.time.Clock()

        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        window_rect = pygame.Rect(0,0,self.window.get_width(),self.window.get_height())
        BOX_RECT.center = (window_rect.center[0], window_rect.center[1]+75)
        self.box_rect = BOX_RECT
        self.inner_box = BOX_RECT.inflate(-(BORDER_THICKNESS * 2), -(BORDER_THICKNESS * 2))
        self.game_font = pygame.font.Font(None, 36)

        self.player = PlayerSprite(self.box_rect.centerx, self.box_rect.centery)
        self.current_enemy = Enemy(self.player)
        self.bullets = []
        self.bombs = []
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
        new_bullets, new_bombs = self.current_enemy.update()
        self.bullets.extend(new_bullets)
        self.bombs.extend(new_bombs)

        remaining_bullets = []
        for b in self.bullets:
            b.move()

            if b.rect.colliderect(self.player.rect):
                self.player.hp -=10
                print("HIT! Player HP:", self.player.hp)
            elif (BOX_RECT.left - 50 < b.x <BOX_RECT.right + 50) and (BOX_RECT.top -50 < b.y < BOX_RECT.bottom):
                remaining_bullets.append(b)
        self.bullets = remaining_bullets

        remaining_bombs = []
        for bomb in self.bombs:
            bomb.update(self.player.rect)

            if bomb.has_exploded:
                self.bullets.extend(bomb.explode())
            elif (BOX_RECT.left - 50 < bomb.x < BOX_RECT.right + 50) and (BOX_RECT.top - 50 < bomb.y < BOX_RECT.bottom + 50):
                remaining_bombs.append(bomb)
        self.bombs = remaining_bombs

        self.score+=1
    
    def render(self):
        self.window.fill((0,0,0))
       
        #Player and Borders/Box
        pygame.draw.rect(self.window, (255, 255, 255), BOX_RECT, BORDER_THICKNESS)
        self.player.draw(self.window)

        #Other Sprite Rendering
        for b in self.bullets:
            b.draw(self.window)

        for bomb in self.bombs:
            bomb.draw(self.window)

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







