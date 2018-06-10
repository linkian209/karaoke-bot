import discord
import sqlite3
import logging
import datetime
from datetime import datetime
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

    # Remove default help
    self.bot.remove_command('help')

    # Logging
    self.log = logging.getLogger(__name__)

    # Embed Color
    self.embed_color = 0xEEE657
  # End init

  # !info
  # Returns information about the bot, the author, and other techy stuff
  @commands.command(pass_context=True)
  async def info(self, ctx):
    description = 'A Discord bot for running a karaoke queue'
    embed = discord.Embed(title='Karaoke Bot', description=description,
                          color=self.embed_color)
    embed.add_field(name='Author', value='linkian209')
    embed.add_field(name='Source',
                    value='[Code](https://github.com/linkian209/karaoke-bot)')
    embed.add_field(name='Questions/Comments',
                    value='[Email](mailto://linkian209@gmail.com)')
    embed.add_field(name='Add me to your server!',
                    value='[Click Me!](https://discordapp.com/api/oauth2/authorize?client_id=451160132139614219&permissions=6144&scope=bot)')

    await ctx.send(embed=embed)
  # End !info

  # !help
  # Print all of the commands that the bot can use
  @commands.command(pass_context=True)
  async def help(self, ctx):
    description = 'The list of commands for the Karaoke Bot'

    # Commands and their descriptions
    commands = [
      'info',
      'help',
      'addMe (Song Name)',
      'removeMe',
      'next',
      'clear',
      'showQueue'
    ]

    mod_commands = [
      'add [Username] (Song Name)',
      'remove [Username]',
      'skipTop',
      'color',
      'cut'
    ]

    descriptions = [
      '\tDisplays information about the bot. Ex: `{}info`',
      '\tDisplays the list of commands. Ex: `{}help`',
      '\tAdds self to queue. Can optionally add the song name. Ex: `{}addMe "Uptown Girl"`',
      '\tRemoves self from the queue. Ex: `{}removeMe`',
      '\tProgress to the next user in the queue. Also shows who is on deck. Ex: `{}next`',
      '\tClears the queue. Ex: `{}clear`',
      '\tDisplays current queue. Ex: `{}showQueue`'
    ]

    mod_descriptions = [
      '\t*Mod Only* Add a user to the queue. Can optionally add the song name. Ex: `{}add user123 "Uptown Girl"`',
      '\t*Mod Only* Remove a user from the queue. Ex: `{}remove user123`',
      '\t*Mod Only* Moves supplied username to front of queue. Ex: `{}skipTop user456`',
      '\t*Mod Only* Sets color for bot embeds. Ex: `{}color 0xDADADA`',
      '\t*Mod Only* Removes user at supplied index from the queue. `{}cut 3`'
    ]

    # Create the response
    embed = discord.Embed(title='Karaoke Bot', description=description, color=self.embed_color)

    # Loop through all commands
    count = 0
    for command in commands:
      cur_command = command
      cur_description = descriptions[count].format(self.bot.command_prefix)
      embed.add_field(name=cur_command, value=cur_description, inline=False)
      count += 1

    # If user is a mod, send the mod commands
    if 'Mod' in [x.name for x in ctx.message.author.roles]:
      count = 0
      for command in mod_commands:
        cur_command = command
        cur_description = mod_descriptions[count].format(self.bot.command_prefix)
        embed.add_field(name=cur_command, value=cur_description, inline=False)
        count += 1

    # Return
    await ctx.message.author.send(embed=embed)
  # End !help

  # !add
  # Add a user (with an optional song) to the self.queue
  @commands.command(pass_context=True)
  @commands.has_role('Mod')
  async def add(self, ctx, user: str, song: str=None):
    # Add person to self.queue, if they aren't already in line
    in_queue = False
    for item in self.queue:
      if item['user'] == user:
        in_queue = True
        break

    if not in_queue:
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
    embed.add_field(name='Current Order', value=make_queue_string(self.queue),
                    inline=False)

    await ctx.send(embed=embed)
  # End !add

  # !remove
  # Remove user from self.queue
  @commands.command(pass_context=True)
  @commands.has_role('Mod')
  async def remove(self, ctx, user: str):
    # If the user is in the self.queue, remove them
    for item in self.queue:
      if item['user'] == user:
        self.queue.remove(item)

    # Create response
    description = 'Removing user {} from queue'.format(user)
    embed = discord.Embed(title='Removing user', description=description,
                          color=self.embed_color)
    embed.add_field(name='Current Order', value=make_queue_string(self.queue),
                    inline=False)

    await ctx.send(embed=embed)
  # End !remove

  #!next
  # Advances the self.queue up one and displays who is on deck
  @commands.command(pass_context=True)
  async def next(self, ctx):
    # First check if there is anyone in the queue
    if len(self.queue) is 0:
      desc = 'There is currently no one in the queue!'
      embed = discord.Embed(title='Next Up', description=desc,
                            color=self.embed_color)
      await ctx.send(embed=embed)

    # Get current user and on deck user
    cur_user = self.queue[0]
    on_deck = None
    if len(self.queue) > 1:
      on_deck = self.queue[1]

    # Pop from self.queue
    self.queue.remove(cur_user)

    # Connect to database
    db_conn = sqlite3.connect(database_name)
    curs = db_conn.cursor()

    # Update statistics on user
    # Check if the user exists
    curs.execute('SELECT count(1) FROM users WHERE username = ?',
                 (cur_user['user'],))
    count = curs.fetchone()[0]

    # If the user exists, update their record
    if count is not 0:
      if cur_user['song'] is not None:
        # First Update user records
        params = (cur_user['song'], datetime.now(), cur_user['user'])
        curs.execute('''UPDATE users
                           SET last_song = ?,
                               last_date = ?,
                               times_sung = times_sung + 1
                         WHERE username = ?''', params)
        db_conn.commit()

      else:
        params = (datetime.now(), cur_user['user'])
        curs.execute('''UPDATE users
                           SET last_date = ?,
                               times_sung = times_sung + 1
                         WHERE username = ?''', params)
        db_conn.commit()
    # User does not exist, make record
    else:
      if cur_user['song'] is not None:
        params = (cur_user['user'], cur_user['song'],
                  datetime.now(), 1)
        curs.execute('''INSERT INTO users
                        (username, last_song, last_date, times_sung)
                        VALUES(?,?,?,?)''', params)
        db_conn.commit()
      else:
        params = (cur_user['user'], datetime.now(), 1)
        try:
          curs.execute('''INSERT INTO users
                          (username, last_date, times_sung)
                          VALUES(?,?,?)''', params)
          db_conn.commit()
        except sqlite3.Error as e:
          print('An error has occured: {}', e.args[0])

    # Now update song record
    if cur_user['song'] is not None:
      # Check if it exists
      params = (cur_user['song'], cur_user['user'])
      curs.execute('''SELECT count(1) FROM songs
                      WHERE song_name = ? AND username = ?''', params)
      count = curs.fetchone()[0]

      # If it exists, update
      if count is not 0:
        params = (datetime.now(), cur_user['song'], cur_user['user'])
        curs.execute('''UPDATE songs
                           SET times_sung = times_sung + 1,
                               last_sung = ?
                        WHERE song_name = ?
                          AND username = ?''', params)
        db_conn.commit()
      # Song does not exist in records, insert record
      else:
        params = (cur_user['song'], cur_user['user'],
                  datetime.now(), 1)
        curs.execute('''INSERT INTO songs
                        (song_name, username, times_sung, last_sung)
                        VALUES (?,?,?,?)''', params)
        db_conn.commit()

    # Commit database changes then close
    db_conn.close()

    # Make response
    next_up_desc = cur_user['user']
    if cur_user['song'] is not None:
      next_up_desc += ' singing {}'.format(cur_user['song'])

    embed = discord.Embed(title='Next Up', description=next_up_desc,
                          color=self.embed_color)

    # If we have someone on deck, report that!
    if on_deck is not None:
      on_deck_desc = on_deck['user']
      # Add song if we have one
      if on_deck['song'] is not None:
        on_deck_desc += ' singing {}'.format(on_deck['song'])

      embed.add_field(name='On Deck', value=on_deck_desc)

    embed.add_field(name='Current Queue', value=make_queue_string(self.queue),
                    inline=False)

    await ctx.send(embed=embed)
  # End !next

  # !skipTop
  # Supplied user name gets shoved to the front of the queue
  @commands.command(pass_context=True)
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
    embed = discord.Embed(title='Skipping to the Top', description=desc,
                      color=self.embed_color)
    embed.add_field(name='Current Queue', value=make_queue_string(self.queue),
                    inline=False)

    await ctx.send(embed=embed)
  # end !skipTop

  # !color
  # Sets the embed color. Must have 'Mod' role
  @commands.command(pass_context=True)
  @commands.has_role('Mod')
  async def color(self, ctx, color: str):
    # Update color
    old_color = self.embed_color

    # Update color
    try:
      new_color = int(color, 0)

      # Make sure new color is in range
      if new_color >= 0 and new_color <= 16777215:
        self.embed_color = new_color

        # Update worked!
        desc = 'Changed color from {} to {}'.format(hex(old_color), color)
        embed = discord.Embed(title='Color Change', description=desc,
                          color=self.embed_color)
      # Show error
      else:
        desc = ("{} is not a valid color, please stay within 0x000000 "
                "and 0xFFFFFF").format(hex(new_color))
        embed = discord.Embed(title='Color Change', description=desc,
                          color=self.embed_color)
    except Exception as e:
      self.log.error('{}: {}'.format(type(e).__name__, str(e)))
      desc = 'Something went wronging changing color to {}'.format(color)
      embed = discord.Embed(title='Color Change', description=desc,
                        color=self.embed_color)

    await ctx.send(embed=embed)
  # End !color

  # !cut
  # Cuts user at specified index from the queue
  @commands.command(pass_context=True)
  @commands.has_role('Mod')
  async def cut(self, ctx, pos_to_cut: int):
    # First check that the position is in the queue
    queue_len = len(self.queue)
    if pos_to_cut - 1 > queue_len or pos_to_cut - 1 < 0:
      # Report Error
      desc = '{} is out of bounds! Queue length is {}'.format(
        pos_to_cut, len(self.queue))
      embed = discord.Embed(title='Cut from queue', description=desc,
                        color=self.embed_color)
    # If we are in the queue, cut that position
    else:
      # Cut user
      cut_user = self.queue[pos_to_cut - 1]
      self.queue.remove(cut_user)

      # Then report back
      desc = '{} was cut from the queue!'.format(cut_user['user'])
      embed = discord.Embed(title='Cut from queue', description=desc,
                        color=self.embed_color)

    await ctx.send(embed=embed)
  # End !cut

  # !showQueue
  # Displays the current queue
  @commands.command(pass_context=True)
  async def showQueue(self, ctx):
    # Simply return the queue
    embed = discord.Embed(title='Current Queue',
                          description=make_queue_string(self.queue),
                          color=self.embed_color)

    await ctx.send(embed=embed)
  # End !queue

  # !clear
  # Clears the queue
  @commands.command(pass_context=True)
  async def clear(self, ctx):
    # Clear queue
    self.queue = []

    # Return
    embed = discord.Embed(title='Clear Queue',
                      description='Queue Cleared!',
                      color=self.embed_color)

    await ctx.send(embed=embed)
  # End !clear

  # !addMe
  # Adds author of message to the queue. Song can also be added
  @commands.command(pass_context=True)
  async def addMe(self, ctx, song: str=None):
    # Get user
    user = ctx.message.author.name

    # Add person to self.queue, if they aren't already in line
    in_queue = False
    for item in self.queue:
      if item['user'] == user:
        in_queue = True
        break

    if not in_queue:
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
    embed.add_field(name='Current Order', value=make_queue_string(self.queue),
                    inline=False)

    await ctx.send(embed=embed)
  # End !addMe

  # !removeMe
  # Removes author from queue
  @commands.command(pass_context=True)
  async def removeMe(self, ctx):
    # Get User
    user = ctx.message.author.name

    # If the user is in the queue, remove them
    for item in self.queue:
      if item['user'] == user:
        self.queue.remove(item)

    # Create response
    description = 'Removing user {} from queue'.format(user)
    embed = discord.Embed(title='Removing user', description=description,
                          color=self.embed_color)
    embed.add_field(name='Current Order', value=make_queue_string(self.queue),
                    inline=False)

    await ctx.send(embed=embed)
  # End !removeMe

# End KaraokeBotCommands

def setup(bot):
  bot.add_cog(KaraokeBotCommands(bot))
