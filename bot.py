import discord
from discord.ext import commands
import json
import random
import time
import os

# ----------------------------
# TOKEN FROM ENVIRONMENT
# ----------------------------
TOKEN = os.getenv("TOKEN")
if TOKEN is None:
    print("❌ TOKEN NOT FOUND!")
    print("Add DISCORD_BOT_TOKEN in Railway Environment Variables")
    exit()

# ----------------------------
# BOT SETUP
# ----------------------------
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

INR_IMAGE = "https://i.imgur.com/3Z6pFJQ.png"

# ----------------------------
# DATABASE SYSTEM
# ----------------------------
def load_data():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_data():
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

users = load_data()

def get_user(uid):
    if str(uid) not in users:
        users[str(uid)] = {
            "balance": 0,
            "last_daily": 0
        }
    return users[str(uid)]

# ----------------------------
# EMBED HELPER
# ----------------------------
def make_embed(title, desc, color):
    embed = discord.Embed(title=title, description=desc, color=color)
    embed.set_thumbnail(url=INR_IMAGE)
    embed.set_footer(text="₹ INR Economy Bot")
    return embed

# ----------------------------
# BOT EVENTS
# ----------------------------
@bot.event
async def on_ready():
    print("✅ Bot Online:", bot.user)

# ----------------------------
# COMMANDS
# ----------------------------

# BALANCE
@bot.command()
async def balance(ctx):
    user = get_user(ctx.author.id)
    bal = user["balance"]

    embed = make_embed(
        "💰 Wallet Balance",
        f"**{ctx.author.name}**, you have:\n\n### ₹{bal} INR",
        discord.Color.green()
    )
    await ctx.send(embed=embed)

# DAILY with 24h Cooldown
@bot.command()
async def daily(ctx):
    user = get_user(ctx.author.id)
    now = time.time()
    cooldown = 86400  # 24 hours

    if now - user["last_daily"] < cooldown:
        remaining = int(cooldown - (now - user["last_daily"]))
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60

        embed = make_embed(
            "⏳ Daily Cooldown",
            f"Come back in **{hours}h {minutes}m** for your next daily cash!",
            discord.Color.red()
        )
        return await ctx.send(embed=embed)

    reward = random.randint(300, 800)
    user["balance"] += reward
    user["last_daily"] = now
    save_data()

    embed = make_embed(
        "🎁 Daily Cash Claimed!",
        f"You received:\n\n### ₹{reward} INR",
        discord.Color.gold()
    )
    await ctx.send(embed=embed)

# HUNT
@bot.command()
async def hunt(ctx):
    user = get_user(ctx.author.id)

    reward = random.randint(50, 300)
    user["balance"] += reward
    save_data()

    animals = ["🐇 rabbit", "🦌 deer", "🐅 tiger", "🐓 chicken"]

    embed = make_embed(
        "🏹 Hunt Successful!",
        f"You hunted a **{random.choice(animals)}**\nEarned: **₹{reward} INR**",
        discord.Color.orange()
    )
    await ctx.send(embed=embed)

# GAMBLE
@bot.command()
async def gamble(ctx, amount: int):
    user = get_user(ctx.author.id)

    if amount <= 0:
        return await ctx.send("❌ Enter a valid amount!")
    if user["balance"] < amount:
        return await ctx.send("❌ Not enough money!")

    win = random.choice([True, False])
    if win:
        user["balance"] += amount
        result = f"🎉 You WON!\nYou gained **₹{amount} INR**"
        color = discord.Color.green()
    else:
        user["balance"] -= amount
        result = f"💀 You LOST!\nYou lost **₹{amount} INR**"
        color = discord.Color.red()

    save_data()
    embed = make_embed("🎰 Gamble Result", result, color)
    await ctx.send(embed=embed)

# COINFLIP
@bot.command()
async def coinflip(ctx, amount: int, choice: str):
    user = get_user(ctx.author.id)
    if user["balance"] < amount:
        return await ctx.send("❌ Not enough money!")

    flip = random.choice(["heads", "tails"])
    if choice.lower() == flip:
        user["balance"] += amount
        msg = f"🪙 It was **{flip}**!\nYou won **₹{amount} INR**"
        color = discord.Color.green()
    else:
        user["balance"] -= amount
        msg = f"🪙 It was **{flip}**!\nYou lost **₹{amount} INR**"
        color = discord.Color.red()

    save_data()
    embed = make_embed("🪙 Coinflip", msg, color)
    await ctx.send(embed=embed)

# LOOTBOX
@bot.command()
async def lootbox(ctx):
    user = get_user(ctx.author.id)
    reward = random.randint(200, 1500)
    user["balance"] += reward
    save_data()

    embed = make_embed(
        "📦 Lootbox Opened!",
        f"You found treasure inside!\n\n### ₹{reward} INR",
        discord.Color.purple()
    )
    await ctx.send(embed=embed)

# TOP LEADERBOARD
@bot.command()
async def top(ctx):
    sorted_users = sorted(users.items(), key=lambda x: x[1]["balance"], reverse=True)
    leaderboard = ""
    for i, (uid, data) in enumerate(sorted_users[:5], start=1):
        user_obj = await bot.fetch_user(int(uid))
        leaderboard += f"**{i}. {user_obj.name}** — ₹{data['balance']} INR\n"

    embed = make_embed(
        "🏆 Top Richest Users",
        leaderboard,
        discord.Color.blue()
    )
    await ctx.send(embed=embed)

# ----------------------------
# RUN BOT
# ----------------------------
bot.run(TOKEN)