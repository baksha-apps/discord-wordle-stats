import os
import random
import time

import discord
from dotenv import dotenv_values

from ui import make_leaderboard_embed, make_wordle_day_embed
from wordle import is_wordle_share, find_try_ratio, WordleStatistics, find_wordle_id

config = dotenv_values(".env")

# Timezone config injection
# set new timezone - defaults to EST, but configurable
os.environ['TZ'] = config.get('TZ_CONFIG') if config.get('TZ_CONFIG') else 'US/Eastern'
time.tzset()

# TESTING PURPOSES: Allows you to specify a channel id to get input data from,
# but only responds to incoming command channel. OPTIONAL.
REDIRECT_CHANNEL = int(config.get('REDIRECTED_INPUT_CHANNEL')) if config.get('REDIRECTED_INPUT_CHANNEL') else None

# Custom VARS for custom situational logic. Does not affect using this bot in other servers.
WORDLE_DAILY_CHANNEL = 937390252576886845
MAIN_CHANNEL = 731718737694162977


class WordleClient(discord.Client):

    def __init__(self, *, loop=None, **options):
        super().__init__(loop=loop, **options)
        self.channel_states = dict()  # <channel_id str: WordleHistoryState>

    async def __channel_import__(self, channel_id: int, import_amount: int = 3000):
        """
        Imports last 1k messages into the bot state.
        There is additional custom logic for my personal server if the conditions are met.
        """
        channel = self.get_channel(channel_id)
        self.channel_states[channel_id] = WordleStatistics()
        messages = await channel.history(limit=import_amount).flatten()
        for message in messages:
            if message.author.bot is True:
                continue
            await self.__add_to_state__(message)

        # Custom logic for "ToG" Server
        # We have the first few wordle sessions in the main channel,
        # so we want to port it over to the wordle channel board instead.
        if channel_id == WORDLE_DAILY_CHANNEL:
            channel = self.get_channel(MAIN_CHANNEL)
            messages = await channel.history(limit=import_amount).flatten()
            for message in messages:
                await self.__add_to_state__(message, WORDLE_DAILY_CHANNEL)

    async def __add_to_state__(self,
                               message: discord.Message,
                               override_leaderboard_id: int = None,
                               is_repliable: bool = False):
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

        self.channel_states[channel_id].add_wordle(player_id=str(message.author),
                                                   wordle_id=wordle_id,
                                                   won_on_try_num=won_on_try,
                                                   total_num_tries=max_tries,
                                                   created_date=message.created_at)

        if is_repliable:

            compliments = [
                "nice one",
                "that's what we like to see",
                "alright mr dictionary",
                "well done",
                "round of applause for this guy",
                "congratulations"
            ]
            soft_insults = [
                "you've done better",
                "are you new here",
                "mediocrity",
                "ok",
                f"{won_on_try} attempts.... ok..",
            ]
            hard_insults = [
                "why did you post this here?",
                "i too do not have eyes",
                "with a score like that, just know that participation matters",
                "honestly just start cheating",
                "use `$today` to see the answer since you clearly did not",
                "https://www.dictionary.com/"
            ]

            if not won_on_try:
                await message.channel.send(f"{message.author.mention} {random.choice(hard_insults)}")
            elif won_on_try <= 4:
                await message.channel.send(f"{message.author.mention} {random.choice(compliments)}")
            else:
                await message.channel.send(f"{message.author.mention} {random.choice(soft_insults)}")


            difference = self.channel_states[channel_id].find_latest_rank_change(str(message.author))
            if difference:
                positive_reactions = ["AYOOOO", "YURRRRR", "LETS GOOOOO", "LOOK @YOU", "WATCH THIS"]
                negative_reactions = ["oh no", "sadly", "ain't no way", "sheesh...", "its not the best...",
                                      "english not ur best"]
                positive_emojis = ["📈", "🆙", "<:dhands:741347089568759829>", "<:thonking:600922118972112896>"]
                negative_emojis = ["🔻", "<:damn:800218841547931700>", "<:yikes:939003738197205042>"]
                reaction_for_change = random.choice(positive_reactions if difference > 0 else negative_reactions)
                emoji_for_change = random.choice(positive_emojis if difference > 0 else negative_emojis)

                await message.channel.send(
                    f"{emoji_for_change} {reaction_for_change} {emoji_for_change}\n"
                    f"{'+' if difference > 0 else ''}{difference} leaderboard rank\n"
                    f"{message.author.mention}"
                )

    async def on_ready(self):
        print('We have logged in as {0.user}'.format(self))

    async def on_message(self, message):
        if message.author.bot:
            return

        if message.content == '$shutdown':
            await message.channel.send('Goodbye!')
            exit(0)

        if message.content.startswith('$hello'):
            await message.channel.send('Hello!\n v1.0.1 \nBetter Wordle Bot says hello!')
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
            embed = make_leaderboard_embed(all_stats_df)
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
            embed = make_wordle_day_embed(wid, avg_turn_won, percent_of_winners, df)
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
            embed = make_wordle_day_embed(wid, avg_turn_won, percent_of_winners, df)
            await message.channel.send(embed=embed)
            return

        if message.content.startswith('$help'):
            await message.channel.send(
                'If this is an emergency, please dial 911. \n'
                'Supported commands: `$today`,`$leaderboard`, `$wordle <id>`, `$hello`, `$help`'
            )
            return

        if message.content.startswith('$time'):
            await message.channel.send(f"**Time:** {time.strftime('%l:%M%p %Z on %b %d, %Y')}")
            return

        # Process these messages so we don't need to recalculate everything again.
        await self.__add_to_state__(message, is_repliable=True)


client = WordleClient()
client.run(config["BOT_TOKEN"])
