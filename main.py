import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()

bot = commands.Bot(command_prefix="$", intents=discord.Intents.all())


@bot.event
async def on_ready():
    try:
        print("Loading the cogs...")
        await bot.load_extension("Cogs.TicketSetupCog")
        synced = await bot.tree.sync()
        print(f"Commandes slash synchronisées ({len(synced)})")
    except Exception as e:
        print(f"Erreur lors de la sync : {e}")


bot.run(os.getenv("DISCORD_TOKEN"))