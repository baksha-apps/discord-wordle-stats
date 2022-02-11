from dotenv import load_dotenv, dotenv_values
import discord
import pandas
from pyparsing import line
from wordle import is_wordle_share, find_try_ratio, WordleHistoryState

config = dotenv_values(".env")

# Custom VARS for custom situational logic. Does not affect using this bot in other servers.
WORDLE_DAILY_CHANNEL = 937390252576886845
MAIN_CHANNEL = 731718737694162977

class WordleClient(discord.Client):

    async def __channel_import__(self, id: str):
        '''
        Imports last 1k messages into the bot state. 
        There is additional custom logic for my personal server if the conditions are met. 
        '''
        channel = self.get_channel(id)
        messages = await channel.history(limit=1000).flatten()
        self.leaderboards[id] = WordleHistoryState()
        for message in messages:
            if message.author.bot is True:
                continue
            self.__proccess_message__(message)

        # Custom logic for "ToG" Server
        # We have the first few wordle sessions in the main channel, so we want to port it over to the wordle channel board instead.
        if id == WORDLE_DAILY_CHANNEL:
            channel = self.get_channel(MAIN_CHANNEL)
            messages = await channel.history(limit=1000).flatten()
            for message in messages:
                self.__proccess_message__(message, WORDLE_DAILY_CHANNEL)

    def __proccess_message__(self, message: discord.Message, overrided_leaderboard_id: str = None):
        """
        Process message from anywhere and add it to the state of the bot.

        :param discord.Message message: 
            Message being sent. It automatically adds the Wordle Game to the the channel's leaderboard.
        :param str overrided_leaderboard_id: 
            Instead of adding this message to the original channel's leaderboard, you may override it to another board.
            This functionality is built-in for consolidating leaderboards from multiple channels into just one. (if needed)
        """
        message_content = message.content.strip()
        if message.author.bot is True or not is_wordle_share(message_content):
            return
        lines = message_content.split('\n')
        wordle_id = int(str(lines[0][7:10]))
        won_on_try, max_tries = find_try_ratio(lines[0])
        id = overrided_leaderboard_id if overrided_leaderboard_id else message.channel.id
        self.leaderboards[id].add_wordle(player_id=message.author.display_name,
                                         wordle_id=wordle_id,
                                         won_on_try_num=won_on_try,
                                         total_num_tries=max_tries,
                                         created_date=message.created_at)

    def __make_leaderboard_embed__(self, title: str, df: pandas.DataFrame):
        embed = discord.Embed(title=f"__**{title}:**__", color=0x03f8fc)
        for index, row in df.iterrows():
            embed.add_field(name=f'**{index + 1}) {row.player_id}**',
                            value=f'Total Games: {row.total_games}\n> Averaging: {row.avg_won_on_attempt}/6 \n> Win %: {row.win_percent}\n> Started: {row.started_date}',
                            inline=False)
        return embed

    async def on_ready(self):
        print('We have logged in as {0.user}'.format(client))
        self.leaderboards = dict()  # <channel_id str: WordleHistoryState>

    async def on_message(self, message):
        if message.author.bot: return
        if message.content == '$shutdown': exit(0)


        if message.content.startswith('$hello'):
            await message.channel.send('Hello!\n v0.0.2 \nBetter Wordle Bot says hello!')
            return

        if message.content == '$leaderboard':
            channel_for_leaderboard = message.channel.id
            # channel_for_leaderboard = WORDLE_DAILY_CHANNEL
            if channel_for_leaderboard not in self.leaderboards:
                await self.__channel_import__(channel_for_leaderboard)
            all_stats_df = self.leaderboards.get(
                channel_for_leaderboard).create_all_stats_df()
            embed = self.__make_leaderboard_embed__(
                "Leaderboard", all_stats_df)
            await message.channel.send(embed=embed)
            return

        if message.content.startswith('$help'):
            await message.channel.send('If this is an emergency, please dial 911. \nSupported commands: `$leaderboard`, `$hello`, `$help`')
            return

        # Process these messages so we don't need to recalculate everything again.
        self.__proccess_message__(message)


client = WordleClient()
client.run(config["BOT_TOKEN"])
