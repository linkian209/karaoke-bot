import logging
import sqlite3

# Utility Functions

# usage
# Prints script arguments
def usage():
  print(
    '''Usage: python karaoke_bot.py [-t|--token] <TOKEN> (options)
       \b\bRequired Options:
       -t
       --token           App Token used for discord\n
       \b\bOptional Options:
       -c
       --command-prefix  Command prefix to respond to in Discord. Default is "!"
    '''
)

# make_queue_string
# Returns a markdown string for the inputted queue
def make_queue_string(queue):
  # Loop through queue and make a markdown string
  cur_queue = ''
  order = 0
  for item in queue:
    order += 1
    cur_queue += '{}. {}'.format(order, item['user'])
    if item['song'] is not None:
      cur_queue += ' singing {}\n'.format(item['song'])
    else:
      cur_queue += '\n'

  # If the queue was empty, report that!
  if cur_queue == '':
    cur_queue = "Empty!"

  return cur_queue

# End Utility Functions

# configure_database
# Creates sqlite3 database for Karaoke Bot to use
def configure_database():
  # Open connection to file
  db_conn = sqlite3.connect('karaokebot.sqlt')
  curs = db_conn. cursor()

  # Create the users table
  curs.execute('''CREATE TABLE users (
                    username   text not null,
                    server     number not null,
                    last_song  test,
                    last_date  date,
                    times_sung number,
                    primary key(username, server))''')

  # Create the songs table
  curs.execute('''CREATE TABLE songs (
                    song_name  text not null,
                    username   text not null,
                    server     number not null,
                    times_sung real,
                    last_sung  date,
                    primary key(song_name, username, server))''')

  # Done!
  db_conn.commit()
  db_conn.close()
