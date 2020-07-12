import re
from src import IRCLine, utils

<<<<<<< HEAD

class StdOut(object):

=======
class StdOut(object):
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
    def __init__(self, prefix):
        self.prefix = prefix
        self._lines = []
        self._assured = False

    def assure(self):
        self._assured = True

    def write(self, text):
<<<<<<< HEAD
        self.write_lines(text.replace("\r", "").replace("\n\n", "\n").split("\n"))

=======
        self.write_lines(
            text.replace("\r", "").replace("\n\n", "\n").split("\n"))
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
    def write_lines(self, lines):
        self._lines += list(filter(None, lines))

    def get_all(self):
        return self._lines.copy()
<<<<<<< HEAD

    def pop(self):
        return self._lines.pop(0)

=======
    def pop(self):
        return self._lines.pop(0)
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
    def insert(self, text):
        self._lines.insert(0, text)

    def has_text(self):
        return bool(self._lines)
<<<<<<< HEAD
=======

>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
