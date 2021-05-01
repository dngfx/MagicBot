from src.letters import Letters
from src.numbers import Numbers
from src.conundrum import Conundrum


def main():
    print(
        """
========================
* Welcome to Countdown *
========================

* A Game about letters, numbers and conundrums *
    """
    )

    while True:
        print("Select a game: ")
        print("  * (L)etters")
        print("  * (N)umbers")
        print("  * (C)onundrum")
        print("  * (E)xit")
        choice = input("  ")

        if choice in ["l", "L"]:
            Letters().run_game()
        if choice in ["n", "N"]:
            Numbers().run_game()
        if choice in ["c", "C"]:
            Conundrum().run_game()

        if choice in ["e", "E", "q", "Q"]:
            print("Thanks for playing Countdown!")
            break
