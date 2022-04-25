# imports
import pygame
import os
import time
import sys
import math
import json

# Variables =======================================================================================

# window size
pygame.init()
WINDOW_SIZE = WIDTH, HEIGHT = 900, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("program")

# frame rate:
FPS = 60

# misc variables
dark_grey = (87, 87, 87)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)

# image imports ---------------------------------

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
delete_bg = pygame.image.load(os.path.join('Assets', 'delete mode.png')).convert()

# text box colour
COLOUR_INACTIVE = pygame.Color('gray')
COLOUR_ACTIVE = pygame.Color('black')

# text display
font = pygame.font.Font(os.path.join('cabin sketch', 'CabinSketch-Regular.ttf'), 60)





# small pygame functions ------------------------


# main background function
def draw_window():
    screen.fill(dark_grey)
    screen.blit(main_bg, (0, 0))


# character drawing function
def draw_character():
    screen.blit(character_sprite, character_rect)


# display text function
def draw_text(text, font, surface, x, y):
    text_obj = font.render(text)
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)


# Classes =========================================================================================


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
        self.side_switch = False
        self.remove_t = False

    # function to make box invisible
    def remove_box(self):
        self.remove = not self.remove

    # function to make text invisible
    def remove_text(self):
        self.remove_t = not self.remove_text
        self.text = ''
        self.txt_surface = font.render(self.text, True, self.colour)

    # function to make the text appear on the right
    def display_right(self):
        self.side_switch = not self.side_switch

    # function to detect when the text box is clicked
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

        # box text input
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    # print(self.text)
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # renders the text again upon a user inputting text
                self.txt_surface = font.render(self.text, True, self.colour)

    # resizes the box; 'sideswitch' is used if the box needs to be expanded to the left rather than to the right
    def update(self):
        # Resize the box if the text is too long.
        if self.side_switch:
            width = max(self.init_width, self.txt_surface.get_width() + 10)
            self.rect.x = self.rect.right - width
            self.rect.w = width
        else:
            width = max(self.init_width, self.txt_surface.get_width() + 10)
            self.rect.w = width

    # displays the box on screen
    def draw(self, screen):
        # display the text
        if self.side_switch:
            screen.blit(self.txt_surface, (self.rect.right - self.txt_surface.get_width() - 10, self.rect.y + 5))
        else:
            screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))

        # display the rectangle
        if self.remove is False:
            pygame.draw.rect(screen, self.colour, self.rect, 2)


# create an input box with 'letter limits' - ie: the max amount of characters that can be inputted
class InputBoxLimit(InputBox):

    def __init__(self, x, y, w, h, limit, text=''):
        super().__init__(x, y, w, h, text)
        self.limit = limit

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
                # print(len(self.text))
                if event.key == pygame.K_RETURN:
                    # print(self.text)
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # text limit
                if len(self.text) > self.limit:
                    self.text = self.text[:-1]

                self.txt_surface = font.render(self.text, True, self.colour)


# create a text box that when clicked opens a planet with said function
class TextBox(InputBox):

    def __init__(self, x, y, w, h, text='', data=[], place=int):
        super().__init__(x, y, w, h, text)
        self.json_number = int
        self.data = data
        self.delete = False
        self.place = place

    def toggle_delete_mode(self):
        global COLOUR_ACTIVE
        global COLOUR_INACTIVE
        self.delete = not self.delete

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # activates the box if the user clicks on the input box rect
            if self.rect.collidepoint(event.pos):
                # toggles whether the box is active or not
                self.active = not self.active
            else:
                self.active = False
            # changes the colour of the box if its active/inactive

        if not self.delete:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.colour = COLOUR_ACTIVE
                self.txt_surface = font.render(self.text, True, self.colour)
            else:
                self.colour = COLOUR_INACTIVE
                self.txt_surface = font.render(self.text, True, self.colour)

        if self.delete:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.colour = pygame.Color('red')
                self.txt_surface = font.render(self.text, True, self.colour)
            else:
                self.colour = pygame.Color('salmon')
                self.txt_surface = font.render(self.text, True, self.colour)

        if self.active and not self.delete:
            temp_planet = Planet(self.data[int(self.json_number)]["mass"], self.data[int(self.json_number)]["radius"])
            print(f'The value of gravity for the planet is {temp_planet.gravity}')
            mainloop(mainloop(mainloop(17, 0.1, (1 * temp_planet.gravity) / 9.8,
                                       temp_planet.gravity * 1.8))
                     )

        if self.active and self.delete:
            with open("planetname.txt", "r") as file:
                lines = file.readlines()
            with open("planetname.txt", "w") as file:
                for line in lines:
                    print(line.strip("\n"), self.text)
                    if line.strip("\n") != self.text:
                        file.write(line)

            # print(self.data)
            # print(self.data[self.json_number])
            self.data.pop(self.json_number)

            with open("planets.json", "w") as write_file:
                print('')

            for item in self.data:
                with open("planets.json", "a") as write_file:
                    json.dump(item, write_file)
                    write_file.write('\n')


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


# use inheritance to change the way g is derived on gaseous planets
class GasGiant(Planet):
    def __init__(self, PlanetMass, PlanetRadius):
        Planet.__init__(self, PlanetMass, PlanetRadius)
        self.mass = self.mass * 0.05245
        self.radius = self.radius * 0.35

        self.GetGravity()


# sorts and searches ==============================================================================
def mergesort(array, left_index, right_index):  # quicksort?
    if left_index >= right_index:
        return

    middle = (left_index + right_index) // 2
    mergesort(array, left_index, middle)
    mergesort(array, middle + 1, right_index)
    merge(array, left_index, right_index, middle)  # quicksort?


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


# Menus ===========================================================================================


def menu_inputs(event, clicking):
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()

    if event.type == pygame.MOUSEBUTTONDOWN:
        clicking = event.button == 1 or event.button == 2
        return clicking

    if event.type == pygame.MOUSEBUTTONUP:
        clicking != event.button == 1 or event.button == 2
        return clicking


def render_message(text1, text2, width1, height1, width2, height2):
    font = pygame.font.Font(os.path.join('cabin sketch', 'CabinSketch-Regular.ttf'), 100)
    text_1 = font.render(text1, True, 'Red')
    text_2 = font.render(text2, True, 'Red')
    screen.blit(text_1, (width1, height1))
    screen.blit(text_2, (width2, height2))


# main menu function
def main_menu():
    global main_bg
    while True:
        clock = pygame.time.Clock()
        screen.fill(BLACK)
        screen.blit(menu_bg, (0, 0))
        mx, my = pygame.mouse.get_pos()
        clicking = False

        for event in pygame.event.get():
            clicking = menu_inputs(event, clicking)

        if 255 < mx < 645:

            if 185 < my < 317 and clicking:
                main_bg = pygame.image.load(os.path.join('Assets', 'earth.png')).convert()
                mainloop()

            if 340 < my < 400 and clicking:
                presets()

            if 415 < my < 485 and clicking:
                create_or_load()

        pygame.display.update()
        clock.tick(FPS)


# load preset planets
def presets():
    topspeed = 17
    acceleration = 0.1
    friction = 1

    while True:
        # mov settings are in the form (topspeed,acceleration,friction,gfs) as a tuple
        global main_bg
        clock = pygame.time.Clock()
        screen.fill(BLACK)
        screen.blit(settings_bg, (0, 0))
        clicking = False
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            clicking = menu_inputs(event, clicking)

            if 175 < my < 279:

                if 7 < mx < 216 and clicking:
                    main_bg = pygame.image.load(os.path.join('Assets', 'earth.png')).convert()
                    mainloop()

                if 235 < mx < 445 and clicking:
                    # gravity slightly increased such that the sprite is still visible
                    moon = Planet(7.35 * 10 ** 22, 1737400)
                    main_bg = pygame.image.load(os.path.join('Assets', 'moon.png')).convert()
                    mainloop(mainloop(topspeed, acceleration, (friction * moon.gravity) / 9.8,
                                      moon.gravity * 1.8, colour=WHITE))

                if 463 < mx < 670 and clicking:
                    mars = Planet(6.39 * 10 ** 23, 3389500)
                    main_bg = pygame.image.load(os.path.join('Assets', 'mars.png')).convert()
                    mainloop(mainloop(topspeed, acceleration, (friction * mars.gravity) / 9.8,
                                      mars.gravity))

                if 685 < mx < 890 and clicking:
                    jupiter = GasGiant(1.898 * 10 ** 27, 69911000)
                    main_bg = pygame.image.load(os.path.join('Assets', 'jupitwo.png')).convert()

                    mainloop(mainloop(topspeed, acceleration, (friction * jupiter.gravity) / 9.8,
                                      jupiter.gravity))

            if 339 < my < 428:
                if 73 < mx < 399 and clicking:
                    main_menu()
                if 500 < mx < 829 and clicking:
                    create_or_load()

        # print(f'x is {mx} y is {my}')
        pygame.display.update()
        clock.tick(FPS)


# create / load planets
def create_or_load():
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

        for event in pygame.event.get():
            clicking = menu_inputs(event, clicking)

            if 138 < mx < 758:
                if 35 < my < 175 and clicking:
                    new_planet()
                if 192 < my < 332 and clicking:
                    load_planet()

            if 387 < my < 474:
                if 35 < mx < 434 and clicking:
                    mainloop(topspeed, acceleration, friction, gravitational_field_strength)
                if 460 < mx < 860 and clicking:
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
    error_exists = False
    no_error = False
    box_loop = 0
    i = 0

    while True:
        screen.blit(new_planet_bg, (0, 0))

        for event in pygame.event.get():
            clicking = menu_inputs(event, clicking)

            for box in input_boxes:
                box.handle_event(event)

        mx, my = pygame.mouse.get_pos()

        if 385 < my < 472:

            if 73 < mx < 399 and clicking:
                # exception handling
                try:
                    if 2 < len(planet_name.text) > 16:
                        temp_planet = Planet(float(mass.text) * (10 ** int(float(mass_exp.text))),
                                             float(radius.text) * (10 ** int(float(radius_exp.text))))
                        no_error = True
                    else:
                        error_exists = True
                        errorType = 5
                except:
                    error_exists = True

                # move this up, remove other if len(x)>2...
                if error_exists:
                    try:
                        float(mass.text)
                        try:
                            int(mass_exp.text)
                            try:
                                float(radius.text)
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

            if 500 < mx < 829 and clicking:
                create_or_load()

        if error_exists:
            screen.blit(blur_bg, (0, 0))
            while box_loop == 0:

                for box in input_boxes:
                    box.remove_text()
                    box.remove_box()
                box_loop += 1

            if errorType == 1:
                render_message('Mass must be a', 'Float Value', 110, 100, 200, 180)

            if errorType == 2:
                render_message('Mass\' exponent', 'must be an Integer', 120, 100, 40, 180)

            if errorType == 3:
                render_message('Radius must be a', 'Float Value', 120, 100, 40, 180)

            if errorType == 4:
                render_message('Radius\' exponent', 'must be an Integer', 80, 100, 40, 180)

            if errorType == 5:
                render_message('Your name must be', '3-16 symbols long', 20, 100, 70, 180)

            if clicking:
                error_exists = False
                i = 0
                for box in input_boxes:
                    box.remove_box()
                    box.remove_text()
                    box_loop = 0

        if no_error:
            with open("planetname.txt", "r") as file:
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
                render_message('Too many planets', 'please delete one', 40, 100, 60, 180)
                load_planet()
            create_or_load()

        for box in input_boxes:
            box.update()

        for box in input_boxes:
            box.draw(screen)

        pygame.display.update()
        clock.tick(FPS)


# load planet
def load_planet():
    delete_mode = False
    text_boxes = []
    data = []

    with open("planets.json") as read_file:
        for line in read_file:
            data.append(json.loads(line))

    with open("planetname.txt", "r") as file:
        sorted_names = file.readlines()
    with open("planetname.txt", "r") as file:
        unsorted_names = file.readlines()

    sorted_names_placement = []

    mergesort(sorted_names, 0, len(sorted_names) - 1)

    stripped_unsorted_names = [s.strip() for s in unsorted_names]
    stripped_sorted_names = [s.strip() for s in sorted_names]

    i = 0
    for name in stripped_sorted_names:
        place = linearsearch(stripped_unsorted_names, stripped_sorted_names[i])
        sorted_names_placement.append(int(place))
        i += 1

    i = 1
    for name in stripped_sorted_names:

        if i % 3 == 1:
            x = 0
        if i % 3 == 2:
            x = 300
        if i % 3 == 0:
            x = 600

        text_boxes.append(
            TextBox(x, ((i - 1) // 3) * 60, 300, 60, text=f'{name}', data=data, place=sorted_names_placement[i - 1]))

        i += 1

    while True:
        # mov settings are in the form (topspeed,acceleration,friction,gfs) as a tuple
        clock = pygame.time.Clock()
        screen.fill(BLACK)
        if not delete_mode:
            screen.blit(load_planet_bg, (0, 0))
        if delete_mode:
            screen.blit(delete_bg, (0, 0))
        mx, my = pygame.mouse.get_pos()
        clicking = False

        for event in pygame.event.get():
            clicking = menu_inputs(event, clicking)

            i = 0
            for box in text_boxes:
                box.handle_event(event)
                box.json_number = sorted_names_placement[i]
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if box.rect.collidepoint(event.pos):
                        del box
                        text_boxes.pop(i)
                        load_planet()

                i += 1

        for box in text_boxes:
            box.update()

        for box in text_boxes:
            box.draw(screen)

        if not delete_mode:
            if 385 < my < 472:

                if 73 < mx < 399 and clicking:

                    for box in text_boxes:
                        box.toggle_delete_mode()
                    delete_mode = True
                    clicking = False

                if 500 < mx < 829 and clicking:
                    create_or_load()

        if delete_mode:
            if 73 < mx < 829 and 385 < my < 472 and clicking:
                for box in text_boxes:
                    box.toggle_delete_mode()
                delete_mode = False
                clicking = False

        pygame.display.update()
        clock.tick(FPS)


# main game loop
def mainloop(*movement_settings, colour=BLACK):
    # frame rate independence - runs at the same speed regardless of conditions
    last_time = time.time()
    clock = pygame.time.Clock()

    # movement - values
    speed = 0
    acceleration = 0.1
    topspeed = 17
    friction = 1
    cap = True

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
    jump_right = False
    jump_left = False
    directional_jump = False
    direction_loops = 0
    # gravity
    gravity = 0
    gravitational_field_strength = 9.8

    # Font
    test_font = pygame.font.Font(None, 50)

    # imports
    MViterations = 0
    for x in movement_settings:
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

        text_1 = test_font.render(f'velocity:{math.trunc(speed)}', True, colour)
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

                # reset button - grounds character
                if event.key == pygame.K_r:
                    character_rect.bottom = 382
                    in_air = False

                if event.key == pygame.K_ESCAPE:
                    main_menu()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_d or event.key == pygame.K_a:
                    inputting_dora = False
            # controller directional check
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 13 or event.button == 14:
                    inputting_dora = True
            if event.type == pygame.JOYBUTTONUP:
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

                    if event.key == pygame.K_e:
                        if not moving_left or speed == 0:
                            moving_right = True
                            moving_left = False
                            speed += 5
                            gravity = -16
                            in_air = True
                        if moving_left and speed > 5:
                            moving_right = False
                            moving_left = True
                            speed -= 5
                            gravity = -16
                            in_air = True
                        else:
                            event.key = pygame.K_q


                        # jump strength

                    if event.key == pygame.K_q:
                        if not moving_right:
                            moving_right = False
                            moving_left = True
                            speed += 5
                            gravity = -16
                            in_air = True
                        if moving_right and speed > 5:
                            moving_right = True
                            moving_left = False
                            speed -= 5
                            gravity = -16
                            in_air = True
                        else:
                            event.key = pygame.K_e

                    if event.key == pygame.K_SPACE:
                        in_air = True
                        # jump strength
                        gravity = -20

                    # debugging tools -------------------------------------------------------------
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
                    if event.key == pygame.K_a or event.key == pygame.K_d or event.key == pygame.K_e or event.key == pygame.K_q:
                        moving_right = False
                        moving_left = False
                        if in_air is False:
                            slow_down = True

                # controller
                if event.type == pygame.JOYBUTTONDOWN:
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
                        # jump strength
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
        if moving_left and moving_right:
            moving_left = False
            moving_right = False

        if direction_loops > 0:
            moving_left = False
            moving_right = True
            direction_loops -= 1

        if in_air:
            gravity += gravitational_field_strength * 0.164 * dt
            character_rect.y += gravity * dt
            if moving_right is True:
                character_rect.x += speed * dt

            if moving_left is True:
                character_rect.x -= speed * dt

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
            if cap:
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


from pygame.locals import *

grass_image = pygame.image.load(os.path.join('Assets', 'grass.png'))

#character_sprite = pygame.transform.scale(character_sprite, (50,50))

dirt_image = pygame.image.load(os.path.join('Assets', 'dirt.png'))

#dirt_image = pygame.transform.scale(dirt_image, (32, 32))
#grass_image = pygame.transform.scale(grass_image, (32, 32))
dirt_image = pygame.transform.scale(dirt_image, (68, 68))
grass_image = pygame.transform.scale(grass_image, (68, 68))

TILE_RES = grass_image.get_width()

#keep at 450,250 for now
display = pygame.Surface((1920, 1080))


game_map = [['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0','0','0','2','2','2','2','2','2','2','2','2','0','0','0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'],
            ['2','2','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','2','2'],
            ['1','1','2','2','2','2','2','2','2','2','2','2','2','2','2','2','2','2','2','2','2','2','2','2','2','2','2','1','1'],
            ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1'],
            ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1'],
            ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1'],
            ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1'],
            ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1']]

# player rect, list of tiles that aren't the ground
def collision_test(rect, tiles):
    # keeps track of all collisions
    hit_list = []
    for tile in tiles:
        # if the rect collides with the tile
        if rect.colliderect(tile):
            # adds to list
            hit_list.append(tile)
    # returns list of collisions
    return hit_list


def move(rect, movement, tiles):
    # dictionary of which way axis the player rect has collided with
    collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
    # handling x and y axis movement separately:
    # applies movement on the x axis
    rect.x += movement[0]
    # list of tiles collided with as a result of the movement
    hit_list = collision_test(rect, tiles)
    # for x axis:
    for tile in hit_list:
        # if the right side of the player rect collides with the right side of the tile:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        # vice versa
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True

    # applies movement on the y axis

    rect.y += movement[1]
    # list of tiles collided with as a result of the movement
    hit_list = collision_test(rect, tiles)
    # same as x axis but bottom with top and top with bottom
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True
    return rect, collision_types


def testloop(*movement_settings, colour=BLACK):

    clock = pygame.time.Clock()
    character_rect = pygame.Rect(50, 50, character_sprite.get_width(), character_sprite.get_height())
    moving_right = False
    moving_left = False
    in_air = False
    slow_down = False

    # speed font
    speed_font = pygame.font.Font(None, 50)

    #
    was_right = False
    was_left = False
    trunc_it = 0

    # movement - values

    gravity = 0
    speed = original_speed = 5
    acceleration = 0.1
    air_timer = 0
    topspeed = 20
    friction = 0.2
    terminal_velocity = 3
    gravitational_field_strength = 10
    last_velocity = 0

    # imports
    MViterations = 0
    for x in movement_settings:
        if MViterations == 0:
            topspeed = x
        if MViterations == 1:
            acceleration = x
        if MViterations == 2:
            friction = x
        if MViterations == 3:
            gravitational_field_strength = x
        MViterations += 1

    gravitational_field_strength = 1
    if gravitational_field_strength < 0.15:
        gravitational_field_strength = 0.15


    # loop

    while True:
        display.fill((146, 244, 255))

        velocity = [0, 0]

        # tiles
        tile_rects = []
        y = 0
        for row in game_map:
            x = 0
            for tile in row:
                if tile == '1':
                    display.blit(dirt_image, (x * TILE_RES, y * TILE_RES))
                if tile == '2':
                    display.blit(grass_image, (x * TILE_RES, y * TILE_RES))
                if tile != '0':
                    tile_rects.append(pygame.Rect(x * TILE_RES, y * TILE_RES, TILE_RES, TILE_RES))
                x += 1
            y += 1

        # if not in_air:
        #     if moving_right:
        #         velocity[0] += speed
        #         speed += acceleration
        #         was_right = True
        #         was_left = False
        #
        #     if moving_left:
        #         velocity[0] -= speed
        #         speed += acceleration
        #         was_right = False
        #         was_left = True
        #
        # else:
        #     gravity += gravitational_field_strength
        #     velocity[1] += gravity
        #
        #     if was_right:
        #         velocity[0] += speed
        #
        #     if was_left:
        #         velocity[0] -= speed
        #
        #     if moving_left is False and moving_right is False:
        #         slow_down = True

        if moving_right is True:
            velocity[0] += speed
            speed += acceleration

        if moving_left is True:
            velocity[0] -= speed
            speed += acceleration

        velocity[1] += gravity
        gravity += gravitational_field_strength


        if speed > topspeed:
            speed = topspeed

        # if gravity > terminal_velocity:
        #     gravity = terminal_velocity

        character_rect, collision_direction = move(character_rect,velocity,tile_rects)

        if collision_direction['top']:
            gravity = 0



        if velocity[1] == last_velocity:
            # print('you\'re in the air')
            # print(air_timer)
            pass
        last_velocity = velocity[1]


        print(collision_direction)
        if collision_direction['bottom']:
            gravity = 0
            air_timer = 0
            in_air = False
        else:
            air_timer += 1
            #print(f'air timer:{air_timer}')

        #print(f'gravity:{gravity}')

        if air_timer > 9:
            #print(f'air timer:{air_timer}')
            in_air = True
            #print(in_air)

        # if slow_down is True and in_air is False:
        #     if trunc_it == 1:
        #         speed = math.trunc(speed)
        #         trunc_it = 0
        #     else:
        #         pass
        #     if was_right:
        #         velocity[0] += speed
        #         print(speed)
        #     if was_left:
        #         velocity[0] -= speed
        #         print(speed)
        #     if speed > 0:
        #         speed -= friction
        #     if speed < 0:
        #         speed = 0

        display.blit(character_sprite, (character_rect.x, character_rect.y))

        for event in pygame.event.get():
            if in_air is False:
                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_d:
                        moving_right = True
                        slow_down = False
                        speed = original_speed
                    if event.key == pygame.K_a:
                        moving_left = True
                        slow_down = False
                        speed = original_speed
                    if event.key == pygame.K_SPACE:
                        in_air = True
                        # jump strength
                        gravity = -20

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a or event.key == pygame.K_d or event.key == pygame.K_e or event.key == pygame.K_q:
                        moving_right = False
                        moving_left = False
                        if in_air is False:
                            slow_down = True

            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_RIGHT:
                    moving_right = True
                if event.key == K_LEFT:
                    moving_left = True
                if event.key == K_UP:
                    if air_timer < 6:
                        gravity = -20

            if event.type == KEYUP:
                if event.key == K_RIGHT:
                    moving_right = False
                    speed = original_speed
                if event.key == K_LEFT:
                    moving_left = False
                    speed = original_speed

        surf = pygame.transform.scale(display,WINDOW_SIZE)
        screen.blit(surf, (0, 0))
        text_1 = speed_font.render(f'velocity:{math.trunc(speed)}', True, colour)
        screen.blit(text_1, (5, 5))

        pygame.display.update()
        clock.tick(FPS)


# import issue prevention
if __name__ == "__main__":
    testloop()
