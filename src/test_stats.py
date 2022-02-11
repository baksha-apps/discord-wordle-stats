from stats import is_wordle_share
import pytest


def test_is_wordle_share_true():
    sample = '''Wordle 215 4/6

🟩⬛⬛⬛⬛
🟩🟩⬛⬛⬛
🟩🟩🟨🟩⬛
🟩🟩🟩🟩🟩
'''
    
    assert is_wordle_share(sample) == True    

def test_is_wordle_share_false():
    sample = '''Nondle 215 4/6

🟩⬛⬛⬛⬛
🟩🟩⬛⬛⬛
🟩🟩🟨🟩⬛
🟩🟩🟩🟩🟩
'''
    
    assert is_wordle_share(sample) == False    