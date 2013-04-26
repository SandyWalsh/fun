import random
import sys


class Square(object):
    def __init__(self):
        self.pile = []
        self.player = None

    def is_empty(self):
        return len(self.pile) == 0 and self.player == None


class GameBoard(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.grid = []
        for i in range(y):
            row = [Square() for j in range(x)]
            self.grid.append(row)

    def get(self, x, y):
        return self.grid[y][x]

    def add_to_pile(self, x, y, entity):
        self.grid[y][x].pile.append(entity)

    def set_player(self, x, y, player):
        self.grid[y][x].player = player

    def dump(self):
        print "   ",
        for i in range(10):
            print "%3d" % i,
        print
        for i, y in enumerate(self.grid):
            print "%3d" % i,
            for x in y:
                tag = ' . '
                if x.player:
                    tag = x.player.dump()
                else:
                    pile = x.pile
                    if len(pile) == 1:
                        tag = pile[0].dump()
                    elif len(pile) > 1:
                        tag = '^'
                print "%3s" % tag,
            print


class Entity(object):
    def __init__(self, tag):
        self.x = None
        self.y = None
        self.tag = tag
        self.inventory = []

    def placeat(self, board, x, y):
        self.x = x
        self.y = y
        # How to add to board left to derived class.

    def move_relative(self, board, _x, _y):
        if self.x + _x >= board.x or \
           self.x + _x < 0 or \
           self.y + _y >= board.y or \
           self.y + _y < 0:
            return
        board.set_player(self.x, self.y, None)
        new_x = self.x + _x
        new_y = self.y + _y
        pile = board.get(new_x, new_y).pile
        permitted = True
        if pile:
            for item in pile:
                ok = item.walked_on(board, self)
                permitted = permitted and ok
        if permitted:
            self.x = new_x
            self.y = new_y
            board.set_player(self.x, self.y, self)

    def walked_on(self, board, other):
        # Something walked on me.
        # By default, they now carry us.
        return True

    def pick_up(self, board, index):
        # board.set(self.x, self.y, [])
        other.carry(self)

    def carry(self, other):
        self.inventory.append(other)

    def dump(self):
        return self.tag

    def __str__(self):
        return self.dump()


class Item(Entity):
    def placeat(self, board, x, y):
        super(Item, self).placeat(board, x, y)
        board.add_to_pile(x, y, self)


class Player(Entity):
   def placeat(self, board, x, y):
        super(Player, self).placeat(board, x, y)
        board.set_player(x, y, self)


def randomly_place_entities(board, entities):
    for e in entities:
        while True:
            x = random.randrange(10)
            y = random.randrange(10)
            if board.get(x, y).is_empty():
                e.placeat(board, x, y)
                break


def direction_to_coordinates(direction):
    x = 0
    y = 0
    if direction == 'n':
        y = -1
    if direction == 's':
        y = 1
    if direction == 'e':
        x = 1
    if direction == 'w':
        x = -1
    return x, y


if __name__=='__main__':
    board = GameBoard(10, 10)
    names = ['SW',]
    players = [Player("*%s" % name) for name in names]
    randomly_place_entities(board, players)

    bombs = [Item("()") for i in range(10)]
    randomly_place_entities(board, bombs)

    coins = [Item("$") for i in range(10)]
    randomly_place_entities(board, coins)

    while True:
        player = players[0]
        board.dump()
        for i, item in enumerate(player.inventory):
            print "%s. %s" % (chr(ord('a')+i), str(item)),
        print

        inp = raw_input("$ ")
        parts = inp.split(' ')
        cmd = parts[0]
        if cmd == 'q':
            sys.exit(1)
        x, y = direction_to_coordinates(cmd)
        if x == 0 and y == 0:
            continue

        player.move_relative(board, x, y)
