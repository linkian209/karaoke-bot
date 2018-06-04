#!/usr/bin/python

import discord
import logging
import getopt
import sys
import sqlite3
import signal
from logging.handlers import RotatingFileHandler
from discord.ext import commands

# Signal Handler
class SignalHandler:
  # Init function
  def __init__(self):
    # Initialize signal catching
    self.recieved_signal = False
    self.recieved_term_signal = False

    # Add listener for signals
    for signum in [1,2,3,10,12,15]:
      signal.signal(signum, self.handler)

  # Signal handler
  def handler(self, signum, frame):
    # Hold the last signal
    self.last_signal = signum
    self.recieved_signal = True

    # If we are a kill signal, set the flag
    if signum in [2,3,15]:
      self.received_term_signal = True

# End Signal Handler

# Globals
embed_color = 0xEEE657
queues = {}

# Utility Functions

# Usage
# Prints script arguments
def usage():
  print(
    '''Usage: python karaoke-bot.py [-t|--token] <TOKEN> (options)
       \b\bRequired Options:
       -t
       --token           App Token used for discord\n
       \b\bOptional Options:
       --backup-count    Number of log files to keep. Default is 5
       -c
       --command-prefix  Command prefix to respond to in Discord. Default is "!"
       -f
       --file            Log file. Defaults to "log.txt" in the current
                         working directory.
       --max-bytes       Number of bytes to keep in one file. Defaults to 10MB.'''
)

# End Utility Functions

# Main Function
def main():
  # Setup signal handler
  sig_handler = SignalHandler()

  # Command line arguments
  # Get started
  try:
    flags = 'hftc'
    long_flags = ['file','help','token','max-bytes','backup-count','command-prefix']
    opts, args = getopt.getopt(sys.argv[1:], flags, long_flags)
  # Whomp, got an error
  except getopt.GetoptError as err:
    print(err)
    usage()
    sys.exit(2)

  # Parse these args
  # Set defaults
  file_name = 'log.txt'
  max_bytes = 10000000
  backup_count = 5
  command_prefix = '!'
  token = None

  # Loop through options
  for o,a in opts:
    if o in ('-h', '--help'):
      usage()
      sys.exit()
    elif o in ('-t', '--token'):
      token = a
    elif o in ('-f', '--file'):
      file_name = a
    elif o in ('-c', '--command-prefix'):
      command_prefix = a
    elif o == '--max-bytes':
      try:
        max_bytes = int(a)
      except ValueError:
        print('{} is not an int'.format(a))
        usage()
        sys.exit(2)
    elif o == '--backup-count':
      try:
        backup_count = int(a)
      except ValueError:
        print('{} is not an int'.format(a))
        usage()
        sys.exit(2)
    else:
      print('{} is not a valid argument'.format(a))
      usage()
      sys.exit(2)

  if token is None:
    usage()
    sys.exit(2)

  # Set up logging
  logger = logging.getLogger('discord')
  logger.setLevel(logging.DEBUG)
  handler = RotatingFileHandler(file_name, mode='a',
                                maxBytes=max_bytes,
                                backupCount=backup_count)
  log_format = '%(asctime)s:%(level)s:%(name)s: %(message)s'
  handler.setFormatter(logging.Formatter(log_format))
  logger.addHandler(handler)

  # Setup bot commands
  bot = commands.Bot(command_prefix=command_prefix)

  # !info
  # Returns information about the bot, the author, and other techy stuff
  @bot.command()
  async def info(ctx):
    description = 'A Discord bot for running a karaoke queue'
    embed = discord.Embed(title='Karaoke Bot', description=description, color=hex_color)
    embed.add_field(name='Author', value='linkian209')
    embed.add_field(name='Source', value='[Github](https://github.com/linkian209/karaoke-bot)')
    embed.add_field(name='Questions/Comments', value='mailto:linkian209@gmail.com')

    await ctx.send(embed=embed)

  # !help
  # Print all of the commands that the bot can use
  bot.remove_command('help')

  @bot.command()
  async def help(ctx):
    description = 'The list of commands for the Karaoke Bot'

    # Commands and their descriptions
    commands = [
      'info',
      'help',
      'add [Username] (Song Name)',
      'remove [Username]',
      'next',
      'clear'
    ]

    descriptions = [
      'Displays information about the bot.',
      'Displays the list of commands.',
      'Add a user to the queue. Can optionally add the song name.',
      'Remove a user from the queue.',
      'Progress to the next user in the queue. Also shows who is on deck.',
      'Clears the queue.'
    ]

    # Create the response
    embed = discord.Embed(title='Karaoke Bot', description=description, color=hex_color)

    # Loop through all commands
    for command in commands:
      cur_command = commands[command]
      cur_description = descriptions[command]
      embed.add_field(name=cur_command, value=cur_description)

    # Return
    await ctx.send(embed=embed)

  # !add
  # Add a user (with an optional song) to the queue
  @bot.command()
  async def add(ctx, user: discord.User, song: str=None):
    # Add person to queue

    # Make response
    description = user

    if song is not None:
      description += ' will be singing {}'.format(song)

    embed = discord.Embed(title='Adding User', value=description)
    embed.add_field(name='Current Order', value=queue)

    await ctx.send(embed=embed)

  # Start the bot
  bot.run(token)

  # Loop until we are told to stop
  loop = True
  while True:
    if sig_handler.recieved_signal:
      if sig_handler.recieved_term_signal:
        logging.warning('Received signal {}. Exiting.'.format(sig_handler.last_signal))
        loop = False

  # Stop the bot
  bot.close()

# Start script
if __name__ = '__main__':
  main()
