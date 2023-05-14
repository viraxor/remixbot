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
        self.SAMPLE = 0
        self.ZIP = 1
        self.NOT_FILE = 2
        
    def check_file(self, fname):
        if fname.lower().endswith((".wav", ".flac", ".ogg")):
            return self.SAMPLE
        elif fname.lower().endswith(".zip"):
            return self.ZIP
        else:
            return self.NOT_FILE
            
    def copy_file(self, fname):
        i = 0
        copy_fname = fname.split("/")[-1]
        copy = True
        while os.path.exists(f"./samples/{copy_fname}"):
            if (os.stat(f"./samples/{copy_fname}").st_size == os.stat(f"./temp.{copy_fname.split('.')[-1]}").st_size) or os.stat(f"./samples/{copy_fname}").st_size > 1000000: # if file is larger than 1mb or is a duplicate
                copy = False # no copying of the file
                break
            else: # if it isn't a duplicate
                i += 1
                copy_fname = fname[:-len(fname.split(".")[-1]) - 1] + f"({i})." + fname.split(".")[-1] # concatenates (1), (2) etc. to the file if the file with that name already exists
                print(copy_fname)
        
        if copy:    
            shutil.copy(f"./temp.{copy_fname.split('.')[-1]}", f"./samples/{copy_fname}")
            self.file_list.append(f"./samples/{copy_fname}")
            
    def copy_zip(self):
        if os.path.exists("./zip"):
            shutil.rmtree("./zip", ignore_errors=True) # delete if zip was extracted before
        shutil.unpack_archive("./temp.zip", "./zip", "zip")
        samples = glob.glob("./zip/**/*.wav", recursive=True)
        samples.extend(glob.glob("./zip/**/*.ogg", recursive=True))
        samples.extend(glob.glob("./zip/**/*.flac", recursive=True))
        for fname in samples:
            shutil.copy(fname, f"./temp.{fname.split('/')[-1].split('.')[-1]}") # copy sample as temp.wav (to work with self.copy_file)
            self.copy_file(fname)
        
    @app_commands.command(name="sample")
    async def sample(self, interaction: discord.Interaction, smpfile: discord.Attachment):
        """Upload samples to the bot through this command."""
        
        if self.check_file(smpfile.filename) == self.SAMPLE:
            if smpfile.size < 1000000: # 1mb?
                await interaction.response.defer() # no error 10062, just in case
                await smpfile.save(f"./temp.{smpfile.filename.split('.')[-1]}")
                fn = partial(self.copy_file, smpfile.filename)
                await self.bot.loop.run_in_executor(None, fn)
                msg = await interaction.original_response
                await msg.edit(content="The file has been saved.")
            else:
                await interaction.response.send_message("The file is too large. Try downsampling it.", ephemeral=True)
        elif self.check_file(smpfile.filename) == self.ZIP:
            await interaction.response.defer() # no error 10062, zips can be large
            await smpfile.save(f"./temp.zip")
            fn = partial(self.copy_zip)
            await self.bot.loop.run_in_executor(None, fn)
            msg = await interaction.original_response()
            await msg.edit(content="The files have been saved.")
        else:
            await interaction.response.send_message("You can send only wav, ogg or flac files!", ephemeral=True)
            
    def make_bitpack(self):
        if os.path.exists("./bitpack"):
            shutil.rmtree("./bitpack", ignore_errors=True) # deletes the bitpack made before
        os.mkdir("./bitpack")
        samples = random.sample(self.file_list, random.randint(20, 35)) # hehe random.sample
        for sample in samples:
            shutil.copy(sample, f"./bitpack/{sample.split('/')[-1]}")
        shutil.make_archive("./pack", "zip", "./bitpack/")
            
    @app_commands.command(name="bitpack")
    async def bitpack(self, interaction: discord.Interaction):
        """Make bitpacks for your battles, easy and fast."""
        
        fn = partial(self.make_bitpack)
        await interaction.response.defer() # no error 10062
        await self.bot.loop.run_in_executor(None, fn)
        file = discord.File("./pack.zip")
        msg = await interaction.original_response()
        await msg.add_files(file)
