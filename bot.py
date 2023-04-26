import discord
from discord.ext import commands
import tokens
import random
import sqlite3
from aiolimiter import AsyncLimiter

# intents contain info on what the bot can interact with.
# the bot can see message content, servers, and server members
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# set up command prefix and authorization for bot
client = commands.Bot(command_prefix='!h ', intents=intents)

rate_limiter = AsyncLimiter(5, 10)

DISCORD_EMOJIS = {"😀", "😁", "😂", "🤣", "😃", "😄", "😅", "😆", "😉", "😊", "😋", "😎", "😍", "😘", "😗", "😙", "😚", "🙂", "🤗", "🤔", "😐", "😑", "😶", "🙄", "😏", "😣", "😥", "😮", "🤐", "😯", "😪", "😫", "😴", "😌", "🤓", "😛", "😜", "😝", "🤤", "😒", "😓", "😔", "😕", "🙃", "🤑", "😲", "☹️", "🙁", "😖", "😞", "😟", "😤", "😢", "😭", "😦", "😧", "😨", "😩", "🤯", "😬", "😰", "😱", "😳", "🤪", "😵", "😡", "😠", "🤬", "😷", "🤒", "🤕", "🤢", "🤮", "🤧", "😇", "🤠", "🤥", "🤫", "🤭", "🧐", "🤯", "🤪", "🤩", "🤗", "🤔", "🤨", "🤫", "🤭", "🤐", "🤑", "🤢", "🤮", "🤧", "🥵", "🥶", "🥴", "😱", "🤪", "🤩", "🥳", "🤠", "😈", "👿", "👹", "👺", "💩", "👻", "💀", "☠️", "👽", "👾", "🤖", "🎃", "😺", "😸", "😹", "😻", "😼", "😽", "🙀", "😿", "😾", "👋", "🤚", "🖐️", "✋", "🖖", "👌", "🤏", "✌️", "🤞", "🤟", "🤘", "🤙", "👈", "👉", "👆", "🖕", "👇", "☝️", "👍", "👎", "✊", "👊", "🤛", "🤜", "👏", "🙌", "👐", "🤲", "🤝", "🙏", "✍️", "💅", "🤳", "💪"}


def generate_alias(emoji_list: list):

    return random.choice(emoji_list)


database = sqlite3.connect("hushBot.db")

cursor = database.cursor()


async def get_alias(senderID: int, recipientID: int) -> str :
    # check if the user has messaged the target before.
    cursor.execute("SELECT * FROM messages WHERE senderID=? AND recipientID = ? LIMIT 1",
                   (senderID, recipientID))
    record = cursor.fetchone()
    print(record)

    # if yes, get the alias they had before
    if record:
        return record[3]
    else:
        cursor.execute("SELECT senderAlias FROM messages WHERE recipientID = ?", (recipientID, ))
        used_aliases = set(cursor.fetchall())
        print(used_aliases)
        new_alias = generate_alias(list(DISCORD_EMOJIS - used_aliases))
        return new_alias


async def get_user_id_by_name_and_discriminator(client: object, username: str, discriminator: str) -> int:
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
                description="Syntax: !h message <discord username> <4-digit discriminator> <message content>")
async def message(ctx: str, username: str, discriminator: str, *, message: str):

    recipientID = await get_user_id_by_name_and_discriminator(client, username, discriminator)
    recipient = await client.fetch_user(recipientID)
    senderID = ctx.author.id

    if recipient is None:
        await ctx.send("User not found")
    else:
        senderAlias = await get_alias(senderID, recipientID)

        embed = discord.Embed(title=f"You have an incoming correspondence from {senderAlias}:\n\n{message}", description="To reply to this message, use the `!h r` command")

        # store message object in variable, so we can take its ID
        message = await recipient.send(embed=embed)
        await ctx.send(f"Message sent to {recipient.name}#{recipient.discriminator}")
        print(f"Message sent to {recipient.name}#{recipient.discriminator}")
        # Store the last user ID for the sender, I.E. whoever called the `message` command

        # create variable to add to SQL INSERT statement
        messageID = message.id
        cursor.execute("INSERT INTO messages (messageID,senderID,recipientID,senderAlias) VALUES(?,?,?,?)", (messageID,senderID,recipientID,str(senderAlias)))

        database.commit()


@client.command(brief="Sends a response to the last message received from the bot",
                description="Must be used after receiving a message from the `message` command."
                            " \n Syntax: !h r <message content>")
async def r(ctx: str, alias: str, *, message: str):
    senderID = ctx.author.id

    if alias is None:
        cursor.execute("SELECT * FROM messages WHERE recipientID = ? LIMIT 1", (senderID,))
        record = cursor.fetchone()

    else:

        print(alias)
        cursor.execute("SELECT * FROM messages WHERE recipientID=? AND senderAlias=? LIMIT 1", (senderID, alias))
        record = cursor.fetchone()
        print(record)

    if record:

        recipientID = record[1]
        print(recipientID)

        # find the original message sender's user object
        bot_user = await client.fetch_user(recipientID)

        senderAlias = await get_alias(senderID, recipientID)

        embed = discord.Embed(title=f"Incoming response from {senderAlias}\n\n{message}", description="To reply to this message, use the `!h r` command")
        # alert the original sender of incoming replies
        message = await bot_user.send(embed=embed)

        # alert replier
        await ctx.send("Response sent")
        print("Response sent")

        messageID = message.id
        cursor.execute("INSERT INTO messages (messageID, senderID, recipientID, senderAlias) VALUES(?, ?, ?, ?)", (messageID, senderID, recipientID, senderAlias))
        database.commit()
    else:
        await ctx.send("No message to respond to")


@client.command(brief="delete the most recent message sent by the bot to a private message recipient")
async def delete(ctx: str, alias: str):

    senderID = ctx.author.id

    if alias is None:
         # find the most recent bot message in the user's dm and delete it
        async for msg in ctx.channel.history():
            if msg.author == client.user:
                await rate_limiter.acquire()
                await msg.delete(delay=0)
                print("successful deletion")
                break
    else:
        cursor.execute("SELECT senderID FROM messages WHERE recipientID = ? AND senderAlias = ? LIMIT 1", (senderID, alias))
        recipientID = cursor.fetchone()[0]
        print(recipientID)
        if recipientID is None:
            await ctx.send("User not found")
        else:
            # check that there is a message in the database from you to the recipient
            cursor.execute("SELECT messageID FROM messages WHERE senderID = ? AND recipientID = ? LIMIT 1", (senderID, recipientID))
            record = cursor.fetchone()

            recipient = await client.fetch_user(recipientID)
            print(recipient.name)
            if record:
                print(f"record found: {record}")
                print(record[0])
                messageID = record[0]
                if recipient.dm_channel is not None:
                    print("dm channel found")

                    # look through user's message history with the bot
                    async for msg in recipient.dm_channel.history():

                        print("looking for messages")
                        # delete the most recent bot message
                        if msg.id == messageID:
                            print("found message!")
                            print(messageID)
                            # delete the message from the DM channel
                            await rate_limiter.acquire()
                            await msg.delete(delay=0)
                            print("deleted message from dm")
                            # delete the message from the database
                            cursor.execute("DELETE FROM messages WHERE messageID = ?", (messageID,))
                            print('deleted message from DB')
                            break
                else:
                    await client.create_dm(recipient)
                    print("created dm with user")
                    async for msg in recipient.dm_channel.history():
                        print("looking for messages")
                        # delete the most recent bot message
                        if msg.id == messageID:
                            print("found message")
                            print(messageID)
                            # delete the message from the DM channel
                            await rate_limiter.acquire()
                            await msg.delete(delay=0)
                            print("deleting message from DM channel")
                            # delete the message from the database
                            cursor.execute("DELETE FROM messages WHERE messageID = ?", (messageID,))


                            print('successfully deleted message from db')
                            break

                database.commit()
                print("committed changes")
            else:
                await ctx.send("Cannot delete messages if you haven't sent any to that user")


@client.command(brief="delete all messages from the bot in your DM")
async def delete_all(ctx: str, alias: str = None):

    if alias is None:
        async for msg in ctx.channel.history():
            if msg.author == client.user:
                await rate_limiter.acquire()
                await msg.delete(delay=0)
                print("successful deletion")
        print("Deletion completed")

    
    else:
        senderID = ctx.author.id
        # find the ID of the user you want to delete messages you sent to
        cursor.execute("SELECT senderID FROM messages WHERE recipientID = ? AND senderAlias = ? LIMIT 1", (senderID, alias))
        recipientID = cursor.fetchone()[0]

        if recipientID is None:
            await ctx.send("User not found")
        else:
            # check that there is a message in the database from you to the recipient
            cursor.execute("SELECT messageID FROM messages WHERE senderID = ? AND recipientID = ?", (senderID, recipientID))

            records = cursor.fetchall()
            recipient = await client.fetch_user(recipientID)

            if records:
                print("records exist")
                for record in records:
                    messageID = record[0]
                    if recipient.dm_channel is not None:
                        print("dm channel exists")

                        # look through user's message history with the bot
                        async for msg in recipient.dm_channel.history():
                            print("looking for messages")

                            if msg.id == messageID:

                                print("messageID found in record")

                                # delete the message from the DM channel
                                await msg.delete(delay=0)
                                print("deleted message")

                                # delete the message from the database
                                cursor.execute("DELETE FROM messages WHERE messageID =?", (messageID,))

                                print('deleting message from db')
                    else:
                        await client.create_dm(recipient)

                        print("dm channel exists")
                        # look through user's message history with the bot
                        async for msg in recipient.dm_channel.history():
                            print("looking for messages")

                            if msg.id == messageID:
                                print("messageID found in record")

                                # delete the message from the DM channel
                                await msg.delete(delay=0)
                                print("deleted message")

                                # delete the message from the database
                                cursor.execute("DELETE FROM messages WHERE messageID = ?", (messageID,))

                                print('deleting message from db')
                    database.commit()
                await ctx.send(f"All messages to {alias} have been deleted")

            else:
               await ctx.send("Cannot delete messages if you haven't sent any to that user")

# provide a token for the bot you are running
client.run(tokens.TOKEN)

# commit to database and end stream
database.commit()
cursor.close()