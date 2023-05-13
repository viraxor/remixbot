import discord
from discord.ext import commands
from discord import app_commands
import os
import shutil
from functools import partial
import glob
import random

async def setup(bot):
    await bot.add_cog(Bitpack(bot))
    
class Bitpack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file_list = glob.glob("./samples/*.*")
        
    def check_file(self, fname):
        if fname.lower().endswith((".wav", ".flac", ".ogg")):
            return True
        else:
            return False
            
    def copy_file(self, fname):
        i = 0
        copy_fname = fname
        copy = True
        while os.path.exists(f"./samples/{copy_fname}"):
            if os.stat(f"./samples/{copy_fname}").st_size == os.stat(f"./temp.{copy_fname.split('.')[-1]}").st_size: # if file sizes are same
                copy = False # the file is a duplicate, therefore
                break
            else:
                i += 1
                copy_fname = fname[2:] + f"({i})"
        
        if copy:    
            shutil.copy(f"./temp.{copy_fname.split('.')[-1]}", f"./samples/{copy_fname}")
            self.file_list.append(f"./samples/{copy_fname}")
        
    @app_commands.command(name="sample")
    async def sample(self, interaction: discord.Interaction, smpfile: discord.Attachment):
        """Upload samples to the bot through this command."""
        
        if self.check_file(smpfile.filename):
            await smpfile.save(f"./temp.{smpfile.filename.split('.')[-1]}")
            fn = partial(self.copy_file, smpfile.filename)
            await self.bot.loop.run_in_executor(None, fn)
            await interaction.response.send_message("The file has been saved.", ephemeral=True)
        else:
            await interaction.response.send_message("You can send only wav, ogg or flac files!", ephemeral=True)
            
    def make_bitpack(self):
        if os.path.exists("./bitpack"):
            os.rmdir("./bitpack") # deletes the bitpack made before
        os.mkdir("./bitpack")
        samples = random.sample(self.file_list, random.randint(20, 35)) # hehe random.sample
        for sample in samples:
            shutil.copy(sample, f"./bitpack/{sample.split('/')[-1]}")
        shutil.make_archive("./pack", "zip", "./bitpack/")
            
    @app_commands.command(name="bitpack")
    async def bitpack(self, interaction: discord.Interaction):
        """Make bitpacks for your battles, easy and fast."""
        
        fn = partial(self.make_bitpack)
        await self.bot.loop.run_in_executor(None, fn)
        file = discord.File("./pack.zip")
        await interaction.response.send_message(file=file, ephemeral=True)
