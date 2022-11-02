#config.py
"""defines some useful constansts for sigmarsGarden.py"""

import math


WIDTH = 600
HEIGHT = WIDTH*1.06

TILE_RADIUS = WIDTH * (math.sqrt(3)/(20*math.sqrt(3)+4))
X_0 = WIDTH * ((2+4*math.sqrt(3))/(4+20*math.sqrt(3)))
Y_0 = WIDTH * ((-16+10*math.sqrt(3))/(4+20*math.sqrt(3)))

MAX_GRID_NUMBER = 9