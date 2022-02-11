from dotenv import load_dotenv, dotenv_values
import discord

config = dotenv_values(".env")

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!\n v0.0.1 \nBetter Worlde Bot says hello!!')

client.run(config["BOT_TOKEN"])
