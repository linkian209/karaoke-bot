#!/usr/bin/python
import discord
import logging
import getopt
import sys
import sqlite3
import signal
import datetime
from discord.ext import commands
from karaoke_bot_funcs import *

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

# Extensions for the bot
startup_extensions = ["KaraokeBotCommands"]

# Main Function
def main():
  # Setup signal handler
  sig_handler = SignalHandler()

  # Command line arguments
  # Get started
  try:
    flags = 'hftc'
    long_flags = ['file','help','token','command-prefix']
    opts, args = getopt.getopt(sys.argv[1:], flags, long_flags)
  # Whomp, got an error
  except getopt.GetoptError as err:
    print(err)
    usage()
    sys.exit(2)

  # Parse these args
  # Set defaults
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
    else:
      print('{} is not a valid argument'.format(a))
      usage()
      sys.exit(2)

  if token is None:
    usage()
    sys.exit(2)

  # Set up logging
  logger.config.fileConfig('logging.conf')

  # Setup bot commands
  bot = commands.Bot(command_prefix=command_prefix)

  # Load in bot extensions
  for extension in startup_extensions:
    try:
      bot.load_extension(extension)
    except Exception as e:
      error = '{}: {}'.format(type(e).__name__, e)
      print('Failed to load extension {}\n{}'.format(extension, error))


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
if __name__ == "__main__":
  main()
