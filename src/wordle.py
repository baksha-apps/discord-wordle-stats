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
        self.wordle_df = pd.DataFrame(columns=[
            'player_id',  # str
            'wordle_id',  # int
            'won_on_try_num',  # optional<int>
            'total_num_tries',  # int
            'created_date'])  # int

    def add_wordle(self, player_id: str, wordle_id: int, won_on_try_num: int, total_num_tries: int, created_date: datetime.datetime):
        self.wordle_df = self.wordle_df.append({'player_id': player_id,
                                                'wordle_id': wordle_id,
                                                'won_on_try_num': won_on_try_num,
                                                'total_num_tries': total_num_tries,
                                                'created_date': created_date},
                                               ignore_index=True)

    def create_all_stats_df(self):  #
        allstatsdf = pd.DataFrame()
        groupedby_players = self.wordle_df.groupby(self.wordle_df.player_id)
        wordle_df = self.wordle_df
        allstatsdf["total_games"] = groupedby_players.size()
        allstatsdf["avg_won_on_attempt"] = groupedby_players.won_on_try_num.mean()
        allstatsdf['win_percent'] = (wordle_df[wordle_df['won_on_try_num'].notna()].groupby(
            wordle_df.player_id).size() / wordle_df.groupby(wordle_df.player_id).size()) * 100
        allstatsdf['started_date'] = groupedby_players.created_date.min()
        return allstatsdf.sort_values(["avg_won_on_attempt", "win_percent", "started_date"],
                                      ascending=(True, False, True)).round(1).reset_index()
