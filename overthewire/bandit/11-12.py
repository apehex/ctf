DIGITS = set('0123456789')
LETTERS = set('abcdefghijklmnopqrstuvwxyz')
PUZZLE = '5Gr8L4qetPEsPk8htqjhRK8XSP6x2RHh'

def _rotate_lowercase_letter(
        char: str,
        count: int) -> str:
    return chr(
        97 + (
            (ord(char) - 97 + count) % 26))

def _rotate_uppercase_letter(
        char: str,
        count: int) -> str:
    return _rotate_lowercase_letter(
        char.lower(),
        count).upper()

def _rotate_single_char(
        char: str,
        count: int) -> str:
    if char in DIGITS:
        return char
    elif char in LETTERS:
        return _rotate_lowercase_letter(char, count)
    else:
        return _rotate_uppercase_letter(char, count)
