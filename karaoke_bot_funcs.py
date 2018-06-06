import logging

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
       -c
       --command-prefix  Command prefix to respond to in Discord. Default is "!"
    '''
)

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
