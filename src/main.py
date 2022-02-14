from datetime import datetime
from dotenv import dotenv_values
import discord
import pandas
import humanize
from wordle import is_wordle_share, find_try_ratio, WordleHistoryState, find_wordle_id, find_solution
import os, time
config = dotenv_values(".env")

# Custom VARS for custom situational logic. Does not affect using this bot in other servers.
WORDLE_DAILY_CHANNEL = 937390252576886845
MAIN_CHANNEL = 731718737694162977

# TESTING PURPOSES: Allows you to specify a channel id to get input data from,
# but only responds to incoming command channel. OPTIONAL.
REDIRECT_CHANNEL = None
if config.get('REDIRECTED_INPUT_CHANNEL'):
    REDIRECT_CHANNEL = int(config.get('REDIRECTED_INPUT_CHANNEL'))


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
    embed = discord.Embed(title=f"__**{title}:**__", color=discord.Color.from_rgb(204, 0, 0))
    for index, row in df.iterrows():
        embed.add_field(name=f'**{index + 1}) {row.player_id}**',
                        value=
                        f'Total Games: `{row.total_games}`\n'
                        f'> Since: `{row.started_date.strftime("%m/%d/%Y").strip()}`\n'
                        f'> Averaging: `{row.avg_won_on_attempt}/6`\n'
                        f'> Win %: `{row.win_percent}`\n',
                        inline=True)
    return embed


def __make_wordle_day_embed__(wid: int, avg_turn_won: float, percent_of_winners: float, df: pandas.DataFrame):
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

    async def __add_to_state__(self, message: discord.Message, override_leaderboard_id: int = None, should_send_rank = False):
        """
        Process message from anywhere and add it to the state of the bot.

        :param discord.Message message: 
            - Message being sent.
            - Adds the Wordle Game to the the channel's state.
        :param str override_leaderboard_id: 
            Instead of adding this message to the original channel's leader-board, you may override it to another board.
            This functionality is built-in for consolidating leader-boards from multiple channels into just one.
            (if needed)
        """
        channel_id = override_leaderboard_id if override_leaderboard_id else message.channel.id
        message_content = message.content.strip()
        if message.author.bot is True or not is_wordle_share(message_content):
            return
        # if we're processing a message and we haven't imported that data yet, let's import it here.
        # typically, we only add to state (memory) on demand to lower cpu/mem usage.
        # but we should make an adjustment on this case.
        if channel_id not in self.channel_states:
            await self.__channel_import__(channel_id)
        header = message_content.split('\n')[0]
        wordle_id = find_wordle_id(header)
        won_on_try, max_tries = find_try_ratio(header)
        ############### cheesy, very unoptimized way check to see if we went up/down in rank
        cached_pre_play_df = self.channel_states[channel_id].compute_all_stats_df()
        ################################

        self.channel_states[channel_id].add_wordle(player_id=str(message.author),
                                                   wordle_id=wordle_id,
                                                   won_on_try_num=won_on_try,
                                                   total_num_tries=max_tries,
                                                   created_date=message.created_at)

        ############### cheesy, very unoptimized way check to see if we went up/down in rank
        if should_send_rank:
            pre_add_ranks = list(cached_pre_play_df.player_id)
            pre_play_player_rank = pre_add_ranks.index(str(message.author))
            post_add_ranks = list(self.channel_states[channel_id].compute_all_stats_df().player_id)
            post_play_player_rank = post_add_ranks.index(str(message.author))

            difference = abs(pre_play_player_rank - post_play_player_rank)
            if post_play_player_rank < pre_play_player_rank:
                await message.channel.send(f"📈 Look at you... 🆙 {str(message.author)} 🆙 +{difference} leaderboard rank")
            elif post_play_player_rank > pre_play_player_rank:
                await message.channel.send(f"Oh no... 🔻 {str(message.author)} 🔻 -{difference} leaderboard rank")
            # else:
                # await message.channel.send(f"No ranking change... {str(message.author)}, {pre_play_player_rank} > {post_play_player_rank} ")
        ###########################

    async def on_ready(self):
        print('We have logged in as {0.user}'.format(self))
        os.environ['TZ'] = 'US/Eastern'  # set new timezone
        time.tzset()

    async def on_message(self, message):
        if message.author.bot:
            return

        if message.content == '$shutdown':
            await message.channel.send('Goodbye!')
            exit(0)

        if message.content.startswith('$hello'):
            await message.channel.send('Hello!\n v1.0.0 \nBetter Wordle Bot says hello!')
            return

        if message.content == '$reset':
            await self.__channel_import__(message.channel.id)
            await message.channel.send('The wordle bot has reset the state.')
            return

        if message.content == '$leaderboard':
            channel_id = message.channel.id \
                if not REDIRECT_CHANNEL \
                else REDIRECT_CHANNEL
            if channel_id not in self.channel_states:
                await self.__channel_import__(channel_id)
            all_stats_df = self \
                .channel_states \
                .get(channel_id) \
                .compute_all_stats_df()
            embed = __make_leaderboard_embed__("All-time Leaderboard",
                                               all_stats_df)
            await message.channel.send(embed=embed)
            return

        if message.content == '$today':
            channel_id = message.channel.id \
                if not REDIRECT_CHANNEL \
                else REDIRECT_CHANNEL
            if channel_id not in self.channel_states:
                await self.__channel_import__(channel_id)
            wid, avg_turn_won, percent_of_winners, df = self \
                .channel_states \
                .get(channel_id) \
                .compute_daily_df()
            embed = __make_wordle_day_embed__(wid, avg_turn_won, percent_of_winners, df)
            await message.channel.send(embed=embed)
            return

        if message.content.startswith('$wordle'):
            channel_id = message.channel.id \
                if not REDIRECT_CHANNEL \
                else REDIRECT_CHANNEL
            wordle_id = int(message.content.split(" ")[1])
            if channel_id not in self.channel_states:
                await self.__channel_import__(channel_id)
            wid, avg_turn_won, percent_of_winners, df = self \
                .channel_states \
                .get(channel_id) \
                .compute_day_df_for_wordle(wordle_id)
            embed = __make_wordle_day_embed__(wid, avg_turn_won, percent_of_winners, df)
            await message.channel.send(embed=embed)
            return

        if message.content.startswith('$help'):
            await message.channel.send(
                'If this is an emergency, please dial 911. \n'
                'Supported commands: `$today`,`$leaderboard`, `$wordle <id>`, `$hello`, `$help`'
            )
            return

        if message.content.startswith('$time'):
            if os.environ.get('TZ') == 'US/Eastern':
                await message.channel.send(f"TZ is EST > {time.strftime('%l:%M%p %Z on %b %d, %Y')}")
                return
            before = time.strftime('%l:%M%p %Z on %b %d, %Y')
            os.environ['TZ'] = 'US/Eastern'  # set new timezone
            time.tzset()
            after = time.strftime('%l:%M%p %Z on %b %d, %Y')
            await message.channel.send(f"TZ: {before} -> {after}")  # before timezone change
            return

        # Process these messages so we don't need to recalculate everything again.
        await self.__add_to_state__(message, should_send_rank=True)


client = WordleClient()
client.run(config["BOT_TOKEN"])
