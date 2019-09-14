import asyncio
import discord
import cogs.utils.configloader as configloader
import cogs.utils.dbutil as dbutil
import random
from discord.ext import commands
from discord.ext.commands import bot
import os
# Import our database, if we have none we can still use this bot without DB functionality!
try:
    import cogs.db as db
    databasePresent = True
except ImportError:
    databasePresent = False
discordConfig = configloader.getDiscordValues()

if databasePresent:
    databaseConfig = configloader.getDatabaseValues()
mapList = discordConfig['vetoMapPool'].split(' ')
# Set in readysystem first, then here.
currentVeto = None
match = None
firstCaptain = None
secondCaptain = None
inProgress = False


class VetoSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(aliases=['ban'])
    async def veto(self, ctx, arg):
        """Strikes a map from the given veto list in the config.
        
        If the bot maintainer has chosen to install Get5-Web, it will also add the vetoes to the match database.
        Once the vetoes are completed, the users will then wait for the bot to configure either the given server,
        or a publically available server on the webpanel(first available). Some variables within this module
        are modified from the readysystem, since we need to pass over the match and captains.
        
        Paramaters
        ----------
        ctx : Context
            Represents the context in which a command is being invoked under.
        arg : str
            Usually the map to strike from the veto."""


        global mapList
        global currentVeto
        global match
        global firstCaptain
        global secondCaptain
        global inProgress
        # make sure they're using the bot setup channel
        if(ctx.message.channel.id != int(discordConfig['setupTextChannelID'])):
            # if they aren't using an appropriate channel, return
            return
        if(inProgress and len(mapList) != 1):
            # Who's turn is it to veto? Check if it's the captain and if it's their turn.
            # await ctx.send("Our captain name {} current veto {}".format(firstCaptain.name, currentVeto))
            if (__debug__):
                if (ctx.author != firstCaptain or ctx.author != secondCaptain):
                    embed = discord.Embed(
                        description="**{}, you are not a captain. Can you don't?**".format(ctx.author.mention), color=0xff0000)
                    await ctx.send(embed=embed)
                    return
                elif (ctx.author == firstCaptain and currentVeto == 'team2'):
                    embed = discord.Embed(
                        description="**{} It is not your turn to veto. C'mon dude.**".format(ctx.author.mention), color=0xff0000)
                    await ctx.send(embed=embed)
                    return
                elif (ctx.author == secondCaptain and currentVeto == 'team1'):
                    embed = discord.Embed(
                        description="**{} It is not your turn to veto. C'mon dude.**".format(ctx.author.mention), color=0xff0000)
                    await ctx.send(embed=embed)
                    return
            # Check to see if map exists in our message. Let users choose to use de or not.
            try:
                if(arg.startswith("de_")):
                    mapList.remove(str(arg).lower())
                else:
                    mapList.remove(str("de_"+arg).lower())
            except ValueError:
                embed = discord.Embed(
                    description="**{} does not exist in the map pool. Please try again.**".format(arg), color=0xff0000)
                await ctx.send(embed=embed)
                return
            # Now that everything is checked and we're successful, let's move on.
            if (databasePresent):
                db.create_veto(match.id, 'team_' + ctx.author.name, arg, 'ban')
            embed = discord.Embed(
                description="**Maps**\n" + " \n ".join(str(x) for x in mapList), color=0x03f0fc)
            await ctx.send(embed=embed)

            if(currentVeto == 'team1'):
                currentVeto = 'team2'
                embed = discord.Embed(description="team_{} please make your ban.".format(
                    secondCaptain.name), color=0x03f0fc)
            else:
                currentVeto = 'team1'
                embed = discord.Embed(description="team_{} please make your ban.".format(
                    firstCaptain.name), color=0x03f0fc)
            if(len(mapList) != 1):
                await ctx.send(embed=embed)
            else:
                # Decider map. Update match if we have database, present to users.
                embed = discord.Embed(
                    description="**Map**\n" + mapList[0] + "\nNow that the map has been decided, go to your favourite 10man service and set it up.", color=0x03f0fc)
                await ctx.send(embed=embed)
                inProgress = False
                firstCaptain = None
                secondCaptain = None
                if(databasePresent):
                    db.create_veto(match.id, 'Decider', mapList[0], 'pick')
                    db.update_match_maps(match.id, str(mapList[0]))
                    embed = discord.Embed(
                        description="**But wait, there's more!**\nGet5 has been enabled on this bot. Now configuring server and match, please wait...", color=0x03f0fc)
                    await ctx.send(embed=embed)
                    await ctx.trigger_typing()
                    # Get server ID from config. If not present, or occupied, then grab the first available public server.
                    if (databaseConfig['serverID']):
                        server = db.get_server(int(databaseConfig['serverID']))
                    if (server is None):
                        # Begin getting first available server.
                        servers = db.get_available_public_servers()
                        # Cycle through and ping to see if available, grab first available.
                        for singleServer in servers:
                            # Check if online.
                            if(dbutil.check_server_connection(databaseConfig['encryptionKey'].encode("latin-1"), singleServer)):
                                server = singleServer
                                break
                    # We now have the server and it's available! Setup the match.
                    url = databaseConfig['get5host'].replace("http://", "")
                    url = databaseConfig['get5host'].replace("https://", "")
                    rconPassword = dbutil.decrypt(databaseConfig['encryptionKey'].encode(
                        "latin-1"), server.rcon_password).decode("latin-1")
                    loadmatchResponse = dbutil.send_rcon_command(
                        server.ip_string, server.port, rconPassword, 'get5_loadmatch_url ' + url)
                    dbutil.send_rcon_command(
                        server.ip_string, server.port, rconPassword, 'get5_web_api_key ' + match.api_key)
                    dbutil.send_rcon_command(
                        server.ip_string, server.port, rconPassword, 'map {}'.format(str(mapList[0])))
                    if (loadmatchResponse):
                        embed = discord.Embed(
                            description="ERROR ERROR ERROR ", color=0xff0000)
                        await ctx.send(embed=embed)
                    embed = discord.Embed(description="Match setup successfully! Please navigate to {}/match/{} and connect from there.".format(
                        databaseConfig['get5host'], match.id), color=0x32CD32)
                    await ctx.send(embed=embed)
                mapList = discordConfig['vetoMapPool'].split(' ')
                currentVeto = None
                match = None
                firstCaptain = None
                secondCaptain = None
                inProgress = False
            return

    @commands.command()
    async def maps(self, ctx):
        global mapList
        """ Returns the current maps that can be striken from the veto """
        # make sure they're using the bot setup channel
        if(ctx.message.channel.id != int(discordConfig['setupTextChannelID'])):
            # if they aren't using an appropriate channel, return
            return
        embed = discord.Embed(
            description=" \n ".join(str(x) for x in mapList), title="Remaining Maps", color=0xff0000)
        await ctx.send(embed=embed)
        return

    @commands.command()
    async def stop(self, ctx):
        global mapList
        global currentVeto
        global match
        global firstCaptain
        global secondCaptain
        global inProgress
        """ Remove the vetoes and match from the database. """
        # make sure they're using the bot setup channel
        if(ctx.message.channel.id != int(discordConfig['setupTextChannelID'])):
            # if they aren't using an appropriate channel, return
            return
        if (ctx.author != firstCaptain or ctx.author != secondCaptain):
            embed = discord.Embed(
                description="**{}, you are not a captain. Can you don't?**".format(ctx.author.mention), color=0xff0000)
            await ctx.send(embed=embed)
        elif(inProgress):
            if(databasePresent):
                db.delete_vetoes(match.id)
                db.delete_match(match.id)
                match = None
            mapList = discordConfig['vetoMapPool'].split(' ')
            currentVeto = None
            firstCaptain = None
            secondCaptain = None
            inProgress = False
        else:
            embed = discord.Embed(
            description="Can't stop what hasn't been started.", color=0xff0000)
            await ctx.send(embed=embed)
        return

def setup(bot):
    bot.add_cog(VetoSystem(bot))
