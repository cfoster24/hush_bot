import discord
from discord.ext import commands

def run_discord_bot():
    TOKEN = "MTA4NjUwMjA4MDI5NTk5NzQ0MA.G_UR5J.N0_Oem2zd_emcDx5BS8whKjvUHvvsS3Uen_h0g"

    intents = discord.Intents.default()
    intents.message_content = True
    client = commands.Bot(command_prefix='Hush: ', intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')

    @client.command(brief="Say hello and I'll say hi back!", pass_context=True)
    async def hello(ctx):
        await ctx.send("Hello, I am a bot")

    sender = None

    @client.command(brief="Sends a private message to a user of your choice", pass_context=True)
    async def message(ctx, user: discord.User, *, message=None):
        global sender

        message = message
        embed = discord.Embed(title=message)


        await ctx.author.send(f'Your message has been sent to {user}')
        await user.send(f'You have an incoming correspondance from an anonymous messager: \n\n', embed=embed)
        sender = ctx.author

    @client.command()
    async def respond(ctx, *, message=None):
        global sender
        message = message
        embed = discord.Embed(title=message)

        if sender == None:
            await ctx.author.send('Sorry, an error has occured')
        else:

            await ctx.author.send('Your response has been sent!')
            await sender.send(f'You have an incoming reply from your message recipient: \n\n', embed=embed)
            sender = ctx.author

    client.run(TOKEN)