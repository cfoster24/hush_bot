import discord
from discord.ext import commands
import tokens
import random
import sqlite3
import emoji

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

DISCORD_EMOJIS_TEXT = [":smiley:", ":smile:", ":grinning:", ":grin:", ":joy:", ":sweat_smile:", ":rofl:", ":slightly_smiling_face:", ":upside_down_face:", ":wink:", ":smirk:", ":neutral_face:", ":expressionless:", ":unamused:", ":roll_eyes:", ":thinking:", ":flushed:", ":disappointed:", ":worried:", ":angry:", ":rage:", ":pensive:", ":confused:", ":slight_frown:", ":frowning2:", ":persevere:", ":confounded:", ":tired_face:", ":weary:", ":cry:", ":sob:", ":triumph:", ":scream:", ":fearful:", ":cold_sweat:", ":hushed:", ":frowning:", ":anguished:", ":open_mouth:", ":astonished:", ":dizzy_face:", ":zipper_mouth:", ":mask:", ":thermometer_face:", ":head_bandage:", ":sleepy:", ":sleeping:", ":zzz:", ":poop:", ":smiling_imp:", ":imp:", ":japanese_ogre:", ":japanese_goblin:", ":skull:", ":ghost:", ":alien:", ":space_invader:", ":robot:", ":smiley_cat:", ":smile_cat:", ":joy_cat:", ":heart_eyes_cat:", ":smirk_cat:", ":kissing_cat:", ":scream_cat:", ":crying_cat_face:", ":pouting_cat:", ":raised_hands:", ":clap:", ":wave:", ":thumbsup:", ":thumbsdown:", ":punch:", ":fist:", ":v:", ":ok_hand:", ":raised_hand:", ":open_hands:", ":muscle:", ":pray:", ":handshake:", ":point_up:", ":point_down:", ":point_left:", ":point_right:", ":metal:", ":vulcan_salute:", ":writing_hand:", ":nail_care:", ":lips:", ":tongue:", ":ear:", ":nose:", ":eye:", ":eyes:", ":bust_in_silhouette:", ":busts_in_silhouette:", ":speaking_head:", ":baby:", ":child:", ":boy:", ":girl:", ":man:", ":woman:", ":person_frowning:", ":person_with_pouting_face:", ":person_with_headscarf:", ":person_in_tuxedo:", ":man_in_tuxedo:", ":woman_in_tuxedo:", ":person_with_veil:", ":man_with_veil:", ":woman_with_veil:", ":blond_haired_person:", ":blond-haired-man:", ":blond-haired-woman:", ":man_bald:", ":woman_bald:", ":bearded_person:", ":older_adult:", ":older_man:", ":older_woman:", ":man_beard:", ":woman_beard:", ":man_health_worker:", ":woman_health_worker:", ":man_student:", ":woman_student:", ":man_teacher:", ":woman_teacher:", ":man_judge:", ":woman_judge:", ":man_farmer:", ":woman_farmer:", ":man_cook:", ":woman_cook:", ":man_mechanic:", ":woman_mechanic:", ":man_factory_worker:", ":woman_factory_worker:", ":man_office_worker:", ":woman_office_worker:", ":man_scientist:", ":woman_scientist:", ":man_technologist:", ":woman_technologist:", ":man_singer:", ":woman_singer:", ":man_artist:", ":woman_artist:", ":man_pilot:"]

def generate_alias():

    return random.choice(DISCORD_EMOJIS)


database = sqlite3.connect("hushBot.db")

cursor = database.cursor()

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

async def message(ctx: str, username: str, discriminator: str, *, message: str):


    recipientID = await get_user_id_by_name_and_discriminator(client, username, discriminator)
    user = await client.fetch_user(recipientID)
    senderID = ctx.author.id

    if user is None:
        await ctx.send("User not found")
    else:
        cursor.execute("SELECT EXISTS(SELECT 1 FROM messages WHERE senderID=? AND recipientID = ? LIMIT 1)", (senderID, recipientID))
        record = cursor.fetchone()
        if record[0] == 1:
            cursor.execute("SELECT senderAlias FROM messages WHERE senderID=? AND recipientID=? LIMIT 1", (senderID, recipientID))
            senderAlias = cursor.fetchone()[0]
        else:
            print("else")
            senderAlias = generate_alias()


        embed = discord.Embed(title=f"You have an incoming correspondence from {senderAlias}:\n\n{message}", description="To reply to this message, use the `Hush: respond` command")

        message = await user.send(embed=embed)
        await ctx.send(f"Message sent to {user.name}#{user.discriminator}")
        print(f"Message sent to {user.name}#{user.discriminator}")
        # Store the last user ID for the sender, I.E. whoever called the `message` command


        messageID = message.id
        cursor.execute("INSERT INTO messages (messageID,senderID,recipientID,senderAlias) VALUES(?,?,?,?)", (messageID,senderID,recipientID,str(senderAlias)))
        printMSG = cursor.execute("SELECT * FROM messages WHERE messageID = messageID")


        database.commit()


@client.command(brief="Sends a response to the last message received from the bot",
                description="Must be used after receiving a message from the `message` command."
                            " \n Syntax: Hush: respond <message content>")
async def respond(ctx: str, alias: str, *, message: str):
    
    senderID = ctx.author.id


    print(alias)
    cursor.execute("SELECT * FROM messages WHERE recipientID=? AND senderAlias=? LIMIT 1", (senderID, alias))
    record = cursor.fetchone()
    print(record)
    if record:

        recipientID = record[1]
        print(recipientID)

        # find the original message sender's user object
        bot_user = await client.fetch_user(recipientID)

        cursor.execute("SELECT EXISTS(SELECT 1 FROM messages WHERE senderID=? AND recipientID = ? LIMIT 1)",
                       (senderID, recipientID))
        record = cursor.fetchone()
        if record[0] == 1:
            cursor.execute("SELECT senderAlias FROM messages WHERE senderID=? AND recipientID=? LIMIT 1",
                           (senderID, recipientID))
            senderAlias = cursor.fetchone()[0]
        else:
            print("else")
            senderAlias = generate_alias()

        embed = discord.Embed(title=f"Incoming response from {senderAlias}\n\n{message}", description="To reply to this message, use the `Hush: respond` command")
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

@client.command(brief="delete the most recent message sent by the bot in your DM")
async def delete(ctx: str):
    # find the most recent bot message in the user's dm and delete it
    async for msg in ctx.channel.history():
        if msg.author == client.user:
            await msg.delete()
            print("successful deletion")
            break

@client.command(brief="delete the most recent message sent by the bot to a private message recipient")
async def oDelete(ctx: str, username: str, discriminator: str):
    id = await get_user_id_by_name_and_discriminator(client, username, discriminator)
    user = await client.fetch_user(id)

    if user is None:
        await ctx.send("User not found")
    else:
        # check that the user you're trying to delete a message from is in the message cache
        if user.id not in last_user_id:
            await ctx.send("Cannot delete messages if you haven't sent any to that user")
        else:
            # look through user's message history with the bot
            async for msg in user.dm_channel.history():

                # delete the most recent bot message
                if msg.author == client.user:
                    await msg.delete()
                    print('successfully deleted message')
                    break

@client.command(brief="delete all messages from the bot in your DM")
async def delete_all(ctx: str):
    messages = await ctx.dm_channel.history(limit=None).flatten()

    for message in messages:
        if message.author == client.user:
            await message.delete()




# provide a token for the bot you are running
client.run(tokens.TOKEN)

# commit to database and end stream
database.commit()
cursor.close()