import config as c
import json
import pygame
pygame.init()
import math
import numpy as np
import random


#constants
METAL_CHAIN = {
    "lead": "tin",
    "tin": "iron",
    "iron": "copper",
    "copper": "silver",
    "silver": "gold"
} #Used to propagate the current metal

#initialize global variables
score = 0
click = pygame.sprite.Group()
unclick = pygame.sprite.Group()
selection1 = None
selection2 = None
play_again_btn = pygame.Rect(c.WIDTH*0.01, c.WIDTH*0.01, c.WIDTH*0.2, c.WIDTH*0.07)
quit_btn = pygame.Rect(c.WIDTH-c.WIDTH*0.21, c.WIDTH*0.01, c.WIDTH*0.2, c.WIDTH*0.07)
element_numbers = {
    'fire': 8,
    'water': 8,
    'air': 8,
    'earth': 8,
    'salt': 4,
    'seperator': 1,
    'quicksilver': 5,
    'lead': 1,
    'tin': 1,
    'iron': 1,
    'copper': 1,
    'silver': 1,
    'gold': 1
}
myFont = pygame.font.SysFont("Times New Roman", 18)

#screen setup
screen = pygame.display.set_mode((c.WIDTH, c.HEIGHT))

class Marble(pygame.sprite.Sprite):
    """extention of pygame sprites to get marble functionality"""
    @staticmethod
    def getCenterOfTile(pos):
        """Gets the pixel coordinates as a tuple of a tile specified by x and y"""
        px = 2*c.TILE_RADIUS * pos[0] - c.TILE_RADIUS * pos[1] + c.X_0
        py = math.sqrt(3) * c.TILE_RADIUS * pos[1] + c.Y_0
        return (px, py)

    def __init__(self, pos, element):
        """Initialize a marble with its grid position and element, including images"""
        self._xGrid = pos[0]
        self._yGrid = pos[1]
        self._element = element
        self._isMetal = element == 'lead' or element == 'tin' or element == 'iron' or element == 'copper' or element == 'silver' or element == 'gold'
        self._selected = False
        #pygame stuff
        pygame.sprite.Sprite.__init__(self) #initialize sprite
        
        self.art = pygame.image.load(f'sprites/{element}.png') #load the image of the marble
        self.art = pygame.transform.scale(self.art, (int(c.TILE_RADIUS * 0.9*2), int(c.TILE_RADIUS * 0.9*2))) #resize the image

        self.image = pygame.surface.Surface((c.TILE_RADIUS*2, c.TILE_RADIUS*2)) #create the base tile
        self.image.set_colorkey((0, 0, 0)) #all black pixels will be rendered as transparent
        #self.image.fill(pygame.Color(200, 100, 100))
        self.rect = self.image.get_rect() #gets the bounding box of the tile
        
        #create the selection image
        self.selection = self.image.copy() #copy base tile
        pygame.draw.circle(self.selection, pygame.Color(255, 255, 255), self.rect.center, c.TILE_RADIUS * 1, 0) #outer selection circle
        self.selection.blit(self.art, (c.TILE_RADIUS * 0.05*2, c.TILE_RADIUS*0.05*2)) #put the marble image ontop
        #create the clickable image
        self.clickable = self.image.copy() #copy base tile
        self.clickable.blit(self.art, (c.TILE_RADIUS * 0.05*2, c.TILE_RADIUS*0.05*2))  #put the marble image ontop
        #create the unclickable image
        self.unclickable = self.image.copy() #copy base tile
        self.unclickable.blit(self.art, (c.TILE_RADIUS * 0.05*2, c.TILE_RADIUS*0.05*2)) #put the marble image ontop
        over = pygame.surface.Surface((c.TILE_RADIUS * 0.9*2, c.TILE_RADIUS * 0.9*2)) #create new surface
        over_rect = over.get_rect() #get bounding box
        over.set_colorkey((0, 0, 0)) #all black pixels will be rendered as transparent
        over.set_alpha(175)
        pygame.draw.circle(over, (255, 255, 255), over_rect.center, c.TILE_RADIUS * 0.9, 0) #draw a white circle to fade the image
        self.unclickable.blit(over, (c.TILE_RADIUS * 0.05*2, c.TILE_RADIUS*0.05*2)) #add overlay onto the base tile

        self.image = self.unclickable #set the first image to unclickable

        self.rect.center = Marble.getCenterOfTile(pos) #move image into position
    @property
    def element(self):
        """Returns the element"""
        return self._element

    @property
    def isMetal(self):
        """Returns if element is metal"""
        return self._isMetal
    
    @property
    def selected(self):
        """Returns if element is currently selected"""
        return self._selected
    
    @selected.setter
    def selected(self, select):
        """Change the staus of selected"""
        self._selected = select
        if select:
            self.image = self.selection #change the image to selected
        else:
            self.image = self.clickable #change the image to clickable (not selected)
    

    def moveToClick(self):
        """remove from unclickabe to clickable"""
        global unclick
        global click
        unclick.remove(self)
        click.add(self)
        self.image = self.clickable #change image to clickable
    
    def remove(self):
        """Removes this marble from the positionGrid and click, sets next metal"""
        global click
        global currentMetal
        global element_numbers
        if self.element == currentMetal and self.element != 'gold':
            currentMetal = METAL_CHAIN[self.element] #change the current metal to the next in the chain
        if self.element != "vitae" and self.element != "mors":
            element_numbers[self.element] -= 1

        click.remove(self)
        global position_grid
        position_grid[self._yGrid][self._xGrid] = None 

    def isMouseIn(self, mousePos):
        """Returns if the location of the mouse is in the marble"""
        distance = math.hypot(mousePos[0] - self.rect.center[0], mousePos[1] - self.rect.center[1])
        return distance <= self.rect.width/2 #true if distance is less than the circle radius

    def checkNeighbors(self):
        """checks if 3 contiguous neighbors are empty"""
        global position_grid

        leftUp = position_grid[self._yGrid-1][self._xGrid-1] is None
        left = position_grid[self._yGrid][self._xGrid-1] is None
        leftDown = position_grid[self._yGrid+1][self._xGrid] is None
        rightDown = position_grid[self._yGrid+1][self._xGrid+1] is None
        right = position_grid[self._yGrid][self._xGrid+1] is None
        rightUp = position_grid[self._yGrid-1][self._xGrid] is None

        return (  leftUp and      left and  leftDown
            or      left and  leftDown and rightDown
            or  leftDown and rightDown and     right
            or rightDown and     right and   rightUp
            or     right and   rightUp and    leftUp
            or   rightUp and    leftUp and      left)

#functions
def createHexagon(surface, center, pointRadius, color, angle, width):
    pygame.draw.polygon(surface, color, [
        (center[0]+pointRadius*math.cos(1/3*math.pi+angle), center[1]+pointRadius*math.sin(1/3*math.pi+angle)),
        (center[0]+pointRadius*math.cos(2/3*math.pi+angle), center[1]+pointRadius*math.sin(2/3*math.pi+angle)),
        (center[0]+pointRadius*math.cos(3/3*math.pi+angle), center[1]+pointRadius*math.sin(3/3*math.pi+angle)),
        (center[0]+pointRadius*math.cos(4/3*math.pi+angle), center[1]+pointRadius*math.sin(4/3*math.pi+angle)),
        (center[0]+pointRadius*math.cos(5/3*math.pi+angle), center[1]+pointRadius*math.sin(5/3*math.pi+angle)),
        (center[0]+pointRadius*math.cos(6/3*math.pi+angle), center[1]+pointRadius*math.sin(6/3*math.pi+angle)),
    ], width)

def updateBoard():
    """Check if the game has been won and updates clickable marbles"""
    if checkWin(): # checks if all marbles are gone
        print('win')
        global score
        score += 1
    checkShowing() #update clickable marbles

def onClick(mousePos):
    """Process a mouse click"""
    global selection1
    global selection2
    global running
    #check if button pressed
    if play_again_btn.collidepoint(mousePos):
        print('button')
        startGame()
    elif quit_btn.collidepoint(mousePos):
        running = False
    #check if marbles are pressed
    for marble in click.sprites(): #go through all clickable marbles
        if marble.isMouseIn(mousePos): #if the mouse is inside the marble
            print('Marble Clicked')
            if marble.element == 'gold': #handle gold exception
                marble.remove()
                updateBoard()
            if selection1 == None: 
                selection1 = marble #save to selection1
                marble.selected = True
            else:
                if selection1 != marble: #only if marble is not selected twice
                    selection2 = marble #save to selection 2
                    marble.selected = True
                    if validPair(selection1, selection2): #check if it is a valid pair
                        selection1.remove() #remove from the game
                        selection2.remove()
                        selection1.selected = False
                        selection1 = None
                        selection2.selected = False
                        selection2 = None

                        updateBoard() #check win and update clickable marbles
                            
                    else: # marbles are not a valid pair
                        selection1.selected = False
                        selection1 = selection2 #replace selection1 with new selection
                        break

def checkWin():
    """checks if the game has been won"""
    return (not click.sprites()) and (not unclick.sprites()) #if both click and unclick are empty lists

def validPair(m1, m2):
    """Uses a list of sets to determine whether a pair of marbles is valid"""
    rulelist = [
        {'fire'}, #fire and fire
        {'water'}, #water and water
        {'earth'}, #earth and earth
        {'air'}, #air and air
        {'salt'}, #salt and salt
        {'fire', 'salt'},
        {'water', 'salt'},
        {'earth', 'salt'},
        {'air', 'salt'},
        {'vitae', 'mors'},
        {'quicksilver', 'lead'},
        {'quicksilver', 'tin'},
        {'quicksilver', 'iron'},
        {'quicksilver', 'copper'},
        {'quicksilver', 'silver'}
    ]
    return {m1.element, m2.element} in rulelist #true if the rule given is part of the list

def checkShowing():
    """Checks if marble has 3 contiguous empty tiles and is the current metal"""
    for marble in unclick.sprites():
        if((marble.isMetal and marble.element == currentMetal) or not marble.isMetal) and marble.checkNeighbors():
            marble.moveToClick() #removes marble from unclick and puts it it click
     
def startGame():
    """initialize a game"""
    global position_grid
    global unclick
    global click
    global currentMetal
    global element_numbers
    
    currentMetal = 'lead' #first metal is lead
    element_numbers = {
        'fire': 8,
        'water': 8,
        'air': 8,
        'earth': 8,
        'salt': 4,
        'seperator': 1,
        'quicksilver': 5,
        'lead': 1,
        'tin': 1,
        'iron': 1,
        'copper': 1,
        'silver': 1,
        'gold': 1
    }
    click.empty()
    unclick.empty()
    position_grid = np.full((13, 13), None) #set a 13 by 13 position grid
    gridNumber = random.randint(1, 9)
    file = open(f'grids/grid{gridNumber:02d}.json') #open a predefined grid
    marblesDictList = json.load(file)
    for marbleDict in marblesDictList: #for each marble in the json
        x = marbleDict["x"]
        y = marbleDict["y"]
        element = marbleDict["element"]
        marble = Marble((x, y), element) #create a marble
        unclick.add(marble) #add to unclickables
        position_grid[y][x] = marble #add marble to position grid

    checkShowing() #update the board

def runGame():
    """check for mouse clicks and draws the board until quit"""
    global running
    global myFont
    global score

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                #print('event mousedown')
                onClick(event.pos) #handle a mouse click

            elif event.type == pygame.QUIT:
                running = False
        
        #background fill
        screen.fill(pygame.Color(200, 200, 200))
        #draw background design
        #createHexagon(screen, (c.WIDTH/2, c.WIDTH/2), c.WIDTH/2, (0, 0, 0), 0, 5)
        for i in range(1, 12):
            for j in range(max(1, i-5), min(12, i+6)):
                createHexagon(screen, Marble.getCenterOfTile((i, j)), (2/math.sqrt(3))*c.TILE_RADIUS, (150, 150, 150), math.pi/2, 3)
        #draw top bar
        pygame.draw.rect(screen, (150, 150, 150), play_again_btn)
        pygame.draw.rect(screen, (150, 150, 150), quit_btn)
        score_text = myFont.render(f'Score: {score}', 1, (0,0,0))
        screen.blit(score_text, (c.WIDTH*0.5, c.WIDTH*0.02))
        again_text = myFont.render('New Board', 1, (0, 0, 0))
        screen.blit(again_text, (c.WIDTH*0.03, c.WIDTH*0.03))

        quit_text = myFont.render('Quit Game', 1, (0, 0, 0))
        screen.blit(quit_text, (c.WIDTH-c.WIDTH*0.19, c.WIDTH*0.03))
        #draw bottom bar
        global element_numbers
        size = 45
        
        #pygame.draw.rect(screen, (0, 0, 0), (int(c.WIDTH/2 - c.TILE_RADIUS*2*2.5), int(c.HEIGHT*(5/7)), int(c.TILE_RADIUS*2*5), int(c.TILE_RADIUS*2 + 10)), 5)
        pygame.draw.rect(screen, (0, 0, 0), (int(c.WIDTH/2 - size*6.5), int(570), int(size*13), int(size + 15)), 5)
        
        keys = list(element_numbers.keys())
        
        for element in keys:
            image = pygame.image.load(f'sprites/{element}.png')
            image = pygame.transform.scale(image, (int(size * 0.9), int(size * 0.9)))
            screen.blit(image, (int(c.WIDTH/2 - size*6.5 + (size * keys.index(element) + 1)), (570 + 7.5)))
            if element_numbers[element] == 0:
                over = pygame.surface.Surface((size * 0.9, size * 0.9)) #create new surface
                over_rect = over.get_rect() #get bounding box
                over.set_colorkey((0, 0, 0)) #all black pixels will be rendered as transparent
                over.set_alpha(175)
                pygame.draw.circle(over, (255, 255, 255), over_rect.center, size * 0.9 * 0.5, 0) #draw a white circle to fade the image
                screen.blit(over, (int(c.WIDTH/2 - size*6.5 + (size * keys.index(element) + 1)), (570 + 7.5)))
            if keys.index(element) <= 6 and element != 'seperator':
                quantity_label = myFont.render(f'{element_numbers[element]}', 1, (0, 0, 0))
                screen.blit(quantity_label, (int(c.WIDTH/2 - size * 5.69 + (size * keys.index(element) + 1)), (570 + 10 + (size/2))))
        #draw marbles
        unclick.draw(screen)
        click.draw(screen)
        #update the display
        pygame.display.update()

startGame()
runGame()
pygame.quit()
#sys.exit()
