import re
import pandas as pd
from datetime import datetime, date


# Helpers


def is_wordle_share(msg: str):
    return re.match('Wordle \d\d\d .\/\d\n\n[⬛⬜🟩🟨]{5}', msg) is not None


def find_try_ratio(wordle_share_msg_header: str):
    '''
    returns: tuple (attempt, of_tries) 
    '''
    header = wordle_share_msg_header
    won_on_try = int(header[-3]) if header[-3].isdigit() else None
    max_attempts = int(header[-1])
    return won_on_try, max_attempts


# State


class WordleHistoryState:

    def __init__(self):
        self.wordle_df = pd.DataFrame(columns=[
            'player_id',  # str
            'wordle_id',  # int
            'won_on_try_num',  # optional<int>
            'total_num_tries',  # int
            'created_date'  # int
        ])

    # TODO: Remove this and just prevent duplicates in add
    def __prepare_for_computation__(self):
        """
        We can lazily prepare for a computation if needed here.
            - Prevents duplicate counts of shares.
                - it would be better if we can just overwrite duplicates on add_wordle()
        """
        self.wordle_df = self.wordle_df.drop_duplicates(subset=['player_id', 'wordle_id'], keep='last')

    def add_wordle(self, player_id: str, wordle_id: int, won_on_try_num: int, total_num_tries: int,
                   created_date: datetime):
        self.wordle_df = self.wordle_df.append({'player_id': player_id,
                                                'wordle_id': wordle_id,
                                                'won_on_try_num': won_on_try_num,
                                                'total_num_tries': total_num_tries,
                                                'created_date': created_date},
                                               ignore_index=True)

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
        self.__prepare_for_computation__()
        wordle_df = self.wordle_df
        all_stats_df = pd.DataFrame()
        groupedby_players = wordle_df.groupby(wordle_df.player_id)
        all_stats_df["total_games"] = groupedby_players.size()
        all_stats_df["avg_won_on_attempt"] = groupedby_players.won_on_try_num.mean()
        all_stats_df['win_percent'] = (wordle_df[wordle_df['won_on_try_num'].notna()].groupby(
            wordle_df.player_id).size() / wordle_df.groupby(wordle_df.player_id).size()) * 100
        all_stats_df['started_date'] = groupedby_players.created_date.min()
        return all_stats_df.sort_values(["avg_won_on_attempt", "win_percent", "started_date"],
                                        ascending=(True, False, True)).round(1).reset_index()

    def compute_daily_df(self, top=None):
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
        self.__prepare_for_computation__()
        df = self.wordle_df
        # maybe we try to reset time zone? - don't know if it is doing anything, too scared to change
        df.created_date = pd\
            .to_datetime(df.created_date, unit='ms')\
            .dt.tz_localize('UTC')\
            .dt.tz_convert('US/Eastern')
        #
        df = df.loc[(date.today() == df['created_date'].dt.date)]
        df.wordle_id = pd.to_numeric(df.wordle_id)
        wid = df.wordle_id.value_counts().idxmax()
        # df = df.loc[(wid == df['wordle_id'])]  # only show the most used wordle id to filter out bad
        percent_of_winners = df.won_on_try_num.notna().mean()
        df.won_on_try_num = pd.to_numeric(df.won_on_try_num)
        avg_turn_won = df.won_on_try_num.mean()
        if top:
            df = df.nlargest(top, 'won_on_try_num')


        df = df.sort_values(["won_on_try_num", "created_date"], ascending=(True, True))
        df = df.reset_index(drop=True)
        return wid, avg_turn_won, percent_of_winners, df
