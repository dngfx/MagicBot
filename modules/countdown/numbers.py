import sys
import time
from random import randint, sample
from colorama import Fore, Back, Style

BIGS = [25, 50, 75, 100]
SMALLS = list(range(1, 11)) * 2


class Numbers:
    def __init__(self):
        pass

    def run_game(self):
        print("\nTime for a numbers round, Select your numbers..\n")
        numbers = self.generate_numbers()
        print(
            Fore.YELLOW
            + f"\n**  {' '.join(str(i) for i in numbers)}  **\n"
            + Style.RESET_ALL
        )
        target = self.generate_target()
        time.sleep(1)
        print("Time to start the countdown")
        for i in range(30):
            sys.stdout.write("\rCountdown %i seconds to go" % (29 - i))
            time.sleep(1)
            sys.stdout.flush()
        print("Time is up. Did you get it?")
        print("Rachael, could it be done?")
        results = Rachael(target, numbers).solve()
        print(Fore.YELLOW)
        if results:
            result = sample(results, 1)[0]
            print(f"I found {len(results)} solutions\nHere is one of them...\n")
            for rt in result:
                print(
                    " ".join([str(item) if type(item) is int else item for item in rt])
                )
            print(Style.RESET_ALL + "\n")
        else:
            print("I couldn't find a solution...")
            print(Style.RESET_ALL)
            print("Rachael, you have one job!\n")

    def generate_numbers(self):
        while True:
            bigs = input("How many big numbers? (0-4) : ")
            try:
                bigs = int(bigs)
                if bigs >= 0 and bigs <= 4:
                    break
                else:
                    print("Not a vaild number! Must be between 0-4")
            except ValueError:
                print("Not a vaild number! Must be between 0-4")

        return sample(BIGS, bigs) + sample(SMALLS, 6 - bigs)

    def generate_target(self):
        print(Fore.YELLOW)

        for i in range(20):
            target = randint(101, 999)
            sys.stdout.write(f"\r{target}")
            time.sleep(0.02)
            sys.stdout.flush()

        sys.stdout.write(f"\r{target}")
        print(Style.RESET_ALL + "\n")
        return target


class Rachael:
    def __init__(self, target, numbers):
        self.target = target
        self.numbers = numbers

        self.add = lambda a, b: a + b
        self.sub = lambda a, b: a - b
        self.mul = lambda a, b: a * b
        self.div = lambda a, b: a / b if a % b == 0 else 0 / 0

        self.operations = [
            (self.add, "+"),
            (self.sub, "-"),
            (self.mul, "*"),
            (self.div, "/"),
        ]

    def evaluate(self, stack):
        try:
            total = 0
            running_total = []
            lastOper = self.add
            lastSymb = "+"
            for item in stack:
                if type(item) is int:
                    start = total
                    total = round(lastOper(total, item))
                    if start != 0:
                        running_total.append([start, lastSymb, item, "=", total])
                else:
                    lastOper = item[0]
                    lastSymb = item[1]
            return total, running_total
        except Exception as e:
            return 0, []

    def solve(self):

        results = []

        def recurse(stack, nums):
            for n in range(len(nums)):
                stack.append(nums[n])

                remaining = nums[:n] + nums[n + 1 :]
                total, running_total = self.evaluate(stack)
                if total == self.target:
                    results.append(running_total)

                if len(remaining) > 0:
                    for op in self.operations:
                        stack.append(op)
                        stack = recurse(stack, remaining)
                        stack = stack[:-1]

                stack = stack[:-1]

            return stack

        recurse([], self.numbers)
        return results
