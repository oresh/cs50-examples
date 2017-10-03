import os
import sys
import random

class Board():
    def __init__(self, w, h):
        self.width = w
        self.height = h
        self.cells = []
        for i in range(w):
            for j in range(h):
                self.cells.append(Cell(i, j))
                
    def shuffleBombs(self, bombs):
        self.bombs = bombs
        r = random.sample(range(len(self.cells)), bombs)
        
        for bomb in r:
            self.cells[bomb].isBomb = True


class Cell():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.isOpened = False
        self.isBomb = False
        self.isFlagged = False
        self.value = 0
        self.display = ''
        
    def calcNumber(self, board):
        summ = 0
        for i in range(0, 3):
            for j in range(0, 3):
                if board.cells[self.x + i][self.y + j].isBomb:
                    summ += 1
        self.value = summ
        
    def show(self, board):
        if self.isOpened:
            return True

        if self.isFlagged:
            # say :o
            return True

        self.isOpened = True
        if self.isBomb:
            self.display = '*'
            # game over
        else:
            self.calcNumber(board)
            self.display = self.value


game = Board(10, 10)
game.shuffleBombs(5)

for i in range(0, 100):
    game.cells[i].show(game)
    print(game.cells[i].display, end=" ")


