import discord
from discord.ext import commands

class KaraokeBotEvents(commands.Cog):
  # Initialize
  def __init__(self, bot):
    self.bot = bot
  # End init

  # on_ready
  # Called when the bot is ready
  async def on_ready(self):
    print('Bot is ready! Logged in as {}'.format(self.bot.user))

# End Events Cog

def setup(bot):
  bot.add_cog(KaraokeBotEvents(bot))
