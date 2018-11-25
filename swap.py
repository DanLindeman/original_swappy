# Star Pusher (a Sokoban clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

#import random
import sys
import copy
import os
import pygame
from pygame.locals import *
pygame.mixer.init()


from itertools import combinations
#pygame.mixer.music.load('Comtemportal.wav')
#pygame.mixer.music.play(-1)

#  if (curx, cury, 'g') in goals:
    #  mapSurf.blit(IMAGESDICT['green wall'], spaceRect)


#TODO: Implement teleportal tiles
#TODO: Implement switches that do things
#TODO: Implement multi-colored doors (purple = red + blue)

teleport_sound_effect = pygame.mixer.Sound('teleport.wav')
walk_sound_effect = pygame.mixer.Sound('walk2.wav')
player_swap_sound_effect = pygame.mixer.Sound('player_swap.wav')
wall_bump_sound_effect = pygame.mixer.Sound('wall_bump.wav')
fanfare_sound_effect = pygame.mixer.Sound('fanfare.wav')


FPS = 30  # frames per second to update the screen
WINWIDTH = 1080  # width of the program's window, in pixels
WINHEIGHT = 800  # height in pixels
HALF_WINWIDTH = int(WINWIDTH / 2)
HALF_WINHEIGHT = int(WINHEIGHT / 2)

# The total width and height of each tile in pixels.
TILEWIDTH = 50
TILEHEIGHT = 85
TILEFLOORHEIGHT = 40

CAM_MOVE_SPEED = 5  # how many pixels per frame the camera moves

# The percentage of outdoor tiles that have additional
# decoration on them, such as a tree or rock.
OUTSIDE_DECORATION_PCT = 20

BRIGHTBLUE = (0, 170, 255)
WHITE = (255, 255, 255)
BGCOLOR = BRIGHTBLUE
TEXTCOLOR = WHITE

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

COLOR_DICT = {0: 'green',
              1: 'blue',
              2: 'red',
              3: 'yellow'}

REVERSE_COLOR_DICT = {'green': 0,
                      'blue': 1,
                      'red': 2,
                      'yellow': 3}

IMG_TO_COLOR = {'g': 0,
                'b': 1,
                'r': 2,
                'y': 3}


def main():
    global REVERSE_COLOR_DICT, IMG_TO_COLOR, COLOR_DICT, FPSCLOCK, DISPLAYSURF, IMAGESDICT, TILEMAPPING, OUTSIDEDECOMAPPING, BASICFONT, PLAYERIMAGES, currentImage

    # Pygame initialization and basic set up of the global variables.
    pygame.init()
    FPSCLOCK = pygame.time.Clock()

    # Because the Surface object stored in DISPLAYSURF was returned
    # from the pygame.display.set_mode() function, this is the
    # Surface object that is drawn to the actual computer screen
    # when pygame.display.update() is called.
    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))

    pygame.display.set_caption('Swappy')
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)

    # A global dict value that will contain all the Pygame
    # Surface objects returned by pygame.image.load().
    IMAGESDICT = {'uncovered goal': pygame.image.load('RedSelector.png'),
                  'covered goal': pygame.image.load('Selector.png'),
                  'red goal': pygame.image.load('RedSelector.png'),
                  'blue goal': pygame.image.load('BlueSelector.png'),
                  'green goal': pygame.image.load('GreenSelector.png'),
                  'yellow goal': pygame.image.load('PinkSelector.png'),
                  'star': pygame.image.load('Star.png'),
                  'corner': pygame.image.load('Wood_Block_Tall.png'),
                  'wall': pygame.image.load('Wood_Block_Tall.png'),
                  'inside floor': pygame.image.load('Plain_Block.png'),
                  'outside floor': pygame.image.load('Grass_Block.png'),
                  'title': pygame.image.load('star_title.png'),
                  'solved': pygame.image.load('star_solved.png'),
                  'princess': pygame.image.load('green_princess.png'),
                  'boy': pygame.image.load('blue_boy.png'),
                  'catgirl': pygame.image.load('red_catgirl.png'),
                  'horngirl': pygame.image.load('yellow_horngirl.png'),
                  'pinkgirl': pygame.image.load('pinkgirl.png'),
                  'rock': pygame.image.load('Rock.png'),
                  'short tree': pygame.image.load('Tree_Short.png'),
                  'tall tree': pygame.image.load('Tree_Tall.png'),
                  'green wall': pygame.image.load('Green_Door.png'),
                  'red wall': pygame.image.load('Red_Door.png'),
                  'yellow wall': pygame.image.load('Yellow_Door.png'),
                  'blue wall': pygame.image.load('Blue_Door.png'),
                  'highlight_glow': pygame.image.load('highlight_glow.png'),
                  'ugly tree': pygame.image.load('Tree_Ugly.png'),
                  'some guy': pygame.image.load("some_guy.png")}

    # These dict values are global, and map the character that appears
    # in the level file to the Surface object it represents.
    TILEMAPPING = {'x': IMAGESDICT['corner'],
                   '#': IMAGESDICT['wall'],
                   ' ': IMAGESDICT['inside floor'],
                   'o': IMAGESDICT['outside floor'],
                   'g': IMAGESDICT['green wall'],
                   'r': IMAGESDICT['red wall'],
                   'y': IMAGESDICT['yellow wall'],
                   'b': IMAGESDICT['blue wall']}
    OUTSIDEDECOMAPPING = {'1': IMAGESDICT['rock'],
                          '2': IMAGESDICT['short tree'],
                          '3': IMAGESDICT['tall tree'],
                          '4': IMAGESDICT['ugly tree']}

    # PLAYERIMAGES is a list of all possible characters the player can be.
    # currentImage is the index of the player's current player image.
    currentImage = 0
    PLAYERIMAGES = [IMAGESDICT['princess'],
                    IMAGESDICT['boy'],
                    IMAGESDICT['catgirl'],
                    IMAGESDICT['pinkgirl']]

    startScreen() # show the title screen until the user presses a key

    # Read in the levels from the text file. See the readLevelsFile() for
    # details on the format of this file and how to make your own levels.
    levels = readLevelsFile('Levels.txt')
    currentLevelIndex = 0

    # The main game loop. This loop runs a single level, when the user
    # finishes that level, the next/previous level is loaded.
    while True:  # main game loop
        # Run the level to actually start playing the game:
        result = runLevel(levels, currentLevelIndex)

        if result in ('solved', 'next'):
            # Go to the next level.
            currentLevelIndex += 1
            if currentLevelIndex >= len(levels):
                # If there are no more levels, go back to the first one.
                currentLevelIndex = 0
        elif result == 'back':
            # Go to the previous level.
            currentLevelIndex -= 1
            if currentLevelIndex < 0:
                # If there are no previous levels, go to the last one.
                currentLevelIndex = len(levels)-1
        elif result == 'reset':
            pass # Do nothing. Loop re-calls runLevel() to reset the level


def runLevel(levels, levelNum):
    global currentImage
    currentImage = 0
    levelObj = levels[levelNum]
    mapObj = decorateMap(levelObj['mapObj'], levelObj['startState']['players'])
    gameStateObj = copy.deepcopy(levelObj['startState'])
    mapNeedsRedraw = True # set to True to call drawMap()
    levelSurf = BASICFONT.render('Level %s of %s' % (levelNum + 1, len(levels)), 1, TEXTCOLOR)
    levelRect = levelSurf.get_rect()
    levelRect.bottomleft = (20, WINHEIGHT - 35)
    mapWidth = len(mapObj) * TILEWIDTH
    mapHeight = (len(mapObj[0]) - 1) * TILEFLOORHEIGHT + TILEHEIGHT
    MAX_CAM_X_PAN = abs(HALF_WINHEIGHT - int(mapHeight / 2)) + TILEWIDTH
    MAX_CAM_Y_PAN = abs(HALF_WINWIDTH - int(mapWidth / 2)) + TILEHEIGHT

    levelIsComplete = False
    # Track how much the camera has moved:
    cameraOffsetX = 0
    cameraOffsetY = 0
    # Track if the keys to move the camera are being held down:
    cameraUp = False
    cameraDown = False
    cameraLeft = False
    cameraRight = False

    while True: # main game loop
        # Reset these variables:
        playerMoveTo = None
        keyPressed = False
        swapped = False
        cur_player = COLOR_DICT[currentImage]
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                # Player clicked the "X" at the corner of the window.
                terminate()

            elif event.type == KEYDOWN:
                # Handle key presses
                keyPressed = True
                if event.key == K_LEFT:
                    playerMoveTo = LEFT
                elif event.key == K_RIGHT:
                    playerMoveTo = RIGHT
                elif event.key == K_UP:
                    playerMoveTo = UP
                elif event.key == K_DOWN:
                    playerMoveTo = DOWN

                # Set the camera move mode.
                elif event.key == K_a:
                    cameraLeft = True
                elif event.key == K_d:
                    cameraRight = True
                elif event.key == K_w:
                    cameraUp = True
                elif event.key == K_s:
                    cameraDown = True

                elif event.key == K_r and (cur_player != "red"):
                    swapped = go_to_red(gameStateObj, mapObj)
                elif event.key == K_b and (cur_player != "blue"):
                    swapped = go_to_blue(gameStateObj, mapObj)
                elif event.key == K_g and (cur_player != "green"):
                    swapped = go_to_green(gameStateObj, mapObj)
                elif event.key == K_y and (cur_player != "yellow"):
                    swapped = go_to_yellow(gameStateObj, mapObj)

                elif event.key == K_n:
                    return 'next'
                elif event.key == K_z:
                    return 'back'

                elif event.key == K_PERIOD:
                    currentImage += 1
                    if currentImage >= len(gameStateObj['players']):
                        currentImage = 0
                    player_swap_sound_effect.play()
                    mapNeedsRedraw = True

                elif event.key == K_COMMA:
                    currentImage -= 1
                    if currentImage < 0:
                        currentImage = len(gameStateObj['players']) - 1
                        #currentImage = 0
                    player_swap_sound_effect.play()
                    mapNeedsRedraw = True

                elif event.key == K_ESCAPE:
                    terminate() # Esc key quits.
                elif event.key == K_BACKSPACE:
                    return 'reset' # Reset the level.

            elif event.type == KEYUP:
                # Unset the camera move mode.
                if event.key == K_a:
                    cameraLeft = False
                elif event.key == K_d:
                    cameraRight = False
                elif event.key == K_w:
                    cameraUp = False
                elif event.key == K_s:
                    cameraDown = False

        if playerMoveTo != None and not levelIsComplete:
            # If the player pushed a key to move, make the move
            # (if possible) and push any stars that are pushable.
            moved = makeMove(mapObj, gameStateObj, playerMoveTo)

            if moved:
                walk_sound_effect.play()
                # increment the step counter.
                #check_for_choices(gameStateObj)
                gameStateObj['stepCounter'] += 1
                #walk_sound_effect.play()
                mapNeedsRedraw = True

            if isLevelFinished(levelObj, gameStateObj):
                # level is solved, we should show the "Solved!" image.
                levelIsComplete = True
                keyPressed = False
        elif swapped and not levelIsComplete:
            if swapped:
                #currentImage = 1
                gameStateObj['stepCounter'] += 1
                mapNeedsRedraw = True
            if isLevelFinished(levelObj, gameStateObj):
                levelIsComplete = True
                keyPressed = False

        DISPLAYSURF.fill(BGCOLOR)
        if levelNum < 6:
            level_text(levelNum)

        if mapNeedsRedraw:
            mapSurf = drawMap(mapObj, gameStateObj, levelObj['goals'])
            mapNeedsRedraw = False

        if cameraUp and cameraOffsetY < MAX_CAM_X_PAN:
            cameraOffsetY += CAM_MOVE_SPEED
        elif cameraDown and cameraOffsetY > -MAX_CAM_X_PAN:
            cameraOffsetY -= CAM_MOVE_SPEED
        if cameraLeft and cameraOffsetX < MAX_CAM_Y_PAN:
            cameraOffsetX += CAM_MOVE_SPEED
        elif cameraRight and cameraOffsetX > -MAX_CAM_Y_PAN:
            cameraOffsetX -= CAM_MOVE_SPEED

        # Adjust mapSurf's Rect object based on the camera offset.
        mapSurfRect = mapSurf.get_rect()
        mapSurfRect.center = (HALF_WINWIDTH + cameraOffsetX, HALF_WINHEIGHT + cameraOffsetY)

        # Draw mapSurf to the DISPLAYSURF Surface object.
        DISPLAYSURF.blit(mapSurf, mapSurfRect)

        DISPLAYSURF.blit(levelSurf, levelRect)
        stepSurf = BASICFONT.render('Steps: %s' % (gameStateObj['stepCounter']), 1, TEXTCOLOR)
        stepRect = stepSurf.get_rect()
        stepRect.bottomleft = (20, WINHEIGHT - 10)
        DISPLAYSURF.blit(stepSurf, stepRect)


        if levelIsComplete:
            # is solved, show the "Solved!" image until the player
            # has pressed a key.
            solvedRect = IMAGESDICT['solved'].get_rect()
            solvedRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)
            DISPLAYSURF.blit(IMAGESDICT['solved'], solvedRect)

            if keyPressed:
                return 'solved'

        pygame.display.update()  # draw DISPLAYSURF to the screen.
        FPSCLOCK.tick()



def go_to_red(gameObj, mapObj):
    global currentImage
    player = COLOR_DICT[currentImage]
    cx, cy, color = (gameObj['players'][player][0], gameObj['players'][player][1], gameObj['players'][player][2][0])
    if isWall(mapObj, cx, cy, ''):
        return False
    if 'red' in gameObj['players']:
        rx, ry = (gameObj['players']['red'][0], gameObj['players']['red'][1])
        if isWall(mapObj, rx, ry, 'r'):
            return False
        if (rx == cx) or (ry == cy):
            gameObj['players']['red'] = (cx, cy, 'r')
            gameObj['players'][player] = (rx, ry, player[0])
            currentImage = REVERSE_COLOR_DICT['red']
            teleport_sound_effect.play()
            return True


def go_to_blue(gameObj, mapObj):
    global currentImage
    player = COLOR_DICT[currentImage]
    cx, cy, color = (gameObj['players'][player][0], gameObj['players'][player][1], gameObj['players'][player][2][0])
    if isWall(mapObj, cx, cy, ''):
        return False
    if 'blue' in gameObj['players']:
        bx, by = (gameObj['players']['blue'][0], gameObj['players']['blue'][1])
        if isWall(mapObj, bx, by, 'b'):
            return False
        if (bx == cx) or (by == cy):
            gameObj['players']['blue'] = (cx, cy, 'b')
            gameObj['players'][player] = (bx, by, player[0])
            currentImage = REVERSE_COLOR_DICT['blue']
            teleport_sound_effect.play()
            return True

def go_to_green(gameObj, mapObj):
    global currentImage
    player = COLOR_DICT[currentImage]
    cx, cy, color = (gameObj['players'][player][0], gameObj['players'][player][1], gameObj['players'][player][2][0])
    if isWall(mapObj, cx, cy, ''):
        return False
    if 'green' in gameObj['players']:
        gx, gy = (gameObj['players']['green'][0], gameObj['players']['green'][1])
        if isWall(mapObj, gx, gy, 'g'):
            return False
        if (gx == cx) or (gy == cy):
            gameObj['players']['green'] = (cx, cy, 'g')
            gameObj['players'][player] = (gx, gy, player[0])
            currentImage = REVERSE_COLOR_DICT['green']
            teleport_sound_effect.play()
            return True

def go_to_yellow(gameObj, mapObj):
    global currentImage
    player = COLOR_DICT[currentImage]
    cx, cy, color = (gameObj['players'][player][0], gameObj['players'][player][1], gameObj['players'][player][2][0])
    if isWall(mapObj, cx, cy, ''):
        return False
    if 'yellow' in gameObj['players']:
        yx, yy = (gameObj['players']['yellow'][0], gameObj['players']['yellow'][1])
        if isWall(mapObj, yx, yy, 'y'):
            return False
        if (yx == cx) or (yy == cy):
            gameObj['players']['yellow'] = (cx, cy, 'y')
            gameObj['players'][player] = (yx, yy, player[0])
            currentImage = REVERSE_COLOR_DICT['yellow']
            teleport_sound_effect.play()
            return True

def check_for_choices(gameStateObj):
    """Checks to see if there are collinear players
    """
    for player1, player2 in combinations(gameStateObj['players'], 2):
        if gameStateObj['players'][player1][1] == gameStateObj['players'][player2][1] or gameStateObj['players'][player1][0] == gameStateObj['players'][player2][0]:
            print("{} and {} are collinear".format(player1, player2))

def isWall(mapObj, x, y, color=None):
    """Returns True if the (x, y) position on
    the map is a wall, otherwise return False."""
    player_color = COLOR_DICT[currentImage][0]
    colors = ['r', 'g', 'b', 'y']
    if color:
        colors.remove(player_color)
    if x < 0 or x >= len(mapObj) or y < 0 or y >= len(mapObj[x]):
        return False # x and y aren't actually on the map.
    elif (mapObj[x][y] in ('#', 'x')):
        return True # wall is blocking
    elif (mapObj[x][y] in (colors)):
        return True
    return False


def decorateMap(mapObj, startxy):
    """Makes a copy of the given map object and modifies it.
    Here is what is done to it:
        * Walls that are corners are turned into corner pieces.
        * The outside/inside floor tile distinction is made.
        * Tree/rock decorations are randomly added to the outside tiles.

    Returns the decorated map object."""
    #player_color = COLOR_DICT[currentImage]
    #print startxy[player_color]
    #startx, starty, startcolor = startxy[player_color] # Syntactic sugar

    # Copy the map object so we don't modify the original passed
    mapObjCopy = copy.deepcopy(mapObj)

    # Remove the non-wall characters from the map data
    for x in range(len(mapObjCopy)):
        for y in range(len(mapObjCopy[0])):
            if mapObjCopy[x][y] in ('$', '.', 'G', 'B', 'Y', 'R', '+', '*', '-'):
                mapObjCopy[x][y] = ' '

    # Flood fill to determine inside/outside floor tiles.
    #floodFill(mapObjCopy, startx, starty, ' ', 'o')

    # Convert the adjoined walls into corner tiles.
    for x in range(len(mapObjCopy)):
        for y in range(len(mapObjCopy[0])):

            if mapObjCopy[x][y] == '#':
                if (isWall(mapObjCopy, x, y - 1) and isWall(mapObjCopy, x + 1, y)) or \
                   (isWall(mapObjCopy, x + 1, y) and isWall(mapObjCopy, x, y + 1)) or \
                   (isWall(mapObjCopy, x, y + 1) and isWall(mapObjCopy, x - 1, y)) or \
                   (isWall(mapObjCopy, x - 1, y) and isWall(mapObjCopy, x, y - 1)):
                    mapObjCopy[x][y] = 'x'

            #elif mapObjCopy[x][y] == ' ' and random.randint(0, 99) < OUTSIDE_DECORATION_PCT:
            #    mapObjCopy[x][y] = random.choice(list(OUTSIDEDECOMAPPING.keys()))

    return mapObjCopy


def isBlocked(mapObj, gameStateObj, x, y):
    """Returns True if the (x, y) position on the map is
    blocked by a wall or star, otherwise return False."""
    color = COLOR_DICT[currentImage][0]
    if isWall(mapObj, x, y, color):
        wall_bump_sound_effect.play()
        return True

    elif x < 0 or x >= len(mapObj) or y < 0 or y >= len(mapObj[x]):
        return True # x and y aren't actually on the map.

    elif (x, y) in gameStateObj['stars']:
        return True # a star is blocking

    return False


def makeMove(mapObj, gameStateObj, playerMoveTo):
    """Given a map and game state object, see if it is possible for the
    player to make the given move. If it is, then change the player's
    position (and the position of any pushed star). If not, do nothing.

    Returns True if the player moved, otherwise False."""

    # Make sure the player can move in the direction they want.
    player_color = COLOR_DICT[currentImage]
    playerx, playery, color = gameStateObj['players'][player_color]


    # This variable is "syntactic sugar". Typing "stars" is more
    # readable than typing "gameStateObj['stars']" in our code.
    stars = gameStateObj['stars']

    # The code for handling each of the directions is so similar aside
    # from adding or subtracting 1 to the x/y coordinates. We can
    # simplify it by using the xOffset and yOffset variables.
    if playerMoveTo == UP:
        xOffset = 0
        yOffset = -1
    elif playerMoveTo == RIGHT:
        xOffset = 1
        yOffset = 0
    elif playerMoveTo == DOWN:
        xOffset = 0
        yOffset = 1
    elif playerMoveTo == LEFT:
        xOffset = -1
        yOffset = 0

    # See if the player can move in that direction.
    if isWall(mapObj, playerx + xOffset, playery + yOffset, color):
        wall_bump_sound_effect.play()
        return False
    else:
        if (playerx + xOffset, playery + yOffset) in stars:
            # There is a star in the way, see if the player can push it.
            if not isBlocked(mapObj, gameStateObj, playerx + (xOffset*2), playery + (yOffset*2)):
                # Move the star.
                ind = stars.index((playerx + xOffset, playery + yOffset))
                stars[ind] = (stars[ind][0] + xOffset, stars[ind][1] + yOffset)
            else:
                wall_bump_sound_effect.play()
                return False
        # Move the player upwards.
        gameStateObj['players'][player_color] = (playerx + xOffset, playery + yOffset, color)
        
        return True

def level_text(level):

    topCoord = 20  # topCoord tracks where to position the top of the text

    instructionText = ['Place the player on the same-colored-goal!',
                       'Players can walk through doors of their color!',
                       'Cycle through players with the L1 and R1!',
                       'Swap places of characters when they line up by using the face buttons!',
                       'It even works vertically!',
                       'You know everything there is to know now, good luck!']

    DISPLAYSURF.fill(BGCOLOR)
    instSurf = BASICFONT.render(instructionText[level], 1, TEXTCOLOR)
    instRect = instSurf.get_rect()
    instRect.top = topCoord
    instRect.centerx = HALF_WINWIDTH
    topCoord += instRect.height 
    DISPLAYSURF.blit(instSurf, instRect)


def startScreen():
    """Display the start screen (which has the title and instructions)
    until the player presses a key. Returns None."""

    # Position the title image.
    titleRect = IMAGESDICT['title'].get_rect()
    topCoord = 50  # topCoord tracks where to position the top of the text
    titleRect.top = topCoord
    titleRect.centerx = HALF_WINWIDTH
    topCoord += titleRect.height

    # Unfortunately, Pygame's font & text system only shows one line at
    # a time, so we can't use strings with \n newline characters in them.
    # So we will use a list with each line in it.
    instructionText = ['Arrow keys to move, WASD for camera control',
                       'Backspace to reset level, Esc to quit.',
                       'N for next level, Z to go back a level.']

    # Start with drawing a blank color to the entire window:
    DISPLAYSURF.fill(BGCOLOR)

    # Draw the title image to the window:
    DISPLAYSURF.blit(IMAGESDICT['title'], titleRect)

    # Position and draw the text.
    for i in range(len(instructionText)):
        instSurf = BASICFONT.render(instructionText[i], 1, TEXTCOLOR)
        instRect = instSurf.get_rect()
        topCoord += 10  # 10 pixels will go in between each line of text.
        instRect.top = topCoord
        instRect.centerx = HALF_WINWIDTH
        topCoord += instRect.height  # Adjust for the height of the line.
        DISPLAYSURF.blit(instSurf, instRect)

    while True:  # Main loop for the start screen.
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                return # user has pressed a key, so return.

        # Display the DISPLAYSURF contents to the actual screen.
        pygame.display.update()
        FPSCLOCK.tick()


def readLevelsFile(filename):
    assert os.path.exists(filename), 'Cannot find the level file: %s' % (filename)
    mapFile = open(filename, 'r')
    # Each level must end with a blank line
    content = mapFile.readlines() + ['\r\n']
    mapFile.close()

    levels = []  # Will contain a list of level objects.
    levelNum = 0
    mapTextLines = []  # contains the lines for a single level's map.
    mapObj = []  # the map object made from the data in mapTextLines
    for lineNum in range(len(content)):
        # Process each line that was in the level file.
        line = content[lineNum].rstrip('\r\n')

        if ';' in line:
            # Ignore the ; lines, they're comments in the level file.
            line = line[:line.find(';')]

        if line != '':
            # This line is part of the map.
            mapTextLines.append(line)
        elif line == '' and len(mapTextLines) > 0:
            # A blank line indicates the end of a level's map in the file.
            # Convert the text in mapTextLines into a level object.

            # Find the longest row in the map.
            maxWidth = -1
            for i in range(len(mapTextLines)):
                if len(mapTextLines[i]) > maxWidth:
                    maxWidth = len(mapTextLines[i])
            # Add spaces to the ends of the shorter rows. This
            # ensures the map will be rectangular.
            for i in range(len(mapTextLines)):
                mapTextLines[i] += ' ' * (maxWidth - len(mapTextLines[i]))

            # Convert mapTextLines to a map object.
            for x in range(len(mapTextLines[0])):
                mapObj.append([])
            for y in range(len(mapTextLines)):
                for x in range(maxWidth):
                    mapObj[x].append(mapTextLines[y][x])

            # Loop through the spaces in the map and find the @, ., and $
            # characters for the starting game state.
            green_startx = None
            green_starty = None
            blue_startx = None
            blue_starty = None
            red_startx = None
            red_starty = None
            yellow_startx = None
            yellow_starty = None
            goals = []  # list of (x, y) tuples for each goal.
            stars = []  # list of (x, y) for each star's starting position.
            chasms = []
            player_dict = {}
            for x in range(maxWidth):
                for y in range(len(mapObj[x])):
                    if mapObj[x][y] in ('G'):
                        # '@' is player, '+' is player & goal
                        green_startx = x
                        green_starty = y
                        player_dict['green'] = (green_startx, green_starty, 'g')
                    if mapObj[x][y] in ('B'):
                        blue_startx = x
                        blue_starty = y
                        player_dict['blue'] = (blue_startx, blue_starty, 'b')
                    if mapObj[x][y] in ('R'):
                        red_startx = x
                        red_starty = y
                        player_dict['red'] = (red_startx, red_starty, 'r')
                    if mapObj[x][y] in ('Y'):
                        yellow_startx = x
                        yellow_starty = y
                        player_dict['yellow'] = (yellow_startx, yellow_starty, 'y')
                    if mapObj[x][y] in ('.', '+', '*', '-'):
                        # '.' green is goal, '*' = blue, + = red, - = yellow 
                        if mapObj[x][y] == '.':
                            goals.append((x, y, 'g'))
                        elif mapObj[x][y] == '*':
                            goals.append((x, y, 'b'))
                        elif mapObj[x][y] == '+':
                            goals.append((x, y, 'r'))
                        elif mapObj[x][y] == '-':
                            goals.append((x, y, 'y'))

                    if mapObj[x][y] in ('$'):
                        # '$' is star
                        stars.append((x, y))
                    if mapObj[x][y] in ('~'):
                        chasms.append((x, y))
            # Create level object and starting game state object.
            gameStateObj = {'players': player_dict,
                            'stepCounter': 0,
                            'stars': stars}
            levelObj = {'width': maxWidth,
                        'height': len(mapObj),
                        'mapObj': mapObj,
                        'goals': goals,
                        'startState': gameStateObj}

            levels.append(levelObj)

            # Reset the variables for reading the next map.
            mapTextLines = []
            mapObj = []
            gameStateObj = {}
            levelNum += 1
    for thing in levels[:30]:
        for stuff in thing['mapObj']:
            print(stuff)
        print("*"*60)
    return levels


def floodFill(mapObj, x, y, oldCharacter, newCharacter):
    """Changes any values matching oldCharacter on the map object to
    newCharacter at the (x, y) position, and does the same for the
    positions to the left, right, down, and up of (x, y), recursively."""

    # In this game, the flood fill algorithm creates the inside/outside
    # floor distinction. This is a "recursive" function.
    # For more info on the Flood Fill algorithm, see:
    #   http://en.wikipedia.org/wiki/Flood_fill
    if mapObj[x][y] == oldCharacter:
        mapObj[x][y] = newCharacter

    if x < len(mapObj) - 1 and mapObj[x+1][y] == oldCharacter:
        floodFill(mapObj, x+1, y, oldCharacter, newCharacter) # call right
    if x > 0 and mapObj[x-1][y] == oldCharacter:
        floodFill(mapObj, x-1, y, oldCharacter, newCharacter) # call left
    if y < len(mapObj[x]) - 1 and mapObj[x][y+1] == oldCharacter:
        floodFill(mapObj, x, y+1, oldCharacter, newCharacter) # call down
    if y > 0 and mapObj[x][y-1] == oldCharacter:
        floodFill(mapObj, x, y-1, oldCharacter, newCharacter) # call up


def drawMap(mapObj, gameStateObj, goals):
    """Draws the map to a Surface object, including the player and
    stars. This function does not call pygame.display.update(), nor
    does it draw the "Level" and "Steps" text in the corner."""

    # mapSurf will be the single Surface object that the tiles are drawn
    # on, so that it is easy to position the entire map on the DISPLAYSURF
    # Surface object. First, the width and height must be calculated.
    mapSurfWidth = len(mapObj) * TILEWIDTH
    mapSurfHeight = (len(mapObj[0]) - 1) * TILEFLOORHEIGHT + TILEHEIGHT
    mapSurf = pygame.Surface((mapSurfWidth, mapSurfHeight))
    mapSurf.fill(BGCOLOR) # start with a blank color on the surface.

    goals = [(goal[0], goal[1], goal[2]) for goal in goals]
    # Draw the tile sprites onto this surface.
    for x in range(len(mapObj)):
        for y in range(len(mapObj[x])):
            spaceRect = pygame.Rect((x * TILEWIDTH, y * TILEFLOORHEIGHT, TILEWIDTH, TILEHEIGHT))
            if mapObj[x][y] in TILEMAPPING:
                baseTile = TILEMAPPING[mapObj[x][y]]
            elif mapObj[x][y] in OUTSIDEDECOMAPPING:
                baseTile = TILEMAPPING[' ']

            # First draw the base ground/wall tile.
            mapSurf.blit(baseTile, spaceRect)

            if mapObj[x][y] in OUTSIDEDECOMAPPING:
                # Draw any tree/rock decorations that are on this tile.
                mapSurf.blit(OUTSIDEDECOMAPPING[mapObj[x][y]], spaceRect)
            elif (x, y) in gameStateObj['stars']:
                if (x, y) in goals:
                    # A goal AND star are on this space, draw goal first.
                    mapSurf.blit(IMAGESDICT['covered goal'], spaceRect)
                # Then draw the star sprite.
                mapSurf.blit(IMAGESDICT['star'], spaceRect)
            elif (x, y, 'g') in goals:
                mapSurf.blit(IMAGESDICT['green goal'], spaceRect)
            elif (x, y, 'b') in goals:
                mapSurf.blit(IMAGESDICT['blue goal'], spaceRect)
            elif (x, y, 'r') in goals:
                mapSurf.blit(IMAGESDICT['red goal'], spaceRect)
            elif (x, y, 'y') in goals:
                mapSurf.blit(IMAGESDICT['yellow goal'], spaceRect)

            # Last draw the players on the board.
            for plyr in gameStateObj['players']:
                curx, cury = (gameStateObj['players'][plyr][0], gameStateObj['players'][plyr][1])
                img = IMG_TO_COLOR[gameStateObj['players'][plyr][2]]
                if (x, y) == (curx, cury):
                    # Note: The value "currentImage" refers
                    # to a key in "PLAYERIMAGES" which has the
                    # specific player image we want to show.
                    if img == currentImage:
                        mapSurf.blit(IMAGESDICT['highlight_glow'], spaceRect)
                    mapSurf.blit(PLAYERIMAGES[img], spaceRect)

                    #mapSurf.blit(IMAGESDICT['some guy'], spaceRect)

    return mapSurf


def isLevelFinished(levelObj, gameStateObj):
    """Returns True if all the goals have the appropriate player in them."""
    all_goals = []
    all_players = []
    for goal in levelObj['goals']:
        all_goals.append(goal)
    for player in gameStateObj['players']:
        status = gameStateObj['players'][player]
        if status not in all_goals:
            return False
    fanfare_sound_effect.play()
    return True


def terminate():
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()