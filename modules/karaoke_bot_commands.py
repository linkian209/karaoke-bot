import discord
import sqlite3
import logging
from discord.ext import commands
from karaoke_bot_funcs import *

# Globals
database_name = 'karaokebot.sqlt'

# Commands for the Karaoke Bot
class KaraokeBotCommands():
  """ KaraokeBot Commands Cog"""
  # Initialization function
  def __init__(self, bot):
    # The bot
    self.bot = bot
    self.queue = []

    # Logging
    self.log = logging.getLogger(__name__)

    # Embed Color
    self.embed_color = 0xEEE657

  # !info
  # Returns information about the bot, the author, and other techy stuff
  @commands.command()
  async def info(self, ctx):
    description = 'A Discord bot for running a karaoke self.queue'
    embed = discord.Embed(title='Karaoke Bot', description=description,
                          color=self.embed_color)
    embed.add_field(name='Author', value='linkian209')
    embed.add_field(name='Source',
                    value='[Code](https://github.com/linkian209/karaoke-bot)')
    embed.add_field(name='Questions/Comments',
                    value='mailto:linkian209@gmail.com')

    await ctx.send(embed=embed)
  # End !info

  # !help
  # Print all of the commands that the bot can use
  bot.remove_command('help')

  @commands.command()
  async def help(self, ctx):
    description = 'The list of commands for the Karaoke Bot'

    # Commands and their descriptions
    commands = [
      'info',
      'help',
      'add [Username] (Song Name)',
      'remove [Username]',
      'next',
      'skipTop',
      'color',
      'cut',
      'clear',
      'queue'
    ]

    descriptions = [
      'Displays information about the bot. Ex: `!info`',
      'Displays the list of commands. Ex: `!help`',
      'Add a user to the self.queue. Can optionally add the song name. Ex: `!add user123 "Uptown Girl"`',
      'Remove a user from the self.queue. `!remove user123`',
      'Progress to the next user in the self.queue. Also shows who is on deck. Ex: `!next`',
      '*Mod Only* Moves supplied username to front of self.queue. Ex: `!skipTop user456`',
      '*Mod Only* Sets color for bot embeds. Ex: `!color 0xDADADA`',
      '*Mod Only* Removes user at supplied index from the self.queue. `!cut 3`',
      'Clears the queue. Ex: `!clear`',
      'Displays current queue. Ex: `!queue`'
    ]

    # Create the response
    embed = discord.Embed(title='Karaoke Bot', description=description, color=self.embed_color)

    # Loop through all commands
    for command in commands:
      cur_command = commands[command]
      cur_description = descriptions[command]
      embed.add_field(name=cur_command, value=cur_description)

    # Return
    await ctx.send(embed=embed)
  # End !help

  # !add
  # Add a user (with an optional song) to the self.queue
  @commands.command()
  async def add(self, ctx, user: str, song: str=None):
    # Add person to self.queue, if they aren't already in line
    in_queue = False
    for item in self.queue:
      if item['user'] == user:
        in_self.queue = True
        break

    if not in_self.queue:
      self.queue.append({'user': user, 'song': song})

    # Make response
    if not in_queue:
      description = user

      if song is not None:
        description += ' will be singing {}'.format(song)
    # If they are already in self.queue, alert them
    else:
      description = '{} is already in queue. Please wait your turn!'.format(user)

    embed = discord.Embed(title='Adding User', description=description,
                          color=self.embed_color)
    embed.add_field(name='Current Order', value=make_queue_string(self.queue))

    await ctx.send(embed=embed)
  # End !add

  # !remove
  # Remove user from self.queue
  @commands.command()
  async def remove(self, ctx, user: str):
    # If the user is in the self.queue, remove them
    for item in self.queue:
      if item['user'] == user:
        self.queue.remove(item)

    # Create response
    description = 'Removing user {} from queue'.format(user)
    embed = discord.Embed(title='Removing user', description=description,
                          color=self.embed_color)
    embed.add_field(name='Current Order', value=make_queue_string(self.queue))

    await ctx.send(embed=embed)
  # End !remove

  #!next
  # Advances the self.queue up one and displays who is on deck
  @commands.command()
  async def next(self, ctx):
    # Get current user and on deck user
    cur_user = self.queue[0]
    on_deck = self.queue[1]

    # Pop from self.queue
    self.queue = self.queue[1:]

    # Connect to database
    db_conn = sqlite3.connect(database_name)

    # Update statistics on user
    curs = db_conn.cursor()

    # Check if the user exists
    curs.execute('SELECT count(1) FROM users WHERE username = ?',
                 cur_user['user'])
    count = curs.fetchone()

    # If the user exists, update their record
    if count is not None:
      if cur_user['song'] is not None:
        # First Update user records
        params = (cur_user['songs'], datetime.now(), cur_user['user'])
        curs.execute('''UPDATE users
                           SET last_song = ?,
                               last_date = ?,
                               times_sung = times_sung + 1
                         WHERE username = ?''', params)

      else:
        params = (datetime.now(), cur_user['user'])
        curs.execute('''UPDATE users
                           SET last_date = ?,
                               times_sung = times_sung + 1
                         WHERE username = ?''', params)
    # User does not exist, make record
    else:
      if cur_user['song'] is not None:
        params = (cur_user['user'], cur_user['song'], datetime.now(), 1)
        curs.execute('''INSERT INTO users
                        (username, last_song, last_date, times_sung)
                        VALUES(?,?,?,?)''', params)
      else:
        params = (cur_user['user'], datetime.now(), 1)
        curs.execute('''INSERT INTO users
                        (username, last_date, times_sung)
                        VALUES(?,?,?)''', params)


    # Now update song record
    if cur_user['song'] is not None:
      # Check if it exists
      params = (cur_user['song'], cur_user['user'])
      curs.execute('''SELECT count(1) FROM songs
                      WHERE song = ? AND username = ?''', params)
      count = curs.fetchone()

      # If it exists, update
      if count is not None:
        params = (datetime.now(), cur_user['song'], cur_user['user'])
        curs.execute('''UPDATE songs
                           SET times_sung = times_sung + 1,
                               last_sung = ?
                        WHERE song = ?
                          AND username = ?''', params)
      # Song does not exist in records, insert record
      else:
        params = (cur_user['song'], cur_user['user'], datetime.now(), 1)
        curs.execute('''INSERT INTO songs
                        (song, username, times_sung, last_sung)
                        VALUES (?,?,?,?)''', params)

    # Commit database changes then close
    db_conn.commit()
    db_conn.close()

    # Make response
    next_up_desc = cur_user['user']
    if cur_user['song'] is not None:
      next_up_desc += ' singing {}'.format(cur_user['song'])

    on_deck_desc = on_deck['user']
    if on_deck['song'] is not None:
      on_deck_desc += ' singing {}'.format(on_deck['song'])

    embed = ctx.Embed(title='Next Up', description=next_up_desc,
                      color=self.embed_color)
    embed.add_field(name='On Deck', value=on_deck_desc)
    embed.add_field(name='Current Queue', value=make_queue_string(self.queue))

    await ctx.send(embed=embed)
  # End !next

  # !skipTop
  # Supplied user name gets shoved to the front of the queue
  @commands.command()
  @commands.has_role('Mod')
  async def skipTop(self, ctx, user: str):
    # Check if that user is in the queue
    user_cutting = None
    for item in self.queue:
      if item['user'] == user:
        user_cutting = item
        break

    if user_cutting is not None:
      self.queue.remove(item)
      self.queue = [item] + self.queue
      desc = '{} cut to the front of the line!'.format(user)
    else:
      desc = '''{} is not in the queue.
                Consider adding them first with `!add`'''.format(user)

    # Return Response
    embed = ctx.Embed(title='Skipping to the Top', description=desc,
                      color=self.embed_color)
    embed.add_field(name='Current Queue', value=make_queue_string(self.queue))

    await ctx.send(embed=embed)
  # end !skipTop

  # !color
  # Sets the embed color. Must have 'Mod' role
  @commands.command()
  @commands.has_role('Mod')
  async def color(self, ctx, color: str):
    # Update color
    old_color = self.embed_color

    # Update color
    try:
      self.embed_color = hex(color, 16)

      # Update worked!
      desc = 'Changed color from {} to {}'.format(old_color, color)
      embed = ctx.Embed(title='Color Change', description=desc,
                        color=self.embed_color)
    except Exception as e:
      self.log.error('{}: {}'.format(type(e).__name__, str(e)))
      desc = 'Something went wronging changing color to {}'.format(color)
      embed = ctx.Embed(title='Color Change', description=desc,
                        color=self.embed_color)

    await ctx.send(embed=embed)
  # End !color

  # !cut
  # Cuts user at specified index from the queue
  @commands.command()
  @commands.has_role('Mod')
  async def cut(self, ctx, pos_to_cut: int):
    # First check that the position is in the queue
    queue_len = len(queue)
    if pos_to_cut - 1 > queue_len or pos_to_cut - 1 < 0:
      # Report Error
      desc = '{} is out of bounds! Queue length is {}'.format(
        pos_to_cut, len(self.queue))
      embed = ctx.Embed(title='Cut from queue', description=desc,
                        color=self.embed_color)
    # If we are in the queue, cut that position
    else:
      # Cut user
      cut_user = self.queue[pos_to_cut]
      self.queue = self.queue.remove(cut_user)

      # Then report back
      desc = '{} was cut from the queue!'.format(cut_user['user'])
      embed = ctx.embed(title='Cut from queue', description=desc,
                        color=self.embed_color)

    await ctx.send(embed=embed)
  # End !cut

  # !queue
  # Displays the current queue
  @commands.command()
  async def queue(self, ctx):
    # Simply return the queue
    embed = ctx.Embed(title='Current Queue',
                      description=make_queue_string(self.queue),
                      color=self.embed_color)

    await ctx.send(embed=embed)
  # End !queue

# End KaraokeBotCommands

def setup(bot):
  bot.add_cog(KaraokeBotCommands(bot))
