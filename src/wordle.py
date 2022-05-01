import io
import re
from datetime import datetime, date
from typing import Optional, Tuple

import numpy as np
import pandas as pd

# the words are hardcoded into the game and WID is really just index
ALL_WORDLE_SOLUTIONS = np.load("words.npy")
# nyt has been removing words... we can remove them for parity
nyt_words_removed = {"agora", "pupal", "lynch", "fibre", "slave", "wench", "pussy"}
ALL_WORDLE_SOLUTIONS = [word for word in ALL_WORDLE_SOLUTIONS if word not in nyt_words_removed]


# Helpers

def find_solution(wid: int) -> str:
    return ALL_WORDLE_SOLUTIONS[wid]


def find_wordle_id(wordle_share_msg_header: str) -> int:
    return int(str(wordle_share_msg_header[7:10]))


def is_wordle_share(msg: str) -> bool:
    msg = msg.replace('*', '')
    return re.match(r'Wordle \d\d\d ./\d\n\n[⬛⬜🟩🟨]{5}', msg) is not None


def find_try_ratio(wordle_share_msg_header: str) -> Tuple[Optional[int], int]:
    """
    returns: Tuple[attempt, of_tries]
    """
    wordle_share_msg_header = wordle_share_msg_header.replace('*', '')
    header = wordle_share_msg_header
    won_on_try = int(header[-3]) if header[-3].isdigit() else None
    max_attempts = int(header[-1])
    return won_on_try, max_attempts


# State
class WordleStatistics:

    def __init__(self, timezone: str = 'US/Eastern'):
        """
        :param timezone: The timezone that the Wordle Statistics will sanitize the data on.
        """
        self.previous_all_time_rankings_before_last_add = None
        self.previous_monthly_rankings_before_last_add = None
        self.last_play_date = None
        self.master_wordle_df = pd.DataFrame(columns=[
            'player_id',  # str
            'wordle_id',  # int
            'won_on_try_num',  # optional<int>
            'total_num_tries',  # int
            'created_date'  # int
        ])
        self.timezone = timezone

    def add_wordle(self,
                   player_id: str,
                   wordle_id: int,
                   won_on_try_num: Optional[int],
                   total_num_tries: int,
                   created_date: datetime):
        self.previous_all_time_rankings_before_last_add = self.current_all_time_leaderboard_ids_ranked
        self.previous_monthly_rankings_before_last_add = self.current_monthly_leaderboard_ids_ranked
        # Reset `self.previous_monthly_rankings_before_last_add` on new latest month
        if self.last_play_date and self.last_play_date.month < created_date.month:
            self.previous_monthly_rankings_before_last_add = None
        # Update last play date
        self.last_play_date = max(created_date, self.last_play_date) \
            if self.last_play_date \
            else created_date

        self.master_wordle_df = self.master_wordle_df.append({'player_id': player_id,
                                                              'wordle_id': wordle_id,
                                                              'won_on_try_num': won_on_try_num,
                                                              'total_num_tries': total_num_tries,
                                                              'created_date': created_date},
                                                             ignore_index=True)

    @property
    def current_all_time_leaderboard_ids_ranked(self):
        """
        :returns: list<str> ranking all the players
        """
        df = self.compute_all_stats_df()
        return list(df.player_id) if not df.empty else []

    @property
    def current_monthly_leaderboard_ids_ranked(self):
        """
        :returns: list<str> ranking all the players
        """
        df = self.compute_monthly_stats_df()
        return list(df.player_id) if not df.empty else []

    def find_latest_rank_change(self, player_id, monthly=False):
        """
        Used to check if a players most recent game changed their standing in the leaderboard.

        :returns: <int> difference of rank after last game was played for a given player.
        if the player hasn't played before,
            None
        """
        if monthly:
            if not self.previous_monthly_rankings_before_last_add \
                    or player_id not in self.previous_monthly_rankings_before_last_add:
                return None
            pre_play_player_rank = self.previous_monthly_rankings_before_last_add.index(str(player_id))
            post_play_player_rank = self.current_monthly_leaderboard_ids_ranked.index(str(player_id))
            return pre_play_player_rank - post_play_player_rank

        if not self.previous_all_time_rankings_before_last_add \
                or player_id not in self.previous_all_time_rankings_before_last_add:
            return None
        pre_play_player_rank = self.previous_all_time_rankings_before_last_add.index(str(player_id))
        post_play_player_rank = self.current_all_time_leaderboard_ids_ranked.index(str(player_id))
        return pre_play_player_rank - post_play_player_rank

    def __make_sanitized_wordle_df__(self) -> pd.DataFrame:
        """
        We can lazily prepare for a computation if needed here.... eventually, this should be optimized
        to prepare each record individually instead of repeatedly in batches.
            - Prevents duplicate counts of shares.
                - it would be better if we can just overwrite duplicates on add_wordle()
            - Does handle funny biz from discord.py package that requires some timezone manipulation
        """
        # clearing up duplicate entries
        wordle_df = self.master_wordle_df \
            .sort_values(["created_date"]) \
            .drop_duplicates(subset=['player_id', 'wordle_id'], keep='last')
        # Time funny biz
        if not wordle_df.created_date.empty:
            wordle_df.created_date = wordle_df.created_date.dt.tz_localize('UTC')
            wordle_df.created_date = wordle_df.created_date.dt.tz_convert(self.timezone)
            wordle_df.created_date = wordle_df.created_date.dt.tz_localize(None)
        return wordle_df

    def compute_all_stats_df(self):  #
        """
        :returns: pandas.DataFrame with columns: *sorted
            index                          int64
            player_id                        str
            total_games                    int64
            avg_won_on_attempt           float64
            win_percent                  float64
            started_date          datetime64[ns]
        """
        wordle_df = self.__make_sanitized_wordle_df__()
        all_stats_df = pd.DataFrame()
        groupedby_players = wordle_df.groupby(wordle_df.player_id)
        all_stats_df["total_games"] = groupedby_players.size()
        all_stats_df["avg_won_on_attempt"] = groupedby_players.won_on_try_num.mean()
        # there must be a simpler way for getting each person's WIN percentage, right?
        all_stats_df['win_percent'] = (wordle_df[wordle_df['won_on_try_num'].notna()].groupby(
            wordle_df.player_id).size() / wordle_df.groupby(wordle_df.player_id).size()) * 100
        all_stats_df['started_date'] = groupedby_players.created_date.min()
        return all_stats_df.sort_values(
            by=["avg_won_on_attempt", "total_games", "win_percent", "started_date"],
            ascending=[True, False, False, True]
        ).round(2).reset_index()

    def compute_monthly_stats_df(self):  #
        """
        :returns: pandas.DataFrame with columns: *sorted
            index                          int64
            player_id                        str
            total_games                    int64
            avg_won_on_attempt           float64
            win_percent                  float64
            started_date          datetime64[ns]
        """
        wordle_df = self.__make_sanitized_wordle_df__()

        # Filter for month
        if not wordle_df.created_date.empty:
            start_filter_date = wordle_df['created_date'].max().date().replace(day=1)
            start_filter_timestamp = pd.Timestamp(start_filter_date)
            monthly_filter_mask = wordle_df['created_date'] >= start_filter_timestamp
            wordle_df = wordle_df[monthly_filter_mask]

        all_stats_df = pd.DataFrame()
        groupedby_players = wordle_df.groupby(wordle_df.player_id)
        all_stats_df["total_games"] = groupedby_players.size()
        all_stats_df["avg_won_on_attempt"] = groupedby_players.won_on_try_num.mean()
        # there must be a simpler way for getting each person's WIN percentage, right?
        all_stats_df['win_percent'] = (wordle_df[wordle_df['won_on_try_num'].notna()].groupby(
            wordle_df.player_id).size() / wordle_df.groupby(wordle_df.player_id).size()) * 100
        all_stats_df['started_date'] = groupedby_players.created_date.min()
        return all_stats_df.sort_values(
            by=["avg_won_on_attempt", "total_games", "win_percent", "started_date"],
            ascending=[True, False, False, True]
        ).round(2).reset_index()

    def compute_day_df_for_wordle(self, wordle_id: int, top: int = None):
        """
        :returns:
            avg attempts for wins
            avg of people who won
            pandas.DataFrame with columns: *sorted
                player_id                  object
                wordle_id                  int64
                won_on_try_num            float64
                total_num_tries            object
                created_date       datetime64[ns]
        """
        df = self.__make_sanitized_wordle_df__()
        df.wordle_id = pd.to_numeric(df.wordle_id)
        df = df.loc[wordle_id == df.wordle_id]
        percent_of_winners = df.won_on_try_num.notna().mean()
        avg_turn_won = df.won_on_try_num.mean()
        if top:
            df = df.nlargest(top, 'won_on_try_num')

        df = df.sort_values(["won_on_try_num", "created_date"], ascending=[True, True])
        df = df.reset_index(drop=True)
        return wordle_id, avg_turn_won, percent_of_winners, df

    def compute_daily_df(self, top: int = None):
        """
        :returns:
            wordle id
            avg attempts for wins
            avg of people who won
            pandas.DataFrame with columns: *sorted
                player_id                  object
                wordle_id                  int64
                won_on_try_num            float64
                total_num_tries            object
                created_date       datetime64[ns]
        """
        df = self.__make_sanitized_wordle_df__()
        df = df.loc[(date.today() == df['created_date'].dt.date)]
        df.wordle_id = pd.to_numeric(df.wordle_id)
        wid = df.wordle_id.value_counts().idxmax()
        percent_of_winners = df.won_on_try_num.notna().mean()
        df.won_on_try_num = pd.to_numeric(df.won_on_try_num)
        avg_turn_won = df.won_on_try_num.mean()
        if top:
            df = df.nlargest(top, 'won_on_try_num')
        df = df.sort_values(["won_on_try_num", "created_date"], ascending=[True, True])
        df = df.reset_index(drop=True)
        return wid, avg_turn_won, percent_of_winners, df

    def draw_activity(self) -> io.BytesIO:
        """
        :return: io.BytesIO of the image drawn
        """
        import matplotlib.pyplot as plt
        plt.style.use("seaborn")

        df = self.__make_sanitized_wordle_df__()
        data = df.created_date.dt.date.value_counts()
        _ = data.plot(x='Regional indicator', y='Ladder score')
        plt.xticks(rotation=90)

        data_stream = io.BytesIO()
        plt.savefig(data_stream, format='png', bbox_inches="tight", dpi=80)
        plt.close()
        data_stream.seek(0)
        return data_stream
