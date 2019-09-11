# =============================================================================
# G5 Bot
# Copyright (C) 2019.  All rights reserved.
# =============================================================================
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import cogs.utils.configloader as config
import discord
from discord.ext import commands

databaseValues = config.getDatabaseValues()
discordValues = config.getDiscordValues()

initial_extensions = ['cogs.readysystem']

bot = commands.Bot(
    command_prefix=discordValues['prefix'], description=discordValues['description'])

# Here we load our extensions(cogs) listed above in [initial_extensions].
if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)


@bot.event
async def on_ready():

    print('------')
    print('Logged in as {} with id {}'.format(bot.user.name, bot.user.id))
    print('VC1 Name is {}\nVC2 Name is {}'.format(
        bot.get_channel(int(discordValues['team1VoiceChannelID'])),
        bot.get_channel(int(discordValues['team2VoiceChannelID']))))
    print('------')
    # loop over all the servers the bots apart

bot.run(discordValues['discordToken'])
