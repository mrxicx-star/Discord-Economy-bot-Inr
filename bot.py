import discord
from discord.ext import commands
import json
import random
import time
import os


# ----------------------------
# BOT SETUP
# ----------------------------
INR_IMAGE = "https://i.imgur.com/3Z6pFJQ.png"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")


# ----------------------------
# TOKEN FIX (GitHub Hosting Safe)
# ----------------------------
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

if TOKEN is None:
    raise ValueError("❌ DISCORD_BOT_TOKEN not found in environment secrets!")


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
        users[str(uid)] = {"balance": 0, "last_daily": 0}
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
# HELP MENU BUTTONS (FIXED)
# ----------------------------
class HelpMenu(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

    async def update_embed(self, interaction, title, desc):
        embed = discord.Embed(title=title, description=desc, color=discord.Color.red())
        embed.set_thumbnail(url=INR_IMAGE)
        embed.set_footer(text="₹ INR Economy Bot | Help Menu")
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="💰 Economy", style=discord.ButtonStyle.green)
    async def economy(self, interaction: discord.Interaction, button: discord.ui.Button):
        desc = (
            "`!balance` ➤ Show your wallet balance\n"
            "`!daily` ➤ Claim daily cash (24h cooldown)\n"
            "`!hunt` ➤ Hunt animals for cash\n"
            "`!lootbox` ➤ Open a lootbox for random cash\n"
            "`!top` ➤ Show top richest users\n"
        )
        await self.update_embed(interaction, "💰 Economy Commands", desc)

    @discord.ui.button(label="🎰 Gambling", style=discord.ButtonStyle.blurple)
    async def gambling(self, interaction: discord.Interaction, button: discord.ui.Button):
        desc = (
            "`!gamble <amount>` ➤ Gamble cash\n"
            "`!coinflip <amount> <heads/tails>` ➤ Flip coin\n"
        )
        await self.update_embed(interaction, "🎰 Gambling Commands", desc)

    @discord.ui.button(label="🎲 Fun", style=discord.ButtonStyle.gray)
    async def fun(self, interaction: discord.Interaction, button: discord.ui.Button):
        desc = "No fun commands yet 😅\nComing soon!"
        await self.update_embed(interaction, "🎲 Fun Commands", desc)

    @discord.ui.button(label="ℹ️ Info", style=discord.ButtonStyle.primary)
    async def info(self, interaction: discord.Interaction, button: discord.ui.Button):
        desc = (
            "`!help` ➤ Show this help menu\n"
            "`!ping` ➤ Check bot latency\n"
        )
        await self.update_embed(interaction, "ℹ️ Info Commands", desc)


# ----------------------------
# EVENTS
# ----------------------------
@bot.event
async def on_ready():
    print(f"✅ Bot Online: {bot.user}")


# ----------------------------
# HELP COMMAND
# ----------------------------
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="🚨 INR Economy Bot Help Menu",
        description="Click buttons below to view commands!",
        color=discord.Color.red()
    )
    embed.set_thumbnail(url=INR_IMAGE)
    embed.set_footer(text="All Commands ✅")
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
            f"Come back in **{hours}h {minutes}m**!",
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
async def ping(ctx):
    await ctx.send(f"🏓 Pong! `{round(bot.latency*1000)}ms`")


# ----------------------------
# RUN BOT
# ----------------------------
bot.run(TOKEN)