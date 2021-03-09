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
apiValues = configloader.getAPIValues()

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

        # make sure they're using the bot setup channel
        if(ctx.message.channel.id != int(discordConfig['setupTextChannelID'])):
            # if they aren't using an appropriate channel, return
            return
        if(glbls.inProgress and len(glbls.mapList) != 1):
            # Who's turn is it to veto? Check if it's the captain and if it's their turn.
            # await ctx.send("Our captain name {} current veto {}".format(firstCaptain.name, currentVeto))
            if (__debug__):
                if (ctx.author.id != glbls.firstCaptain.id and ctx.author.id != glbls.secondCaptain.id):
                    embed = discord.Embed(
                        description="**{}, you are not a captain. Can you don't?**".format(ctx.author.mention), color=0xff0000)
                    await ctx.send(embed=embed)
                    return
                elif (ctx.author.id == glbls.firstCaptain.id and glbls.currentVeto == 'team2'):
                    embed = discord.Embed(
                        description="**{} It is not your turn to veto. C'mon dude.**".format(ctx.author.mention), color=0xff0000)
                    await ctx.send(embed=embed)
                    return
                elif (ctx.author.id == glbls.secondCaptain.id and glbls.currentVeto == 'team1'):
                    embed = discord.Embed(
                        description="**{} It is not your turn to veto. C'mon dude.**".format(ctx.author.mention), color=0xff0000)
                    await ctx.send(embed=embed)
                    return
                elif(int(glbls.selectedServerId) < 0):
                    embed = discord.Embed(
                        description="**The server has not been selected yet. Please select the server before continuing.**", color=0xff0000)
                    await ctx.send(embed=embed)
                    return
            else:
                embed = discord.Embed(
                    description="**{} is currently selecting, but captain is {} or {}**".format(ctx.author.mention, glbls.firstCaptain.mention, glbls.secondCaptain.mention), color=0xff0000)
                await ctx.send(embed=embed)
            # Check to see if map exists in our message. Let users choose to use de or not.
            try:
                if(arg.startswith("de_")):
                    glbls.mapList.remove(str(arg).lower())
                    api.vetoMap(str(arg).lower(), 'team_'+ctx.author.name, glbls.matchApiID, 'ban')
                else:
                    glbls.mapList.remove(str("de_"+arg).lower())
                    api.vetoMap(str("de_"+arg).lower(), 'team_'+ctx.author.name, glbls.matchApiID, 'ban')
            except ValueError:
                embed = discord.Embed(
                    description="**{} does not exist in the map pool. Please try again.**".format(arg), color=0xff0000)
                await ctx.send(embed=embed)
                return
            except Exception as error:
                embed = discord.Embed(
                    description="**{} That's the error lmao**".format(error), color=0xff0000)
                await ctx.send(embed=embed)
                return
            # Now that everything is checked and we're successful, let's move on.
            embed = discord.Embed(
                description="**Maps**\n" + " \n ".join(str(x) for x in glbls.mapList), color=0x03f0fc)
            await ctx.send(embed=embed)

            if(glbls.currentVeto == 'team1'):
                glbls.currentVeto = 'team2'
                embed = discord.Embed(description="team_{} please make your ban.".format(
                    glbls.secondCaptain.name), color=0x03f0fc)
            else:
                glbls.currentVeto = 'team1'
                embed = discord.Embed(description="team_{} please make your ban.".format(
                    glbls.firstCaptain.name), color=0x03f0fc)
            if(len(glbls.mapList) != 1):
                await ctx.send(embed=embed)
            else:
                # Decider map. Update match if we have database, present to users.
                embed = discord.Embed(
                    description="**Map**\n" + glbls.mapList[0] + "\nNow that the map has been decided, go to your favourite 10man service and set it up.", color=0x03f0fc)
                await ctx.send(embed=embed)
                api.vetoMap(glbls.mapList[0], 'Decider', glbls.matchApiID, 'pick')
                api.assignServer(glbls.matchApiID, glbls.selectedServerId)
                strEmbed = "Match is now configured! Please navigate to {}/match/{} to connect sign in and connect to the match!".format(apiValues['get5host'][:-4], glbls.matchApiID)
                embed = discord.Embed(description=strEmbed)
                await ctx.send(embed=embed)
                glbls.inProgress = False
                glbls.firstCaptain = None
                glbls.secondCaptain = None
                glbls.mapList = discordConfig['vetoMapPool'].split(' ')
                glbls.matchApiID = -1
                glbls.currentVeto = None
            return

    @commands.command()
    async def maps(self, ctx):
        """ Returns the current maps that can be striken from the veto """
        # make sure they're using the bot setup channel
        if(ctx.message.channel.id != int(discordConfig['setupTextChannelID'])):
            # if they aren't using an appropriate channel, return
            return
        embed = discord.Embed(
            description=" \n ".join(str(x) for x in glbls.mapList), title="Remaining Maps", color=0xff0000)
        await ctx.send(embed=embed)
        return

    @commands.command()
    async def captains(self, ctx):
        embed = discord.Embed(
            description="Your captains today are: {} and {}".format(glbls.firstCaptain.mention, glbls.secondCaptain.mention), color=0x03f0fc)
        await ctx.send(embed=embed)
        return


def setup(bot):
    bot.add_cog(VetoSystem(bot))
