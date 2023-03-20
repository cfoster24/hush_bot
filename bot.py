import discord
from discord.ext import commands
import tokens

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
client = commands.Bot(command_prefix='Hush: ', intents=intents)

last_user_id = {}
async def get_user_id_by_name_and_discriminator(client, username: str, discriminator: str) -> int:
    for guild in client.guilds:
        member = discord.utils.get(guild.members, name=username, discriminator=discriminator)
        if member:
            return member.id
    return None
@client.event
async def on_ready():
    print(f'{client.user} is now running!')

@client.command(brief="Sends a private message to a user of your choice")
async def message(ctx, username: str, discriminator: str, *, message=None):
    id = await get_user_id_by_name_and_discriminator(client, username, discriminator)
    user = await client.fetch_user(id)

    if user is None:
        await ctx.send("User not found")
    else:
        embed = discord.Embed(title=message)
        await user.send(f'You have an incoming correspondence from an anonymous messager: \n\n', embed=embed)
        await ctx.send(f"Message sent to {user.name}#{user.discriminator}")

        # Store the last user ID for the sender
        last_user_id[user.id] = ctx.author.id

@client.command(brief="Sends a response to the last message received from the bot")
async def respond(ctx, *, message=None):
    if ctx.author.id not in last_user_id:
        await ctx.send("No message to respond to")
    else:
        bot_user = await client.fetch_user(last_user_id[ctx.author.id])
        if bot_user.dm_channel is None:
            await bot_user.create_dm()
        await bot_user.dm_channel.send("Incoming Reply:\n", embed= discord.Embed(title=message))
        await ctx.send("Message sent to bot owner")

        #store the responder's ID in the recipient's last_user_id dict
        last_user_id[bot_user.id] = ctx.author.id


client.run(tokens.TOKEN)