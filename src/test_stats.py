from wordle import is_wordle_share, find_try_ratio
import pytest

# is_wordle_share TESTS
def test_is_wordle_share_true():
    valid_wordle = '''Wordle 215 4/6

🟩⬛⬛⬛⬛
🟩🟩⬛⬛⬛
🟩🟩🟨🟩⬛
🟩🟩🟩🟩🟩
'''
    
    assert is_wordle_share(valid_wordle) == True    

def test_is_wordle_share_false():
    invalid_wordle = '''Nondle 215 4/6

🟩⬛⬛⬛⬛
🟩🟩⬛⬛⬛
🟩🟩🟨🟩⬛
🟩🟩🟩🟩🟩
'''
    
    assert is_wordle_share(invalid_wordle) == False    

def test_find_try_ratio_4of6():
    wordle = '''Nondle 215 4/6

🟩⬛⬛⬛⬛
🟩🟩⬛⬛⬛
🟩🟩🟨🟩⬛
🟩🟩🟩🟩🟩
'''
    
    assert find_try_ratio(wordle) == (4, 6)

def test_find_try_ratio_Xof6():
    wordle = '''Nondle 215 X/6

🟩⬛⬛⬛⬛
🟩🟩⬛⬛⬛
🟩🟩🟨🟩⬛
⬛⬛⬛⬛⬛
⬛⬛⬛⬛⬛
⬛⬛⬛⬛⬛
'''
    
    assert find_try_ratio(wordle) == (None, 6)