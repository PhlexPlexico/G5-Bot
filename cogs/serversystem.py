import asyncio
import discord
import cogs.globals as glbls
import cogs.utils.api as api
import cogs.utils.configloader as configloader
import random
import cogs.globals as glbls
from discord.ext import commands
from discord.ext.commands import bot
import os
discordConfig = configloader.getDiscordValues()

class ServerSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def servers(self, ctx):
        servers = api.getAvailablePublicServers()
        servers.extend(api.getListedServers())
        strServers = ""
        for server in servers:
                strServers = strServers + "\n**ID:** {}\n**Name:** {}\n **Country:** :flag_{}:\n".format(server['id'], server['display_name'], server['flag'].lower())
        embed = discord.Embed(
            description=strServers, color=0x03f0fc)
        await ctx.send(embed=embed)
        return

    @commands.command()
    async def select(self, ctx, arg):
        if(ctx.message.channel.id != int(discordConfig['setupTextChannelID'])):
            # if they aren't using an appropriate channel, return
            return
        if(not glbls.inProgress):
            return
        glbls.selectedServerId = arg
        # Randomly select who vetoes first.
        glbls.currentVeto = 'team1' if random.getrandbits(
            1) else 'team2'
        if (glbls.currentVeto == "team1"):
            firstToVeto = "team_{}".format(glbls.firstCaptain)
        else:
            firstToVeto = "team_{}".format(glbls.secondCaptain)
        embedStr = '''
        Selected server {}
        \n***Now onto vetoes!***
        \nFor vetoes, please use `{}veto map_name` or `{}ban map_name` to strike a map. Last map will be the decider.\n\n
        **Our current maps are:**\n
        '''.format(glbls.selectedServerId, discordConfig['prefix'], discordConfig['prefix'])
        embedStr = embedStr + discordConfig['vetoMapPool'].replace(' ', '\n')
        embedStr = embedStr + "\n\n**{}** please make the first veto.".format(firstToVeto)
        embed = discord.Embed(
            description=embedStr, color=0x03f0fc)
        await ctx.send(embed=embed)
        return
def setup(bot):
    bot.add_cog(ServerSystem(bot))