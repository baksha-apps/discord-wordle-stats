from dotenv import load_dotenv, dotenv_values
import discord
import pandas
from pyparsing import line
from wordle import is_wordle_share, find_try_ratio, WordleHistoryState
config = dotenv_values(".env")

WORDLE_DAILY_CHANNEL = 937390252576886845
MAIN_CHANNEL = 731718737694162977

class WordleClient(discord.Client):

    async def __channel_import__(self, id: str):
        channel = self.get_channel(id)
        messages = await channel.history(limit=1000).flatten()
        self.leaderboards[id] = WordleHistoryState()
        for message in messages:
            message_content = message.content.strip()
            if message.author.bot is True:
                continue

            if is_wordle_share(message_content):
                lines = message_content.split('\n')
                wordle_id = int(str(lines[0][7:10]))
                won_on_try, max_tries = find_try_ratio(
                    lines[0])  # just give header
                self.leaderboards[id].add_wordle(player_id=message.author.display_name,
                                                 wordle_id=wordle_id,
                                                 won_on_try_num=won_on_try,
                                                 total_num_tries=max_tries,
                                                 created_date=message.created_at)
        # special logic for my server -
        # if this is the wordle channel, let's also import main channel wordle games for same leaderboard
        if id == WORDLE_DAILY_CHANNEL:
            # import main
            channel = self.get_channel(MAIN_CHANNEL)
            messages = await channel.history(limit=1000).flatten()
            for message in messages:
                message_content = message.content.strip()
                if message.author.bot is True:
                    continue

                if is_wordle_share(message_content):
                    lines = message_content.split('\n')
                    wordle_id = int(str(lines[0][7:10]))
                    won_on_try, max_tries = find_try_ratio(lines[0])  # param is header of share
                    self.leaderboards[WORDLE_DAILY_CHANNEL].add_wordle(player_id=message.author.display_name,
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
        if message.author.bot:
            return

        if message.content == '$shutdown':
            exit(0)

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

        if message.content.startswith('$hello'):
            await message.channel.send('Hello!\n v0.0.1 \nBetter Worlde Bot says hello!!')
        
        if message.content.startswith('$help'):
            await message.channel.send('If this is an emergency, please dial 911. \nSupported commands: `$leaderboard`')

        # store new wordles so we don't need to import again 
        # TODO: Not working... 
        if is_wordle_share(message.content.strip()):
            message_content = message.content.strip()
            lines = message_content.split('\n')
            wordle_id = int(str(lines[0][7:10]))
            won_on_try, max_tries = find_try_ratio(
                lines[0])  # just give header
            self.leaderboards[id].add_wordle(player_id=message.author.display_name,
                                                wordle_id=wordle_id,
                                                won_on_try_num=won_on_try,
                                                total_num_tries=max_tries,
                                                created_date=message.created_at)


client = WordleClient()
client.run(config["BOT_TOKEN"])
