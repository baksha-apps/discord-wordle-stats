import pandas
import discord
import humanize
from datetime import datetime
from wordle import find_solution


def make_leaderboard_embed(df: pandas.DataFrame):
    """
    :param: df: pandas.DataFrame
        Requires DataFrame with the following dtypes
            player_id                     object
            total_games                    int64
            avg_won_on_attempt           float64
            win_percent                  float64
            started_date          datetime64[ns]
    """
    embed = discord.Embed(title=f"__**All-time Leaderboard:**__", color=discord.Color.from_rgb(204, 0, 0))
    for index, row in df.iterrows():
        embed.add_field(name=f'**{index + 1}) {row.player_id}**',
                        value=
                        f'Total Games: `{row.total_games}`\n'
                        f'> Since: `{row.started_date.strftime("%m/%d/%Y").strip()}`\n'
                        f'> Averaging: `{row.avg_won_on_attempt}/6`\n'
                        f'> Win %: `{row.win_percent}`\n',
                        inline=True)
    return embed


def make_wordle_day_embed(wid: int, avg_turn_won: float, percent_of_winners: float, df: pandas.DataFrame):
    """
    :param: df pandas.DataFrame
    with columns: *sorted
        player_id                  object
        wordle_id                  object
        won_on_try_num            float64
        total_num_tries            object
        created_date       datetime64[ns]
    """
    embed = discord.Embed(title=f"__**Wordle {wid}:**__", color=discord.Color.from_rgb(255, 255, 0))
    last_day_for_wid = None  # should probably be part of the input ui for SoC, but too lazy.
    # better practice would be to utilize ui models, but maybe that's too much for python
    for index, row in df.iterrows():
        embed.add_field(name=f'**{index + 1}) {row.player_id}**',
                        value=f'> `{row.won_on_try_num}/6`\n' +
                              (f'> *{humanize.naturaltime(row.created_date)}*'
                               if row.created_date.date() == datetime.now().date()
                               else f"> *{row.created_date.strftime('%-I:%M%p')}*"),
                        inline=True)
        last_day_for_wid = row.created_date
    embed.add_field(name=f'__**Overall Daily Statistics**__',
                    value=f'<:thonking:726838160809787464>',
                    inline=False)
    embed.add_field(name=f"How many won?",
                    value=f"> `{percent_of_winners * 100}`%")
    embed.add_field(name=f"Average Attempts",
                    value=f"> `{avg_turn_won}`")
    embed.add_field(name=f"Solution:",
                    value=f"> ||{find_solution(wid=wid).upper()}||")
    embed.set_footer(text=f"{last_day_for_wid.strftime('%B %d, %Y')}")
    return embed