from src.utils import datetime

<<<<<<< HEAD

=======
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
def duration(s: str):
    if s[0] == "+":
        duration = datetime.parse.from_pretty_time(s[1:])
        if not duration == None:
            return duration
    return None
<<<<<<< HEAD
=======

>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
