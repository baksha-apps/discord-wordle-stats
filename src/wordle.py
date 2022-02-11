import re
import pandas as pd
import datetime
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
        self.world_df = pd.DataFrame(columns=[
                                     'player_id',  # str
                                     'wordle_id',  # int
                                     'won_on_try_num',  # optional<int>
                                     'total_num_tries',  # int
                                     'created_date'])  # int

    def add_wordle(self, player_id: str, wordle_id: int, won_on_try_num: int, total_num_tries: int, created_date: datetime.datetime):
        self.world_df = self.world_df.append({'player_id': player_id,
                                              'wordle_id': wordle_id,
                                              'won_on_try_num': won_on_try_num,
                                              'total_num_tries': total_num_tries,
                                              'created_date': created_date},
                                             ignore_index=True)

    def create_all_stats_df(self):  # wordle df
        wordle_df = self.world_df
        allstatsdf = pd.DataFrame()
        allstatsdf["total_games"] = wordle_df.groupby(
            wordle_df.player_id).size()
        allstatsdf["avg_won_on_attempt"] = wordle_df.groupby(
            wordle_df.player_id).won_on_try_num.mean()
        allstatsdf['win_percent'] = (wordle_df[wordle_df['won_on_try_num'].notna()].groupby(
            wordle_df.player_id).size() / wordle_df.groupby(wordle_df.player_id).size()) * 100
        allstatsdf['started_date'] = wordle_df.groupby(
            wordle_df.player_id).created_date.min()
        return allstatsdf.sort_values(["total_games", "win_percent", "avg_won_on_attempt", "started_date"],
                                      ascending=(False, False, True, True)).reset_index()
