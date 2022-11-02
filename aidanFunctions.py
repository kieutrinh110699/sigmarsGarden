def checkWin():
    return (not click) and (not unclick)

def validPair(m1, m2):
    rulelist = [
        {'fire'}, #fire and fire
        {'water'}, #water and water
        {'earth'}, #earth and earth
        {'air'}, #air and air
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
    return {m1.element, m2.element} in rulelist

def checkShowing():
    for marble in unclick:
        if((marble.isMetal and marble.element == currentMetal) or not marble.isMetal) and checkNeighbors(marble):
            marble.remove()


        
def checkNeighbors(marble):
    global positionGrid

    leftUp = positionGrid[marble.y-1][marble.x-1] is None
    left = positionGrid[marble.y][marble.x-1] is None
    leftDown = positionGrid[marble.y+1][marble.x] is None
    rightDown = positionGrid[marble.y+1][marble.x+1] is None
    right = positionGrid[marble.y][marble.x+1] is None
    rightUp = positionGrid[marble.y-1][marble.x] is None

    return (  leftUp and      left and  leftDown
        or      left and  leftDown and rightDown
        or  leftDown and rightDown and     right
        or rightDown and     right and   rightUp
        or     right and   rightUp and    leftUp
        or   rightUp and    leftUp and      left)