import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import asyncio 
import aiofiles #AI said this is better for async file operations
import csv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}")

#Detect if a user sends a message with the word "shit"
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "shit" in message.content.lower():
        await message.delete()
        await message.channel.send(f"That's not a nice word! Please refrain from using offensive language.")
        #await message.author.send(f"Your message was deleted because it contained inappropriate language: {message.content}")

    await bot.process_commands(message)

# Command to create a Student Info Poll
# List of schools (customize this list)
SCHOOLS = ["SMK Subang Utama", "SMK USJ12", "SMK Seafield", "SMK Chong Hwa"]
STATES = ["Selangor", "Kuala Lumpur", "Penang", "Johor", "Sabah", "Sarawak", "Melaka", "Negeri Sembilan", "Perak", "Pahang", "Terengganu", "Kelantan", "Perlis", "Kedah"]

#Student Info command
@bot.command()
async def studentInfo(ctx):
    # School selection
    # Build poll message with emojis
    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]  # Supports up to 4 schools
    description = "\n".join([f"{emojis[i]} - {SCHOOLS[i]}" for i in range(len(SCHOOLS))])
    poll_msg = await ctx.author.send(
        f"**Which school are you from?**\n\n{description}\n\nReact with the corresponding emoji."
    )

    # Add reaction options
    for i in range(len(SCHOOLS)):
        await poll_msg.add_reaction(emojis[i])

    def check(reaction, user):
        return (
            user == ctx.author
            and str(reaction.emoji) in emojis
            and reaction.message.id == poll_msg.id
        )

    try:
        # Wait for reaction (60s timeout)

        reaction, user = await bot.wait_for('reaction_add', timeout=60, check=check)
        selected_index = emojis.index(str(reaction.emoji))
        selected_school = SCHOOLS[selected_index]

        await ctx.author.send(f"✅ Thanks! You selected **{selected_school}**.")

        # Gender selection
        gender_msg = await ctx.author.send("Please select your gender:\n1️⃣ Male\n2️⃣ Female")
        await gender_msg.add_reaction("1️⃣")
        await gender_msg.add_reaction("2️⃣")

        def check_gender(reaction, user):
            return (
                user == ctx.author
                and str(reaction.emoji) in ["1️⃣", "2️⃣"]
                and reaction.message.id == gender_msg.id
            )

        reaction , user = await bot.wait_for('reaction_add', timeout=60, check=check_gender)
        if str(reaction.emoji) == "1️⃣":
            selected_gender = "Male"
        else:
            selected_gender = "Female"
        await ctx.author.send(f"✅ You selected **{selected_gender}**.")

        # State selection
        # Use regional indicator emojis for A-Z (up to 26 states)
        indicator_emojis = [chr(0x1F1E6 + i) for i in range(len(STATES))]  # 🇦 to 🇿

        state_options = "\n".join([f"{indicator_emojis[i]} {state}" for i, state in enumerate(STATES)])
        state_msg = await ctx.author.send("Please select your state:\n" + state_options)
        for emoji in indicator_emojis:
            await state_msg.add_reaction(emoji)

        def check_state(reaction, user):
            return (
            user == ctx.author
            and str(reaction.emoji) in indicator_emojis
            and reaction.message.id == state_msg.id
            )

        reaction, user = await bot.wait_for('reaction_add', timeout=60, check=check_state)
        selected_index = indicator_emojis.index(str(reaction.emoji))
        selected_state = STATES[selected_index]
        await ctx.author.send(f"✅ You selected **{selected_state}**.")
        # Save asynchronously

        async with aiofiles.open('Student_data.csv', mode='a', newline='', encoding='utf-8') as file:
            row = f"{user.name},{user.id},{selected_school},{selected_gender},{selected_state}\n"
            await file.write(row)


    except asyncio.TimeoutError:
        await ctx.author.send('⏳ You didn\'t react in time! type "!studentInfo" to try again.')

# Retrieve the last two messages sent in the channel by anyone (excluding the bot)
@bot.command()
async def retrieve(ctx):
    messages = []
    async for message in ctx.channel.history(limit=10):
        if message.author != bot.user:
            messages.append(message)
        if len(messages) == 2:
            break
    if messages:
        for msg in reversed(messages):
            await ctx.send(f"Message from {msg.author.name}: {msg.content}")
    else:
        await ctx.send("No previous messages found.")

# Retrieve the number of reactions on a specific message by message ID, and identify the users who reacted and how many reactions each user placed
# Also, save the message ID and number of reactions per user in Student_data.csv
@bot.command()
async def retrieve_reactions(ctx, message_id: int):
    try:
        message = await ctx.channel.fetch_message(message_id)
    except discord.NotFound:
        await ctx.send("Message not found.")
        return
    except discord.Forbidden:
        await ctx.send("I don't have permission to fetch that message.")
        return
    except discord.HTTPException:
        await ctx.send("Failed to fetch the message due to an HTTP error.")
        return

    reaction_count = sum(reaction.count for reaction in message.reactions)
    await ctx.send(f"Message ID {message_id} has {reaction_count} reactions.")

    user_reaction_counts = {}
    for reaction in message.reactions:
        async for user in reaction.users():
            if user == bot.user:
                continue
            user_reaction_counts[user] = user_reaction_counts.get(user, 0) + 1

    if user_reaction_counts:
        details = "\n".join(f"{user.name}: {count} reaction(s)" for user, count in user_reaction_counts.items())
        await ctx.send(f"Users who reacted:\n{details}")

        # Read all lines, update the user's line, and write back
        async with aiofiles.open('Student_data.csv', mode='r', encoding='utf-8') as file:
            lines = await file.readlines()

        updated_lines = []
        for line in lines:
            parts = line.strip().split(',')
            if len(parts) < 2:
                updated_lines.append(line)
                continue
            username, userid = parts[0], parts[1]
            # Check if this user reacted
            user_obj = next((u for u in user_reaction_counts if str(u.id) == userid), None)
            if user_obj:
                # Append message_id and reaction count
                new_line = line.strip() + f",message_id:{message_id},reactions:{user_reaction_counts[user_obj]}\n"
                updated_lines.append(new_line)
            else:
                updated_lines.append(line)

        async with aiofiles.open('Student_data.csv', mode='w', encoding='utf-8') as file:
            await file.writelines(updated_lines)
    else:
        await ctx.send("No users reacted to this message.")



bot.run(token, log_handler=handler, log_level=logging.DEBUG)
