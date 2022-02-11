from dotenv import load_dotenv, dotenv_values
import discord
import pandas
from pyparsing import line
from wordle import is_wordle_share, find_try_ratio, WordleHistoryState
config = dotenv_values(".env")


class WordleClient(discord.Client):

    async def __channel_import__(self, id: str):
        channel = self.get_channel(id)
        messages = await channel.history(limit=1000).flatten()
        print('messages len', len(messages))
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
        print(self.leaderboards[id])

    def __make_leaderboard_embed__(self, title: str, df: pandas.DataFrame):

        embed = discord.Embed(title=f"__**{title}:**__", color=0x03f8fc)
        for index, row in df.iterrows():
            print(index, row)
            embed.add_field(name=f'**{index + 1}) {row.player_id}**',
                            value=f'Total Games: {row.total_games}\n> Averaging: {row.avg_won_on_attempt}/6 \n> Win %: {row.win_percent}\n> Started: {row.started_date}', inline=False)
        return embed

    async def on_ready(self):
        print('We have logged in as {0.user}'.format(client))
        self.leaderboards = dict()  # <channel_id: WordleHistoryState>

    async def on_message(self, message):

        if message.content == '$shutdown':  # and message.author.display_name == 'Goose':
            exit(0)

        if message.content == '$leaderboard':
            if message.channel.id not in self.leaderboards:
                await self.__channel_import__(message.channel.id)
            all_stats_df = self.leaderboards.get(
                message.channel.id).create_all_stats_df()
            embed = self.__make_leaderboard_embed__("Leaderboard", all_stats_df)
            # await message.channel.send(embed=embed)
            return

        if message.content.startswith('$hello'):
            await message.channel.send('Hello!\n v0.0.1 \nBetter Worlde Bot says hello!!')

        # store new wordles so we don't need to import again
        if message.author.bot is False and is_wordle_share(message.content):
            lines = message.content.split('\n')
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
