"""
Gomoku game
https://en.wikipedia.org/wiki/Gomoku
"""
from __future__ import annotations
import string
from typing import Literal, Union


class GameError(Exception):
    pass


class Game:
    DIMENSION = 9
    INITIAL_STATE = [None] * (DIMENSION * DIMENSION)
    CHAR_MAP = {
        0: "o",
        1: "x",
    }

    def __init__(self) -> None:
        self.state: list[Union[None, Literal[0], Literal[1]]] = []
        self._init_state()

    def _init_state(self):
        """Copy the state from initial"""
        self.state = self.INITIAL_STATE[:]

    def field(self) -> list[list[Union[None, Literal[0], Literal[1]]]]:
        """render a 2d field for the game"""
        return [
            self.state[row * self.DIMENSION : (row + 1) * self.DIMENSION]
            for row in range(self.DIMENSION)
        ]

    def is_draw(self):
        return None not in self.state

    def dump(self) -> str:
        blacks = []
        whites = []
        for i, v in enumerate(self.state):
            if v == 0:
                whites.append(i)
            elif v == 1:
                blacks.append(i)
        return blacks, whites

    def load(self, blacks: list[int], whites: list[int]) -> None:
        for i in blacks:
            self.state[i] = 1
        for i in whites:
            self.state[i] = 0

    def _pos_to_idx(self, pos: str) -> int:
        pos = pos.upper()
        try:
            col, row = list(pos)
            row = int(row) - 1
        except ValueError:
            raise GameError(f"Invalid pos: {pos}")
        col = ord(col) - ord("A")
        if row >= self.DIMENSION or col >= self.DIMENSION:
            raise GameError(f"Invalid pos: {pos}")
        res = row * self.DIMENSION + col
        if self.state[res] is not None:
            raise GameError(f"Invalid pos: {pos} is occupied")
        return res

    def show(self):
        print(" ", *string.ascii_uppercase[: self.DIMENSION], sep=" ")
        for row in range(self.DIMENSION):
            print(
                row + 1,
                *[
                    self.CHAR_MAP.get(v, " ")
                    for v in self.state[
                        row * self.DIMENSION : (row + 1) * self.DIMENSION
                    ]
                ],
                sep=" ",
            )

    def _check_line(self, line):
        """0: white win, 1: black win, other: none wins"""
        role = None
        number = 0
        for v in line:
            if v is not None:
                if role != v:
                    role = v
                    number = 0
                number += 1
                if number >= 5:
                    return role
            else:
                role, number = None, 0

    def check_field(self, idx):
        s = self.state
        D = self.DIMENSION
        max_len = len(s)
        # Rows
        if (
            ret := self._check_line(s[(idx // D) * D : (idx // D + 1) * D])
        ) is not None:
            return ret
        # Columns
        if (ret := self._check_line(s[idx % D : max_len : D])) is not None:
            return ret
        # down left to upper right
        if (
            ret := self._check_line(s[idx % (D - 1) : max_len - 1 : D - 1])
        ) is not None:
            return ret
        # upper left to down right
        if (ret := self._check_line(s[idx % (D + 1) : max_len : D + 1])) is not None:
            return ret

    def _ask_for_idx(self, message: str) -> int:
        ans = input(message).strip()
        try:
            idx = self._pos_to_idx(ans)
        except GameError as e:
            print(e)
            return self._ask_for_idx(message)
        else:
            return idx

    def drop(self, idx: int, role: Union[Literal[0], Literal[1]]) -> None:
        self.state[idx] = role

    def play(self):
        role = 1
        self.show()
        while True:
            idx = self._ask_for_idx(
                "{}'s turn({}), please input:".format(
                    "Black" if role else "White", self.CHAR_MAP.get(role)
                )
            )
            self.drop(idx, role)
            self.show()
            if (ret := self.check_field(idx)) == 1:
                print("Black win!")
            elif ret == 0:
                print("White win!")
            else:
                role ^= 1
                continue
            if input("Press 'q' to quit, any other key to restart") == "q":
                exit(0)
            self._init_state()
            role = 1
            self.show()


if __name__ == "__main__":
    game = Game()
    game.play()
