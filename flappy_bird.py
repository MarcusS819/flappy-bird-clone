import pygame
from sys import exit

# Function will get each frame in the image file when called with the following parameters.
# the frame variable is how much frames are in the single image file
# the width and height varaible is the width and height per frame
# scale variable is to resize the image
def get_sprite_frame(sheet, frame, width, height, scale):
    x = frame * width
    y = 0
    sprite_frame = sheet.subsurface(pygame.Rect(x, y, width, height))
    sprite_frame = pygame.transform.scale(sprite_frame, (width * scale, height * scale))
    return sprite_frame

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        PLAYER_SPRITE_WIDTH = 16
        PLAYER_SPRITE_HEIGHT = 16
        PLAYER_FRAME_COUNT = 4
        PLAYER_SCALE = 4

        # Sprites
        player_sprite_sheet = pygame.image.load("Player/StyleBird1/Bird1-1.png").convert_alpha()
        self.current_frame = 0
        self.frames = [get_sprite_frame(player_sprite_sheet, frame, PLAYER_SPRITE_WIDTH, PLAYER_SPRITE_HEIGHT, PLAYER_SCALE) for frame in range(PLAYER_FRAME_COUNT)]
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(midright = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        self.up_angle_velocity = 10
        self.down_angle_velocity = 1.5
        self.target_up_angle = 30
        self.target_down_angle = -90

        # For player jump control logic
        self.time_key_pressed = 0
        self.is_jump = False
        self.jump_velocity = 8
        self.jump_distance = 56
        self.target_y_pos = None

        # For gravity
        self.gravity = 0
        self.gravity_velocity = 0.3

        self.angle = 0
    
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
        else:
            if self.angle > self.target_down_angle: self.angle -= self.down_angle_velocity
            self.image = pygame.transform.rotate(self.image, self.angle)
        
    
    
    # Call the functions so it updates each frame when called 
    def update(self):
        self.player_controls()
        self.apply_gravity()
        self.animation_state()

pygame.init()

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

background_surf = pygame.image.load("Background/Background3.png").convert()
background_surf = pygame.transform.scale(background_surf, (SCREEN_WIDTH, SCREEN_HEIGHT))

player = pygame.sprite.GroupSingle()
player.add(Player())

clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    screen.blit(background_surf, (0, 0))
    player.draw(screen)
    player.update()

    pygame.display.update()
    clock.tick(60)