import time
import sys
from random import choice
from colorama import Fore, Back, Style


class Conundrum:
    def __init__(self):
        self.word = choice(self.load_dictionary())

    def run_game(self):
        print("\nTime for the crucial conundrum...\n")
        input(Fore.YELLOW + "Press enter to reveil the conundrum... " + Style.RESET_ALL)
        print("\n")
        print(
            "\t"
            + Fore.GREEN
            + " ".join(l.capitalize() for l in self.shuffle(self.word))
            + Style.RESET_ALL
        )
        print("\n")

        for i in range(30):
            sys.stdout.write("\rCountdown %i seconds to go" % (29 - i))
            time.sleep(1)
            sys.stdout.flush()

        print("\nTime is up!")
        print(
            f"\nThe word was {Fore.YELLOW + self.word.capitalize() + Style.RESET_ALL}"
        )
        print("\n")

    def load_dictionary(self):
        dictonary = "/usr/share/dict/words"
        return list(word.strip() for word in open(dictonary) if len(word) == 10)

    def shuffle(self, word):
        array = list(word)
        shuffle = []
        for i in range(len(array)):
            letter = choice(array)
            shuffle.append(letter)
            array.remove(letter)
        return "".join(shuffle)
