import enum, re, typing
from .time import duration
from .types import try_int
from src.utils.datetime.parse import date_human

<<<<<<< HEAD

class SpecTypeError(Exception):

    def __init__(self, message: str, arg_count: int = 1):
        self.message = message
        self.arg_count = arg_count


=======
class SpecTypeError(Exception):
    def __init__(self, message: str, arg_count: int=1):
        self.message = message
        self.arg_count = arg_count

>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
class SpecArgumentContext(enum.IntFlag):
    CHANNEL = 1
    PRIVATE = 2
    ALL = 3

<<<<<<< HEAD

class SpecArgumentType(object):
    context = SpecArgumentContext.ALL

    def __init__(self,
                 type_name: str,
                 name: typing.Optional[str],
                 modifier: typing.Optional[str],
                 exported: typing.Optional[str]):
=======
class SpecArgumentType(object):
    context = SpecArgumentContext.ALL

    def __init__(self, type_name: str, name: typing.Optional[str],
            modifier: typing.Optional[str], exported: typing.Optional[str]):
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
        self.type = type_name
        self._name = name
        self._set_modifier(modifier)
        self.exported = exported

    def _set_modifier(self, modifier: typing.Optional[str]):
        pass

    def name(self) -> typing.Optional[str]:
        return self._name
<<<<<<< HEAD

    def simple(self, args: typing.List[str]) -> typing.Tuple[typing.Any, int]:
        return None, -1

    def error(self) -> typing.Optional[str]:
        return None


class SpecArgumentTypePattern(SpecArgumentType):
    _pattern: typing.Pattern

    def _set_modifier(self, modifier):
        self._pattern = re.compile(modifier)

=======
    def simple(self, args: typing.List[str]) -> typing.Tuple[typing.Any, int]:
        return None, -1
    def error(self) -> typing.Optional[str]:
        return None

class SpecArgumentTypePattern(SpecArgumentType):
    _pattern: typing.Pattern
    def _set_modifier(self, modifier):
        self._pattern = re.compile(modifier)
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
    def simple(self, args):
        match = self._pattern.search(" ".join(args))
        if match:
            return match, match.group(0).rstrip(" ").count(" ")
        else:
            return None, 1

<<<<<<< HEAD

class SpecArgumentTypeWord(SpecArgumentType):

=======
class SpecArgumentTypeWord(SpecArgumentType):
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
    def simple(self, args):
        if args:
            return args[0], 1
        return None, 1
<<<<<<< HEAD


class SpecArgumentTypeAdditionalWord(SpecArgumentType):

=======
class SpecArgumentTypeAdditionalWord(SpecArgumentType):
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
    def simple(self, args):
        if len(args) > 1:
            return args[0], 1
        return None, 1
<<<<<<< HEAD


class SpecArgumentTypeWordLower(SpecArgumentTypeWord):

=======
class SpecArgumentTypeWordLower(SpecArgumentTypeWord):
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
    def simple(self, args):
        out = SpecArgumentTypeWord.simple(self, args)
        if out[0]:
            return out[0].lower(), out[1]
        return out

<<<<<<< HEAD

class SpecArgumentTypeString(SpecArgumentType):

    def name(self):
        return "%s ..." % SpecArgumentType.name(self)

=======
class SpecArgumentTypeString(SpecArgumentType):
    def name(self):
        return "%s ..." % SpecArgumentType.name(self)
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
    def simple(self, args):
        if args:
            return " ".join(args), len(args)
        return None, 1
<<<<<<< HEAD


class SpecArgumentTypeTrimString(SpecArgumentTypeString):

    def simple(self, args):
        return SpecArgumentTypeString.simple(self, list(filter(None, args)))


class SpecArgumentTypeWords(SpecArgumentTypeString):

=======
class SpecArgumentTypeTrimString(SpecArgumentTypeString):
    def simple(self, args):
        return SpecArgumentTypeString.simple(self, list(filter(None, args)))
class SpecArgumentTypeWords(SpecArgumentTypeString):
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
    def simple(self, args):
        if args:
            out = list(filter(None, args))
            return out, len(out)
        return None, 1

<<<<<<< HEAD

class SpecArgumentTypeInt(SpecArgumentType):

=======
class SpecArgumentTypeInt(SpecArgumentType):
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
    def simple(self, args):
        if args:
            return try_int(args[0]), 1
        return None, 1

<<<<<<< HEAD

class SpecArgumentTypeDuration(SpecArgumentType):

    def name(self):
        return "+%s" % (SpecArgumentType.name(self) or "duration")

=======
class SpecArgumentTypeDuration(SpecArgumentType):
    def name(self):
        return "+%s" % (SpecArgumentType.name(self) or "duration")
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
    def simple(self, args):
        if args:
            return duration(args[0]), 1
        return None, 1
<<<<<<< HEAD

    def error(self) -> typing.Optional[str]:
        return "Invalid timeframe"


class SpecArgumentTypeDate(SpecArgumentType):

    def name(self):
        return SpecArgumentType.name(self) or "yyyy-mm-dd"

=======
    def error(self) -> typing.Optional[str]:
        return "Invalid timeframe"

class SpecArgumentTypeDate(SpecArgumentType):
    def name(self):
        return SpecArgumentType.name(self) or "yyyy-mm-dd"
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
    def simple(self, args):
        if args:
            return date_human(args[0]), 1
        return None, 1

<<<<<<< HEAD

class SpecArgumentPrivateType(SpecArgumentType):
    context = SpecArgumentContext.PRIVATE


=======
class SpecArgumentPrivateType(SpecArgumentType):
    context = SpecArgumentContext.PRIVATE

>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
SPEC_ARGUMENT_TYPES = {
    "word": SpecArgumentTypeWord,
    "aword": SpecArgumentTypeAdditionalWord,
    "wordlower": SpecArgumentTypeWordLower,
    "string": SpecArgumentTypeString,
    "words": SpecArgumentTypeWords,
    "tstring": SpecArgumentTypeTrimString,
    "int": SpecArgumentTypeInt,
    "date": SpecArgumentTypeDate,
    "duration": SpecArgumentTypeDuration,
    "pattern": SpecArgumentTypePattern
}

<<<<<<< HEAD

=======
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
class SpecArgument(object):
    consume = True
    optional: bool = False
    types: typing.List[SpecArgumentType] = []

    @staticmethod
    def parse(optional: bool, argument_types: typing.List[str]):
        out: typing.List[SpecArgumentType] = []
        for argument_type in argument_types:
            exported = None
            if "~" in argument_type:
                exported = argument_type.split("~", 1)[1]
                argument_type = argument_type.replace("~", "", 1)

            argument_type_name: typing.Optional[str] = None
            name_end = argument_type.find(">")
            if name_end > 0 and argument_type.startswith("<"):
                argument_type_name = argument_type[1:name_end]
<<<<<<< HEAD
                argument_type = argument_type[name_end + 1:]
=======
                argument_type = argument_type[name_end+1:]
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5

            argument_type_modifier: typing.Optional[str] = None
            modifier_start = argument_type.find("(")
            if modifier_start > 0 and argument_type.endswith(")"):
<<<<<<< HEAD
                argument_type_modifier = argument_type[modifier_start + 1:-1]
=======
                argument_type_modifier = argument_type[modifier_start+1:-1]
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
                argument_type = argument_type[:modifier_start]

            argument_type_class = SpecArgumentType
            if argument_type in SPEC_ARGUMENT_TYPES:
                argument_type_class = SPEC_ARGUMENT_TYPES[argument_type]
            elif exported:
                argument_type_class = SpecArgumentPrivateType

<<<<<<< HEAD
            out.append(argument_type_class(argument_type, argument_type_name, argument_type_modifier, exported))
=======
            out.append(argument_type_class(argument_type,
                argument_type_name, argument_type_modifier, exported))
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5

        spec_argument = SpecArgument()
        spec_argument.optional = optional
        spec_argument.types = out
        return spec_argument

    def format(self, context: SpecArgumentContext) -> typing.Optional[str]:
        if self.optional:
            format = "[%s]"
        else:
            format = "<%s>"

        names: typing.List[str] = []
        for argument_type in self.types:
<<<<<<< HEAD
            if not (context & argument_type.context) == 0:
=======
            if not (context&argument_type.context) == 0:
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
                name = argument_type.name() or argument_type.type
                if name and not name in names:
                    names.append(name)
        if names:
            return format % "|".join(names)
        return None

<<<<<<< HEAD

class SpecArgumentTypeLiteral(SpecArgumentType):

=======
class SpecArgumentTypeLiteral(SpecArgumentType):
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
    def simple(self, args: typing.List[str]) -> typing.Tuple[typing.Any, int]:
        if args and args[0] == self.name():
            return args[0], 1
        return None, 1
<<<<<<< HEAD

    def error(self) -> typing.Optional[str]:
        return None


class SpecLiteralArgument(SpecArgument):

=======
    def error(self) -> typing.Optional[str]:
        return None
class SpecLiteralArgument(SpecArgument):
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
    @staticmethod
    def parse(optional: bool, literals: typing.List[str]) -> SpecArgument:
        spec_argument = SpecLiteralArgument()
        spec_argument.optional = optional
<<<<<<< HEAD
        spec_argument.types = [SpecArgumentTypeLiteral("literal", l, None, None) for l in literals]
=======
        spec_argument.types = [
            SpecArgumentTypeLiteral("literal", l, None, None) for l in literals]
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
        return spec_argument

    def format(self, context: SpecArgumentContext) -> typing.Optional[str]:
        return "|".join(t.name() or "" for t in self.types)

<<<<<<< HEAD

=======
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
def argument_spec(spec: str) -> typing.List[SpecArgument]:
    out: typing.List[SpecArgument] = []
    for spec_argument in spec.split(" "):
        optional = spec_argument[0] == "?"

        if spec_argument[1] == "'":
<<<<<<< HEAD
            out.append(SpecLiteralArgument.parse(optional, spec_argument[2:].split(",")))
=======
            out.append(SpecLiteralArgument.parse(optional,
                spec_argument[2:].split(",")))
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
        else:
            consume = True
            if spec_argument[1] == "-":
                consume = False
                spec_argument = spec_argument[1:]

<<<<<<< HEAD
            spec_argument_obj = SpecArgument.parse(optional, spec_argument[1:].split("|"))
=======
            spec_argument_obj = SpecArgument.parse(optional,
                spec_argument[1:].split("|"))
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
            spec_argument_obj.consume = consume
            out.append(spec_argument_obj)

    return out

<<<<<<< HEAD

def argument_spec_human(spec: typing.List[SpecArgument], context: SpecArgumentContext = SpecArgumentContext.ALL) -> str:
=======
def argument_spec_human(spec: typing.List[SpecArgument],
        context: SpecArgumentContext=SpecArgumentContext.ALL) -> str:
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
    arguments: typing.List[str] = []
    for spec_argument in spec:
        if spec_argument.consume:
            out = spec_argument.format(context)
            if out:
                arguments.append(out)
    return " ".join(arguments)
