
# Utility Functions

# Usage
# Prints script arguments
def usage():
  print(
    '''Usage: python karaoke_bot.py [-t|--token] <TOKEN> (options)
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

def make_queue_string(queue):
  # Loop through queue and make a markdown string
  cur_queue = ''
  order = 0
  for item in queue:
    order += 1
    cur_queue += '{}. {}'.format(order, item['user'])
    if item['song'] is not None:
      cur_queue += ' singing {}\n'
    else:
      cur_queue += '\n'

  return cur_queue

# End Utility Functions
