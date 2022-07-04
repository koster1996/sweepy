from typing import Dict, List
from minefield.mineField import MineField, ExplosionException
from enum import Enum
from random import randrange, randint
from typing import Tuple

# Copying this from the mineField library
BEGINNER_FIELD = {"width": 10, "height": 10, "number_of_mines": 10}
INTERMEDIATE_FIELD = {"width": 16, "height": 16, "number_of_mines": 40}
EXPERT_FIELD = {"width": 30, "height": 16, "number_of_mines": 99}


class Sweeper:
    def __init__(self, field: MineField, difficulty: Dict) -> None:
        self.minefield = field
        self.height = difficulty["height"]
        self.width = difficulty["width"]

        # dict with key being (row, column) and value the value returned by doSweep()
        self.openSquares = {}
        # List with mine locations, formatted as (row, column)
        self.mines = []

        self.hitMine = False

        self.count = 0

    def solve(self) -> List:
        # the first sweep is always free. We start in the middle, cuz why not
        self.openSquares[(self.height // 2, self.width // 2)] = self.doSweep(
            self.height // 2, self.width // 2
        )
        # we keep going until we have no more unknown squares
        while (
            len(self.openSquares) + len(self.mines) < self.height * self.width
            and not self.hitMine
        ):
            # print(self.openSquares)
            print(self.count)
            # If we did not open any new squares last step, we are going to open one at random
            if len(self.openSquares) + len(self.mines) == self.count:

                newSquare = self.getNewRandomLocation()
                self.openSquares[newSquare] = self.doSweep(newSquare[0], newSquare[1])
            self.count = len(self.openSquares) + len(self.mines)

            # First, see if we have any openSquares which do not have any mines next to it and unknown squares we can make known
            # Currently, this is a hack, as dict.items does not allow resizing during looping through it
            for openSquare in {k: v for k, v in self.openSquares.items()}.items():
                if openSquare[1] == 0:
                    for newOpenSquare in self.obtainUnknownNeighourSquares(
                        openSquare[0][0], openSquare[0][1]
                    ):
                        self.openSquares[newOpenSquare] = self.doSweep(
                            newOpenSquare[0], newOpenSquare[1]
                        )

            # second, find locations that are definitely bombs
            self.findDefinitelyMines()

            # third, find new locations that are safe as we know the bombs around it
            self.findSafeSquares()

        return self.mines

    # we cycle through the currently open Squares and see if the number of unknown squares + the number of neighbouring mines match each value for each open square. Set all the unknown values to bombs
    def findDefinitelyMines(self) -> None:
        for openSquare in {k: v for k, v in self.openSquares.items()}.items():
            # print(
            #     openSquare[1],
            #     self.obtainUnknownNeighourSquares(openSquare[0][0], openSquare[0][1]),
            #     self.obtainUnknownNeighourMines(openSquare[0][0], openSquare[0][1]),
            # )
            if openSquare[1] > 0 and openSquare[1] == len(
                self.obtainUnknownNeighourSquares(openSquare[0][0], openSquare[0][1])
                + self.obtainKnownNeighourMines(openSquare[0][0], openSquare[0][1])
            ):
                for newSquare in self.obtainUnknownNeighourSquares(
                    openSquare[0][0], openSquare[0][1]
                ):
                    if newSquare not in self.mines:
                        self.mines.append(newSquare)

    # cycling through the current open squares, checking if the number of boms surrounding it equal its current value. If so, any surrounding unknown squares can be sweeped
    def findSafeSquares(self) -> None:
        # fix me
        for openSquare in {k: v for k, v in self.openSquares.items()}.items():
            if openSquare[1] > 0 and openSquare[1] == len(
                self.obtainKnownNeighourMines(openSquare[0][0], openSquare[0][1])
            ):
                for newOpenSquare in self.obtainUnknownNeighourSquares(
                    openSquare[0][0], openSquare[0][1]
                ):
                    self.openSquares[newOpenSquare] = self.doSweep(
                        newOpenSquare[0], newOpenSquare[1]
                    )

    def doSweep(self, row: int, column: int) -> int:
        out = 0
        try:
            out = self.minefield.sweep_cell(column, row)
        except ExplosionException as e:
            print("Boooooomm")
            self.hitMine = True
        return out

    # returns all neighouring tiles of the specified location that are not in self.openSquares and self.mines
    def obtainUnknownNeighourSquares(self, row: int, column: int) -> List:
        unknownSquares = []
        for deltaRow in [-1, 0, 1]:
            for deltaColumn in [-1, 0, 1]:
                if (
                    not (deltaRow == 0 and deltaColumn == 0)
                    and row + deltaRow >= 0
                    and column + deltaColumn >= 0
                    and row + deltaRow < self.height
                    and column + deltaColumn < self.width
                ):
                    unknownSquare = (row + deltaRow, column + deltaColumn)
                    if (
                        unknownSquare not in self.mines
                        and unknownSquare not in self.openSquares.keys()
                    ):
                        unknownSquares.append(unknownSquare)
        return unknownSquares

    # returns all mine neighbour tiles of the specified location
    def obtainKnownNeighourMines(self, row: int, column: int) -> List:
        mineSquares = []
        for deltaRow in [-1, 0, 1]:
            for deltaColumn in [-1, 0, 1]:
                if (
                    not (deltaRow == 0 and deltaColumn == 0)
                    and row + deltaRow >= 0
                    and column + deltaColumn >= 0
                    and row + deltaRow < self.height
                    and column + deltaColumn < self.width
                ):
                    mineSquare = (row + deltaRow, column + deltaColumn)
                    if mineSquare in self.mines:
                        mineSquares.append(mineSquare)
        return mineSquares

    # returns a new random square that is not in self.openSquares or self.bombs
    def getNewRandomLocation(self) -> tuple:
        valid = False
        while not valid:
            randomSquare = (randint(0, self.height - 1), randint(0, self.width - 1))
            if (
                randomSquare not in self.openSquares.keys()
                and randomSquare not in self.mines
            ):
                valid = True

        return randomSquare


def main() -> None:
    difficulty = BEGINNER_FIELD

    MineFieldInstance = MineField(
        width=difficulty["width"],
        height=difficulty["height"],
        number_of_mines=difficulty["number_of_mines"],
    )

    sweeper = Sweeper(MineFieldInstance, difficulty)

    mines = sweeper.solve()
    print("Mine locations:")
    for i, mine in enumerate(mines):
        print("Mine {} location: {}".format(i + 1, mine))  # hahahahaha one indexing


if __name__ == "__main__":
    main()

