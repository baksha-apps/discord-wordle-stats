import re

# Helpers

def is_wordle_share(msg: str):
    return re.match('Wordle \d\d\d .\/\d\n\n[⬛⬜🟩🟨]{5}', msg) is not None


# State
