##This file is part of Battleship.
##
##Battleship is free software: you can redistribute it and/or modify
##it under the terms of the GNU General Public License as published by
##the Free Software Foundation, either version 3 of the License, or
##(at your option) any later version.
##
##Battleship is distributed in the hope that it will be useful,
##but WITHOUT ANY WARRANTY; without even the implied warranty of
##MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##GNU General Public License for more details.
##
##You should have received a copy of the GNU General Public License
##along with Battleship.  If not, see <http://www.gnu.org/licenses/>.
from pygame.locals import *
from ocempgui.widgets.Constants import *
from ocempgui.widgets.components import *
from ocempgui.widgets import *
import pygame, sys, socket, threading
import boats, eztext, ezmenu

class Pointer(pygame.sprite.Sprite):
    """ A pointer on the grid """
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((16,16)); self.image.fill((0,0,255))
        self.rect = self.image.get_rect()
        self.x = x; self.y = y

    def update(self):
        self.rect.x = self.x
        self.rect.y = self.y

class Hit(pygame.sprite.Sprite):
    """ A spot where we know a ship is """
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((16,16)); self.image.fill((255,0,0))
        self.rect = self.image.get_rect()
        self.x = x; self.y = y
        self.type = 'hit'

    def update(self):
        self.rect.x = self.x
        self.rect.y = self.y

class Miss(pygame.sprite.Sprite):
    """ A spot where we know a ship isn't """
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((16,16)); self.image.fill((0,255,0))
        self.rect = self.image.get_rect()
        self.x = x; self.y = y
        self.type = 'miss'

    def update(self):
        self.rect.x = self.x
        self.rect.y = self.y

class Var(object): pass

def makegrid(size, xinterval, yinterval, xstart=0, ystart=0):
    grid = []
    for x in range(xstart, size[0], xinterval):
        for y in range(ystart, size[1], yinterval):
            grid.append((x, y, x+xinterval, y+yinterval))
    return grid

def findgrid(x, y, grid):
    for pos in grid:
        if x >= pos[0] and x <= pos[2] and\
           y >= pos[1] and y <= pos[3]:
            return pos

def drawgrid(screensize, xinterval, yinterval, color, bgcolor=None, transparent=True):
    gridimg = pygame.Surface(screensize)
    if not bgcolor:
        if color == (255,255,255): bgcolor = (0,0,0)
        else: bgcolor = (255,255,255)
        gridimg.fill(bgcolor)
    else: gridimg.fill(bgcolor)
    for x in range(0, screensize[0], xinterval):
        pygame.draw.line(gridimg, color, (x, 0), (x, screensize[1]))
    for y in range(0, screensize[1], yinterval):
        pygame.draw.line(gridimg, color, (0, y), (screensize[0], y))
    if transparent: gridimg.set_colorkey(bgcolor)
    return gridimg

def wordwrap(string, line_length):
    words = string.split(' ')
    lines = []; curline = ''; final = ''
    for word in words:
        _curline = str(curline)
        curline += word+' '
        if len(curline[:-1]) > line_length:
            lines.append(_curline[:-1])
            curline = word+' '
    lines.append(curline[:-1])
    for line in lines: final += line+'\n' # add final scentence
    return final[:-1] # remove final '\n'

def net_start(screen):
    menu = ezmenu.EzMenu(
        ['Serve Game', lambda: net_srv(screen)],
        ['Join Game', lambda: net_jn(screen)])

    menu.center_at(320, 240)

    screen.fill((255,255,255))
    menu.draw(screen)
    clock = pygame.time.Clock()
    pygame.display.flip()

    while 1:
        clock.tick(30)
        
        events = pygame.event.get()
        inf = menu.update(events)

        if inf != None: return inf

        for event in events:
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((255,255,255))
        menu.draw(screen)
        pygame.display.flip()

def net_srv(screen):
    global sock, connected
    font = pygame.font.Font(None, 32)
    text = font.render('Waiting for connection...', 1, (0,0,0))
    screen.fill((255,255,255))
    screen.blit(text, (320-text.get_width()/2, 240-text.get_height()/2))
    clock = pygame.time.Clock()
    pygame.display.flip()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    talk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', 255594))
    talk.bind(('', 255595))
    listen.bind(('', 255596))
    sock.listen(1); talk.listen(1); listen.listen(1); connected = False

    def connect():
        global conn, conn1, conn2, addr, connected
        conn, addr = sock.accept()
        conn1, addr = talk.accept()
        conn2, addr = listen.accept()
        connected = True

    thread = threading.Thread(target=connect)
    thread.start()

    while 1:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        if connected: return (conn, conn1, conn2, addr, 'server')

        screen.fill((255,255,255))
        screen.blit(text, (320-text.get_width()/2, 240-text.get_height()/2))
        pygame.display.flip()

def net_jn(screen):
    screen.fill((255,255,255))
    text = eztext.Input(prompt='connect to: ', x=160, y=230)
    clock = pygame.time.Clock()

    while 1:
        clock.tick(30)

        events = pygame.event.get()
        text.update(events)

        for event in events:
            if event.type == QUIT: return None
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE: return None
                elif event.key == K_RETURN:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    talk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((text.value, 255594))
                    listen.connect((text.value, 255595))
                    talk.connect((text.value, 255596))
                    return (sock, talk, listen, text.value, 'client')

        screen.fill((255,255,255))
        text.draw(screen)
        pygame.display.flip()

def win(screen, gui):
    screen.fill((255,255,255))
    font = pygame.font.Font('freesansbold.ttf', 32)
    text = font.render('You Won!', 1, (0,0,0))
    rect = text.get_rect()
    rect.centerx = 320; rect.centery = 240
    screen.blit(text, rect)
    clock = pygame.time.Clock()
    pygame.display.flip()

    while 1:
        clock.tick(30)

        for event in pygame.event.get():
            gui.distribute_events(event)
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        gui.update()
        screen.fill((255,255,255))
        screen.blit(text, rect)
        screen.blit(gui.screen, (0,0))
        pygame.display.flip()

def loose(screen, gui):
    screen.fill((255,255,255))
    font = pygame.font.Font('freesansbold.ttf', 32)
    text = font.render('You Lost', 1, (0,0,0))
    rect = text.get_rect()
    rect.centerx = 320; rect.centery = 240
    screen.blit(text, rect)
    clock = pygame.time.Clock()
    pygame.display.flip()

    while 1:
        clock.tick(30)

        for event in pygame.event.get():
            gui.distribute_events(event)
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        gui.update()
        screen.fill((255,255,255))
        screen.blit(text, rect)
        screen.blit(gui.screen, (0,0))
        pygame.display.flip()

def game(_screen, ships_, shiplist, gridimg, grid):
    global hits, ships, othits, conn, state, pointer, screen
    ships = ships_; del ships_; deadships = 0; screen = _screen; del _screen
    inf = net_start(screen)
    conn = inf[0]; hitship = False
    talk = inf[1]; listen = inf[2]
    pointer = Pointer(0,0)
    hits = pygame.sprite.Group(); hitlist = []
    othits = pygame.sprite.Group()
    font = pygame.font.Font('freesansbold.ttf', 12)
    if inf[4] == 'server': state = 1
    else: state = 0
    pos = findgrid(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], grid)
    pointer.x = pos[0]; pointer.y = pos[1]
    pointer.update(); statedelay = 15; statecount = 0
    text = font.render('Click to shoot', 1, (0,0,0))
    state4delay = 60; state4count = 0; instate4 = False;
    state5delay = 60; state5count = 0; instate5 = False;
    oldmessagelen = 0

    # gui for text box
    # first, set a better font
    base.GlobalStyle.styles["default"]["font"]["name"] = "tuffy.ttf"
    base.GlobalStyle.styles["default"]["font"]["size"] = 12
    gui = Renderer()
    gui.color = (1,1,1)
    gui.screen = pygame.Surface(screen.get_size())
    gui.screen.set_colorkey((1,1,1))
    chat = Window('Chat')
    frame = VFrame()
    messages = ScrolledList(300,150)
    messages.selectionmode = SELECTION_NONE
    m_input = Entry()
    m_input.set_minimum_size(300,m_input.height)
    frame.add_child(messages, m_input)
    chat.child = frame
    chat.topleft = 300, 250
    gui.add_widget(chat)
    old_temp = None

    def state0():
        hitship = False
        pos = conn.recv(1024)
        pos = pos.split(',')
        pos = (int(pos[0]), int(pos[1]))
        for ship in ships.sprites():
            if pos[0] >= ship.rect.left and\
               pos[0] < ship.rect.right and\
               pos[1] >= ship.rect.top and\
               pos[1] < ship.rect.bottom:
                ship.hit(); hitship = True
        if not hitship:
            m = Miss(pos[0], pos[1]); m.update()
            hits.add(m)
            conn.send('miss')
        else:
            h = Hit(pos[0], pos[1]); h.update()
            hits.add(h)
            conn.send('hit')
        pygame.event.post(pygame.event.Event(USEREVENT, {'code' : 4}))

    def state1():
        conn.send(str(pointer.x)+','+str(pointer.y))
        hitmiss = conn.recv(1024)
        if hitmiss == 'hit':
            h = Hit(pointer.x, pointer.y); h.update()
            othits.add(h)
        else:
            m = Miss(pointer.x, pointer.y); m.update()
            othits.add(m)
        pygame.event.post(pygame.event.Event(USEREVENT, {'code' : 5}))

    def wait_msg():
        while 1:
            msg = listen.recv(1024)
            pygame.event.post(pygame.event.Event(USEREVENT, {'code' : 6, 'message' : msg}))

    if state == 0:
        screen.fill((255,255,255))
        ships.draw(screen)
        screen.blit(pointer.image, pointer.rect)
        screen.blit(gridimg, (0,0))

    if state == 1:
        screen.fill((255,255,255))
        screen.blit(pointer.image, pointer.rect)
        screen.blit(text, (pointer.rect.right+5, pointer.rect.y))
        screen.blit(gridimg, (0,0))

    wait_thread = threading.Thread(target=wait_msg)
    wait_thread.start()

    clock = pygame.time.Clock()
    pygame.display.flip()

    while 1:
        clock.tick(30)

        if state == 4:
            if state4count == 0:
                if not instate4:
                    state4count = state4delay
                    instate4 = True
                else:
                    instate4 = False
                    state = 1
            else: state4count -= 1

        if state == 5:
            if state5count == 0:
                if not instate5:
                    state5count = state5delay
                    instate5 = True
                else:
                    instate5 = False
                    state = 0
            else: state5count -= 1

        if state == 0:
            thread0 = threading.Thread(target=state0)
            state = 2; thread0.start()

        for event in pygame.event.get():
            gui.distribute_events(event)
            if event.type == QUIT:
                conn.close()
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if state == 1 and gui.screen.get_at(pygame.mouse.get_pos())[:3] == (1,1,1):
                    if (pointer.x, pointer.y) not in hitlist:
                        hitlist.append((pointer.x, pointer.y))
                        thread1 = threading.Thread(target=state1)
                        state = 3; thread1.start()
                    else: pass
            if event.type == USEREVENT:
                if event.code == 0: state = 0
                elif event.code == 1: state = 1
                elif event.code == 2: state = 2
                elif event.code == 3: state = 3
                elif event.code == 4: state = 4
                elif event.code == 5: state = 5
                elif event.code == 6:
                    messages.items.append(TextListItem(event.message))
                    
        for ship in ships.sprites():
            if ship.dead and not ship.accounted:
                deadships += 1
                talk.send('*You sunk a(n) %s!' % ship.type)
                messages.items.append(TextListItem('*%s sunk.' % ship.type))
            
        if deadships == len(ships.sprites()): loose(screen, gui)

        otdeadships = 0
        for hitmiss in othits.sprites():
            if hitmiss.type == 'hit': otdeadships += 1
        if otdeadships == 22: win(screen, gui)

        if old_temp != m_input._temp:
            old_temp = m_input._temp
            if old_temp:
                messages.items.append(TextListItem('you: '+old_temp))
                talk.send('enemy: '+old_temp)
                m_input.set_text('')

        if oldmessagelen != len(messages.items):
            # make sure we are at bottom
            print oldmessagelen
            messages.vscrollbar.value = messages.vscrollbar.maximum
            oldmessagelen = len(messages.items)

        # only ten messages at a time
        if len(messages.items) > 10:
            messages.items.remove(messages.items[0])

        mousepos = pygame.mouse.get_pos()
        mousepos = findgrid(mousepos[0], mousepos[1], grid)
        pointer.x = mousepos[0]; pointer.y = mousepos[1]

        if state == 0:
            pointer.update()
            gui.update()
            screen.fill((255,255,255))
            ships.draw(screen)
            hits.draw(screen)
            screen.blit(pointer.image, pointer.rect)
            screen.blit(gridimg, (0,0))
            screen.blit(gui.screen, (0,0))
            pygame.display.flip()

        if state == 2:
            pointer.update()
            gui.update()
            screen.fill((255,255,255))
            ships.draw(screen)
            hits.draw(screen)
            screen.blit(pointer.image, pointer.rect)
            screen.blit(gridimg, (0,0))
            screen.blit(gui.screen, (0,0))
            pygame.display.flip()

        if state == 1:
            pointer.update()
            gui.update()
            screen.fill((255,255,255))
            othits.draw(screen)
            screen.blit(pointer.image, pointer.rect)
            screen.blit(text, (pointer.rect.right+5, pointer.rect.y))
            screen.blit(gridimg, (0,0))
            screen.blit(gui.screen, (0,0))
            pygame.display.flip()

        if state == 5:
            pointer.update()
            gui.update()
            screen.fill((255,255,255))
            othits.draw(screen)
            screen.blit(pointer.image, pointer.rect)
            screen.blit(gridimg, (0,0))
            screen.blit(gui.screen, (0,0))
            pygame.display.flip()

        if state == 3:
            pointer.update()
            gui.update()
            screen.fill((255,255,255))
            othits.draw(screen)
            screen.blit(pointer.image, pointer.rect)
            screen.blit(gridimg, (0,0))
            screen.blit(gui.screen, (0,0))
            pygame.display.flip()

        if state == 4:
            pointer.update()
            gui.update()
            screen.fill((255,255,255))
            ships.draw(screen)
            hits.draw(screen)
            screen.blit(pointer.image, pointer.rect)
            screen.blit(gridimg, (0,0))
            screen.blit(gui.screen, (0,0))
            pygame.display.flip()

def main(screen):
    pygame.display.set_caption('Battleship')
    screen.fill((255,255,255))
    gridimg = drawgrid(screen.get_size(), 16, 16, (0,0,0))
    grid = makegrid(screen.get_size(), 16,16)
    pointer = Pointer(0,0); mousepos = (0,0)
    ships = pygame.sprite.Group(); shiplist = []
    atshipnumber = 0; font = pygame.font.Font('freesansbold.ttf', 12)
    shiptext = font.render('Aircraft Carrier', 1, (0,0,0))

    clock = pygame.time.Clock()
    pointer.update()
    screen.blit(gridimg, (0,0))
    screen.blit(pointer.image, pointer.rect)
    pygame.display.flip()

    while 1:
        clock.tick(30)

        mousepos = findgrid(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], grid)[:2]

        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if len(shiplist) == atshipnumber and\
                       mousepos not in shiplist:
                        if atshipnumber == 0: shiptoadd = boats.AircraftCarrier(mousepos, (16,16))
                        elif atshipnumber == 1: shiptoadd = boats.Battleship(mousepos, (16,16))
                        elif atshipnumber == 2: shiptoadd = boats.Destroyer(mousepos, (16,16))
                        elif atshipnumber == 3: shiptoadd = boats.Submarine(mousepos, (16,16))
                        elif atshipnumber == 4: shiptoadd = boats.Submarine(mousepos, (16,16))
                        elif atshipnumber == 5: shiptoadd = boats.PatrolBoat(mousepos, (16,16))
                        elif atshipnumber == 6: shiptoadd = boats.PatrolBoat(mousepos, (16,16))
                        shiptoadd.update()
                        if shiptoadd.rect.bottom <= screen.get_height() and\
                           shiptoadd.rect.right <= screen.get_width():
                            ships.add(shiptoadd)
                            del shiptoadd
                            shiplist.append(mousepos)
                        else:
                            shiptoadd.turn()
                            if shiptoadd.rect.bottom <= screen.get_height() and\
                               shiptoadd.rect.right <= screen.get_width():
                                ships.add(shiptoadd)
                                del shiptoadd
                                shiplist.append(mousepos)
                    else:
                        for ship in ships.sprites():
                            if mousepos[0] >= ship.rect.left and\
                               mousepos[0] < ship.rect.right and\
                               mousepos[1] >= ship.rect.top and\
                               mousepos[1] < ship.rect.bottom:
                                ship.turn()
                                if ship.rect.bottom > screen.get_height() or\
                                   ship.rect.right > screen.get_width():
                                    ship.turn()
                if event.button == 3:
                    for ship in ships.sprites():
                        if mousepos[0] >= ship.rect.left and\
                           mousepos[0] < ship.rect.right and\
                           mousepos[1] >= ship.rect.top and\
                           mousepos[1] < ship.rect.bottom and\
                           len(shiplist) > atshipnumber:
                            # make sure we don't remove the other ships
                            if atshipnumber == 0 and ship.type == 'Aircraft Carrier': ship.kill(); shiplist.remove((ship.x, ship.y))
                            elif atshipnumber == 1 and ship.type == 'Battleship': ship.kill(); shiplist.remove((ship.x, ship.y))
                            elif atshipnumber == 2 and ship.type == 'Destroyer': ship.kill(); shiplist.remove((ship.x, ship.y))
                            elif atshipnumber == 3 and ship.type == 'Submarine': ship.kill(); shiplist.remove((ship.x, ship.y))
                            elif atshipnumber == 4 and ship.type == 'Submarine': ship.kill(); shiplist.remove((ship.x, ship.y))
                            elif atshipnumber == 5 and ship.type == 'Patrol Boat': ship.kill(); shiplist.remove((ship.x, ship.y))
                            elif atshipnumber == 6 and ship.type == 'Patrol Boat': ship.kill(); shiplist.remove((ship.x, ship.y))
            elif event.type == KEYDOWN:
                if event.key == K_RETURN:
                    if len(shiplist) == atshipnumber+1:
                        atshipnumber += 1
                        if atshipnumber == 1: shiptext = font.render('Battleship', 1, (0,0,0))
                        elif atshipnumber == 2: shiptext = font.render('Destroyer', 1, (0,0,0))
                        elif atshipnumber == 3: shiptext = font.render('Submarine', 1, (0,0,0))
                        elif atshipnumber == 4: shiptext = font.render('Submarine', 1, (0,0,0))
                        elif atshipnumber == 5: shiptext = font.render('Patrol Boat', 1, (0,0,0))
                        elif atshipnumber == 6: shiptext = font.render('Patrol Boat', 1, (0,0,0))
                        elif atshipnumber == 7: game(screen, ships, shiplist, gridimg, grid)

        pointer.x = mousepos[0]
        pointer.y = mousepos[1]

        pointer.update()
        ships.update()
        screen.fill((255,255,255))
        ships.draw(screen)
        screen.blit(pointer.image, pointer.rect)
        screen.blit(gridimg, (0,0))
        screen.blit(shiptext, (pointer.rect.right+5, pointer.rect.y))
        pygame.display.flip()

def standalone():
    pygame.init()
    screen = pygame.display.set_mode((640,480), DOUBLEBUF)
    main(screen)
    pygame.quit()
    return

if __name__ == '__main__': standalone()
