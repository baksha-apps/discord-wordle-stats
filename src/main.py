from dotenv import dotenv_values
import discord
import pandas
from wordle import is_wordle_share, find_try_ratio, WordleHistoryState

config = dotenv_values(".env")

# Custom VARS for custom situational logic. Does not affect using this bot in other servers.
WORDLE_DAILY_CHANNEL = 937390252576886845
MAIN_CHANNEL = 731718737694162977

TEST_IN_TEST_SV = True

def __make_leaderboard_embed__(title: str, df: pandas.DataFrame):
    """
    :param: df: pandas.DataFrame
        Requires DataFrame with the following dtypes
            player_id                     object
            total_games                    int64
            avg_won_on_attempt           float64
            win_percent                  float64
            started_date          datetime64[ns]
    """
    embed = discord.Embed(title=f"__**{title}:**__", color=0x03f8fc)
    for index, row in df.iterrows():
        embed.add_field(name=f'**{index + 1}) {row.player_id}**',
                        value=f'Total Games: {row.total_games}\n'
                              f'> Averaging: {row.avg_won_on_attempt}/6\n'
                              f'> Win %: {row.win_percent}\n'
                              f'> Started: {row.started_date}',
                        inline=False)
    return embed


def __make_today_embed__(title: str, avg_turn_won: float, percent_of_winners: float, df: pandas.DataFrame):
    """
    :param: df pandas.DataFrame
    with columns: *sorted
        player_id                  object
        wordle_id                  object
        won_on_try_num            float64
        total_num_tries            object
        created_date       datetime64[ns]
    """
    embed = discord.Embed(title=f"__**{title}:**__", color=0x03f8fc)
    for index, row in df.iterrows():
        embed.add_field(name=f'**{index + 1}) {row.player_id}**',
                        value=f'> {row.won_on_try_num}/6\n'
                              f'> Time: {row.created_date}\n',
                        inline=False)
    embed.add_field(name=f'**Overall Daily Statistics**',
                    value=f'-------------------------',
                    inline=False)
    embed.add_field(name=f"\t Winning Percentage",
                    value= f"{percent_of_winners * 100}%")
    embed.add_field(name=f"\t Avg turn won on: %",
                    value= f"{avg_turn_won}")
    embed.set_footer(text=f"Today was a great day!")
    return embed


class WordleClient(discord.Client):

    def __init__(self, *, loop=None, **options):
        super().__init__(loop=loop, **options)
        self.channel_states = dict()  # <channel_id str: WordleHistoryState>

    async def __channel_import__(self, channel_id: int):
        """
        Imports last 1k messages into the bot state.
        There is additional custom logic for my personal server if the conditions are met.
        """
        channel = self.get_channel(channel_id)
        messages = await channel.history(limit=1000).flatten()
        self.channel_states[channel_id] = WordleHistoryState()
        for message in messages:
            if message.author.bot is True:
                continue
            await self.__add_to_state__(message)

        # Custom logic for "ToG" Server
        # We have the first few wordle sessions in the main channel,
        # so we want to port it over to the wordle channel board instead.
        if channel_id == WORDLE_DAILY_CHANNEL:
            channel = self.get_channel(MAIN_CHANNEL)
            messages = await channel.history(limit=1000).flatten()
            for message in messages:
                await self.__add_to_state__(message, WORDLE_DAILY_CHANNEL)

    async def __add_to_state__(self, message: discord.Message, overrided_leaderboard_id: int = None):
        """
        Process message from anywhere and add it to the state of the bot.

        :param discord.Message message: 
            - Message being sent.
            - Adds the Wordle Game to the the channel's state.
        :param str overrided_leaderboard_id: 
            Instead of adding this message to the original channel's leader-board, you may override it to another board.
            This functionality is built-in for consolidating leader-boards from multiple channels into just one.
            (if needed)
        """
        channel_id = overrided_leaderboard_id if overrided_leaderboard_id else message.channel.id
        message_content = message.content.strip()
        if message.author.bot is True or not is_wordle_share(message_content):
            return
        # if we're processing a message and we haven't imported that data yet, let's import it here.
        # typically, we only add to state (memory) on demand to lower cpu/mem usage.
        # but we should make an adjustment on this case.
        if channel_id not in self.channel_states:
            await self.__channel_import__(channel_id)
        lines = message_content.split('\n')
        wordle_id = int(str(lines[0][7:10]))
        won_on_try, max_tries = find_try_ratio(lines[0])
        self.channel_states[channel_id].add_wordle(player_id=message.author.display_name,
                                                   wordle_id=wordle_id,
                                                   won_on_try_num=won_on_try,
                                                   total_num_tries=max_tries,
                                                   created_date=message.created_at)

    async def on_ready(self):
        print('We have logged in as {0.user}'.format(self))

    async def on_message(self, message):
        if message.author.bot:
            return

        if message.content == '$shutdown':
            exit(0)

        if message.content.startswith('$hello'):
            await message.channel.send('Hello!\n v0.0.2 \nBetter Wordle Bot says hello!')
            return

        if message.content == '$restart-state':
            await self.__channel_import__(message.channel.id)
            await message.channel.send('The wordle bot has restarted.')

        if message.content == '$leaderboard':
            channel_id = message.channel.id if not TEST_IN_TEST_SV else WORDLE_DAILY_CHANNEL
            if channel_id not in self.channel_states:
                await self.__channel_import__(channel_id)
            all_stats_df = self.channel_states.get(
                channel_id
            ).compute_all_stats_df()
            embed = __make_leaderboard_embed__(
                "Leaderboard", all_stats_df)
            await message.channel.send(embed=embed)
            return

        if message.content == '$today':
            channel_id = message.channel.id if not TEST_IN_TEST_SV else WORDLE_DAILY_CHANNEL
            if channel_id not in self.channel_states:
                await self.__channel_import__(channel_id)
            wid, avg_turn_won, percent_of_winners, df = self.channel_states.get(
                channel_id
            ).compute_daily_df()
            embed = __make_today_embed__(f"Wordle {wid}", avg_turn_won, percent_of_winners, df)
            await message.channel.send(embed=embed)
            return

        if message.content.startswith('$help'):
            await message.channel.send(
                'If this is an emergency, please dial 911. \nSupported commands: `$leaderboard`, `$hello`, `$help`')
            return

        # Process these messages so we don't need to recalculate everything again.
        await self.__add_to_state__(message)


client = WordleClient()
client.run(config["BOT_TOKEN"])
