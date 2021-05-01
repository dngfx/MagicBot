import sys
import time
import collections

from colorama import Fore, Back, Style
from random import choice

CONSTONANTS = {
    "b": 2,
    "c": 1,
    "d": 1,
    "f": 1,
    "g": 1,
    "h": 1,
    "j": 1,
    "k": 1,
    "l": 2,
    "m": 1,
    "n": 2,
    "p": 2,
    "q": 1,
    "r": 1,
    "s": 2,
    "t": 2,
    "v": 1,
    "w": 1,
    "x": 1,
    "y": 1,
    "z": 1,
}

VOWELS = {"a": 3, "e": 3, "i": 3, "o": 3, "u": 2}


class Letters:
    def __init__(self):
        self.letters = []
        self.consonants = []
        self.vowels = []

    def run_game(self):

        print("\nTime for a letters round, Select your letters..\n")

        self.select_letters()

        time.sleep(1)
        print("Time to start the countdown")

        for i in range(30):
            sys.stdout.write("\rCountdown %i seconds to go" % (29 - i))
            time.sleep(1)
            sys.stdout.flush()

        print("\nTime is up. How many did you get?")
        print("\nSusie what else could they have had?")
        matches = self.find_words()
        matches.sort(key=lambda s: len(s), reverse=True)
        print(Fore.GREEN)
        print(f"{len(matches[0])} was the best they could of had.")
        print(f"Some of the words i found were {' '.join(matches[:5])}")
        print(Style.RESET_ALL)

    def select_letters(self):
        while True:
            option = input("Select a (v)owel or (c)onsonant: ")
            if option == "c":
                if len(self.consonants) >= 6:
                    print(
                        Fore.RED
                        + "You've reached your limit of 6 consonants"
                        + Style.RESET_ALL
                    )
                    continue
                else:
                    letter = choice([l for l, c in CONSTONANTS.items() if c > 0])
                    CONSTONANTS[letter] -= 1
                    self.consonants.append(letter)
            elif option == "v":
                if len(self.vowels) >= 5:
                    print(
                        Fore.RED
                        + "You've reached your limit of 5 vowels"
                        + Style.RESET_ALL
                    )
                    continue
                else:
                    letter = choice([l for l, c in VOWELS.items() if c > 0])
                    VOWELS[letter] -= 1
                    self.vowels.append(letter)
            else:
                print(Fore.RED + "invalid choice!" + Style.RESET_ALL)
                continue

            self.letters.append(letter)
            print(
                Fore.GREEN
                + f"* {' '.join(l.capitalize() for l in self.letters)} *"
                + Style.RESET_ALL
            )

            if len(self.letters) == 9:
                break

    def load_dictionary(self):
        dictonary = "/usr/share/dict/words"
        return set(
            word.strip() for word in open(dictonary) if len(word) <= 9 and len(word) > 1
        )

    def find_words(self):
        matches = []
        words = self.load_dictionary()
        letter_counter = collections.Counter(self.letters)
        for word in words:
            # if all letters in word are in leters list
            if all(x in self.letters for x in word):
                word_counter = collections.Counter(word)
                diff = word_counter - letter_counter
                if not diff:
                    matches.append(word)
        return matches
