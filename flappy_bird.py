import pygame
import random
from sys import exit

# Function will get each frame in the image file when called with the following parameters.
# the frame variable is how much frames are in the single image file
# the width and height varaible is the width and height per frame
# scale variable is to resize the image
def get_sprite_frame(sheet, frame, width, height, row, scale):
    x = frame * width
    y = row * height
    sprite_frame = sheet.subsurface(pygame.Rect(x, y, width, height))
    sprite_frame = pygame.transform.scale(sprite_frame, (width * scale, height * scale))
    return sprite_frame

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        PLAYER_SPRITE_WIDTH = 16
        PLAYER_SPRITE_HEIGHT = 16
        SPRITE_SHEET_ROW = 0
        PLAYER_SCALE = 4
        PLAYER_FRAME_COUNT = 4
        self.X_OFF_SET = 50
        self.is_hit = False
 
        # Sprites
        player_sprite_sheet = pygame.image.load("Player/StyleBird1/Bird1-1.png").convert_alpha()
        self.current_frame = 0
        self.frames = [get_sprite_frame(player_sprite_sheet, frame, PLAYER_SPRITE_WIDTH, PLAYER_SPRITE_HEIGHT, SPRITE_SHEET_ROW, PLAYER_SCALE) for frame in range(PLAYER_FRAME_COUNT)]
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(midright = ((SCREEN_WIDTH / 2) - self.X_OFF_SET, SCREEN_HEIGHT / 2))
        self.mask = pygame.mask.from_surface(self.image)
        self.up_angle_velocity = 10
        self.down_angle_velocity = 1.5
        self.target_up_angle = 30
        self.target_down_angle = -90

        # For player jump control logic
        self.jump_sound = pygame.mixer.Sound("sfx/jump.ogg")
        self.jump_sound.set_volume(1.5)
        self.hit_sound = pygame.mixer.Sound("sfx/hit.ogg")
        self.hit_sound.set_volume(0.5)
        self.time_key_pressed = 0
        self.is_jump = False
        self.jump_velocity = 8
        self.jump_distance = 72
        self.target_y_pos = None

        # For gravity
        self.gravity = 0
        self.gravity_velocity = 0.45

        self.angle = 0
    
    def get_default_rect(self):
        self.default_rect = self.image.get_rect(midright = ((SCREEN_WIDTH / 2) - self.X_OFF_SET, SCREEN_HEIGHT / 2))
        return self.default_rect
    
    # Get the difference between the current elapsed time when the game is started, and the time when the key is pressed.
    # Cooldown is 100ms. If the time difference is greater than 100ms, disable the cooldown
    # Otherwise, enable the cooldown
    def key_press_cooldown(self):
        cooldown = 150
        current_time = float(pygame.time.get_ticks())
        time_difference = current_time - self.time_key_pressed
        if time_difference > cooldown:
            return False   
        return True       
    
    # Call key_press_cooldown to check if the time is above 100ms. Will return true if it is. Explaination in the above function
    # Create a dictionary of all the keys as the keyword. Returns true or false if key is pressed or not
    # When space is pressed, get the time of of when the space bar is pressed for the above function
    # Make is_jump true so we can play the jumping animation and reach our target distance
    # The target distance is obtained by getting the difference between the current sprite positon
    # and the set jump distance (y - jump_distance)
    # Will slowly decrease the rect y value by the jump velocity when the rect y value is less than the target y value. Otherwise, disable is_jump
    def player_controls(self):
        keys = pygame.key.get_pressed()
        if not self.key_press_cooldown():
            if keys[pygame.K_SPACE]:
                self.time_key_pressed = float(pygame.time.get_ticks())
                self.jump_sound.play()
                self.is_jump = True
                self.gravity = 0
                self.target_y_pos = self.rect.y - self.jump_distance  
        
        if self.is_jump and self.rect.y > self.target_y_pos: 
            self.rect.y -= self.jump_velocity
        else:
            self.is_jump = False
        
    # Only apply the gravity is the player is not jumping
    def apply_gravity(self):
        if not self.is_jump:
            self.gravity += self.gravity_velocity
            self.rect.y += self.gravity

    # Slowly increment the current_frame (which is the index) by 0.1. Take the integer of the float value to get a integer value for the index
    # Set the current_frame to 0 if it reches to the max length of the frame list
    def animation_state(self):
        self.current_frame += 0.1
        if self.current_frame >= len(self.frames): self.current_frame = 0
        self.image = self.frames[int(self.current_frame)]
        if self.is_jump:
            if self.angle < self.target_up_angle: self.angle += self.up_angle_velocity
            self.image = pygame.transform.rotate(self.image, self.angle)
            self.rect = self.image.get_rect(midright = self.rect.midright)
            self.mask = pygame.mask.from_surface(self.image)
        else:
            if self.angle > self.target_down_angle: self.angle -= self.down_angle_velocity
            self.image = pygame.transform.rotate(self.image, self.angle)
            self.rect = self.image.get_rect(midright = self.rect.midright)
            self.mask = pygame.mask.from_surface(self.image)
        
    # Call the functions so it updates each frame when called 
    def update(self):
        self.player_controls()
        self.animation_state()
        self.apply_gravity()

class Ground(pygame.sprite.Sprite):
    def __init__(self, x_position):
        super().__init__()
        GROUND_HEIGHT = 32
        GROUND_HEIGHT_SCALE = 4

        self.image = pygame.image.load("ground/ground.png").convert()
        self.image = pygame.transform.scale(self.image, (SCREEN_WIDTH * 2, GROUND_HEIGHT * GROUND_HEIGHT_SCALE))
        self.rect = self.image.get_rect(bottomleft = (0, SCREEN_HEIGHT))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = x_position
        
        self.ground_velocity = 3.5
    
    def move_ground(self):
        self.rect.right -= self.ground_velocity 
        if self.rect.right <= 0:
            self.rect.left = SCREEN_WIDTH
    
    def update(self):
        self.move_ground()

class Pipe(pygame.sprite.Sprite):
    def __init__(self, y_placement, x_placement, pipe_type):
        super().__init__()
        PIPE_SCALE = 3

        self.pipe_velocity = 3.5

        if pipe_type == "top pipe":
            self.image = pygame.image.load("pipe/toppipe.png").convert()
            self.image = self.scale_image(PIPE_SCALE)
            self.rect = self.image.get_rect(bottomleft = (x_placement, y_placement))
            self.mask = pygame.mask.from_surface(self.image)
            self.scored = True
        elif pipe_type == "bottom pipe":
            self.image = pygame.image.load("pipe/bottompipe.png").convert()
            self.image = self.scale_image(PIPE_SCALE)
            self.rect = self.image.get_rect(topleft = (x_placement, y_placement))
            self.mask = pygame.mask.from_surface(self.image)
            self.scored = False

    def scale_image(self, pipe_scale):
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * pipe_scale, self.image.get_height() * pipe_scale))
        return self.image

    def move_pipe(self):
        self.rect.left -= self.pipe_velocity

    def update(self):
        self.move_pipe()
        self.destroy()

    def destroy(self):
	    if self.rect.right <= 0:
	        self.kill()

def collision_sprite():
    if pygame.sprite.spritecollide(player.sprite,pipe_group,False, pygame.sprite.collide_mask) or pygame.sprite.spritecollide(player.sprite,ground,False, pygame.sprite.collide_mask):
        return False
    else: return True

def get_score(player, pipes, score):
    for pipe in pipes:
        if not pipe.scored and player.rect.right > pipe.rect.left + 50:
            pipe.scored = True
            score_sound.play()
            score = score + 1
            break
    return score

def display_score(score):
    score_surf = test_font.render(f'{score}',False,(255,255,255))
    score_rect = score_surf.get_rect(center = (SCREEN_WIDTH / 2, (SCREEN_HEIGHT / 2) - 250))
    screen.blit(score_surf,score_rect)

pygame.init()

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 1000

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

player = pygame.sprite.GroupSingle()
player.add(Player())

test_font = pygame.font.Font('font/Pixeltype.ttf', 50)

ground1 = Ground(0)
ground2 = Ground(SCREEN_WIDTH)
ground = pygame.sprite.Group()
ground.add(ground1)
ground.add(ground2)

pipe_group = pygame.sprite.Group()

background_surf = pygame.image.load("background/Background3.png").convert()
background_surf = pygame.transform.scale(background_surf, (SCREEN_WIDTH, SCREEN_HEIGHT - ground1.rect.height))

score_sound = pygame.mixer.Sound('sfx/point.ogg')
score_sound.set_volume(0.8)
score = 0

game_message = test_font.render('Press space to retry',False,(255,255,255))
game_message_rect = game_message.get_rect(center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100))

clock = pygame.time.Clock()

pipe_timer = pygame.USEREVENT + 1
pygame.time.set_timer(pipe_timer,1700)

game_active = True
running = True
while running:
    game_active = collision_sprite()
    screen.blit(background_surf, (0, 0))
    pipe_group.draw(screen)
    ground.draw(screen)
    player.draw(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if game_active:
            if event.type == pipe_timer:
                toppipe_y_placement = random.randint(100, 600)
                bottompipe_y_placement = toppipe_y_placement + 175
                pipe_group.add(Pipe(toppipe_y_placement, SCREEN_WIDTH, "top pipe"))
                pipe_group.add(Pipe(bottompipe_y_placement, SCREEN_WIDTH, "bottom pipe"))
        else: 
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                pipe_group.empty()
                score = 0
                player.sprite.rect = player.sprite.get_default_rect()
                player.sprite.is_hit = False
                game_active = True

    if game_active:
        score = get_score(player.sprite, pipe_group.sprites(), score)
        pipe_group.update()
        ground.update()
        player.update()
    else:
        if not player.sprite.is_hit:
            player.sprite.hit_sound.play()
            player.sprite.is_hit = True
        screen.blit(game_message,game_message_rect)

    display_score(score)

    pygame.display.update()
    clock.tick(60)