import discord
from discord.ext import commands
import json
import random
import time
import os

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
bot.remove_command("help")

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
# BOT READY
# ----------------------------

@bot.event
async def on_ready():
    print("✅ Bot Online:", bot.user)

# ----------------------------
# HELP MENU WITH BUTTONS
# ----------------------------

class HelpMenu(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

    async def update(self, interaction, title, desc):
        embed = discord.Embed(
            title=title,
            description=desc,
            color=discord.Color.red()
        )
        embed.set_footer(text="₹ Economy Bot Help Menu")

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="💰 Economy", style=discord.ButtonStyle.danger)
    async def economy(self, interaction, button):
        await self.update(
            interaction,
            "💰 Economy Commands",
            "**Earn and manage your money!**\n\n"
            "`!balance` ➝ Check your wallet\n"
            "`!daily` ➝ Claim daily reward (24h cooldown)\n"
            "`!hunt` ➝ Hunt animals for cash\n"
            "`!lootbox` ➝ Open lootbox for surprise money\n\n"
            "📌 These commands help you earn INR easily!"
        )

    @discord.ui.button(label="🎲 Games", style=discord.ButtonStyle.danger)
    async def games(self, interaction, button):
        await self.update(
            interaction,
            "🎲 Gambling & Fun Commands",
            "**Risk money and win big!**\n\n"
            "`!gamble <amount>` ➝ 50/50 win or lose\n"
            "`!coinflip <amount> <heads/tails>` ➝ Flip a coin\n\n"
            "⚠ Use carefully, you can lose money!"
        )

    @discord.ui.button(label="🏆 Leaderboard", style=discord.ButtonStyle.danger)
    async def leaderboard(self, interaction, button):
        await self.update(
            interaction,
            "🏆 Ranking Commands",
            "**See richest users in server!**\n\n"
            "`!top` ➝ Top 5 richest players\n\n"
            "🔥 Compete and become #1 richest!"
        )


@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="📌 INR Economy Bot Help Menu",
        description=
        "**Welcome to INR Economy Bot!**\n\n"
        "Click buttons below to explore commands.\n\n"
        "💰 Economy System\n"
        "🎲 Gambling Games\n"
        "🏆 Leaderboards\n",
        color=discord.Color.red()
    )
    embed.set_footer(text="All Commands Working ✅")

    await ctx.send(embed=embed, view=HelpMenu())

# ----------------------------
# ECONOMY COMMANDS
# ----------------------------

@bot.command()
async def balance(ctx):
    user = get_user(ctx.author.id)

    embed = make_embed(
        "💰 Wallet Balance",
        f"**{ctx.author.name}**, you have:\n\n### ₹{user['balance']} INR",
        discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command()
async def daily(ctx):
    user = get_user(ctx.author.id)
    now = time.time()

    cooldown = 86400

    if now - user["last_daily"] < cooldown:
        remaining = int(cooldown - (now - user["last_daily"]))
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60

        embed = make_embed(
            "⏳ Daily Cooldown",
            f"Come back in **{hours}h {minutes}m** for daily cash!",
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

@bot.command()
async def hunt(ctx):
    user = get_user(ctx.author.id)

    reward = random.randint(50, 300)
    user["balance"] += reward
    save_data()

    animals = ["🐇 Rabbit", "🦌 Deer", "🐅 Tiger", "🐓 Chicken"]

    embed = make_embed(
        "🏹 Hunt Successful!",
        f"You hunted a **{random.choice(animals)}**\nEarned: **₹{reward} INR**",
        discord.Color.orange()
    )
    await ctx.send(embed=embed)

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
# GAMBLING COMMANDS
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
        msg = f"🎉 You WON!\nGained **₹{amount} INR**"
        color = discord.Color.green()
    else:
        user["balance"] -= amount
        msg = f"💀 You LOST!\nLost **₹{amount} INR**"
        color = discord.Color.red()

    save_data()
    await ctx.send(embed=make_embed("🎰 Gamble Result", msg, color))

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
    await ctx.send(embed=make_embed("🪙 Coinflip Result", msg, color))

# ----------------------------
# LEADERBOARD
# ----------------------------

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
# RUN BOT
# ----------------------------

bot.run(TOKEN)