import discord
from wordle import is_wordle_share, find_wordle_id, find_try_ratio, WordleHistoryState
from dotenv import dotenv_values
from asyncio import run

config = dotenv_values(".env")
client = discord.Client()

WORDLE_DAILY_CHANNEL = 937390252576886845


state = WordleHistoryState()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    channel = client.get_channel(WORDLE_DAILY_CHANNEL)
    messages = await (channel.history(limit=1000).flatten())
    for message in messages:
        message_content = message.content.strip()
        if message.author.bot is True or not is_wordle_share(message_content):
            continue

        header = message_content.split('\n')[0]
        wordle_id = find_wordle_id(header)
        won_on_try, max_tries = find_try_ratio(header)
        state.add_wordle(player_id=str(message.author),
                         wordle_id=wordle_id,
                         won_on_try_num=won_on_try,
                         total_num_tries=max_tries,
                         created_date=message.created_at)

    state.__make_sanitized_wordle_df__().to_csv("stubbed_messages.csv")

# client.run(config["BOT_TOKEN"])