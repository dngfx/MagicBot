import typing

<<<<<<< HEAD
=======

>>>>>>> parent of 139a1327a... merged
def try_int(s: str) -> typing.Optional[int]:
    try:
        return int(s)
    except ValueError:
        return None
