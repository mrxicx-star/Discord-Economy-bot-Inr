import discord
from discord.ext import commands
import json
import random
import time

# ----------------------------
# BOT SETUP
# ----------------------------
TOKEN = "YOUR_BOT_TOKEN_HERE"
INR_IMAGE = "https://i.imgur.com/3Z6pFJQ.png"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")  # Disable default help


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
# HELP MENU BUTTONS (OwO-style)
# ----------------------------
class HelpMenu(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def update_embed(self, interaction, title, desc):
        embed = discord.Embed(title=title, description=desc, color=discord.Color.red())
        embed.set_thumbnail(url=INR_IMAGE)
        embed.set_footer(text="₹ INR Economy Bot | Help Menu")
        await interaction.response.edit_message(embed=embed, view=self)

    # Economy Category
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

    # Gambling Category
    @discord.ui.button(label="🎰 Gambling", style=discord.ButtonStyle.blurple)
    async def gambling(self, interaction: discord.Interaction, button: discord.ui.Button):
        desc = (
            "`!gamble <amount>` ➤ Gamble cash to win or lose\n"
            "`!coinflip <amount> <heads/tails>` ➤ Flip a coin to win or lose\n"
        )
        await self.update_embed(interaction, "🎰 Gambling Commands", desc)

    # Fun Category
    @discord.ui.button(label="🎲 Fun", style=discord.ButtonStyle.grey)
    async def fun(self, interaction: discord.Interaction, button: discord.ui.Button):
        desc = (
            "No fun commands yet, but coming soon!\n"
            "Stay tuned for more interactive features!"
        )
        await self.update_embed(interaction, "🎲 Fun Commands", desc)

    # Info / Bot Category
    @discord.ui.button(label="ℹ️ Info", style=discord.ButtonStyle.blurple)
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
        description="Click the buttons below to view different command categories!",
        color=discord.Color.red()
    )
    embed.set_thumbnail(url=INR_IMAGE)
    embed.set_footer(text="All Commands ✅ | Click a button for details")
    await ctx.send(embed=embed, view=HelpMenu())

# ----------------------------
# ECONOMY COMMANDS
# ----------------------------
@bot.command()
async def balance(ctx):
    user = get_user(ctx.author.id)
    embed = make_embed("💰 Wallet Balance",
                       f"**{ctx.author.name}**, you have:\n\n### ₹{user['balance']} INR",
                       discord.Color.green())
    await ctx.send(embed=embed)

@bot.command()
async def daily(ctx):
    user = get_user(ctx.author.id)
    now = time.time()
    cooldown = 86400  # 24h
    if now - user["last_daily"] < cooldown:
        remaining = int(cooldown - (now - user["last_daily"]))
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60
        embed = make_embed("⏳ Daily Cooldown",
                           f"Come back in **{hours}h {minutes}m** for your next daily cash!",
                           discord.Color.red())
        return await ctx.send(embed=embed)
    reward = random.randint(300, 800)
    user["balance"] += reward
    user["last_daily"] = now
    save_data()
    embed = make_embed("🎁 Daily Cash Claimed!",
                       f"You received:\n\n### ₹{reward} INR",
                       discord.Color.gold())
    await ctx.send(embed=embed)

@bot.command()
async def hunt(ctx):
    user = get_user(ctx.author.id)
    reward = random.randint(50, 300)
    user["balance"] += reward
    save_data()
    animals = ["🐇 rabbit", "🦌 deer", "🐅 tiger", "🐓 chicken"]
    embed = make_embed("🏹 Hunt Successful!",
                       f"You hunted a **{random.choice(animals)}**\nEarned: **₹{reward} INR**",
                       discord.Color.orange())
    await ctx.send(embed=embed)

@bot.command()
async def lootbox(ctx):
    user = get_user(ctx.author.id)
    reward = random.randint(200, 1500)
    user["balance"] += reward
    save_data()
    embed = make_embed("📦 Lootbox Opened!",
                       f"You found treasure inside!\n\n### ₹{reward} INR",
                       discord.Color.purple())
    await ctx.send(embed=embed)

@bot.command()
async def top(ctx):
    sorted_users = sorted(users.items(), key=lambda x: x[1]["balance"], reverse=True)
    leaderboard = ""
    for i, (uid, data) in enumerate(sorted_users[:5], start=1):
        try:
            user_obj = await bot.fetch_user(int(uid))
            leaderboard += f"**{i}. {user_obj.name}** — ₹{data['balance']} INR\n"
        except:
            leaderboard += f"**{i}. Unknown User** — ₹{data['balance']} INR\n"
    embed = make_embed("🏆 Top Richest Users", leaderboard, discord.Color.blue())
    await ctx.send(embed=embed)

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

# ----------------------------
# RUN BOT
# ----------------------------
bot.run(TOKEN)