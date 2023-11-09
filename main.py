import random
import pygame

# pygame setup
pygame.init()
width = 1280
height = 720
screen = pygame.display.set_mode((width, height))
surface = pygame.Surface((width, height), pygame.SRCALPHA) #SRCALPHA - allows us to draw things onto surface w/ transparency
pygame.display.set_caption("Welcome to Neal's Jetpack Joyride!")
clock = pygame.time.Clock()
font = pygame.font.Font("freesansbold.ttf", 32) #be sure to find different fonts and sizes!
bg_color = (128, 128, 128)
pause = False

initial_y = height -130
player_y = initial_y
booster = False
counter = 0
y_velocity = 0
gravity = 0.4 #play around with this
new_bg = 0

line_list = [0, width/4, 2*width/4, 3*width/4] #these represent the lines in the background
game_speed = 2

gameOn = True
new_laser = True
laser = []
distance = 0
restart_cmd = False

#rocket stuff
rocket_counter = 0
rocket_active = False
rocket_delay = 0
rocket_coords = []

#load in player info from beginning
file = open('player_info.txt', 'r')
read = file.readlines()
high_score = int(read[0])
lifetime = int(read[1])
file.close()


#move lines to create illusion of motion, draw background images via transparency
def draw_screen(lines, lase):
    screen.fill("black")
    pygame.draw.rect(surface, (bg_color[0], bg_color[1], bg_color[2], 50), [0,0, width, height]) #this is to allow for transparency
    screen.blit(surface, (0, 0))
    top = pygame.draw.rect(screen, 'gray', [0, 0, width, 50])
    bottom = pygame.draw.rect(screen, 'gray', [0, height - 50, width, 50])
    for i in range(len(lines)):
        pygame.draw.line(screen, 'black', (lines[i], 0), (lines[i], 50), 3)
        pygame.draw.line(screen, 'black', (lines[i], height - 50), (lines[i], 50), 3)
        if not pause:
            lines[i] -= game_speed #move it to the left at game speed
            lase[0][0] -= game_speed
            lase[1][0] -= game_speed
        if lines[i] < 0:
            lines[i] = width    #off the screen
    #draw lasers
    lase_line = pygame.draw.line(screen, 'yellow', (lase[0][0], lase[0][1]), (lase[1][0], lase[1][1]), 10)
    pygame.draw.circle(screen, 'yellow', (lase[0][0], lase[0][1]), 12)
    pygame.draw.circle(screen, 'yellow', (lase[1][0], lase[1][1]), 12)
    screen.blit(font.render(f'Distance: {int(distance)} m', True, 'white'), (10,10))
    screen.blit(font.render(f'High Score: {int(high_score)} m', True, 'white',), (10,70))

    return lines, top, bottom, lase, lase_line


#draw player with different animations
def draw_player():
    player_hitbox = pygame.rect.Rect((120, player_y + 10), (25, 60))
    #pygame.draw.rect(screen, 'green',player_hitbox, 5) #hitbox

    if player_y < initial_y or pause: #if we're on the ground we should be running
        if booster:
            pygame.draw.ellipse(screen, 'red', [100, player_y + 50, 20, 30])
            pygame.draw.ellipse(screen, 'orange', [106, player_y + 50, 14, 30])
            pygame.draw.ellipse(screen, 'yellow', [111, player_y + 50, 9, 30])
        pygame.draw.rect(screen, 'purple', [128, player_y + 60, 10, 20], 0, 3) #left leg
        pygame.draw.rect(screen, 'purple', [130, player_y + 60, 10, 20], 0, 3) #right leg
    else:
        #running stuff
        if counter <= 10:
            pygame.draw.line(screen, 'purple', (128, player_y + 60), (140, player_y + 80), 10)
            pygame.draw.line(screen, 'purple', (130, player_y + 60), (120, player_y + 80), 10)
        elif 10 < counter <= 20:
            pygame.draw.rect(screen, 'purple', [128, player_y + 60, 10, 20], 0, 3)
            pygame.draw.rect(screen, 'purple', [130, player_y + 60, 10, 20], 0, 3)
        elif 20 < counter <= 30:
            pygame.draw.line(screen, 'purple', (128, player_y + 60), (120, player_y + 80), 10)
            pygame.draw.line(screen, 'purple', (130, player_y + 60), (140, player_y + 80), 10)
        else:
            pygame.draw.rect(screen, 'purple', [128, player_y + 60, 10, 20], 0, 3)  # left leg
            pygame.draw.rect(screen, 'purple', [130, player_y + 60, 10, 20], 0, 3)  # right leg



    #jetpack, body, head
    pygame.draw.rect(screen, 'white', [100, player_y + 20, 20, 30], 0, 5) #jetpack
    pygame.draw.ellipse(screen, 'purple', [120, player_y + 20, 30, 50]) #player
    pygame.draw.circle(screen, 'purple', (135, player_y + 15), 10) #head
    return player_hitbox
def check_colliding(): #returns a list of two booleans, representing [ISTOUCHING_BOTTOM, ISTOUCHING_TOP]
    coll = [False, False]
    rstrt = False
    if player.colliderect(bottom_platform):
        coll[0] = True
    elif player.colliderect(top_platform):
        coll[1] = True
    if laser_line.colliderect(player):
        rstrt = True
    if rocket_active:
        if rocket.colliderect(player):
            rstrt = True
    return coll, rstrt
def generate_laser():
    # 0 = horizontal laser
    #1 = vertical laser
    laser_type = random.randint(0,1)
    offset = random.randint(10,300)
    if laser_type == 0:
        laser_width = random.randint(100, 300)
        laser_y = random.randint(100, height - 100)
        new_lase = [[width + offset, laser_y], [width + offset + laser_width, laser_y]] #look into this - must understand random boundaries
    elif laser_type == 1:
        laser_height = random.randint(100, 300)
        laser_y = random.randint(100, height - 400)
        new_lase = [[width + offset, laser_y], [width + offset, laser_y + laser_height]]  # look into this - must understand random boundaries
    return new_lase
def draw_rocket(coords, mode):
    if mode == 0:
        rock = pygame.draw.rect(screen, 'dark red', [coords[0] - 60, coords[1] - 25, 50, 50], 0, 5)
        screen.blit(font.render('!', True, 'black'), (coords[0] - 40, coords[1] - 20))
        if not pause:
            if coords[1] > player_y + 10:   #to make the offscreen warning track the player
                coords[1] -= 3
            else:
                coords[1] += 3
    else:
        rock = pygame.draw.rect(screen, 'red', [coords[0], coords[1] - 10, 50, 20], 0, 5)
        pygame.draw.ellipse(screen, 'orange', [coords[0] + 50, coords[1] - 10, 50, 20], 7) #THIS MIGHT BE WRONG
        if not pause:
            coords[0] -= 10 + game_speed #make rocket faster over time
    return coords, rock
def draw_pause():
    pygame.draw.rect(surface, (128, 128, 128, 150), [0,0, width, height]) #transparent mask
    pygame.draw.rect(surface, 'dark grey', [200, 150, 600, 50], 0, 10)
    surface.blit(font.render("game paused. press 'ESC' to resume", True, 'black'), (220, 160))
    restart_cmd = pygame.draw.rect(surface, 'white', [200, 220, 280, 50], 0, 10)
    surface.blit(font.render("restart", True, 'black'), (220, 230))
    quit_cmd = pygame.draw.rect(surface, 'white', [520, 220, 280, 50], 0, 10)
    surface.blit(font.render("quit", True, 'black'), (540, 230))
    pygame.draw.rect(surface, 'dark grey', [200, 300, 600, 50], 0, 10)
    surface.blit(font.render(f"total distance traveled: {int(lifetime)}", True, 'black'), (220, 310))
    screen.blit(surface, (0, 0))
    return restart_cmd, quit_cmd

def modify_player_info():
    global high_score, lifetime
    if distance > high_score:
        high_score = distance
    lifetime += distance
    file = open('player_info.txt', 'w')
    file.write(str(int(high_score)) + '\n')
    file.write(str(int(lifetime)))
    file.close()

while gameOn:
    clock.tick(60) #this is fps; lower if needed

    if counter < 40: #change this?
        counter += 1
    else:
        counter = 0

    if new_laser:
        laser = generate_laser()
        new_laser = False
    lines, top_platform, bottom_platform, laser, laser_line = draw_screen(line_list, laser)

    if pause:
        restart, quit_game = draw_pause()

    if not rocket_active and not pause:
        rocket_counter += 1
    if rocket_counter > 180:    #about 3 seconds - feel free to change
        rocket_counter = 0
        rocket_active = True
        rocket_delay = 0    #for the warning thing
        rocket_coords = [width, height / 2]
    if rocket_active:
        if rocket_delay < 90: #make it smaller if you want it to go for less time
            if not pause:
                rocket_delay += 1
            rocket_coords, rocket = draw_rocket(rocket_coords, 0)
        else:
            rocket_coords, rocket = draw_rocket(rocket_coords, 1)
        if rocket_coords[0] < -50:
            rocket_active = False

    player = draw_player()
    colliding, restart_cmd = check_colliding()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: #this is when you click the red X to quit
            modify_player_info()
            gameOn = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not pause:             #if we're pressing the space bar, booster is on
                booster = True
            if event.key == pygame.K_ESCAPE:
                if not pause:
                    pause = True
                else:
                    pause = False
        if event.type == pygame.KEYUP:                                #if we're no longer pressing, booster is off
            if event.key == pygame.K_SPACE:
                booster = False
        if event.type == pygame.MOUSEBUTTONDOWN and pause:
            if restart.collidepoint(event.pos):
                restart_cmd = True
            if quit_game.collidepoint(event.pos):
                modify_player_info()
                gameOn = False

    if not pause:
        distance += game_speed
        if booster:
            y_velocity -= gravity #-= goes up in pygame
        else:
            y_velocity += gravity

        if (colliding[0] and y_velocity > 0) or (colliding[1] and y_velocity < 0): #if we're falling on ground or accelerating to top - STOP
            y_velocity = 0

        player_y += y_velocity

    #speed increases
    if distance < 50000:
        game_speed = 1 + ((distance) // 500) / 10       #every 500 m traveled, speed increases by .1
    else:
        game_speed = 11

    if laser[0][0] < 0 and laser[1][0] < 0: #if the laser is off the screen, we make a new one
        new_laser= True\

    if distance - new_bg > 500:
        new_bg = distance
        bg_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) #weird syntax to avoid our character being blocked

    if restart_cmd:
        modify_player_info()
        distance = 0
        pause = False
        player_y = initial_y
        y_velocity = 0
        restart_cmd = 0
        new_laser = True
        rocket_active = False
        rocket_counter = 0
    if distance > high_score:
        high_score = int(distance)

    pygame.display.flip()



pygame.quit()