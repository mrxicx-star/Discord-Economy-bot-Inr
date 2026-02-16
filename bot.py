import discord
from discord.ext import commands
import json
import random
import time
import os

# ----------------------------
# TOKEN FROM RENDER ENV
# ----------------------------

TOKEN = os.getenv("TOKEN")

if TOKEN is None:
    print("❌ TOKEN NOT FOUND!")
    print("Add TOKEN in Render Environment Variables")
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
    embed.set_footer(text="₹ INR Economy Bot • Made with ❤️")
    return embed

# ----------------------------
# BOT READY
# ----------------------------

@bot.event
async def on_ready():
    print("✅ Bot Online:", bot.user)

# ----------------------------
# HELP COMMAND
# ----------------------------

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="📌 INR Economy Bot Commands",
        description="Welcome! Here are all available commands:\n\n"
                    "**💰 Economy System**\n"
                    "`!balance` → Check your wallet balance\n"
                    "`!daily` → Claim daily reward (24h cooldown)\n"
                    "`!hunt` → Hunt animals to earn money\n"
                    "`!lootbox` → Open lootbox for random cash\n\n"
                    "**🎲 Gambling Games**\n"
                    "`!gamble <amount>` → 50/50 chance win or lose\n"
                    "`!coinflip <amount> <heads/tails>` → Flip coin & bet\n\n"
                    "**🏆 Leaderboard**\n"
                    "`!top` → Show richest users in server\n\n"
                    "━━━━━━━━━━━━━━━━━━\n"
                    "Type commands with prefix: `!`\n"
                    "Enjoy your economy journey 💸",
        color=discord.Color.blue()
    )

    embed.set_thumbnail(url=INR_IMAGE)
    embed.set_footer(text="INR Economy Bot • Help Menu")

    await ctx.send(embed=embed)

# ----------------------------
# BALANCE
# ----------------------------

@bot.command()
async def balance(ctx):
    user = get_user(ctx.author.id)
    bal = user["balance"]

    embed = make_embed(
        "💰 Wallet Balance",
        f"**{ctx.author.name}**, you currently have:\n\n### ₹{bal} INR",
        discord.Color.green()
    )
    await ctx.send(embed=embed)

# ----------------------------
# DAILY (24H COOLDOWN)
# ----------------------------

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
            f"Come back in **{hours}h {minutes}m** to claim again!",
            discord.Color.red()
        )
        return await ctx.send(embed=embed)

    reward = random.randint(300, 800)
    user["balance"] += reward
    user["last_daily"] = now
    save_data()

    embed = make_embed(
        "🎁 Daily Reward Claimed!",
        f"You received:\n\n### ₹{reward} INR",
        discord.Color.gold()
    )
    await ctx.send(embed=embed)

# ----------------------------
# HUNT
# ----------------------------

@bot.command()
async def hunt(ctx):
    user = get_user(ctx.author.id)

    reward = random.randint(50, 300)
    user["balance"] += reward
    save_data()

    animals = ["🐇 Rabbit", "🦌 Deer", "🐅 Tiger", "🐓 Chicken"]

    embed = make_embed(
        "🏹 Hunt Successful!",
        f"You hunted a **{random.choice(animals)}**\n\nEarned: **₹{reward} INR**",
        discord.Color.orange()
    )
    await ctx.send(embed=embed)

# ----------------------------
# GAMBLE
# ----------------------------

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

# ----------------------------
# COINFLIP
# ----------------------------

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
    embed = make_embed("🪙 Coinflip Result", msg, color)
    await ctx.send(embed=embed)

# ----------------------------
# LOOTBOX
# ----------------------------

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

# ----------------------------
# TOP LEADERBOARD
# ----------------------------

@bot.command()
async def top(ctx):
    sorted_users = sorted(users.items(), key=lambda x: x[1]["balance"], reverse=True)

    leaderboard = ""
    for i, (uid, data) in enumerate(sorted_users[:5], start=1):
        user_obj = await bot.fetch_user(int(uid))
        leaderboard += f"**{i}. {user_obj.name}** — ₹{data['balance']} INR\n"

    embed = make_embed(
        "🏆 Top Richest Users",
        leaderboard if leaderboard else "No users yet!",
        discord.Color.blue()
    )
    await ctx.send(embed=embed)

# ----------------------------
# RUN BOT
# ----------------------------

bot.run(TOKEN)