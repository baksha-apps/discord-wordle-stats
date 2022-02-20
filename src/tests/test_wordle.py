import pandas as pd
from wordle import is_wordle_share, find_try_ratio, find_wordle_id, WordleState
from datetime import datetime, timedelta
import textwrap

MASTER_DF_FIXTURE = pd.read_csv('src/tests/res/stubbed_messages.csv', parse_dates=['created_date'])


def test_is_wordle_share_true():
    valid_wordle = '''\
        Wordle 215 4/6
    
        🟩⬛⬛⬛⬛
        🟩🟩⬛⬛⬛
        🟩🟩🟨🟩⬛
        🟩🟩🟩🟩🟩'''

    assert is_wordle_share(textwrap.dedent(valid_wordle))


def test_is_wordle_share_true_with_ast():
    valid_wordle = '''\
        Wordle 215 4/6*

        🟩⬛⬛⬛⬛
        🟩🟩⬛⬛⬛
        🟩🟩🟨🟩⬛
        🟩🟩🟩🟩🟩'''

    assert is_wordle_share(textwrap.dedent(valid_wordle))


def test_is_wordle_share_false():
    invalid_wordle = '''\
        Nordle 215 4/6
    
        🟩⬛⬛⬛⬛
        🟩🟩⬛⬛⬛
        🟩🟩🟨🟩⬛
        🟩🟩🟩🟩🟩'''

    assert not is_wordle_share(textwrap.dedent(invalid_wordle))


def test_find_try_ratio_4of6():
    header = '''Wordle 215 4/6'''
    assert find_try_ratio(header) == (4, 6)


def test_find_try_ratio_4of6_with_atsrk():
    header = '''Wordle 215 4/6*'''
    assert find_try_ratio(header) == (4, 6)


def test_find_try_ratio_Xof6():
    header = '''Nondle 215 X/6'''
    assert find_try_ratio(header) == (None, 6)


def test_find_wordle_id():
    header = '''Wordle 215 X/6'''
    assert find_wordle_id(header) == 215


def test_add_games_to_state():
    # given
    sut = WordleState()

    # when
    sut.add_wordle("id1", 1, 1, 6, datetime.now())
    sut.add_wordle("id2", 1, None, 6, datetime.now())

    # then
    assert len(sut.master_wordle_df) == 2


def test_make_sanitized_df():
    # given
    sut = WordleState()

    # when
    sut.add_wordle("id1", 1, 1, 6, datetime.now())
    sut.add_wordle("id1", 1, None, 6, datetime.now() + timedelta(minutes=2))
    sut.add_wordle("id2", 1, 1, 6, datetime.now())
    sut.add_wordle("id2", 2, None, 6, datetime.now() + timedelta(minutes=2))
    # then
    assert len(sut.__make_sanitized_wordle_df__()) == 3


def test_compute_daily():
    # given
    sut = WordleState()
    sut.master_wordle_df = MASTER_DF_FIXTURE
    sut.add_wordle("travie", 1000, 1, 5, datetime.now())
    sut.add_wordle("travis", 1000, None, 5, datetime.now())
    sut.add_wordle("tarvis", 1000, None, 5, datetime.now() + timedelta(minutes=5))
    sut.add_wordle("ravis", 1000, 2, 5, datetime.now() + timedelta(minutes=10))

    # when
    wid, avg_turn_won, percent_of_winners, df = sut.compute_daily_df()

    # then
    assert wid == 1000
    assert avg_turn_won == 1.5
    assert percent_of_winners == .5
    assert df.player_id.count() == 4
    assert df.iloc[0].player_id == 'travie'
    assert df.iloc[1].player_id == 'ravis'
    assert df.iloc[2].player_id == 'travis'
    assert df.iloc[3].player_id == 'tarvis'


def test_compute_all():
    # given
    sut = WordleState()
    sut.master_wordle_df = MASTER_DF_FIXTURE

    # when
    df = sut.compute_all_stats_df()

    # then - too lazy to test all sort mechanisms, missing win_percent priority
    assert df.player_id.count() == 8
    assert df.iloc[0].player_id == 'makattacks#8585'
    assert df.iloc[1].player_id == 'phantommenace#6507'
    assert df.iloc[2].player_id == 'PHELIX#2475'
    assert df.iloc[3].player_id == 'Kat#3908'
    assert df.iloc[4].player_id == 'MarkZ#0100'
    assert df.iloc[5].player_id == 'super bad trav#4632'
    assert df.iloc[6].player_id == 'dhong#8046'
    assert df.iloc[7].player_id == 'Lequip#2992'


def test_current_leaderboard_ids_ranked():
    # given
    sut = WordleState()
    sut.master_wordle_df = MASTER_DF_FIXTURE
    # setups up the internal cache rankings_before_last_add, since too lazy to not use fixture
    sut.add_wordle("BEST_PLAYER", 123, 1, 5, datetime.now())

    # when
    rankings = sut.current_leaderboard_ids_ranked()

    # then
    assert len(rankings) == len(set(sut.master_wordle_df.player_id))
    assert rankings[0] == 'BEST_PLAYER'
    assert rankings[1] == 'makattacks#8585'
    assert rankings[2] == 'phantommenace#6507'
    assert rankings[3] == 'PHELIX#2475'
    assert rankings[4] == 'Kat#3908'
    assert rankings[5] == 'MarkZ#0100'
    assert rankings[6] == 'super bad trav#4632'
    assert rankings[7] == 'dhong#8046'
    assert rankings[8] == 'Lequip#2992'


def test_last_add_changed_rank():
    # given
    sut = WordleState()
    sut.master_wordle_df = MASTER_DF_FIXTURE
    # setups up the internal cache rankings_before_last_add, since too lazy to not use fixture
    sut.add_wordle("SAMPLE_PLAYER", 123, 3, 6, datetime.now())

    # when
    sut.add_wordle("BEST_PLAYER", 123, 1, 6, datetime.now())

    # then
    assert sut.find_latest_rank_change('makattacks#8585') == -1


def test_last_add_changed_rank_on_first_game():
    # given
    sut = WordleState()
    sut.master_wordle_df = MASTER_DF_FIXTURE
    # setups up the internal cache rankings_before_last_add, since too lazy to not use fixture
    sut.add_wordle("SAMPLE_PLAYER", 123, 3, 6, datetime.now())

    # when
    sut.add_wordle("WORST_PLAYER", 123, 1, 6, datetime.now())

    # then
    assert sut.find_latest_rank_change('WORST_PLAYER') is None
