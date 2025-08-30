import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import re
import datetime
import pytz
import csv

malaysia_time = datetime.datetime.now(pytz.timezone("Asia/Kuala_Lumpur"))

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Enable members intent

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


STANDARD_COLUMNS = ['Message Sent At', 'Message ID', 'Channel ID', 'Member ID', 'Username', 'Member Roles', 'Row Created At', 'Content']

# -----------------------Collect AI Diffusion member pings-------------------------
k=227
@bot.command()
async def Data_Art(ctx):
    messages = []
    async for msg in ctx.channel.history(limit=k):
        messages.append(msg)
    messages = [m for m in messages if m.id != ctx.message.id][:k]

    rows = []
    for msg in messages:
        match = re.search(r"<@(\d+)>", msg.content)
        member_id = match.group(1) if match else None
        if member_id:
            member = ctx.guild.get_member(int(member_id))
            if not member:
                try:
                    member = await ctx.guild.fetch_member(int(member_id))
                except discord.NotFound:
                    member = None
            username = member.name if member else "Unknown"
            member_roles = [role.name for role in member.roles if role.name != "@everyone"] if member else ["Unknown"]
            row = [
                msg.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                msg.id,
                msg.channel.id if msg.channel else None,
                member_id,
                username,
                member_roles,
                malaysia_time.strftime('%Y-%m-%d %H:%M:%S'),
                "AI Generated Image prompted by this user"
            ]
            rows.append(row)

    with open('1a_engage_diffusion.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(STANDARD_COLUMNS)
        writer.writerows(rows)

    await ctx.send(f"Fetched previous {k} messages and saved to 1a_engage_diffusion.csv. Check console for details.")

#----------------------------------Collect messages from module 4-------------------------------------------------------------------------------

n=50
@bot.command()
async def Data_mod_4(ctx):
    # Fetch the last n messages before the command message
    messages = []
    async for msg in ctx.channel.history(limit=n):  # includes the command message
        messages.append(msg)
    messages = [m for m in messages if m.id != ctx.message.id][:n]  # exclude command message

    rows = []
    for msg in messages:
        member = ctx.guild.get_member(msg.author.id)
        if not member:
            try:
                member = await ctx.guild.fetch_member(msg.author.id)
            except discord.NotFound:
                member = None
        username = member.name if member else str(msg.author)
        member_roles = [role.name for role in member.roles if role.name != "@everyone"] if member else ["Unknown"]
        row = [
            msg.created_at.strftime('%Y-%m-%d %H:%M:%S'), #Time of message creation
            msg.id,
            msg.channel.id if msg.channel else None,
            msg.author.id,
            username,
            member_roles,
            malaysia_time.strftime('%Y-%m-%d %H:%M:%S'),
            msg.content
        ]
        rows.append(row)

    # Write to CSV (append mode)
    file_exists = os.path.isfile('Module_4.csv')
    with open('Module_4.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        if not file_exists or os.path.getsize('Module_4.csv') == 0:
            writer.writerow(STANDARD_COLUMNS)
        writer.writerows(rows)

    await ctx.send(f"Fetched previous {n} messages and saved to Module_4.csv. Check console for details.")

#-----------------------------------------Collect Reactions-------------------------------------

@bot.command()
async def collect_reactions(ctx, channel_id: int, message_id: int):
    channel = bot.get_channel(channel_id)
    if not channel:
        await ctx.send("Channel not found.")
        return

    try:
        message = await channel.fetch_message(message_id)
    except discord.NotFound:
        await ctx.send("Message not found.")
        return

    rows = []
    for reaction in message.reactions:
        async for user in reaction.users():
            member = ctx.guild.get_member(user.id)
            if not member:
                try:
                    member = await ctx.guild.fetch_member(user.id)
                except discord.NotFound:
                    member = None
            username = member.name if member else user.name
            user_roles = [role.name for role in member.roles if role.name != "@everyone"] if member else ["Unknown"]
            row = [
                "N/A",  # Message Sent At not available for reactions
                message_id,
                channel_id,
                user.id,
                username,
                user_roles,
                malaysia_time.strftime('%Y-%m-%d %H:%M:%S'),
                f"Reaction by user: {str(reaction.emoji)}"
            ]
            rows.append(row)

    # Save to CSV in append mode
    file_exists = os.path.isfile('reactions.csv')
    with open('reactions.csv', 'a', newline='', encoding='utf-8') as csvfile: 
        writer = csv.writer(csvfile)
        if not file_exists or os.path.getsize('reactions.csv') == 0:
            writer.writerow(STANDARD_COLUMNS)
        writer.writerows(rows)

    await ctx.send(f"Reactions for message {message_id} saved to reactions.csv.")

#--------------------------------------Collect General--------------------------------------------

x=3000
@bot.command()
async def collect_general(ctx):
    # Fetch the last x messages before the command message
    messages = []
    async for msg in ctx.channel.history(limit=x):  # includes the command message
        messages.append(msg)
    messages = [m for m in messages if m.id != ctx.message.id][:x]  # exclude command message

    rows = []
    for msg in messages:
        if msg.author.name == "AI Image Generator": #Dealing with AI Image Generator messages #Oh this should be under the for loop 
            match = re.search(r"<@(\d+)>", msg.content)
            member_id = match.group(1) if match else None
            member = None
            username = "Unknown"
            member_roles = ["Unknown"]
            if member_id:
                member = ctx.guild.get_member(int(member_id))
                if not member:
                    try:
                        member = await ctx.guild.fetch_member(int(member_id))
                    except discord.NotFound:
                        member = None
                username = member.name if member else "Unknown"
                member_roles = [role.name for role in member.roles if role.name != "@everyone"] if member else ["Unknown"]
            row = [
                msg.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                msg.id,
                msg.channel.id if msg.channel else None,
                member_id if member_id else "Unknown",
                username,
                member_roles,
                malaysia_time.strftime('%Y-%m-%d %H:%M:%S'),
                "AI Generated Image prompted by this user"
            ]
            rows.append(row)
        elif (msg.content == ""):
            pass
        else:  # Normal messages
            member = ctx.guild.get_member(msg.author.id)
            if not member:
                try:
                    member = await ctx.guild.fetch_member(msg.author.id)
                except discord.NotFound:
                    member = None
            username = member.name if member else str(msg.author)
            member_roles = [role.name for role in member.roles if role.name != "@everyone"] if member else ["Unknown"]
            row = [
                msg.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                msg.id,
                msg.channel.id if msg.channel else None,
                msg.author.id,
                username,
                member_roles,
                malaysia_time.strftime('%Y-%m-%d %H:%M:%S'),
                msg.content
            ]
            rows.append(row)
    
    # Write to CSV (append mode)
    file_exists = os.path.isfile('General.csv')
    with open('General.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        if not file_exists or os.path.getsize('General.csv') == 0:
            writer.writerow(STANDARD_COLUMNS)
        writer.writerows(rows)

    await ctx.send(f"Fetched previous {x} messages and saved to General.csv. Check console for details.")

#=====================================get member join method =================================================

'''
Invite method tracked by invite tracker bot:
Content of message 1410592121278300282:
Sent At: 2025-08-28 11:49:29
Channel ID: 1389347115469242532
Member ID: 720351927581278219
Username: Invite Tracker
Member Roles: ['Invite Tracker']
Content: @LEONG SIN LOONG (1347760985271963791) has joined the server using the invite URL discord.gg/a4h3Pxuk. This invite code has been used 4 times.

Execution steps: 
1) Get the member ID, username, time of joining, roles, row created at
2) get the invite code
3) Save to CSV
'''
v=700
@bot.command()
async def join_method(ctx):
    messages = []
    async for msg in ctx.channel.history(limit=v):
        messages.append(msg)
    messages = [m for m in messages if m.id != ctx.message.id][:v]

    rows = []
    for msg in messages:
        # Example content:
        # @LEONG SIN LOONG (1347760985271963791) has joined the server using the invite URL discord.gg/a4h3Pxuk. This invite code has been used 4 times.
        join_match = re.search(r"\((\d+)\).*invite URL discord\.gg/([A-Za-z0-9]+)\.", msg.content)
        if join_match:
            joined_member_id = join_match.group(1)
            invite_code = join_match.group(2)  # Only the code after the /
            member = ctx.guild.get_member(int(joined_member_id))
            if not member:
                try:
                    member = await ctx.guild.fetch_member(int(joined_member_id))
                except discord.NotFound:
                    member = None
            username = member.name if member else "Unknown"
            member_roles = [role.name for role in member.roles if role.name != "@everyone"] if member else ["Unknown"]
            row = [
                msg.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                msg.id,
                msg.channel.id if msg.channel else None,
                joined_member_id,
                username,
                member_roles,
                malaysia_time.strftime('%Y-%m-%d %H:%M:%S'),
                invite_code
            ]
            rows.append(row)

    with open('join_method.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Member joined at","Message ID","Channel ID", "Member ID", "Username", "Member Roles", "Row Created At", "Invite Code"])
        writer.writerows(rows)

    await ctx.send(f"Fetched previous {v} messages and saved to join_method.csv. Check console for details.")



#-------------------------------------get specific message------------------------------------------------------

@bot.command()
async def get_message(ctx, channel_id: int, message_id: int):
    channel = bot.get_channel(channel_id)
    if not channel:
        await ctx.send("Channel not found.")
        return

    try:
        message = await channel.fetch_message(message_id)
    except discord.NotFound:
        await ctx.send("Message not found.")
        return

    member = ctx.guild.get_member(message.author.id)
    if not member:
        try:
            member = await ctx.guild.fetch_member(message.author.id)
        except discord.NotFound:
            member = None
    username = member.name if member else str(message.author)
    member_roles = [role.name for role in member.roles if role.name != "@everyone"] if member else ["Unknown"]

    await ctx.send(
        f"Content of message `{message_id}`:\n"
        f"Sent At: {message.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Channel ID: {message.channel.id if message.channel else None}\n"
        f"Member ID: {message.author.id}\n"
        f"Username: {username}\n"
        f"Member Roles: {member_roles}\n"
        f"Content: {message.content}"
    )


bot.run(token)

