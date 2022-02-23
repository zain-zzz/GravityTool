# imports
import pygame
import os
import time
import sys
import math
import json

# window size
pygame.init()
WIDTH, HEIGHT = 900, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("program")

# frame rate:
FPS = 60

# misc variables
dark_grey = (87, 87, 87)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)

# character sprite +/ collision rect
character_sprite = pygame.image.load(os.path.join('Assets', 'char1.png')).convert_alpha()
character_rect = character_sprite.get_rect(topleft=(0, 256))

# background image imports
main_bg = pygame.image.load(os.path.join('Assets', 'background.png')).convert()
menu_bg = pygame.image.load(os.path.join('Assets', 'main menu.png')).convert()
settings_bg = pygame.image.load(os.path.join('Assets', 'Settings.png')).convert()
custom_bg = pygame.image.load(os.path.join('Assets', 'Custom Settings.png')).convert()
custom_bg2 = pygame.image.load(os.path.join('Assets', 'Custom Settings 2.png')).convert()
new_planet_bg = pygame.image.load(os.path.join('Assets', 'New Planet.png')).convert()
blur_bg = pygame.image.load(os.path.join('Assets', 'background blur.png')).convert()
load_planet_bg = pygame.image.load(os.path.join('Assets', 'load planet.png')).convert()

# text box colour
COLOUR_INACTIVE = pygame.Color('gray')
COLOUR_ACTIVE = pygame.Color('black')

# text display
font = pygame.font.Font(os.path.join('cabin sketch', 'CabinSketch-Regular.ttf'), 60)


# main background function
def draw_window(): #could this take a background as an arguement so you can use it to load different backgrounds? - ollie
    screen.fill(dark_grey)
    screen.blit(main_bg, (0, 0))


# character drawing function
def draw_character():
    screen.blit(character_sprite, character_rect)


# display text function
def draw_text(text, font, colour, surface, x, y): #colour isn't used here, should it be? - ollie
    text_obj = font.render(text)
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)


# create input box class
class InputBox:

    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.init_width = w
        self.colour = COLOUR_INACTIVE
        self.text = text
        self.txt_surface = font.render(text, True, self.colour)
        self.active = False
        self.remove = False
        self.sideswitch = False
        self.remove_t = False

    def remove_box(self):
        self.remove = not self.remove

    def remove_text(self):
        self.remove_t = not self.remove_text
        self.text = ''
        self.txt_surface = font.render(self.text, True, self.colour)

    def display_right(self):
        self.sideswitch = not self.sideswitch

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # activates the box if the user clicks on the input box rect
            if self.rect.collidepoint(event.pos):
                # toggles whether the box is active or not
                self.active = not self.active
            else:
                self.active = False

            # changes the colour of the box if its active/inactive
            if self.active:
                self.colour = COLOUR_ACTIVE
            else:
                self.colour = COLOUR_INACTIVE

        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # renders the text again upon a user inputting text
                self.txt_surface = font.render(self.text, True, self.colour)

    def update(self):
        # Resize the box if the text is too long.
        if self.sideswitch:
            width = max(self.init_width, self.txt_surface.get_width() + 10)
            self.rect.x = self.rect.right - width
            self.rect.w = width
        else:
            width = max(self.init_width, self.txt_surface.get_width() + 10)
            self.rect.w = width

    def draw(self, screen):
        # display the text
        if self.sideswitch:
            screen.blit(self.txt_surface, (self.rect.right - self.txt_surface.get_width() - 10, self.rect.y + 5))
        else:
            screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))

        # display the rectangle
        if self.remove is False:
            pygame.draw.rect(screen, self.colour, self.rect, 2)


# create an input box with letter limits - nice use of objects I'm impressed so far - ollie
class InputBoxLimit(InputBox):
    def __init__(self, x, y, w, h, limit, text=''): #can you call the constructor of the super class - ollie
        #(super().__init__(x, y, w, h, text)) - ollie
        self.rect = pygame.Rect(x, y, w, h)
        self.init_width = w
        self.colour = COLOUR_INACTIVE
        self.text = text
        self.limit = limit
        self.txt_surface = font.render(text, True, self.colour)
        self.active = False
        self.remove = False
        self.sideswitch = False
        self.remove_t = False

    def handle_event(self, event):
        # Reworks it such that you can't type if the length of the text is the same as the limit
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            if self.active:
                self.colour = COLOUR_ACTIVE
            else:
                self.colour = COLOUR_INACTIVE

        if event.type == pygame.KEYDOWN:
            if self.active:
                print(len(self.text))
                if event.key == pygame.K_RETURN:
                    print(self.text)
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # text limit
                if len(self.text) > self.limit:
                    self.text = self.text[:-1]

                self.txt_surface = font.render(self.text, True, self.colour)


def planet_text_box(text, x, y, w, h):
    rect = pygame.Rect(x, y, w, h)
    txt_surface = font.render(text, True, BLACK)
    screen.blit(txt_surface, (rect.x + 5, rect.y + 5))
    pygame.draw.rect(screen, BLACK, rect, 2)


# sorts and searches
def mergesort(array, left_index, right_index): #extra marks if you used a more complex/faster sorting algorithm (quicksort) but don't priorise this - ollie
    if left_index >= right_index:
        return

    middle = (left_index + right_index) // 2
    mergesort(array, left_index, middle)
    mergesort(array, middle + 1, right_index)
    merge(array, left_index, right_index, middle)


def merge(array, left_index, right_index, middle):
    left_array = array[left_index:middle + 1]
    right_array = array[middle + 1:right_index + 1]

    left_array_index = 0
    right_array_index = 0
    sorted_index = left_index

    while left_array_index < len(left_array) and right_array_index < len(right_array):

        # if left array > right, place in sorted list
        if left_array[left_array_index] <= right_array[right_array_index]:
            array[sorted_index] = left_array[left_array_index]
            left_array_index = left_array_index + 1
        # opposite
        else:
            array[sorted_index] = right_array[right_array_index]
            right_array_index = right_array_index + 1

        # move pointer forward
        sorted_index = sorted_index + 1

    # loop through remaining elements if one list is empty
    while left_array_index < len(left_array):
        array[sorted_index] = left_array[left_array_index]
        left_array_index = left_array_index + 1
        sorted_index = sorted_index + 1

    while right_array_index < len(right_array):
        array[sorted_index] = right_array[right_array_index]
        right_array_index = right_array_index + 1
        sorted_index = sorted_index + 1


def binarysearch(array, target):
    start = 0
    end = len(array) - 1

    while start <= end:
        middle = (start + end) / 2
        middle = int(middle)
        midpoint = array[middle]
        if midpoint > target:
            end = middle - 1
        elif midpoint < target:
            start = middle + 1
        else:
            return midpoint


def linearsearch(array, target):
    for i in range(len(array)):
        if array[i] == target:
            return i
    return -1


# menu function
def main_menu():
    while True:
        clock = pygame.time.Clock()
        screen.fill(BLACK)
        screen.blit(menu_bg, (0, 0))
        mx, my = pygame.mouse.get_pos()
        clicking = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: #how about clicking = event.button == 1 or event.button == 2, saves 3 lines - ollie
                    clicking = True
                if event.button == 2:
                    clicking = True
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: #how about clicking != ((event.button == 1 or event.button == 2) and clicking), saves 3 lines - ollie
                    clicking = False
                if event.button == 2:
                    clicking = False

        if 255 < mx < 645: # no magic numbers, please define constant variables - ollie

            if 185 < my < 317 and clicking: #is True: you don't need 'is True' for a boolean type, just use the variable as the expression - ollie
                mainloop()

            if 340 < my < 400 and clicking is True:
                settings()

            if 415 < my < 485 and clicking is True:
                custom_settings()

        pygame.display.update()
        clock.tick(FPS)


# create planet based on mass and radius
class Planet:
    def __init__(self, PlanetMass, PlanetRadius):
        self.friction = None
        self.mass = PlanetMass
        self.radius = PlanetRadius
        self.G = 6.674 * pow(10, -11)

        self.GetGravity()
        self.GetFriction()

    def GetGravity(self):
        self.gravity = ((self.G * self.mass) / (self.radius ** 2))

    def GetFriction(self):
        self.GetGravity()
        self.friction = self.gravity / 9.8


# use inheritance to change the way g is derived on gaseous
class GasGiant(Planet):
    def __init__(self, PlanetMass, PlanetRadius):
        Planet.__init__(self, PlanetMass, PlanetRadius)
        self.mass = self.mass * 0.05245
        self.radius = self.radius * 0.35

        self.GetGravity()


# load preset planets
def settings():
    topspeed = 17
    acceleration = 0.1
    friction = 1

    while True:
        # mov settings are in the form (topspeed,acceleration,friction,gfs) as a tuple
        clock = pygame.time.Clock()
        screen.fill(BLACK)
        screen.blit(settings_bg, (0, 0))
        clicking = False
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu()
            if event.type == pygame.MOUSEBUTTONDOWN: #you can use the same tricks I meantioned on lines 277 and 282 - ollie
                if event.button == 1:
                    clicking = True
                if event.button == 2:
                    clicking = True
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    clicking = False
                if event.button == 2:
                    clicking = False

            if 175 < my < 279: #magic numbers - ollie

                if 7 < mx < 216 and clicking is True:
                    mainloop()

                if 235 < mx < 445 and clicking is True:
                    # gravity slightly increased such that the sprite is still visible
                    moon = Planet(7.35 * 10 ** 22, 1737400)
                    mainloop(mainloop(topspeed, acceleration, (friction * moon.gravity) / 9.8,
                                      moon.gravity * 1.8))

                if 463 < mx < 670 and clicking is True:
                    mars = Planet(6.39 * 10 ** 23, 3389500)
                    mainloop(mainloop(topspeed, acceleration, (friction * mars.gravity) / 9.8,
                                      mars.gravity))

                if 685 < mx < 890 and clicking is True:
                    jupiter = GasGiant(1.898 * 10 ** 27, 69911000)
                    mainloop(mainloop(topspeed, acceleration, (friction * jupiter.gravity) / 9.8,
                                      jupiter.gravity))

            if 339 < my < 428:
                if 73 < mx < 399 and clicking is True:
                    main_menu()
                if 500 < mx < 829 and clicking is True:
                    custom_settings()

        # print(f'x is {mx} y is {my}')
        pygame.display.update()
        clock.tick(FPS)


# create / load planets
def custom_settings():
    topspeed = 17
    acceleration = 0.1
    friction = 1
    gravitational_field_strength = 9.8
    while True:
        # mov settings are in the form (topspeed,acceleration,friction,gfs) as a tuple
        clock = pygame.time.Clock()
        screen.fill(BLACK)
        screen.blit(custom_bg2, (0, 0))
        clicking = False
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get(): #these event loops are very similar across some of your functions, you should try and create an helper function to reduce duplication - ollie
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    clicking = True
                if event.button == 2:
                    clicking = True
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    clicking = False
                if event.button == 2:
                    clicking = False

            if 138 < mx < 758:
                if 35 < my < 175 and clicking is True:
                    new_planet()
                if 192 < my < 332 and clicking is True:
                    load_planet()

            if 387 < my < 474:
                if 35 < mx < 434 and clicking is True:
                    mainloop(topspeed, acceleration, friction, gravitational_field_strength)
                if 460 < mx < 860 and clicking is True:
                    main_menu()

        # print(f'x is {mx} y is {my}')
        pygame.display.update()
        clock.tick(FPS)


# create planet
def new_planet():
    # input box in for x y width height
    clock = pygame.time.Clock()
    mass = InputBoxLimit(80, 115, 80, 60, 4)
    mass.display_right()
    mass_exp = InputBoxLimit(300, 115, 80, 60, 2)
    radius = InputBoxLimit(560, 115, 80, 60, 4)
    radius.display_right()
    radius_exp = InputBoxLimit(780, 115, 80, 60, 2)
    planet_name = InputBox(150, 260, 600, 60)
    input_boxes = [mass, mass_exp, radius, radius_exp, planet_name]
    clicking = False
    errorExists = False
    noError = False
    box_loop = 0
    i = 0

    while True:
        screen.blit(new_planet_bg, (0, 0))

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    clicking = True
                if event.button == 2:
                    clicking = True

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    clicking = False
                if event.button == 2:
                    clicking = False

            for box in input_boxes:
                box.handle_event(event)

        mx, my = pygame.mouse.get_pos()

        if 385 < my < 472:

            if 73 < mx < 399 and clicking is True:
                # exception handling
                try:
                    if len(planet_name.text) > 2:
                        temp_planet = Planet(float(mass.text) * (10 ** int(float(mass_exp.text))),
                                             float(radius.text) * (10 ** int(float(radius_exp.text))))
                        noError = True
                    else:
                        errorExists = True
                        errorType = 5
                        try: # This is very hard to read or look a, you shouldn't be casting like this
                            float(mass.text)
                            try:
                                int(mass_exp.text)
                                try:
                                    int(radius.text)
                                    try:
                                        int(radius_exp.text)
                                    except:
                                        errorType = 4

                                except:
                                    errorType = 3

                            except:
                                errorType = 2

                        except:
                            errorType = 1

                except:
                    errorExists = True
                    try:
                        float(mass.text)
                        try:
                            int(mass_exp.text)
                            try:
                                int(radius.text)
                                try:
                                    int(radius_exp.text)
                                except:
                                    errorType = 4

                            except:
                                errorType = 3

                        except:
                            errorType = 2

                    except:
                        errorType = 1

                clicking = False

            if 500 < mx < 829 and clicking is True:
                custom_settings()

        if errorExists:
            screen.blit(blur_bg, (0, 0))
            while box_loop == 0:

                for box in input_boxes:
                    box.remove_text()
                    box.remove_box()
                box_loop += 1
                font = pygame.font.Font(os.path.join('cabin sketch', 'CabinSketch-Regular.ttf'), 100)

            if errorType == 1: #All 5 of these cases change the same values so create a function that takes these out - ollie
                # something like def rendermessage(text1, text2, w1, h1, w2, h2):
                #                text_1 = font.render(text1, True, 'Red')
                #                text_2 = font.render(text2, True, 'Red')
                #                screen.blit(text_1, (w1, h1))
                #                screen.blit(text_2, (w2, h2))


                text_1 = font.render('Mass must be a', True, 'Red')
                text_2 = font.render('Float Value', True, 'Red')
                screen.blit(text_1, (110, 100))
                screen.blit(text_2, (200, 180))

            if errorType == 2:
                text_1 = font.render('Mass\' exponent', True, 'Red')
                text_2 = font.render('must be an Integer', True, 'Red')
                screen.blit(text_1, (120, 100))
                screen.blit(text_2, (40, 180))

            if errorType == 3:
                text_1 = font.render('Radius must be a', True, 'Red')
                text_2 = font.render('Float Value', True, 'Red')
                screen.blit(text_1, (80, 100))
                screen.blit(text_2, (200, 180))

            if errorType == 4:
                text_1 = font.render('Radius\' exponent', True, 'Red')
                text_2 = font.render('must be an Integer', True, 'Red')
                screen.blit(text_1, (80, 100))
                screen.blit(text_2, (40, 180))

            if errorType == 5:
                text_1 = font.render('Your name must be', True, 'Red')
                text_2 = font.render('>2 symbols long', True, 'Red')
                screen.blit(text_1, (20, 100))
                screen.blit(text_2, (70, 180))

            if clicking is True:
                font = pygame.font.Font(os.path.join('cabin sketch', 'CabinSketch-Regular.ttf'), 60)
                errorExists = False
                i = 0
                for box in input_boxes:
                    box.remove_box()
                    box.remove_text()
                    box_loop = 0

        if noError:
            with open("planetname.txt", "r") as file: #might need to check for file IO errors - ollie
                for x in file.readlines():
                    i += 1
            if i < 12:
                with open("planets.json", "a") as write_file:
                    json.dump(temp_planet.__dict__, write_file)
                    write_file.write('\n')
                with open("planetname.txt", "a") as f:
                    print(planet_name.text)
                    f.write(planet_name.text)
                    f.write('\n')
            else:
                pass
            custom_settings()
            # overwrite latest line with new file/// after showing warning
            # figure out a way to link the name to the json dump other than line number
            # right now im thinking of creating a sorted list for the names then using a search to link it to the line number of the json dump

        for box in input_boxes:
            box.update()

        for box in input_boxes:
            box.draw(screen)

        pygame.display.update()
        clock.tick(FPS)


# # load planet
def load_planet():
    pass
#     while True:
#         # mov settings are in the form (topspeed,acceleration,friction,gfs) as a tuple
#         clock = pygame.time.Clock()
#         screen.fill(BLACK)
#         screen.blit(load_planet_bg, (0, 0))
#         clicking = False
#         mx, my = pygame.mouse.get_pos()
#
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 sys.exit()
#             if event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_ESCAPE:
#                     main_menu()
#             if event.type == pygame.MOUSEBUTTONDOWN:
#                 if event.button == 1:
#                     clicking = True
#                 if event.button == 2:
#                     clicking = True
#             if event.type == pygame.MOUSEBUTTONUP:
#                 if event.button == 1:
#                     clicking = False
#                 if event.button == 2:
#                     clicking = False
#
#         with open("planetname.txt", "r") as file:
#             x = file.readlines()
#         with open("planetname.txt", "r") as file:
#             y = file.readlines()
#
#         mergesort(x, 0, len(x) - 1)
#
#         stripped_y = [s.strip() for s in y]
#         stripped_x = [s.strip() for s in x]
#
#         text_1 = font.render(stripped_y[0], True, 'Red')
#         text_2 = font.render(stripped_y[1], True, 'Red')
#         text_3 = font.render(stripped_y[2], True, 'Red')
#         text_4 = font.render(stripped_y[3], True, 'Red')
#         text_5 = font.render(stripped_y[4], True, 'Red')
#         text_6 = font.render(stripped_y[5], True, 'Red')
#         text_7 = font.render(stripped_y[6], True, 'Red')
#         text_8 = font.render(stripped_y[7], True, 'Red')
#         text_9 = font.render(stripped_y[8], True, 'Red')
#         text_10 = font.render(stripped_y[9], True, 'Red')
#         text_11 = font.render(stripped_y[10], True, 'Red')
#         text_12 = font.render(stripped_y[11], True, 'Red')
#
#         screen.blit(text_1, (10, 0))
#         screen.blit(text_2, (320, 0))
#         screen.blit(text_3, (620, 0))
#         screen.blit(text_4, (10, 60))
#         screen.blit(text_5, (320, 60))
#         screen.blit(text_6, (620, 60))
#         screen.blit(text_7, (10, 120))
#         screen.blit(text_8, (320, 120))
#         screen.blit(text_9, (620, 120))
#         screen.blit(text_10, (10, 180))
#         screen.blit(text_11, (320, 180))
#         screen.blit(text_12, (620, 180))
#
#         text_box('string',450,300)
#         # pick_placement = int(input(stripped_x))
#         # place = linearsearch(stripped_y, stripped_x[pick_placement])
#         # print(stripped_y[place])
#
#         pygame.display.update()
#         clock.tick(FPS)


def mainloop(*movSettings):
    # frame rate independence - runs at the same speed regardless of conditions
    last_time = time.time()
    clock = pygame.time.Clock()

    # movement - values
    speed = 0
    acceleration = 0.1
    topspeed = 17
    friction = 1

    # loops program window running - ensures it won't close
    run = True

    # movement - bools
    moving_right = False
    moving_left = False
    inputting_dora = False
    in_air = False
    slow_down = False
    was_left = False
    was_right = False

    # gravity
    gravity = 0
    gravitational_field_strength = 9.8

    # Font
    test_font = pygame.font.Font(None, 50)

    # imports
    MViterations = 0
    for x in movSettings:
        if MViterations == 0:
            topspeed = x
        if MViterations == 1:
            acceleration = x
        if MViterations == 2:
            friction = x
        if MViterations == 3:
            gravitational_field_strength = x
        MViterations += 1

    # loop -------------------------------------------------------------------#
    while run:
        # more frame rate independence

        dt = time.time() - last_time
        dt *= 60
        last_time = time.time()

        # background/sprites -------------------------------------------------#
        draw_window()
        draw_character()

        text_1 = test_font.render(f'velocity:{math.trunc(speed)}', True, 'Black')
        screen.blit(text_1, (5, 5))

        # controller
        pygame.joystick.init()
        joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

        # buttons ------------------------------------------------------------#
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            # checks directional inputs if airborne
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d or event.key == pygame.K_a:
                    inputting_dora = True
                if event.key == pygame.K_ESCAPE:
                    main_menu()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_d or event.key == pygame.K_a:
                    inputting_dora = False
            # controller directional check
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 13 or event.button == 14: #inputting_dora = event.button == 13 or event.button == 14 - same for all of these, but make sure you do right boolean logic - ollie
                    inputting_dora = True
            if event.type == pygame.JOYBUTTONUP: # if these event.types are mutually exclusive you should use elif - it's more efficent - ollie
                if event.button == 13 or event.button == 14:
                    inputting_dora = False

            # keyboard inputs
            if in_air is False:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_d:
                        moving_right = True
                        slow_down = False
                        speed = 3
                    if event.key == pygame.K_a:
                        moving_left = True
                        slow_down = False
                        speed = 3
                    if event.key == pygame.K_SPACE:
                        in_air = True
                        gravity = -20
                    # debugging tools - remove once done ***********************#
                    if event.key == pygame.K_1:
                        topspeed += 1
                        print(f'Max speed up, max speed is at:{topspeed}')
                    if event.key == pygame.K_2:
                        topspeed -= 1
                        print(f'Max speed down, max speed is at: {topspeed}')
                    if event.key == pygame.K_3:
                        gravitational_field_strength += 1
                        print(f'Gravity up, GFS is at: {gravitational_field_strength}')
                    if event.key == pygame.K_4:
                        gravitational_field_strength -= 1
                        print(f'Gravity down, GFS is at: {gravitational_field_strength}')

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a or event.key == pygame.K_d:
                        moving_right = False
                        moving_left = False
                        if in_air is False:
                            slow_down = True

                # controller
                if event.type == pygame.JOYBUTTONDOWN:
                    print(event)
                    if event.button == 14:
                        moving_right = True
                        slow_down = False
                        speed = 3
                    if event.button == 13:
                        moving_left = True
                        slow_down = False
                        speed = 3
                    if event.button == 2 or event.button == 3:
                        in_air = True
                        gravity = -20

                if event.type == pygame.JOYBUTTONUP:
                    if event.button == 13 or event.button == 14:
                        moving_right = False
                        moving_left = False
                        if in_air is False:
                            slow_down = True

        # slows down to a halt rather than immediately stopping
        if slow_down is True and in_air is False:
            if trunc_it == 1:
                speed = math.trunc(speed)
                trunc_it = 0
            else:
                pass
            if was_right:
                character_rect.x += speed * dt
            if was_left:
                character_rect.x -= speed * dt
            if speed > 0:
                speed -= friction
            if speed < 0:
                speed = 0

        else:
            trunc_it = 0

        # actions -----------------------------------------------------------#
        if moving_left is True and moving_right is True:
            moving_left = False
            moving_right = False

        if in_air is True:
            gravity += gravitational_field_strength * 0.164 * dt
            character_rect.y += gravity * dt
            if moving_right is True:
                character_rect.x += speed * dt
                # was_right = True
                # was_left = False
            if moving_left is True:
                character_rect.x -= speed * dt
                # was_right = False
                # was_left = True

        if in_air is False:
            if moving_right is True:
                character_rect.left += speed * dt
                speed += acceleration
                was_right = True
                was_left = False

            if moving_left is True:
                character_rect.left -= speed * dt
                speed += acceleration
                was_right = False
                was_left = True

            if moving_left is False and moving_right is False:
                slow_down = True

        if speed >= topspeed:
            speed = topspeed

        if was_right is True:
            moving_left = False
        if was_left is True:
            moving_right = False

        # boundaries ---------------------------------------------------------#
        if character_rect.left > 900:
            character_rect.right = 0
        if character_rect.right < 0:
            character_rect.left = 900
        if character_rect.bottom > 382:
            character_rect.bottom = 382
            # checks if they're airborne
            in_air = False
        # ensures movement doesn't continue upon landing
        if not inputting_dora and not in_air:
            moving_right = False
            moving_left = False
        # update =============================================================#
        pygame.display.update()
        clock.tick(FPS)
    pygame.quit()


# import issue prevention
if __name__ == "__main__":
    main_menu()
