import asyncio
import cogs.utils.configloader as configloader
import discord
from cogs.globals import discordConfig
from discord.ext import commands
from discord.ext.commands import bot
import os
import random
import sqlite3

class LinkSystem(commands.Cog):
    def __init__(self, bot):
        # Create the database if it doesn't exist.
        if not os.path.isfile(r"./steam_auths.db"):
            db = sqlite3.connect(r"./steam_auths.db")
            newCur = db.cursor()
            newCur.execute("CREATE TABLE steam_auth (discord_id, steam_id)")
            db.commit()
        self.bot = bot
    
    @commands.command(aliases=['link'])
    async def linkSteam(self, ctx, arg):
        try:
            db = sqlite3.connect(r"./steam_auths.db")
            res = db.cursor().execute("SELECT count(*) FROM steam_auth WHERE discord_id=?", [ctx.author.id])
            if (res.fetchone()[0] > 0):
                await ctx.send("You're already linked!")
            else:
                newVal = (ctx.author.id, arg)
                db.cursor().execute("INSERT INTO steam_auth (discord_id, steam_id) VALUES (?,?);", newVal)
                db.commit()
                tmpRole = ctx.guild.get_role(int(discordConfig['mentionableID']))
                await ctx.author.add_roles(tmpRole)
                await ctx.send("Successfully linked accounts!")
        except sqlite3.Error as error:
            await ctx.send("Error in adding to our sqlite3 db.", error)
        finally:
            db.close()
    @commands.command(aliases=['unlink'])
    async def unlinkSteam(self, ctx):
        try:
            db = sqlite3.connect(r"./steam_auths.db")
            res = db.cursor().execute("SELECT count(*) FROM steam_auth WHERE discord_id=?", [ctx.author.id])
            if (res.fetchone()[0] < 1):
                await ctx.send("You're not linked!")
            else:
                db.cursor().execute("DELETE FROM steam_auth WHERE discord_id = ?;", [ctx.author.id])
                db.commit()
                tmpRole = ctx.guild.get_role(int(discordConfig['mentionableID']))
                await ctx.author.remove_roles(tmpRole)
                await ctx.send("Successfully unlinked accounts!")
        except sqlite3.Error as error:
            await ctx.send("Error in adding to our sqlite3 db.", error)
        finally:
            db.close()

    @commands.command(aliases=['halp'])
    async def helpsetup(self, ctx):
        try:
            apiUrl = configloader.getAPIValues()
            helpText = """Hey there! This is PugBot. PugBot is meant to be used privately to setup 10mans within a Discord, and link all your stats to G5API - """+apiUrl['get5host']+""".
            
            In order to get started, please link your account by using the !link command, followed by your steam URL.
            `"""+discordConfig['prefix']+"""link https://steamcommunity.com/id/phlexplexico`
            as an example.
            
            If you wish to unlink and not be mentioned and join 10mans, just call """+discordConfig['prefix']+"""unlink.
            
            To ready for a match, call !ready. Make sure you're in a voice channel so I can move you to the proper team channel when captains pick their teammates.
            As a captain, you can do the following to pick a user:
            `"""+discordConfig['prefix']+"""pick @user`
            to choose a user. Once captains have chosen all their teammates, I will randomly select a team to start the veto process.
            
            In order to veto, all you have to call is
            `"""+discordConfig['prefix']+"""ban [map_name]`
            Where [map_name] is in the list.
            
            After that, there will be a server selection, brought to you by whoever has set me up! Once the server gets selected, you'll be off to the races to start a match!"""
            await ctx.send(helpText)
        except sqlite3.Error as error:
            await ctx.send("I can't help you :)")

def setup(bot):
    bot.add_cog(LinkSystem(bot))

def checkLink(id):
    try:
        db = sqlite3.connect(r"./steam_auths.db")
        res = db.cursor().execute("SELECT count(*) FROM steam_auth WHERE discord_id=?", [id])
        if (res.fetchone()[0] < 1):
            return True
        else:
            return False
    except sqlite3.Error as error:
        return False
    finally:
        db.close()