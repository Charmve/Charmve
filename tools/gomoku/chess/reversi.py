"""
Reversi game
https://en.wikipedia.org/wiki/Reversi
"""
from __future__ import annotations
import string
from typing import Literal, Union


class GameError(Exception):
    pass


class Game:
    DIMENSION = 8
    INITIAL_STATE = [None] * (DIMENSION * DIMENSION)
    CHAR_MAP = {
        0: "o",
        1: "x",
    }

    def __init__(self) -> None:
        self.state: list[list[Union[None, Literal[0], Literal[1]]]] = []
        self._init_state()

    def _init_state(self):
        """Copy the state from initial"""
        self.state = self.INITIAL_STATE[:]
        self.state[(self.DIMENSION // 2 - 1) * (self.DIMENSION + 1)] = self.state[
            self.DIMENSION // 2 * (self.DIMENSION + 1)
        ] = 0
        self.state[self.DIMENSION // 2 * (self.DIMENSION - 1)] = self.state[
            (self.DIMENSION // 2 + 1) * (self.DIMENSION - 1)
        ] = 1

    def _pos_to_idx(self, pos: str) -> int:
        try:
            col, row = list(pos)
            row = int(row) - 1
        except ValueError:
            raise GameError(f"Invalid pos: {pos}")
        col = ord(col) - ord("a")
        if row >= self.DIMENSION or col >= self.DIMENSION:
            raise GameError(f"Invalid pos: {pos}")
        return row * self.DIMENSION + col

    def show(self):
        print(" ", *string.ascii_lowercase[: self.DIMENSION], sep=" ")
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

    def check_game(self):
        """Check the game field to see if someone win."""
        count_1 = 0
        count_0 = 0
        for v in self.state:
            if v == 1:
                count_1 += 1
            elif v == 0:
                count_0 += 1
            else:
                return
        if count_1 > count_0:
            print("Black win!")
        elif count_1 < count_0:
            print("White win!")
        else:
            print("Draw!")
        if input("Press 'q' to quit, any other key to restart") == "q":
            exit(0)
        self._init_state()

    def ask_for_idx(self, message: str) -> int:
        ans = input(message)
        try:
            idx = self._pos_to_idx(ans)
            if self.state[idx] is not None:
                raise GameError(f"Invalid pos: {ans.strip()} is occupied")
        except GameError as e:
            print(e)
            return self.ask_for_idx(message)
        else:
            return idx

    def drop(self, idx: int, role: Union[Literal[0], Literal[1]]) -> None:
        s = self.state
        D = self.DIMENSION
        max_len = len(s)
        s[idx] = role
        to_paint = []
        right = next(
            (i for i in range(idx + 1, D * (idx // D + 1)) if s[i] == role),
            None,
        )
        if right is not None and None not in s[idx + 1 : right]:
            to_paint.extend(range(idx + 1, right))
        left = next(
            (i for i in range(idx - 1, D * (idx // D) - 1, -1) if s[i] == role),
            None,
        )
        if left is not None and None not in s[left + 1 : idx]:
            to_paint.extend(range(left + 1, idx))
        down = next((i for i in range(idx + D, max_len, D) if s[i] == role), None)
        if down is not None and None not in s[idx + D : down : D]:
            to_paint.extend(range(idx + D, down, D))
        up = next(
            (i for i in range(idx - D, -1, -D) if s[i] == role),
            None,
        )
        if up is not None and None not in s[idx - D : up : -D]:
            to_paint.extend(range(idx - D, up, -D))
        upleft = next((i for i in range(idx - D - 1, -1, -D - 1) if s[i] == role), None)
        if upleft is not None and None not in s[idx - D - 1 : upleft : -D - 1]:
            to_paint.extend(range(idx - D - 1, upleft, -D - 1))
        upright = next((i for i in range(idx - D + 1, 0, -D + 1) if s[i] == role), None)
        if upright is not None and None not in s[idx - D + 1 : upright : -D + 1]:
            to_paint.extend(range(idx - D + 1, upright, -D + 1))
        downleft = next(
            (i for i in range(idx + D - 1, max_len - 1, D - 1) if s[i] == role),
            None,
        )
        if downleft is not None and None not in s[idx + D - 1 : downleft : D - 1]:
            to_paint.extend(range(idx + D - 1, downleft, D - 1))
        downright = next(
            (i for i in range(idx + D + 1, max_len, D + 1) if s[i] == role),
            None,
        )
        if downright is not None and None not in s[idx + D + 1 : downright : D + 1]:
            to_paint.extend(range(idx + D + 1, downright, D + 1))
        for i in to_paint:
            s[i] = role

    def play(self):
        role = 1
        while True:
            self.check_game()
            self.show()
            idx = self.ask_for_idx(
                "{}'s turn({}), please input:".format(
                    "Black" if role else "White", self.CHAR_MAP.get(role)
                )
            )
            self.drop(idx, role)
            role ^= 1


if __name__ == "__main__":
    game = Game()
    game.play()
