import pygame, heapq, math, os
from pygame.locals import *
from pygame import gfxdraw

pygame.init()

# Various Chores
infoWindow = pygame.display.Info()
widthWindow = 1920
heightWindow = 1080
widthRatio = infoWindow.current_w / widthWindow
heightRatio = infoWindow.current_h / heightWindow
widthMenu = 400
heightMenu = 0
window = pygame.Surface((widthWindow, heightWindow))
scaledWin = pygame.display.set_mode((infoWindow.current_w, infoWindow.current_h), pygame.FULLSCREEN)
background = pygame.image.load("maze.jpg")

clock = pygame.time.Clock()

# Colors
black = (0, 0, 0)
green = (0, 255, 0)
darkGreen = (0, 100, 0)
red = (255, 0, 0)
darkRed = (100, 0, 0)
blue = (0, 0, 255)
lightGray = (200, 200, 200)
gray = (150, 150, 150)
darkGray = (100, 100, 100)
yellow = (255, 255, 0)
white = (255, 255, 255)

# Fonts
font = pygame.font.Font(None, 30)
fontSymbols = pygame.font.Font(None, 100)
fontNumbers = pygame.font.Font(None, 50)
fontTitle = pygame.font.Font(None, 400)

# Variables
numCells = 50
offset = 20
xOffset = offset
yOffset = offset
arrayPlace = 0
playerx = 0
movex = 0
startx = 0
playery = 0
movey = 0
starty = 0
canMoveTime = True
counter = 0
runMaze = False
exitPosx = 0
exitPosy = 0
botPos = 0
scheduleExit = False
scheduleExitFrame = 0
targetx = 0
targety = 0
moveBOOL = True
finish_pos = None
mouseClicked = False
spacebarPressed = False
radiusMenu = 10
startScreen = True
mazeName = ""
grey_block = (0, 0)
typingMenu = None
tempFileName = ""

# Bot Variables
botAbove = 0
botBelow = 0
botLeft = 0
botRight = 0

# animations
p_loc = (0, 0)
l_time = 0
animation_time = 10
animation_mode = 0

# Setting Array
mazeArrayStart = [None] * (numCells * numCells)
mazeArray = [None] * (numCells * numCells)
instructionList = []
grayBlockList = []

# menu variables
menu_items = []
animation_mode_items = []
fog_mode_items = []
button_items = []
reset_item = []
movement_items = []
speed_item = []


def get_cell(x, y):
    if x < 0 or x >= numCells or y < 0 or y >= numCells:
        return 1
    return mazeArray[y + x * numCells]


# Get Array Index Based on x/y Coordinates
def get_pos(x, y):
    return y + x * numCells


def map(v, a, b, c, d):
    return (v - a) / (b - a) * (d - c) + c


def smooth_trans(x):
    if animation_mode_items[0].selected:
        return 1
    elif animation_mode_items[1].selected:
        return x
    elif animation_mode_items[2].selected:
        return x**2
    elif animation_mode_items[3].selected:
        return (-2 * x**3) + (3 * x**2)
    elif animation_mode_items[4].selected:
        return (2 * x) - (x**2)


def animation_offset(cur, last):
    return int(
        map(smooth_trans(map(l_time, 0.0, float(animation_time), 0.0, 1.1)), 0.0, 1.0, float(cur - last) * offset,
            0.0) if l_time < animation_time else 0)


class PathTree(object):
    NEIGHBORS = ((0, 1), (0, -1), (-1, 0), (1, 0))

    def __init__(self, x, y):
        self.sx = x
        self.sy = y
        parents = {}
        dists = {(x, y): 0}
        open = [(0, (x, y))]
        heapq.heapify(open)
        iters = numCells * numCells
        while open:
            if iters <= 0:
                raise RuntimeError('Spent too long pathing!')
            iters -= 1
            nearest = heapq.heappop(open)[1]
            dist = dists[nearest]
            ndist = dist + 1
            for dx, dy in self.NEIGHBORS:
                neigh = (nearest[0] + dx, nearest[1] + dy)
                cell = get_cell(*neigh)
                if not (cell % 10 in (2, 3) or (cell >= 10 and cell % 10 == 0)):
                    continue
                if neigh in dists:
                    if dists[neigh] > ndist:
                        dists[neigh] = ndist
                        parents[neigh] = nearest
                else:
                    dists[neigh] = ndist
                    parents[neigh] = nearest
                    heapq.heappush(open, (ndist, neigh))
        self.parents = parents
        self.dists = dists

    def get_path(self, dx, dy):
        co = (dx, dy)
        if co not in self.parents:
            return None
        path = [co]
        while co != (self.sx, self.sy):
            co = self.parents[co]
            path.append(co)
        return list(reversed(path))

    def get_dists(self):
        return self.dists


class Label(object):
    def __init__(self, string):
        self.name = string

    def get_width(self):
        return widthMenu

    def get_height(self):
        return 20

    def render(self, pos):
        textSurface = font.render(self.name, True, black)
        window.blit(textSurface, [pos[0] + self.get_width() / 2 - textSurface.get_width() / 2,
                                  pos[1] + self.get_height() / 2 - textSurface.get_height() / 2])


class RadialButton(object):
    def __init__(self, button_list, string):
        self.selected = False
        self.buttons = button_list
        self.name = string

    def get_width(self):
        return widthMenu

    def get_height(self):
        return radiusMenu * 2

    def render(self, pos, clicked, mousePos):
        textSurface = font.render(self.name, True, black)
        pygame.gfxdraw.filled_circle(window, pos[0] + radiusMenu + 5, pos[1] + self.get_height() / 2, radiusMenu, black)
        if self.selected:
            pygame.gfxdraw.filled_circle(window, pos[0] + radiusMenu + 5, pos[1] + self.get_height() / 2,
                                         radiusMenu - 3, gray)
            pygame.gfxdraw.filled_circle(window, pos[0] + radiusMenu + 5, pos[1] + self.get_height() / 2,
                                         radiusMenu - 5, blue)
        else:
            pygame.gfxdraw.filled_circle(window, pos[0] + radiusMenu + 5, pos[1] + self.get_height() / 2,
                                         radiusMenu - 3, white)
        if clicked and (pos[0] + radiusMenu + 5 - mousePos[0])**2 + (pos[1] + radiusMenu + 5 - mousePos[1])**2 < (
                radiusMenu)**2:
            for iter in self.buttons:
                iter.selected = False
            self.selected = True
        window.blit(textSurface,
                    [pos[0] + radiusMenu * 2 + 10, pos[1] + self.get_height() / 2 - textSurface.get_height() / 2])


class Button(object):
    def __init__(self, h, button_list, string, colorOn, colorOff, colorText):
        self.selected = False
        self.height = h
        self.buttons = button_list
        self.name = string
        self.colorOn = colorOn
        self.colorOff = colorOff
        self.colorText = colorText

    def get_width(self):
        return widthMenu

    def get_height(self):
        return self.height

    def render(self, pos, clicked, mousePos):
        textSurface = font.render(self.name, True, self.colorText)
        pygame.draw.rect(window, black, Rect(pos[0] + 5, pos[1] + 2, self.get_width() - 10, self.get_height()))
        if self.selected:
            pygame.draw.rect(window, self.colorOn,
                             Rect(pos[0] + 7, pos[1] + 4, self.get_width() - 14, self.get_height() - 4))
        else:
            pygame.draw.rect(window, self.colorOff,
                             Rect(pos[0] + 7, pos[1] + 4, self.get_width() - 14, self.get_height() - 4))
        if clicked and mousePos[0] > pos[0] + 5 and mousePos[0] < pos[0] + self.get_width() - 5 and mousePos[1] > pos[
            1] + 2 and mousePos[1] < pos[1] + self.get_height() + 2:
            for iter in self.buttons:
                iter.selected = False
            self.selected = True
        window.blit(textSurface, [pos[0] + self.get_width() / 2 - textSurface.get_width() / 2,
                                  pos[1] + self.get_height() / 2 - textSurface.get_height() / 2])


class NumSelector(object):
    def __init__(self, h, button_list, number):
        self.height = h
        self.buttons = button_list
        self.value = number

    def get_width(self):
        return widthMenu

    def get_height(self):
        return self.height

    def render(self, pos, clicked, mousePos):
        # Drawing Minus Button
        textMinus = fontSymbols.render("-", True, black)
        pygame.draw.rect(window, black, Rect(pos[0] + 5, pos[1] + 2, self.get_width() / 3 - 10, self.get_height()))
        pygame.draw.rect(window, lightGray,
                         Rect(pos[0] + 7, pos[1] + 4, self.get_width() / 3 - 14, self.get_height() - 4))
        window.blit(textMinus, [pos[0] + (self.get_width() / 3 - textMinus.get_width()) / 2,
                                pos[1] - (textMinus.get_height() - self.get_height()) / 2])
        if clicked and mousePos[0] > pos[0] and mousePos[0] < pos[0] + self.get_width() / 3 - 10 and mousePos[1] > pos[
            1] and mousePos[1] < pos[1] + self.get_height() and self.value > 1:
            self.value -= 1
        # Drawing Plus Button
        textPlus = fontSymbols.render("+", True, black)
        pygame.draw.rect(window, black,
                         Rect(pos[0] + self.get_width() / 3 * 2 + 5, pos[1] + 2, self.get_width() / 3 - 10,
                              self.get_height()))
        pygame.draw.rect(window, lightGray,
                         Rect(pos[0] + self.get_width() / 3 * 2 + 7, pos[1] + 4, self.get_width() / 3 - 14,
                              self.get_height() - 4))
        window.blit(textPlus, [pos[0] + (self.get_width() * 2 - self.get_width() / 3 - textPlus.get_width()) / 2,
                               pos[1] - (textPlus.get_height() - self.get_height()) / 2 - 2])
        if clicked and mousePos[0] > pos[0] + self.get_width() * 2 / 3 + 5 and mousePos[0] < pos[
            0] + self.get_width() - 5 and mousePos[1] > pos[1] and mousePos[1] < pos[1] + self.get_height():
            self.value += 1
        # Drawing Number Display
        textSurface = fontNumbers.render(str(self.value), True, black)
        pygame.draw.rect(window, black, Rect(pos[0] + self.get_width() / 3 + 10, pos[1] + 2, self.get_width() / 3 - 20,
                                             self.get_height()))
        pygame.draw.rect(window, white, Rect(pos[0] + self.get_width() / 3 + 12, pos[1] + 4, self.get_width() / 3 - 24,
                                             self.get_height() - 4))
        window.blit(textSurface, [pos[0] + (self.get_width() - textSurface.get_width()) / 2,
                                  pos[1] - (textSurface.get_height() - self.get_height()) / 2 + 2])


class FileSelector(object):
    def __init__(self, h, fileName, y):
        self.widthBox = 550
        self.height = h
        self.tempFile = ""
        self.file = fileName
        self.clicked = False
        self.y = y

    def render(self, clicked, mousePos, cTextInterface):
        # Drawing the Box
        textLabel = fontNumbers.render("Maze:", True, black)
        pygame.draw.rect(window, black, Rect(widthWindow / 2 - self.widthBox / 2, self.y, self.widthBox, self.height))
        pygame.draw.rect(window, white,
                         Rect(widthWindow / 2 - self.widthBox / 2 + 2, self.y + 2, self.widthBox - 4, self.height - 4))
        window.blit(textLabel,
                    [widthWindow / 2 - self.widthBox / 2 + 10, self.y + self.height / 2 - textLabel.get_height() / 2])
        # Detecting a Click
        if not self.clicked:
            textSurface = fontNumbers.render(self.file, True, black)
            window.blit(textSurface, [widthWindow / 2 + textLabel.get_width() / 2 - textSurface.get_width() / 2,
                                      self.y + self.height / 2 - textSurface.get_height() / 2])
        else:
            textSurface = fontNumbers.render(self.tempFile, True, black)
            window.blit(textSurface, [widthWindow / 2 + textLabel.get_width() / 2 - textSurface.get_width() / 2,
                                      self.y + self.height / 2 - textSurface.get_height() / 2])
        if clicked and widthWindow / 2 - self.widthBox / 2 < mousePos[
            0] < widthWindow / 2 + self.widthBox / 2 and self.y < mousePos[1] < self.y + self.height:
            self.clicked = True
            self.tempFile = ""
            cTextInterface.currentTextBox = self


class CurrentTextInterface(object):

    def __init__(self):
        self.currentTextBox = None


textTitle = fontTitle.render("Maze Bot", True, white)
textTitleOutline = fontTitle.render("Maze Bot", True, black)
menuStart = (widthWindow / 2 - widthMenu / 2, heightWindow / 2 - heightMenu / 2 + 150)
fileSelector = FileSelector(100, mazeName, textTitle.get_height())
currentTextInterface = CurrentTextInterface()

# Append Start and Stop Buttons
button_items.append(Button(60, button_items, "Start", green, darkGreen, black))
button_items.append(Button(60, button_items, "Stop", red, darkRed, black))
for iter in button_items:
    menu_items.append(iter)
button_items[1].selected = True

# Append Reset Button
reset_item.append(Button(60, reset_item, "Reset", gray, gray, black))
menu_items.append(reset_item[0])

# Append Animation Settings
menu_items.append(Label("Animation Settings"))
animation_mode_items.append(RadialButton(animation_mode_items, "No Animation"))
animation_mode_items.append(RadialButton(animation_mode_items, "Smooth Movement"))
animation_mode_items.append(RadialButton(animation_mode_items, "Accelerate"))
animation_mode_items.append(RadialButton(animation_mode_items, "Sudden Start, Decelerate"))
animation_mode_items.append(RadialButton(animation_mode_items, "Accelerate and Decelerate"))
for iter in animation_mode_items:
    menu_items.append(iter)
animation_mode_items[1].selected = True

# Append Fog of War Settings
menu_items.append(Label("Fog of War Settings"))
fog_mode_items.append(RadialButton(fog_mode_items, "Normal"))
fog_mode_items.append(RadialButton(fog_mode_items, "Fog of War"))
for iter in fog_mode_items:
    menu_items.append(iter)
fog_mode_items[0].selected = True

# Append Exploration Settings
menu_items.append(Label("Movement Settings"))
movement_items.append(RadialButton(movement_items, "Auto Mode"))
movement_items.append(RadialButton(movement_items, "Ignore Exit Mode"))
movement_items.append(RadialButton(movement_items, "Seek Exit Mode"))
for iter in movement_items:
    menu_items.append(iter)
movement_items[0].selected = True

# Append Speed Settings
menu_items.append(Label("Frames Per Move"))
speed_item.append(NumSelector(60, speed_item, animation_time))
menu_items.append(speed_item[0])

# Append Menu Button
button_items.append(Button(60, button_items, "Back to Menu", lightGray, lightGray, black))
menu_items.append(button_items[len(button_items) - 1])

# Append Quit Button
button_items.append(Button(60, button_items, "Quit", black, black, white))
menu_items.append(button_items[len(button_items) - 1])

# Main Loop
while True:

    # Start Screen
    while startScreen:

        # Blit Background
        window.blit(background, (0, 0))
        window.blit(textTitleOutline, [widthWindow / 2 - textTitleOutline.get_width() / 2 - 5, 5])
        window.blit(textTitleOutline, [widthWindow / 2 - textTitleOutline.get_width() / 2 + 5, -5])
        window.blit(textTitleOutline, [widthWindow / 2 - textTitleOutline.get_width() / 2 - 5, -5])
        window.blit(textTitleOutline, [widthWindow / 2 - textTitleOutline.get_width() / 2 + 5, 5])
        window.blit(textTitleOutline, [widthWindow / 2 - textTitleOutline.get_width() / 2 - 5, 0])
        window.blit(textTitleOutline, [widthWindow / 2 - textTitleOutline.get_width() / 2 + 5, 0])
        window.blit(textTitleOutline, [widthWindow / 2 - textTitleOutline.get_width() / 2, -5])
        window.blit(textTitleOutline, [widthWindow / 2 - textTitleOutline.get_width() / 2, 5])
        window.blit(textTitle, [widthWindow / 2 - textTitle.get_width() / 2, 0])

        # Detect Mouse Position
        posMouse = pygame.mouse.get_pos()
        posMouse = (posMouse[0] / widthRatio, posMouse[1] / heightRatio)
        for event in pygame.event.get():

            # Checking Mouse Click
            if event.type == MOUSEBUTTONDOWN:
                mouseClicked = True
                if not currentTextInterface.currentTextBox == None:
                    if not currentTextInterface.currentTextBox.withinBounds(posMouse):
                        currentTextInterface.currentTextBox.clicked = False
                        currentTextInterface.currentTextBox = None

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    exit()

            if event.type == KEYDOWN and not currentTextInterface.currentTextBox == None:
                tempFileName = currentTextInterface.currentTextBox.tempFile
                if event.key == K_a:
                    tempFileName += "a"
                if event.key == K_b:
                    tempFileName += "b"
                if event.key == K_c:
                    tempFileName += "c"
                if event.key == K_d:
                    tempFileName += "d"
                if event.key == K_e:
                    tempFileName += "e"
                if event.key == K_f:
                    tempFileName += "f"
                if event.key == K_g:
                    tempFileName += "g"
                if event.key == K_h:
                    tempFileName += "h"
                if event.key == K_i:
                    tempFileName += "i"
                if event.key == K_j:
                    tempFileName += "j"
                if event.key == K_k:
                    tempFileName += "k"
                if event.key == K_l:
                    tempFileName += "l"
                if event.key == K_m:
                    tempFileName += "m"
                if event.key == K_n:
                    tempFileName += "n"
                if event.key == K_o:
                    tempFileName += "o"
                if event.key == K_p:
                    tempFileName += "p"
                if event.key == K_q:
                    tempFileName += "q"
                if event.key == K_r:
                    tempFileName += "r"
                if event.key == K_s:
                    tempFileName += "s"
                if event.key == K_t:
                    tempFileName += "t"
                if event.key == K_u:
                    tempFileName += "u"
                if event.key == K_v:
                    tempFileName += "v"
                if event.key == K_w:
                    tempFileName += "w"
                if event.key == K_x:
                    tempFileName += "x"
                if event.key == K_y:
                    tempFileName += "y"
                if event.key == K_z:
                    tempFileName += "z"
                if event.key == K_0:
                    tempFileName += "0"
                if event.key == K_1:
                    tempFileName += "1"
                if event.key == K_2:
                    tempFileName += "2"
                if event.key == K_3:
                    tempFileName += "3"
                if event.key == K_4:
                    tempFileName += "4"
                if event.key == K_5:
                    tempFileName += "5"
                if event.key == K_6:
                    tempFileName += "6"
                if event.key == K_7:
                    tempFileName += "7"
                if event.key == K_8:
                    tempFileName += "8"
                if event.key == K_9:
                    tempFileName += "9"
                if event.key == K_PERIOD:
                    tempFileName += "."
                if event.key == K_UNDERSCORE:
                    tempFileName += "_"
                if event.key == K_BACKSPACE:
                    tempFileName = tempFileName[0:len(tempFileName) - 1]
                if event.key == K_RETURN:
                    if os.path.exists(currentTextInterface.currentTextBox.tempFile):
                        currentTextInterface.currentTextBox.clicked = False
                        currentTextInterface.currentTextBox.file = currentTextInterface.currentTextBox.tempFile
                        currentTextInterface.currentTextBox = None
                    else:
                        currentTextInterface.currentTextBox.clicked = False
                        currentTextInterface.currentTextBox = None
                if not currentTextInterface.currentTextBox == None:
                    currentTextInterface.currentTextBox.tempFile = tempFileName

            # Checking for Quit
            if event.type == QUIT:
                pygame.quit()
                exit()

        fileSelector.render(mouseClicked, posMouse, currentTextInterface)

        # Menu
        heightMenu = 10
        for iter in menu_items:
            if not iter == menu_items[1] and not iter == menu_items[2] and not iter == menu_items[len(menu_items) - 2]:
                heightMenu += iter.get_height() + 5
        menu_start_pos = (widthWindow / 2 - widthMenu / 2, heightWindow / 2 - heightMenu / 2 + 150)
        pygame.draw.rect(window, white, Rect(menu_start_pos[0], menu_start_pos[1], widthMenu, heightMenu))
        menu_start_pos = (menu_start_pos[0], menu_start_pos[1] + 5)
        for iter in menu_items:
            if not iter == menu_items[1] and not iter == menu_items[2] and not iter == menu_items[len(menu_items) - 2]:
                iter.render(menu_start_pos, mouseClicked, posMouse)
                menu_start_pos = (menu_start_pos[0], menu_start_pos[1] + iter.get_height() + 5)

        # Check if Started
        if button_items[0].selected == True:
            mazeName = fileSelector.file
            startScreen = False
            runMaze = True

        # Quit Button
        if button_items[len(button_items) - 1].selected:
            pygame.quit()
            exit()

        pygame.transform.smoothscale(window, scaledWin.get_size(), scaledWin)
        mouseClicked = False
        pygame.display.update()
    button_items[0].selected == False
    button_items[1].selected == True

    # Opening and Filling in the Array
    mazeData = open(mazeName, 'r')
    for i in range(0, len(mazeArrayStart), 1):
        temp = mazeData.read(1)
        # Putting Walls into the Array
        if temp == "1":
            mazeArrayStart[i] = 1
        # Putting Start into the Array
        if temp == "2":
            mazeArrayStart[i] = 2
        # Putting Finish into the Array
        if temp == "3":
            mazeArrayStart[i] = 3
        # Putting Space into the Array
        if temp == "0":
            mazeArrayStart[i] = 0

    for i in range(0, len(mazeArrayStart), 1):
        mazeArray[i] = mazeArrayStart[i]

    # Putting the Bot at the Start

    arrayPlace = 0
    for x in range(0, numCells, 1):
        for y in range(0, numCells, 1):
            if mazeArray[arrayPlace] == 2:
                playerx = x
                startx = x
                playery = y
                starty = y
                start_pos = (x, y)
                p_loc = (playerx, playery)
            arrayPlace += 1

    # Main Loop
    while runMaze:
        # Detect Mouse Position
        posMouse = pygame.mouse.get_pos()
        posMouse = (posMouse[0] / widthRatio, posMouse[1] / heightRatio)

        # Resetting the Animation Time
        animation_time = speed_item[0].value

        # Reset Array
        arrayPlace = 0
        # Reset Screen
        window.fill(black)

        # Resetting the Maze
        if reset_item[0].selected:
            for i in range(0, len(mazeArrayStart), 1):
                mazeArray[i] = mazeArrayStart[i]
            button_items[0].selected = False
            button_items[1].selected = True
            counter = 0
            if instructionList:
                del instructionList[:]
            canMoveTime = False
            l_time = 0
            p_loc = start_pos
            playerx = start_pos[0]
            playery = start_pos[1]
            scheduleExit = False
            scheduleExitFrame = 0
            reset_item[0].selected = False
            finish_pos = None

        # Moving Bot
        for event in pygame.event.get():

            # Checking for Pressing Down Key
            if event.type == KEYDOWN and movex == 0 and movey == 0:
                if event.key == K_UP:
                    # movey-=offset
                    movey = -1
                elif event.key == K_DOWN:
                    # movey+=offset
                    movey = 1
                elif event.key == K_LEFT:
                    # movex-=offset
                    movex = -1
                elif event.key == K_RIGHT:
                    # movex+=offset
                    movex = 1

            # Checking for Letting go of Key
            if event.type == KEYUP:
                if event.key == K_UP:
                    movey = 0
                elif event.key == K_DOWN:
                    movey = 0
                elif event.key == K_LEFT:
                    movex = 0
                elif event.key == K_RIGHT:
                    movex = 0

            # Checking Mouse Click
            if event.type == MOUSEBUTTONDOWN:
                mouseClicked = True

            # Checking for Quit
            if event.type == QUIT:
                pygame.quit()
                exit()

        # Draw Maze
        for xOffset in range((widthWindow / 2 - offset * numCells / 2), (widthWindow / 2 + offset * numCells / 2),
                             offset):
            for yOffset in range((heightWindow / 2 - offset * numCells / 2), (heightWindow / 2 + offset * numCells / 2),
                                 offset):
                # Draw Spaces
                if mazeArray[arrayPlace] % 10 == 0:
                    pygame.draw.rect(window, white if fog_mode_items[0].selected else black,
                                     Rect(xOffset, yOffset, offset, offset))
                # Draw Walls
                if mazeArray[arrayPlace] % 10 == 1:
                    pygame.draw.rect(window, black, Rect(xOffset, yOffset, offset, offset))
                # Draw Start
                if mazeArray[arrayPlace] % 10 == 2:
                    pygame.draw.rect(window, green, Rect(xOffset, yOffset, offset, offset))
                # Draw Finish
                if mazeArray[arrayPlace] % 10 == 3:
                    pygame.draw.rect(window, red if finish_pos is not None or fog_mode_items[0].selected else black,
                                     Rect(xOffset, yOffset, offset, offset))
                if not movement_items[1].selected and mazeArray[arrayPlace] == 11:
                    mazeArray[arrayPlace] = 3
                # Draw Path Found
                if mazeArray[arrayPlace] == 10:
                    pygame.draw.rect(window, gray, Rect(xOffset, yOffset, offset, offset))
                    targetx = xOffset
                    targety = yOffset
                    grayBlockList.append((xOffset, yOffset))
                # Draw Path Explored
                if mazeArray[arrayPlace] == 20:
                    pygame.draw.rect(window, yellow, Rect(xOffset, yOffset, offset, offset))
                arrayPlace += 1

        # Draw Bot
        if instructionList and not scheduleExit:
            for co in instructionList:
                pygame.draw.circle(window, red, (widthWindow / 2 - offset * numCells / 2 + co[0] * offset + offset / 2,
                                                 heightWindow / 2 - offset * numCells / 2 + co[
                                                     1] * offset + offset / 2), offset / 4, 0)
        pygame.draw.circle(window, blue, (
        (widthWindow / 2 - offset * numCells / 2 + offset / 2) + playerx * offset - animation_offset(playerx, p_loc[0]),
        (heightWindow / 2 - offset * numCells / 2 + offset / 2) + playery * offset - animation_offset(playery,
                                                                                                      p_loc[1])),
                           offset / 2, 0)

        # Reading the Surroundings
        botPos = get_cell(playerx, playery)
        botAbove = get_cell(playerx, playery - 1)
        botBelow = get_cell(playerx, playery + 1)
        botLeft = get_cell(playerx - 1, playery)
        botRight = get_cell(playerx + 1, playery)

        # Setting if Block has Been Found
        if botAbove < 10 and playery - 1 >= 0 and not mazeArray[get_pos(playerx, playery - 1)] == 1:
            mazeArray[get_pos(playerx, playery - 1)] = 10 + botAbove % 10
            if mazeArray[get_pos(playerx, playery - 1)] % 10 == 3:
                finish_pos = (playerx, playery - 1)
        if botBelow < 10 and playery + 1 < numCells and not mazeArray[get_pos(playerx, playery + 1)] == 1:
            mazeArray[get_pos(playerx, playery + 1)] = 10 + botBelow % 10
            if mazeArray[get_pos(playerx, playery + 1)] % 10 == 3:
                finish_pos = (playerx, playery + 1)
        if botLeft < 10 and playerx - 1 >= 0 and not mazeArray[get_pos(playerx - 1, playery)] == 1:
            mazeArray[get_pos(playerx - 1, playery)] = 10 + botLeft % 10
            if mazeArray[get_pos(playerx - 1, playery)] % 10 == 3:
                finish_pos = (playerx - 1, playery)
        if botRight < 10 and playerx + 1 < numCells and not mazeArray[get_pos(playerx + 1, playery)] == 1:
            mazeArray[get_pos(playerx + 1, playery)] = 10 + botRight % 10
            if mazeArray[get_pos(playerx + 1, playery)] % 10 == 3:
                finish_pos = (playerx + 1, playery)

        # Setting if Block has Been Traveled
        if botPos < 20:
            mazeArray[get_pos(playerx, playery)] = 20 + botPos % 10

        # Checking if End was Reached
        if get_cell(playerx, playery) % 10 == 3 and not movement_items[1].selected == True:
            scheduleExit = True

        if scheduleExit:
            scheduleExitFrame += 1
            if scheduleExitFrame >= 60:
                playerx = start_pos[0]
                playery = start_pos[1]
                scheduleExit = False
                scheduleExitFrame = 0

        if button_items[0].selected:

            # Counter Stuff
            if not canMoveTime and not scheduleExit:
                counter += 1
            if counter >= animation_time:
                canMoveTime = True
                counter = 0

            # Automoving the Bot
            if instructionList:
                pc = (playerx, playery)
                while instructionList and instructionList[0] != pc:
                    instructionList.pop(0)
                if len(instructionList) <= 1 or movement_items[1]:
                    del instructionList[:]
            if not instructionList:
                pathTree = PathTree(playerx, playery)
                if finish_pos is not None:
                    if movement_items[0].selected or movement_items[2].selected:
                        instructionList = pathTree.get_path(*finish_pos)
                if not instructionList and not movement_items[2].selected:
                    grey_block = None
                    pairs = sorted(pathTree.dists.items(), key=lambda pair: pair[1])
                    for loc, dist in pairs:
                        if 10 <= get_cell(*loc) < 20:
                            grey_block = loc
                            break
                    if grey_block is None and not movement_items[1].selected:
                        instructionList = pathTree.get_path(*finish_pos)
                    else:
                        if not grey_block is None:
                            instructionList = pathTree.get_path(*grey_block)
            if instructionList:
                pc = (playerx, playery)
                while instructionList and instructionList[0] != pc:
                    instructionList.pop(0)
                if len(instructionList) > 1:
                    # Compute next target
                    target = instructionList[1]
                    movex = target[0] - playerx
                    movey = target[1] - playery
                else:
                    del instructionList[:]
            else:
                movex = 0
                movey = 0

            l_time += 1
            # Moving the Bot
            if canMoveTime and not animation_time == 0:
                canMoveTime = False
                if get_cell(playerx + movex, playery + movey) % 10 != 1:
                    p_loc = (playerx, playery)
                    playerx += movex
                    playery += movey
                    l_time = 0

        # Confine Bot to Bounds
        if playerx < 0:
            playerx = 0
        if playerx > numCells - 1:
            playerx = numCells - 1
        if playery < 0:
            playery = 0
        if playery > numCells - 1:
            playery = numCells - 1

        # BUTTONS
        # Lefthand Menu
        heightMenu = 10
        for iter in menu_items:
            heightMenu += iter.get_height() + 5
        menu_start_pos = (
        (widthWindow / 2 - numCells * offset / 2) / 2 - widthMenu / 2, heightWindow / 2 - heightMenu / 2)
        pygame.draw.rect(window, white, Rect(menu_start_pos[0], menu_start_pos[1], widthMenu, heightMenu))
        menu_start_pos = (menu_start_pos[0], menu_start_pos[1] + 5)
        for iter in menu_items:
            iter.render(menu_start_pos, mouseClicked, posMouse)
            menu_start_pos = (menu_start_pos[0], menu_start_pos[1] + iter.get_height() + 5)

        # Back to Menu
        if button_items[len(button_items) - 2].selected:
            runMaze = False
            button_items[0].selected = False
            button_items[1].selected = True
            if instructionList:
                del instructionList[:]
            canMoveTime = False
            l_time = 0
            p_loc = start_pos
            playerx = start_pos[0]
            playery = start_pos[1]
            scheduleExit = False
            scheduleExitFrame = 0
            reset_item[0].selected = False
            arrayPlace = 0
            startScreen = True
            finish_pos = None

        # Quit Button
        if button_items[len(button_items) - 1].selected:
            pygame.quit()
            exit()

        pygame.transform.smoothscale(window, scaledWin.get_size(), scaledWin)

        mouseClicked = False
        # Updating Things
        pygame.display.update()
        clock.tick(60)
