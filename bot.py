import discord
from discord.ext import commands
import json
import random
import time
import os

# ✅ Token from Railway Variables
TOKEN = os.getenv("TOKEN")

if TOKEN is None:
    print("❌ TOKEN not found! Add TOKEN in Railway Variables.")
    exit()

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

INR_IMAGE = "https://i.imgur.com/3Z6pFJQ.png"

# ----------------------------
# Database System
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
# Embed Helper
# ----------------------------

def make_embed(title, desc, color):
    embed = discord.Embed(title=title, description=desc, color=color)
    embed.set_thumbnail(url=INR_IMAGE)
    embed.set_footer(text="₹ INR Economy Bot")
    return embed

# ----------------------------
# Bot Ready Event
# ----------------------------

@bot.event
async def on_ready():
    print(f"✅ Bot Online Successfully: {bot.user}")

# ----------------------------
# Commands
# ----------------------------

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="📌 INR Economy Bot Help Menu",
        description="Click below commands to use economy system",
        color=discord.Color.red()
    )

    embed.add_field(name="💰 Balance", value="`!balance` → Check wallet", inline=False)
    embed.add_field(name="🎁 Daily", value="`!daily` → Claim daily cash", inline=False)
    embed.add_field(name="🏹 Hunt", value="`!hunt` → Earn money by hunting", inline=False)
    embed.add_field(name="🎰 Gamble", value="`!gamble <amount>` → Gamble your cash", inline=False)
    embed.add_field(name="🪙 Coinflip", value="`!coinflip <amount> <heads/tails>`", inline=False)
    embed.add_field(name="📦 Lootbox", value="`!lootbox` → Open lootbox rewards", inline=False)
    embed.add_field(name="🏆 Top", value="`!top` → Leaderboard richest users", inline=False)

    embed.set_footer(text="Economy Bot • Railway Hosting")
    await ctx.send(embed=embed)

# BALANCE
@bot.command()
async def balance(ctx):
    user = get_user(ctx.author.id)
    embed = make_embed("💰 Wallet Balance",
                       f"**{ctx.author.name}**, you have:\n\n### ₹{user['balance']} INR",
                       discord.Color.green())
    await ctx.send(embed=embed)

# DAILY
@bot.command()
async def daily(ctx):
    user = get_user(ctx.author.id)
    now = time.time()
    cooldown = 86400

    if now - user["last_daily"] < cooldown:
        remaining = int(cooldown - (now - user["last_daily"]))
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60

        embed = make_embed("⏳ Daily Cooldown",
                           f"Come back in **{hours}h {minutes}m**",
                           discord.Color.red())
        return await ctx.send(embed=embed)

    reward = random.randint(300, 800)
    user["balance"] += reward
    user["last_daily"] = now
    save_data()

    embed = make_embed("🎁 Daily Claimed!",
                       f"You received **₹{reward} INR**",
                       discord.Color.gold())
    await ctx.send(embed=embed)

# HUNT
@bot.command()
async def hunt(ctx):
    user = get_user(ctx.author.id)
    reward = random.randint(50, 300)
    user["balance"] += reward
    save_data()

    embed = make_embed("🏹 Hunt Successful!",
                       f"You earned **₹{reward} INR**",
                       discord.Color.orange())
    await ctx.send(embed=embed)

# LOOTBOX
@bot.command()
async def lootbox(ctx):
    user = get_user(ctx.author.id)
    reward = random.randint(200, 1500)
    user["balance"] += reward
    save_data()

    embed = make_embed("📦 Lootbox Opened!",
                       f"You found **₹{reward} INR**",
                       discord.Color.purple())
    await ctx.send(embed=embed)

# TOP
@bot.command()
async def top(ctx):
    sorted_users = sorted(users.items(), key=lambda x: x[1]["balance"], reverse=True)

    leaderboard = ""
    for i, (uid, data) in enumerate(sorted_users[:5], start=1):
        user_obj = await bot.fetch_user(int(uid))
        leaderboard += f"**{i}. {user_obj.name}** — ₹{data['balance']} INR\n"

    embed = make_embed("🏆 Top Richest Users", leaderboard, discord.Color.blue())
    await ctx.send(embed=embed)

# ----------------------------
# Run Bot
# ----------------------------

bot.run(TOKEN)