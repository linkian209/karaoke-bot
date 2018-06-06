# Karaoke Discord Bot
A bot for running a karaoke queue in a Discord Server

# SQLite
Since I designed this bot to run on a Raspberry Pi, I have decided to use SQLite3. This is fine because Python has tight integration with it... and nothing else works out of the box.

# Requirements
* discord.py
  * pip install -U git+https://github.com/Rapptz/discord.py@rewrite#egg=discord.py[voice]
