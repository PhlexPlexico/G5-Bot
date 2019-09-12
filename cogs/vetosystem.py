import asyncio
import discord
import cogs.utils.configloader as configloader
import random
from discord.ext import commands
from discord.ext.commands import bot
import os
# Import our database, if we have none we can still use this bot without DB functionality!
try:
    import cogs.db as db
    databasePresent=True
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
            await ctx.send("Our captain name {} current veto {}".format(firstCaptain.name, currentVeto))
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
            # Check to see if map exists in our message.
            try:
                mapList.remove(str(arg))
            except ValueError:
                embed = discord.Embed(
                        description="**{} does not exist in the map pool. Please try again.**".format(arg), color=0xff0000)
                await ctx.send(embed=embed)
                return
            # Now that everything is checked and we're successful, let's move on.
            if (databasePresent):
                db.create_veto(match.id, 'team_' + ctx.author.name, arg, 'ban')
            embed = discord.Embed(description="**Maps**\n"+ " \n ".join(str(x) for x in mapList), color=0x03f0fc)
            await ctx.send(embed=embed)
            
            if(currentVeto == 'team1'):
                currentVeto = 'team2'
                embed = discord.Embed(description="team_{} please make your ban.".format(secondCaptain.name), color=0x03f0fc)
            else:
                currentVeto = 'team1'
                embed = discord.Embed(description="team_{} please make your ban.".format(firstCaptain.name), color=0x03f0fc)
            if(len(mapList) != 1):
                await ctx.send(embed=embed)
            else:
                # Decider map. Update match if we have database, present to users.
                embed = discord.Embed(description="**Map**\n" + mapList[0] + "\nNow that the map has been decided, go to your favourite 10man service and set it up.", color=0x03f0fc)
                await ctx.send(embed=embed)
                inProgress = False
                firstCaptain = None
                secondCaptain = None
                if(databasePresent):
                    db.create_veto(match.id, 'Decider', mapList[0], 'pick')
                    db.update_match_maps(match.id, str(mapList[0]))
                    embed = discord.Embed(description="But wait, there's more! Get5 has been enabled on this bot. Now configuring server and match...", color=0x03f0fc)
                    await ctx.send(embed=embed)

                    # TODO: STEAM IMPLEMENTATION
            return
        else:
            await ctx.send("Our maplist is at {} and this is a debug statement. GG.".format(len(mapList)))
            
def setup(bot):
    bot.add_cog(VetoSystem(bot))
