# G5 Bot
## Discord Bot Supplement for Get5-Web
This bot is meant to be used in supplement with [Get5-Web](https://github.com/phlexplexico/get5-web) or as a standalone 10man gathering bot.

## What does it do?
G5 Bot will allow you to create an organize ten mans, moving people to respective voice channels, and hound people to ready up after reaching a certain amount. It will be able to do vetoes within Discord via reactions, so you can avoid the hassle of setting up a server only having to go tgrough vetoes in-game. As a standalone bot, it is very limited as it will only work on the Discord side, moving people and creating teams. The real features come from the integration with the Get5-Web database.

Ideally, when the teams are created, a match will inserted into the database, and vetoes and server selection will be done through the Discord, via reacts based on the bots output. It will query the database for any available public servers, check if they're online, and add them to the list of available servers (or pick the first available, haven't decided). Once vetoes and server has been selected, the bot will send a few rcon commands to the server to setup the match, and present you with the match page, ready to connect!

## How do I run it?
```python
python3 -m venv venv
source venv/bin/activate
pip3 install requirements.txt
cp settingsTemplate.ini > settings.ini
```

If you wish to have full functionality, and you have Get5-Web installed on your system, input the get5 database user, port, host, and database name located in the `[DATABASE]` section of the INI file. Get your Discord bot token, channels, mentionable roles, etc. inputted and simply run the bot with `python bot.py`. This will launch the bot with the given settings and you should be good to go! If no database is supplied or it fails to connect, it will automagically remove the get5 functionality, so you can use it just as a regular bot to setup teams and decide on a map!

### This bot is currently in its alpha stages, and not all of the functionality has been inputted, nor tested. Please do file bug reports, and I will look into them when I have time. Pull Requests are always welcome!

## Thanks
[meeoh](https://github.com/meeoh) for his initial implementation of a discord 10man bot!

[bboychris168](https://github.com/bboychris168) for helping me with some Discord.py functionality!
