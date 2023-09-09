import json
import os
import re
from pathlib import Path
from subprocess import check_call
from typing import Literal, Union

from github3 import login
from jinja2 import Template

from chess.gomoku import Game

BASE_DIR = Path(__file__).parent


def print_title(title: str):
    print("=" * 8 + " " + title + " " + "=" * 8)


class Runner:
    GAME_META = BASE_DIR / "gomoku.json"
    GAME_STATS = BASE_DIR / "stats.json"
    README = BASE_DIR.parent / "tools/gomoku/README.md"
    ROLES = {0: "white", 1: "black"}
    TEMPLATE = BASE_DIR / "templates/readme.j2"
    SUMMARY_TEMPLATE = BASE_DIR / "templates/summary.j2"

    def __init__(self) -> None:
        self.meta = json.load(self.GAME_META.open(encoding="utf-8"))
        self.stats = json.load(self.GAME_STATS.open(encoding="utf-8"))
        self.readme = self.README.read_text(encoding="utf-8")

    def play_game(
        self, role: Union[Literal[0], Literal[1]], pos: str, user: str
    ) -> None:
        """Title: gomoku|drop|black|b4"""
        game = Game()
        assert (
            role == self.meta["role"]
        ), f"Current player role doesn't match, should be {self.ROLES[self.meta['role']]}"
        game.load(self.meta["blacks"], self.meta["whites"])
        if game.is_draw() or self.meta["winner"] is not None:
            raise ValueError("The game is already over, please start a new game.")
        idx = game._pos_to_idx(pos)
        game.drop(idx, role)
        self.stats["all_players"][user] = self.stats["all_players"].get(user, 0) + 1
        self.meta["turn"] += 1
        self.meta["last_steps"].insert(
            0, {"user": user, "color": self.ROLES[role], "pos": pos}
        )
        self.meta["blacks"], self.meta["whites"] = game.dump()
        winner = game.check_field(idx)
        if winner is not None:
            self.end_game(winner, user)
        else:
            self.meta["role"] ^= 1

    def dump(self):
        print_title("dumping data")
        json.dump(self.meta, self.GAME_META.open("w", encoding="utf-8"))
        json.dump(self.stats, self.GAME_STATS.open("w", encoding="utf-8"))
        self.README.write_text(self.readme, "utf-8")

    def new_game(self):
        print_title("initializing game")
        self.meta.update(
            turn=0, last_steps=[], blacks=[], whites=[], role=1, winner=None
        )

    def update_readme(self) -> None:
        print_title("Updating README")
        game = Game()
        game.load(self.meta["blacks"], self.meta["whites"])
        top_wins = sorted(
            self.stats["winning_players"].items(), key=lambda x: x[1], reverse=True
        )[:10]
        context = {
            "total_players": len(self.stats["all_players"]),
            "total_moves": sum(self.stats["all_players"].values()),
            "completed_games": self.stats["completed_games"],
            "winner": self.ROLES.get(self.meta["winner"]),
            "draw": game.is_draw(),
            "dimension": game.DIMENSION,
            "field": game.field(),
            "color": self.ROLES.get(self.meta["role"]),
            "last_steps": self.meta["last_steps"],
            "top_wins": top_wins,
            "repo": os.getenv("REPO"),
        }
        template = Template(self.TEMPLATE.read_text("utf-8"))
        self.readme = re.sub(
            r"(<\!--START_SECTION:gomoku-->\n)(.*)(\n<\!--END_SECTION:gomoku-->)",
            r"\1" + template.render(**context) + r"\3",
            self.readme,
            flags=re.DOTALL,
        )

    def commit_files(self, message: str):
        check_call(["git", "add", "-A", "."])
        check_call(["git", "commit", "-m", message])

    def end_game(self, win_role: int, winner: str):
        print_title("end of game")
        self.meta["winner"] = win_role
        self.stats["completed_games"] += 1
        self.stats["winning_players"][winner] = (
            self.stats["winning_players"].get(winner, 0) + 1
        )
        game = Game()
        game.load(self.meta["blacks"], self.meta["whites"])
        template = Template(self.SUMMARY_TEMPLATE.read_text("utf-8"))
        context = {
            "dimension": game.DIMENSION,
            "field": game.field(),
            "color": self.ROLES.get(win_role),
            "winner": winner,
            "last_steps": self.meta["last_steps"],
            "root": f"https://github.com/{os.getenv('REPO')}",
        }
        summary_text = template.render(**context)
        # print(summary_text)
        gh = login(token=os.getenv("GITHUB_TOKEN"))
        namespace, repo = os.getenv("REPO").split("/")
        issue_num = int(os.getenv("ISSUE_NUMBER"))
        issue = gh.issue(namespace, repo, issue_num)
        print(issue.create_comment(summary_text))

    def main(self):
        issue_title = os.getenv("ISSUE_TITLE")
        parts = issue_title.split("|")
        user = os.getenv("PLAYER")
        if len(parts) < 4 and "new" in parts:
            print_title("new game")
            self.new_game()
            message = f"@{user} starts a new game"
        elif len(parts) < 4 and "surrender" in parts:
            print_title("surrender")
            try:
                last_step = self.meta["last_steps"][0]
            except IndexError:
                last_step = None
            if last_step is not None:
                winner = last_step["user"]
                color = last_step["color"]
                role = 1 if color == "black" else 0
                self.end_game(role, winner)
            self.new_game()
            message = (
                f"@{user} surrenders and @{last_step['user']} wins"
                if last_step
                else f"@{user} surrenders"
            )
        else:
            print_title("perform drop")
            *_, color, pos = parts
            input_role = 1 if color == "black" else 0
            self.play_game(input_role, pos, user)
            message = f"@{user} drops a {color} piece at {pos.upper()}"
        message += f"\nClose #{os.getenv('ISSUE_NUMBER')}"
        self.update_readme()
        self.dump()
        self.commit_files(message)


if __name__ == "__main__":
    Runner().main()
