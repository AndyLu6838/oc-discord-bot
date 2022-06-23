# code a discord bot that can get images from the user
# and save them to a folder


# import the discord.py module
import asyncio
import datetime
from collections import OrderedDict
from dotenv import load_dotenv
from os import getenv
import discord

load_dotenv()

client = discord.Client()
TOKEN: str = getenv("TOKEN")
MOD_CHANNEL_ID = int(getenv("MOD_CHANNEL_ID"))
MODERATOR_ID = int(getenv("MODERATOR_ID"))
PREFIX: str = "!"
TIMEOUT = 60  # seconds

# dictionary of all bot commands
commands: dict[str, str] = {
    'hello': 'say hello to the bot',
    'about': 'about the bot',
    'help': 'display this menu',
    'testmint': 'test mint',
    'modconfirm': 'confirm an image request',

}

mint_info = OrderedDict()


# print message in console when bot is ready
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    print(f"Bot started at {datetime.datetime.now()}")


# message events
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith(PREFIX):
        command: str = message.content.strip().split()[0][1:]
        if command == 'hello':
            await test(message)

        elif command == 'about':
            await message.channel.send('This is a bot that can get images from the user and save them to a folder.')

        elif command == 'testmint':
            await parse_message(message)

        # elif command == 'confirm':
        #     if message.author in mint_info:
        #         print(mint_info[message.author])
        #         mod_channel = discord.utils.get(client.get_all_channels(), id=MOD_CHANNEL_ID)
        #         await message.channel.send('success')
        #         await mod_channel.send(f"<@&{MODERATOR_ID}>\n" + message.author.mention + " has submitted a new image.")
        #     else:
        #         await message.channel.send('Please input info first')

        elif command == "modconfirm":
            if message.channel.id == MOD_CHANNEL_ID:
                if mint_info:
                    # get the key for current image being confirmed
                    current = list(mint_info.keys())[0]
                    (name, description, url) = mint_info[current]
                    queue_str = f"""The next image in the queue is:\n"
                    Name: {name}\n
                    Description: {description}\n
                    URL: {url}\n
                    Submitted by: <@{current.id}>\n
                    Does this look good? Type !confirm to confirm your selection (10 mins)"""
                    await message.channel.send(queue_str)

                    def check(m):
                        return m.content in [PREFIX + 'confirm', PREFIX + 'deny'] and m.channel == message.channel and \
                               m.author == message.author

                    try:
                        msg = await client.wait_for('message', timeout=600, check=check)
                    except asyncio.TimeoutError:
                        await message.channel.send("You waited too long, request denied")
                    else:
                        if msg.content == PREFIX + 'confirm':
                            await message.channel.send("mod confirm")
                            del mint_info[current]
                        else:
                            await message.channel.send("mod deny")
                            del mint_info[current]

                else:
                    await message.channel.send("The image queue is empty!")


        # use dictionary to print help menu
        elif command == 'help':
            help_str = "```+\n"
            for command_name in sorted(commands.keys()):
                help_str += PREFIX + command_name + " - " + commands[command_name].capitalize() + "\n"
            help_str += "```"
            await message.channel.send(help_str)


async def test(message):
    await message.channel.send(message.content)


# get image name, description and URL
async def parse_message(message):
    message.content = message.content.strip()
    message.content = message.content.replace("\n", " ")
    # get the message content
    name = ""
    description = ""
    url = ""
    name_prefix = "name:"
    description_prefix = "description:"
    error = ""
    # get the name of the image
    # for word in message.content.split(" "):
    #     name_prefix = "name:"
    #     if word.startswith(name_prefix):
    #         name = word[len(name_prefix):]
    # # get the description of the image
    # for word in message.content.split(" "):
    #     description_prefix = "description:"
    #     if word.startswith(description_prefix):
    #         description = word[len(description_prefix):]

    try:
        name_index = message.content.lower().index(name_prefix)
    except ValueError:
        name_index = -1
    try:
        description_index = message.content.lower().index(description_prefix)
    except ValueError:
        description_index = -1

    if name_index != -1:
        name = message.content[name_index + len(name_prefix):description_index].strip()
    else:
        error += "You have not inputted a name.\n"
    if description_index != -1:
        description = message.content[description_index + len(description_prefix) + 1:].strip()
    else:
        error += "You have not inputted a description.\n"

    # get the url
    if len(message.attachments) == 1:
        url = message.attachments[0].url.strip()
    elif len(message.attachments) > 1:
        error += 'Please only upload one image.\n'
    else:
        error += 'Please upload an image.\n'

    statement = ""
    if len(name) == 0 or len(description) == 0 or len(url) == 0:
        error += "Please try inputting all information again."
    else:
        statement = "Name: " + name + "\nDescription: " + description + "\nURL: " + url
        statement += f"\nDoes this look good? Type !confirm to confirm your selection ({TIMEOUT} seconds)."
    if error != "":
        await message.channel.send(error)
    else:
        await message.channel.send(statement)

        def check(m):
            return m.content == PREFIX + 'confirm' and m.channel == message.channel and m.author == message.author

        try:
            msg = await client.wait_for('message', timeout=TIMEOUT, check=check)
        except asyncio.TimeoutError:
            await message.channel.send('You waited too long')
        else:
            mod_channel = discord.utils.get(client.get_all_channels(), id=MOD_CHANNEL_ID)
            await msg.channel.send('success')
            await mod_channel.send(f"<@&{MODERATOR_ID}>\n" + msg.author.mention + " has submitted a new image.")
            mint_info[msg.author] = (name, description, url)


client.run(TOKEN)
