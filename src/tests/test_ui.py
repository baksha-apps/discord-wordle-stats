from datetime import datetime, timedelta

import pandas as pd

import ui
from wordle import WordleStatistics

MASTER_DF_FIXTURE = pd.read_csv('src/tests/res/stubbed_messages.csv', parse_dates=['created_date'])


# These just verify that they do not throw an error when creating

def test_make_leaderboard_embed():
    # given
    sut = WordleStatistics()
    sut.master_wordle_df = MASTER_DF_FIXTURE
    sut.add_wordle("travie", 1000, 1, 5, datetime.now())
    sut.add_wordle("travis", 1000, None, 5, datetime.now())
    sut.add_wordle("tarvis", 1000, None, 5, datetime.now() + timedelta(minutes=5))
    sut.add_wordle("ravis", 1000, 2, 5, datetime.now() + timedelta(minutes=10))
    # when
    df = sut.compute_all_stats_df()
    # then
    _ = ui.make_leaderboard_embed(df)


def test_make_wordle_day_embed():
    # given
    sut = WordleStatistics()
    sut.master_wordle_df = MASTER_DF_FIXTURE
    sut.add_wordle("travie", 1000, 1, 5, datetime.now())
    sut.add_wordle("travis", 1000, None, 5, datetime.now())
    sut.add_wordle("tarvis", 1000, None, 5, datetime.now() + timedelta(minutes=5))
    sut.add_wordle("ravis", 1000, 2, 5, datetime.now() + timedelta(minutes=10))
    # when
    wordle_id, avg_turn_won, percent_of_winners, df = sut.compute_day_df_for_wordle(228)
    # then
    _ = ui.make_wordle_day_embed(wordle_id, avg_turn_won, percent_of_winners, df)
