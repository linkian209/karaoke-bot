import discord
import logging
import os
from random import randint
from discord.ext import commands
from karaoke_bot_funcs import *


# Random Commands for the Karaoke Bot
class KaraokeBotRandom():
  """ KaraokeBot Random Cog"""
  # Initialization function
  def __init__(self, bot):
    # The bot
    self.bot = bot
    self.queue = []

    # Logging
    self.log = logging.getLogger(__name__)

    # List of emojis for various things
    self.clap_emojis = [':clap:', ':raised_hands:', ':pray:']
  # End init

  # !clap
  # Bot will clap
  @commands.command(pass_context=True)
  @commands.has_role('Mod')
  async def clap(self, ctx):
    # Get a list of all available gifs
    gifs = os.listdir('{}/gifs/clapping/'.format(os.getcwd()))

    # Pick a random one to send
    lucky_gif = randint(0, len(gifs)-1)

    # Open the file and send
    filename = '{}/gifs/clapping/{}'.format(os.getcwd(), gifs[lucky_gif])

    await ctx.send(file=discord.File(filename, 'clap.gif'))
  # End !clap

  # !applause
  # Send applause!
  @commands.command(pass_context=True)
  async def applause(self, ctx):
    # Make response of fifteen random emojis
    response = [self.clap_emojis[randint(0, len(self.clap_emojis) - 1)]
                for i in range(15)]

    # Return!
    await ctx.send(' '.join(response))
  # end !applause

# End KaraokeBotRandom

def setup(bot):
  bot.add_cog(KaraokeBotRandom(bot))
