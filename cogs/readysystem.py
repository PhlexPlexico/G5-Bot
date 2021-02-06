import asyncio
import discord
import cogs.utils.api as api
import cogs.utils.configloader as configloader
import random
import cogs.vetosystem as vetosystem
import cogs.globals as glbls
from cogs.linksystem import checkLink
from discord.ext import commands
from discord.ext.commands import bot
import os
discordConfig = configloader.getDiscordValues()




class ReadySystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['gaben'])
    async def ready(self, ctx):
        # we received a message
        # modifying these globals

        # extract the author and message from context.
        author = ctx.author
        message = ctx.message

        # make sure they're using the bot setup channel
        if(message.channel.id != int(discordConfig['setupTextChannelID'])):
            # await ctx.send("Lmao u suck message chan id is {} and config id is {}".format(message.channel.id, discordConfig['setupTextChannelID']))
            return

        # ready command
        if (not glbls.inProgress and len(glbls.readyUsers) < 10):
            # check if they are already ready. If debug, then we can allow users to join multiple times.
            if(author in glbls.readyUsers and __debug__):
                embed = discord.Embed(
                    description=author.mention + "You're already ready, chill.", color=0x03f0fc)
                await ctx.send(embed=embed)
                return
            elif (checkLink(author.id) and __debug__):
                embed = discord.Embed(
                    description=author.mention + "You haven't linked accounts. Please use !link \{steam account\} before continuing.", color=0x03f0fc)
                await ctx.send(embed=embed)
                return
            # actually readying up
            else:
                # add them to the ready list and send a message
                glbls.readyUsers.append(author)
                if(len(glbls.readyUsers) == 8 or len(glbls.readyUsers) == 9):
                    embed = discord.Embed(description="<@&" + discordConfig['mentionableID'] + ">" + " we only need " + str(
                        10 - len(glbls.readyUsers)) + " more players. `!ready` to join", color=0x03f0fc)
                    await ctx.send(embed=embed)
                elif(len(glbls.readyUsers) == 10):
                    # we have 10 ready users, now need captains
                    embed = discord.Embed(
                        description="**WE BALLIN'. Now randomly selecting captains.**", color=0x03f0fc)
                    await ctx.send(embed=embed)
                    await ctx.trigger_typing()
                    glbls.inProgress = True
                    glbls.firstCaptain = glbls.readyUsers[random.randrange(
                        len(glbls.readyUsers))]
                    glbls.readyUsers.remove(glbls.firstCaptain)
                    glbls.secondCaptain = glbls.readyUsers[random.randrange(
                        len(glbls.readyUsers))]
                    glbls.readyUsers.remove(glbls.secondCaptain)
                    embed = discord.Embed(description="**Captains**\nTeam: " +
                                          glbls.firstCaptain.mention + "\nTeam: " + glbls.secondCaptain.mention, color=0x03f0fc)
                    await ctx.send(embed=embed)
                    embed = discord.Embed(description=glbls.firstCaptain.mention + " it is now your pick, pick with `" + discordConfig['prefix'] +
                                          "pick @user`. Please choose from\n" + " \n ".join(str(x.mention) for x in glbls.readyUsers), color=0x03f0fc)
                    await ctx.send(embed=embed)

                    glbls.team1ApiID = api.createTeam("team_"+glbls.firstCaptain.name, glbls.firstCaptain.id, glbls.firstCaptain.name)
                    glbls.team2ApiID = api.createTeam("team_"+glbls.secondCaptain.name, glbls.secondCaptain.id, glbls.secondCaptain.name)
                    # Retrieve servers as well.
                    glbls.serverList = api.getAvailablePublicServers()
                    glbls.serverList.extend(api.getListedServers())
                elif(len(glbls.readyUsers) != 0):
                    embed = discord.Embed(description=author.mention + " **is now ready, we need **" + str(
                        10 - len(glbls.readyUsers)) + " **more**", color=0x03f0fc)
                    await ctx.send(embed=embed)
                return

        return

    @commands.command(aliases=['ungaben', 'notready'])
    async def unready(self, ctx):
        # make sure they're using the bot setup channel
        if(ctx.message.channel.id != int(discordConfig['setupTextChannelID'])):
            # if they aren't using an appropriate channel, return
            return

        author = ctx.author
        if(glbls.inProgress):
            embed = discord.Embed(description=author.mention +
                                  " You dare leave during the team selection? How dare you.", color=0x3f0fc)
            await ctx.send(embed=embed)
            return

        try:
            glbls.readyUsers.remove(author)
            # unready message
            embed = discord.Embed(description=author.mention + " You are no longer ready. We now need " +
                                  str(10 - len(glbls.readyUsers)) + " more", color=0x3f0fc)
            await ctx.send(embed=embed)
        except ValueError:
            embed = discord.Embed(description=author.mention +
                                  " You are not in the ready list to begin with!", color=0x3f0fc)
            await ctx.send(embed=embed)

        return

    @commands.command(aliases=['stop'])
    async def done(self, ctx):
        # make sure they're using the bot setup channel
        if(ctx.message.channel.id != int(discordConfig['setupTextChannelID'])):
            # if they aren't using an appropriate channel, return
            return
        if(glbls.inProgress):
            api.deleteTeam(glbls.team1ApiID)
            api.deleteTeam(glbls.team2ApiID)
            api.deleteVetoes(glbls.matchApiID)
            api.cancelMatch(glbls.matchApiID)
        glbls.inProgress = False
        glbls.readyUsers = []
        glbls.firstCaptain = None
        glbls.secondCaptain = None
        glbls.teamOne = []
        glbls.teamTwo = []
        glbls.pickNum = 1
        # Don't care if we don't delete or not, just force it.
        glbls.team1ApiID = -1
        glbls.team2ApiID = -1
        glbls.matchApiID = -1
        glbls.mapList = discordConfig['vetoMapPool'].split(' ')
        glbls.currentVeto = None
        embed = discord.Embed(
            description="**Current 10man finished, need** 10 **readied players**", color=0xff0000)
        await ctx.send(embed=embed)
        return

    @commands.command()
    async def whosready(self, ctx):
        # make sure they're using the bot setup channel
        if(ctx.message.channel.id != int(discordConfig['setupTextChannelID'])):
            # if they aren't using an appropriate channel, return
            return
        if (len(glbls.readyUsers) == 0):
            embed = discord.Embed(
                description="There is currently no players in queue!", color=0xff0000)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(description="__**Readied Users:**__ \n" +
                                  " \n ".join(sorted(str(x.name) for x in glbls.readyUsers)), color=0xebe534)
            await ctx.send(embed=embed)
        return

    @commands.command()
    async def pick(self, ctx):
        # Get the voice channels.
        if glbls.team1VoiceChannel is None:
            glbls.team1VoiceChannel = ctx.bot.get_channel(
                int(discordConfig['team1VoiceChannelID']))
        if glbls.team2VoiceChannel is None:
            glbls.team2VoiceChannel = ctx.bot.get_channel(
                int(discordConfig['team2VoiceChannelID']))
        # make sure they're using the bot setup channel
        if(ctx.message.channel.id != int(discordConfig['setupTextChannelID'])):
            # if they aren't using an appropriate channel, return
            return
        if (glbls.inProgress and glbls.pickNum < 9):
            author = ctx.author
            message = ctx.message
            # make sure a captain is picking, and its his turn
            if (author == glbls.firstCaptain and (glbls.pickNum == 1 or glbls.pickNum == 4 or glbls.pickNum == 6 or glbls.pickNum == 8)):
                # get the user they picked
                if(len(message.mentions) != 1):
                    embed = discord.Embed(
                        description="Please pick a user by @ing them. `" + discordConfig['prefix'] + "pick @user`", color=0x03f0fc)
                    await ctx.send(embed=embed)
                    return

                pickedUser = message.mentions[0]
                # make sure hes a real user
                if(pickedUser not in (name for name in glbls.readyUsers)):
                    embed = discord.Embed(description=str(
                        pickedUser) + " `is not in the 10man, please pick again.`", color=0x03f0fc)
                    await ctx.send(embed=embed)
                    return

                # add him to team one
                glbls.teamOne.append(pickedUser)
                api.addPlayer(glbls.team1ApiID, pickedUser.id, pickedUser.name)
                # move him to voice channel for team 1
                try:
                    await pickedUser.move_to(glbls.team1VoiceChannel)
                except (AttributeError, discord.errors.HTTPException):
                    embed = discord.Embed(description=str(
                        pickedUser.name) + " `is not connected to voice, however we will continue user selection.`", color=0xff0000)
                    await ctx.send(embed=embed)

                # remove him from ready users
                glbls.readyUsers.remove(pickedUser)

                # increment pick number
                glbls.pickNum += 1
                # check if we're done picking
                if(glbls.pickNum == 9):
                    strServers = "The teams are now made and bot setup is finished."
                    strServers = strServers + "\nTeam {}: ".format(glbls.firstCaptain.name) + ", ".join(str(x.name) for x in glbls.teamOne)
                    strServers = strServers + "\nTeam {}: ".format(glbls.secondCaptain.name) + ", ".join(str(x.name) for x in glbls.teamTwo)
                    strServers = strServers + "\nPlease select from the following servers via `{}select [server_id]`.\n".format(discordConfig['prefix'])
                    for server in glbls.serverList:
                        strServers = strServers + "\n**ID:** {}\n**Name:** {}\n **Country:** :flag_{}:\n".format(server['id'], server['display_name'], server['flag'].lower())
                    
                    try:
                        await glbls.firstCaptain.move_to(glbls.team1VoiceChannel)
                    except (AttributeError, discord.errors.HTTPException):
                        embed = discord.Embed(description=str(
                            pickedUser.name) + " `is not connected to voice, however we will continue user selection.`", color=0xff0000)
                        await ctx.send(embed=embed)
                    try:
                        await glbls.secondCaptain.move_to(glbls.team2VoiceChannel)
                    except (AttributeError, discord.errors.HTTPException):
                        embed = discord.Embed(description=str(
                            pickedUser.name) + " `is not connected to voice, however we will continue user selection.`", color=0xff0000)
                        await ctx.send(embed=embed)

                    embed = discord.Embed(description=strServers, color=0x3f0fc)
                    await ctx.send(embed=embed)
                    glbls.readyUsers = []
                    glbls.teamOne = []
                    glbls.teamTwo = []

                    # Create the match without the server.
                    glbls.matchApiID = api.createMatch(glbls.team1ApiID, glbls.team2ApiID)
                    glbls.pickNum = 1
                    return
                # check if we need to pick again or its other captains turn
                if (glbls.pickNum == 2 or glbls.pickNum == 3 or glbls.pickNum == 5 or glbls.pickNum == 7):
                    embed = discord.Embed(description=glbls.secondCaptain.mention + " it is now your pick, pick with `" +
                                          discordConfig['prefix'] + "pick @user`. Please choose from " + " \n ".join(str(x.mention) for x in glbls.readyUsers), color=0x03f0fc)
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(description=glbls.firstCaptain.mention + " it is now your pick, pick with `" +
                                          discordConfig['prefix'] + "pick @user`. Please choose from " + " \n ".join(str(x.mention) for x in glbls.readyUsers), color=0x03f0fc)
                    await ctx.send(embed=embed)
                return

            elif (author == glbls.secondCaptain and (glbls.pickNum == 2 or glbls.pickNum == 3 or glbls.pickNum == 5 or glbls.pickNum == 7)):
                # get the user they picked
                if(len(message.mentions) != 1):
                    embed = discord.Embed(
                        description="Please pick a user by @ing them. `" + discordConfig['prefix'] + "pick @user`", color=0x03f0fc)
                    await ctx.send(embed=embed)
                    return

                pickedUser = message.mentions[0]
                glbls.teamTwo.append(pickedUser)

                # move him to voice channel for team 2
                try:
                    await pickedUser.move_to(glbls.team2VoiceChannel)
                except (AttributeError, discord.errors.HTTPException):
                    embed = discord.Embed(description=str(
                        pickedUser.name) + " `is not connected to voice, however we will continue user selection.`", color=0xff0000)
                    await ctx.send(embed=embed)

                api.addPlayer(glbls.team2ApiID, pickedUser.id, pickedUser.name)

                # remove him from ready users
                glbls.readyUsers.remove(pickedUser)

                glbls.pickNum += 1
                if(glbls.pickNum == 1 or glbls.pickNum == 4 or glbls.pickNum == 6 or glbls.pickNum == 8):
                    embed = discord.Embed(description=glbls.firstCaptain.mention + " it is now your pick, pick with `" +
                                          discordConfig['prefix'] + "pick @user`. Please choose from " + " \n ".join(str(x.mention) for x in glbls.readyUsers), color=0x03f0fc)
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(description=glbls.secondCaptain.mention + " it is now your pick, pick with `" +
                                          discordConfig['prefix'] + "pick @user`. Please choose from " + " \n ".join(str(x.mention) for x in glbls.readyUsers), color=0x03f0fc)
                    await ctx.send(embed=embed)
                return
            else:
                embed = discord.Embed(
                    description="You're not a captain, sorry, but please let the captains select!", color=0x03f0fc)
                await ctx.send(embed=embed)
        return


def setup(bot):
    bot.add_cog(ReadySystem(bot))
