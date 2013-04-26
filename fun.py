import random
import sys


class Square(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.pile = []
        self.player = None

    def is_empty(self):
        return len(self.pile) == 0 and self.player == None

    def pick_from_pile(self, index):
        # We'll need some locking on this if
        # we're ever multiplayer.
        return self.pile.pop(index)

    def __str__(self):
        return "(%d, %d)" % (self.x, self.y)


class GameBoard(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.grid = []
        for i in range(y):
            row = [Square(j, i) for j in range(x)]
            self.grid.append(row)

    def get(self, x, y):
        return self.grid[y][x]

    def add_to_pile(self, x, y, entity):
        self.grid[y][x].pile.append(entity)

    def remove(self, x, y, index):
        pass

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

    def invalid_square(self, x, y):
        return x >= self.x or x < 0 or \
               y >= self.y or y < 0


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

    def walked_on(self, board, other):
        # Something walked on me.
        return True

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

   def move_relative(self, board, _x, _y):
        new_x = self.x + _x
        new_y = self.y + _y
        if board.invalid_square(new_x, new_y):
            return
        board.set_player(self.x, self.y, None)
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


class Handler(object):
    def __init__(self, board, player):
        self.board = board
        self.player = player


class Move(Handler):
    def can_handle(self, parts):
        return parts[0] in ['n', 's', 'w', 'e']

    def handle(self, parts):
        x, y = direction_to_coordinates(parts[0])
        self.player.move_relative(self.board, x, y)


class Quit(Handler):
    def can_handle(self, parts):
        return parts[0] == 'q'

    def handle(self, parts):
        sys.exit(0)


class Pickup(Handler):
    def can_handle(self, parts):
        return parts[0] == '.'

    def handle(self, parts):
        # . <direction>
        # maybe use argparse for this stuff?
        x = self.player.x
        y = self.player.y
        if len(parts) > 1:
            _x, _y = direction_to_coordinates(parts[1])
            x += _x
            y += _y
        square = self.board.get(x, y)
        item = square.pick_from_pile(0)
        self.player.carry(item)


if __name__=='__main__':
    board = GameBoard(10, 10)
    names = ['SW',]
    players = [Player("*%s" % name) for name in names]
    randomly_place_entities(board, players)

    bombs = [Item("()") for i in range(10)]
    randomly_place_entities(board, bombs)

    coins = [Item("$") for i in range(10)]
    randomly_place_entities(board, coins)

    player = players[0]
    handlers = [Move(board, player), Quit(board, player),
                Pickup(board, player)]

    while True:
        board.dump()
        for i, item in enumerate(player.inventory):
            print "%s. %s" % (i+1, str(item)),
        print

        inp = raw_input("$ ")
        parts = inp.split(' ')
        for handler in handlers:
            if handler.can_handle(parts):
                handler.handle(parts)
                continue
        print "Invalid command"
