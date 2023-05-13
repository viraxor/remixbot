import discord
from discord.ext import commands
from discord import app_commands

from dotenv import load_dotenv
from os import getenv

bot = commands.Bot(command_prefix="/", intents=discord.Intents.default())

@bot.tree.command(name="reload")
async def reload(interaction: discord.Interaction, name: str):
    if interaction.user.id == 523887995850326017:
        await bot.reload_extension(f"cogs.{name}")
        await interaction.response.send_message("reloaded", ephemeral=True)

@bot.tree.command(name="sync")
async def sync(interaction: discord.Interaction):
    if interaction.user.id == 523887995850326017:
        await bot.tree.sync()
        await interaction.response.send_message("synced", ephemeral=True)
        
load_dotenv("./.env")
token = getenv("TOKEN")

@bot.event
async def on_ready():
    await bot.load_extension("cogs.bitpack")
    await bot.tree.sync()

bot.run(token)
