#!/usr/bin/python
import discord
import logging.config
import getopt
import sys
import os
import signal
import datetime
import configparser
from discord.ext import commands
from karaoke_bot_funcs import *

# Extensions for the bot
startup_extensions = ["modules.karaoke_bot_commands",
                      "modules.karaoke_bot_events",
                      "modules.karaoke_bot_random"]

# Main Function
def main():
  # Set defaults
  command_prefix = '!'
  token = None

  print('Karaoke-Bot Starting up...\nReading Config...')

  # First parse config
  config = configparser.ConfigParser()
  config.read('karaoke_bot.conf')

  for section in config.sections():
    if section == 'General':
      for item in config[section]:
        if item == 'command_prefix':
          command_prefix = config[section][item]
        elif item == 'token':
          token = config[section][item]
        else:
          print('Unrecognized item: {}'.format(item))
          usage()
          sys.exit(2)

  # Command line arguments trump config
  print('Parsing Command Line Options...')
  # Get started
  try:
    flags = 'ht:c:'
    long_flags = ['help','token=','command-prefix=']
    opts, args = getopt.getopt(sys.argv[1:], flags, long_flags)
  # Whomp, got an error
  except getopt.GetoptError as err:
    print(err)
    usage()
    sys.exit(2)

  # Parse these args
  # Loop through options
  for o,a in opts:
    if o in ('-h', '--help'):
      usage()
      sys.exit()
    elif o in ('-t', '--token'):
      token = a
    elif o in ('-c', '--command-prefix'):
      command_prefix = a
    else:
      print('{} is not a valid argument'.format(a))
      usage()
      sys.exit(2)

  if token is None:
    usage()
    sys.exit(2)

  # Set up database
  print('Configuring Database...')
  if not os.path.isfile('karaokebot.sqlt'):
    print('Database does not exist! Creating...')
    configure_database()

  # Set up logging
  print('Setting Up Loggers...')
  logger = logging.config.fileConfig('logging.conf')

  # Setup bot commands
  print('Configuring Bot...')
  bot = commands.Bot(command_prefix=command_prefix,
                     activity=discord.Game('{}help'.format(command_prefix)))
  print('  - Command Prefix: {}'.format(command_prefix))

  # Load in bot extensions
  for extension in startup_extensions:
    try:
      bot.load_extension(extension)
      print('  - Loaded extension {}'.format(extension))
    except Exception as e:
      error = '{}: {}'.format(type(e).__name__, e)
      print('Failed to load extension {}\n{}'.format(extension, error))


  # Create event loop and run!
  print('Starting Bot!')
  bot.run(token)

  # Once we get a signal to quit, logout then exit!
  bot.logout()
  print('Exiting!')
  sys.exit(0)

# Start script
if __name__ == "__main__":
  main()
