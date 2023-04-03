import discord
from discord.ext import commands
import tokens
import random

# intents contain info on what the bot can interact with.
# the bot can see message content, servers, and server members
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# set up command prefix and authorization for bot
client = commands.Bot(command_prefix='Hush: ', intents=intents)

# dictionary for storing messenger ids
last_user_id = {"default": None}

DISCORD_EMOJIS = ["😀", "😁", "😂", "🤣", "😃", "😄", "😅", "😆", "😉", "😊", "😋", "😎", "😍", "😘", "😗", "😙", "😚", "☺️", "🙂", "🤗", "🤔", "😐", "😑", "😶", "🙄", "😏", "😣", "😥", "😮", "🤐", "😯", "😪", "😫", "😴", "😌", "🤓", "😛", "😜", "😝", "🤤", "😒", "😓", "😔", "😕", "🙃", "🤑", "😲", "☹️", "🙁", "😖", "😞", "😟", "😤", "😢", "😭", "😦", "😧", "😨", "😩", "🤯", "😬", "😰", "😱", "😳", "🤪", "😵", "😡", "😠", "🤬", "😷", "🤒", "🤕", "🤢", "🤮", "🤧", "😇", "🤠", "🤥", "🤫", "🤭", "🧐", "🤯", "🤪", "🤩", "🤗", "🤔", "🤨", "🤫", "🤭", "🤐", "🤑", "🤢", "🤮", "🤧", "🥵", "🥶", "🥴", "😱", "🤪", "🤩", "🥳", "🤠", "😈", "👿", "👹", "👺", "💩", "👻", "💀", "☠️", "👽", "👾", "🤖", "🎃", "😺", "😸", "😹", "😻", "😼", "😽", "🙀", "😿", "😾", "👋", "🤚", "🖐️", "✋", "🖖", "👌", "🤏", "✌️", "🤞", "🤟", "🤘", "🤙", "👈", "👉", "👆", "🖕", "👇", "☝️", "👍", "👎", "✊", "👊", "🤛", "🤜", "👏", "🙌", "👐", "🤲", "🤝", "🙏", "✍️", "💅", "🤳", "💪"]

def generate_alias():


    return random.choice(DISCORD_EMOJIS)



async def get_user_id_by_name_and_discriminator(client, username: str, discriminator: str) -> int:
    # search through all servers the bot is in
    for guild in client.guilds:
        # find a member with matching username and discriminator
        member = discord.utils.get(guild.members, name=username, discriminator=discriminator)

        if member:
            return member.id
    return None


@client.event
async def on_ready():
    print(f'{client.user} is now running!')


@client.command(brief="Sends a private message to a user of your choice",
                description="Syntax: Hush: message <discord username> <4-digit discriminator> <message content>")
async def message(ctx, username: str, discriminator: str, *, message: str):

    id = await get_user_id_by_name_and_discriminator(client, username, discriminator)
    user = await client.fetch_user(id)
    alias = generate_alias()

    if user is None:
        await ctx.send("User not found")
    else:
        embed = discord.Embed(title=f"You have an incoming correspondence from {alias}:\n\n{message}", description="To reply to this message, use the `Hush: respond` command")

        await user.send(embed=embed)
        await ctx.send(f"Message sent to {user.name}#{user.discriminator}")
        # Store the last user ID for the sender, I.E. whoever called the `message` command
        last_user_id[user.id] = ctx.author.id
        print(last_user_id)


@client.command(brief="Sends a response to the last message received from the bot",
                description="Must be used after receiving a message from the `message` command."
                            " \n Syntax: Hush: respond <message content>")
async def respond(ctx, *, message: str):
    if ctx.author.id not in last_user_id:
        # if the person calling the command is not present in any stored user's message history, error
        await ctx.send("No message to respond to")
    else:
        # find the original message sender's user object
        bot_user = await client.fetch_user(last_user_id[ctx.author.id])

        # if there is no DM open with the bot user, create one
        if bot_user.dm_channel is None:
            await bot_user.create_dm()

        alias = generate_alias()
        embed = discord.Embed(title=f"Incoming response from {alias}\n\n{message}", description="To reply to this message, use the `Hush: respond` command")
        # alert the original sender of incoming replies
        await bot_user.dm_channel.send(embed=embed)

        # alert replier
        await ctx.send("Response sent")

        # store the responder's ID in the recipient's last_user_id dict
        last_user_id[bot_user.id] = ctx.author.id
        print(last_user_id)

@client.command(brief="delete the most recent message sent by the bot in your DM")
async def delete(ctx):
    async for msg in ctx.channel.history():
        if msg.author == client.user:
            await msg.delete()
            break

@client.command(brief="delete the most recent message sent by the bot to a private message recipient")
async def oDelete(ctx, username: str, discriminator: str):
    id = await get_user_id_by_name_and_discriminator(client, username, discriminator)
    user = await client.fetch_user(id)

    if user is None:
        await ctx.send("User not found")
    else:
        if user.id not in last_user_id:
            await ctx.send("Cannot delete messages if you haven't sent any to that user")
        else:
            async for msg in user.dm_channel.history():
                if msg.author == client.user:
                    await msg.delete()
                    break

@client.command(brief="delete all messages from the bot in your DM")
async def delete_all(ctx):
    messages = await ctx.dm_channel.history(limit=None).flatten()

    for message in messages:
        if message.author == client.user:
            await message.delete()



# provide a token for the bot you are running
client.run(tokens.TOKEN)
