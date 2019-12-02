# Karaoke Discord Bot
A bot for running a karaoke queue in a Discord Server using Python 3.7

# SQLite
Since I designed this bot to run on a Raspberry Pi, I have decided to use SQLite3. This is fine because Python has tight integration with it... and nothing else works out of the box.

# Service
A systemctl service file is included for use. It requires screen to use, so you may need to `sudo apt-get install screen`. This service expects the code to be in the directory /users/discord/karaoke_bot

To install it:
1. Copy the file to /etc/systemd/system/ under the name discord_service@.service
2. `sudo systemctl enable discord_service@karaoke_bot`
3. ???
4. Profit

systemctl should start the screen session up. You can attach to the screen session by typing `screen -r discord-karaoke_bot`. This will allow you to see the console output. If you wish to disconnect from the screen session while keeping it running, press `Ctrl+a` then `Ctrl+d`.

# Configuration File
The systemctl service does not provide command line arguments. You can utilize the configuration file to provide the arguments.

# Requirements
* discord.py

# Updates
I was forced to update the version of discord.py, and thus the python version, to fix an issue with reactions breaking the bot. I have refactored the code to now work inside a virtualenv, please take note.
