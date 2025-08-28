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
            if member:
                member_roles = [role.name for role in member.roles if role.name != "@everyone"] if member else ["Unknown"]
                username = member.name
            else:
                username = "Unknown"
            row = [
                msg.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                member_id,
                username,
                msg.id,
                member_roles if member else ["Unknown"],
                malaysia_time.strftime('%Y-%m-%d %H:%M:%S'),
            ]
            rows.append(row)

    with open('1a_engage_diffusion.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Message Sent At', 'Member ID', 'Username', 'Message ID', 'Member Roles', 'Row Created At'])
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
        member_roles = [role.name for role in member.roles if role.name != "@everyone"] if member else ["Unknown"]
        row = [
            msg.created_at.strftime('%Y-%m-%d %H:%M:%S'), #Time of message creation
            msg.id,
            msg.author.id,
            malaysia_time.strftime('%Y-%m-%d %H:%M:%S'), #Time of row creation
            msg.author,
            msg.channel.id if msg.channel else None, 
            member_roles,
            msg.content
        ]
        rows.append(row)

    # Write to CSV (append mode)
    file_exists = os.path.isfile('Module_4.csv')
    with open('Module_4.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        if not file_exists or os.path.getsize('Module_4.csv') == 0:
            writer.writerow(['Message Sent At', 'Message ID','Member ID', 'Row Created At', 'Author', "Thread ID", 'Member Roles', 'Content'])
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
            user_roles = [role.name for role in member.roles if role.name != "@everyone"] if member else ["Unknown"]
            rows.append([
                message_id,
                channel_id,
                str(reaction.emoji),
                user.id,
                user.name,
                user_roles,
                malaysia_time.strftime('%Y-%m-%d %H:%M:%S')
            ])

    # Save to CSV in append mode
    file_exists = os.path.isfile('reactions.csv')
    with open('reactions.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists or os.path.getsize('reactions.csv') == 0:
            writer.writerow(['Message ID', "Channel ID", 'Emoji', 'User ID', 'Username', 'User Roles','Row Created At'])
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
            if member_id:
                member = ctx.guild.get_member(int(member_id))
                if not member:
                    try:
                        member = await ctx.guild.fetch_member(int(member_id))
                    except discord.NotFound:
                        member = None
                if member:
                    member_roles = [role.name for role in member.roles if role.name != "@everyone"] if member else ["Unknown"]
                    username = member.name
                else:
                    username = "Unknown" 
                row = [ #'Message Sent At', 'Member ID', 'Message ID', 'Row Created At', 'Author', "Thread ID", 'Member Roles', 'Content'
                    msg.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    member_id,
                    msg.id,
                    malaysia_time.strftime('%Y-%m-%d %H:%M:%S'),
                    username,
                    msg.channel.id if msg.channel else None,
                    member_roles if member else ["Unknown"],
                    "AI Generated Image prompted by this user"
                ]
                rows.append(row)
        elif (msg.content == ""):  # Skip empty messages
            pass
        else:  # Normal messages
            member = ctx.guild.get_member(msg.author.id)
            if not member:
                try:
                    member = await ctx.guild.fetch_member(msg.author.id)
                except discord.NotFound:
                    member = None
            member_roles = [role.name for role in member.roles if role.name != "@everyone"] if member else ["Unknown"]
            row = [ #'Message Sent At', 'Member ID', 'Message ID', 'Row Created At', 'Author', "Thread ID", 'Member Roles', 'Content'
                msg.created_at.strftime('%Y-%m-%d %H:%M:%S'), #Time of message creation
                msg.author.id,
                msg.id,
                malaysia_time.strftime('%Y-%m-%d %H:%M:%S'), #Time of row creation
                msg.author,
                msg.channel.id if msg.channel else None, 
                member_roles,
                msg.content
            ]
            rows.append(row)



    
    # Write to CSV (append mode)
    file_exists = os.path.isfile('General.csv')
    with open('General.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        if not file_exists or os.path.getsize('General.csv') == 0:
            writer.writerow(['Message Sent At', 'Member ID', 'Message ID', 'Row Created At', 'Author', "Thread ID", 'Member Roles', 'Content'])
        writer.writerows(rows)

    await ctx.send(f"Fetched previous {x} messages and saved to General.csv. Check console for details.")


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

    await ctx.send(f"Content of message `{message_id}`:\n{message.content}, author: {message.author.name}")


bot.run(token)

