import asyncio
import discord
import cogs.utils.configloader as configloader
import random
import sqlite3
from discord.ext import commands
from discord.ext.commands import bot
import os


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
                await ctx.send("Successfully unlinked accounts!")
        except sqlite3.Error as error:
            await ctx.send("Error in adding to our sqlite3 db.", error)
        finally:
            db.close()


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