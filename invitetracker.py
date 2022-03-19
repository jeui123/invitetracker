import discord
import requests
import logging
import sqlite3
import json
import os
import os.path
import re
import asyncio
from discord.ext import commands
from contextlib import closing
from discord.ext.commands import has_permissions, MissingPermissions
from discord import Member


if not os.path.exists("config.json"):
    f = open("config.json", "w")
    default_json= {
        "token": "",
        "guild-id": "",
        "logs-channel": "",
        "role1-id": "",
        "role1-pts": "",
        "role2-id": "",
        "role2-pts": "",
        "role3-id": "",
        "role3-pts": ""
    }
    json.dump(default_json, f, indent=4)
    print("config not found, new file created. re-run the file after filling out the config")
    exit()

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(intents=intents, command_prefix='%')

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

connection = sqlite3.connect("completes.db")



cfg = open("config.json", "r")
tmpconfig = cfg.read()
cfg.close()
config = json.loads(tmpconfig)

token = config["token"]
guild_id = config["guild-id"]
logs_channel = config["logs-channel-id"]
role1_id = config["role1-id"]
role2_id = config["role2-id"]
role3_id = config["role3-id"]
role1_pts = config["role1-pts"]
role2_pts = config["role2-pts"]
role3_pts = config["role3-pts"]

global membercache

memberrcache = []

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


async def getID(ign):
    guild = bot.get_guild(int(guild_id))
    members = guild.members
    notfound = ign
    id = 0
    try:
        for i in members:
            if (i.name and i.name.lower() == ign.lower()) or (i.nick and i.nick.lower() == ign.lower()):
                id = i.id
                notfound = ""
    except Exception as e:
        print(e)
    print(id)
    return (id, notfound)

dataconnection = sqlite3.connect("data.db")

invites = {}
last = ""

async def fetch():
    global last
    global invites
    await bot.wait_until_ready()
    gld = bot.get_guild(int(guild_id))
    logs = bot.get_channel(int(logs_channel))
    while True:
        invs = await gld.invites()
        tmp = []
        for i in invs:
            for s in invites:
                if s[0] == i.code:
                    if int(i.uses) > s[1]:
                        usr = gld.get_member(int(last))
                        testh = f"{usr.name} **joined**; Invited by **{i.inviter.name}** (**{str(i.uses)}** invites)"
                        with closing(sqlite3.connect("data.db")) as dataconnection:
                            with closing(dataconnection.cursor()) as cursor:
                                try:
                                    cursor.execute("INSERT INTO invites(id, inviter_id) VALUES(?,?)", [str(usr.id), str(i.inviter.id)])
                                    dataconnection.commit()
                                except:
                                    print("error in fetch")
                        await logs.send(testh)
            tmp.append(tuple((i.code, i.uses)))
        invites = tmp
        await asyncio.sleep(4)

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))
    

@bot.command(name="stats")
async def stats(ctx, arg=None):
    uid = ctx.author.id
    if not arg is None:
        uid = int(re.sub('[<!@>]', '', arg))
    user = ctx.message.guild.get_member(uid)
    username = user.nick
    if user.nick is None:
        username = user.name
    points = 0
    with closing(sqlite3.connect("data.db")) as dataconnection:
        with closing(dataconnection.cursor()) as cursor:
            try:
                points = cursor.execute("SELECT points FROM members WHERE id=?", [uid]).fetchone()[0]
            except:
                points = 0
    embed=discord.Embed(title=f"{username}'s Stats", color=0xbfd515)
    embed.add_field(name="Points", value=f"```{points}```")
    await ctx.send(embed=embed)

@bot.command(name="addpoints")
@has_permissions(manage_roles=True)
async def addpoints(ctx, *args):
    uid = int(re.sub('[<!@>]', '', args[0]))
    user = ctx.message.guild.get_member(uid)
    username = user.nick
    if user.nick is None:
        username = user.name
    points = args[1]
    with closing(sqlite3.connect("data.db")) as dataconnection:
        with closing(dataconnection.cursor()) as cursor:
            try:   
                cursor.execute("INSERT INTO members (id, points) VALUES(?, ?) ON CONFLICT(id) DO UPDATE SET points=points+? WHERE id=?", [uid, points, points, uid])
                dataconnection.commit()
            except:
                print("error adding points")
    await ctx.send(f"Added {points} for {username}")

@addpoints.error
async def addpoints_error(ctx, error):
    if isinstance(error, MissingPermissions):
        text = "Sorry {}, you do not have permissions to do that!".format(ctx.message.author)
        await ctx.send(text)

@bot.command(name="leaderboard", aliases=["lb"])
async def leaderboard(ctx):
    with closing(sqlite3.connect("data.db")) as dataconnection:
        with closing(dataconnection.cursor()) as cursor:
            plb = cursor.execute("SELECT * FROM members ORDER BY points DESC LIMIT 5").fetchall()
    print(plb)

    embed=discord.Embed(title="Leaderboard", color=0xe19d09)
    embed.add_field(name="\u200b", value="Top 5, organized by: **invite points**", inline=False)
    for i in range(1,6):
        embed.add_field(name="\u200b", value=f"{i}. <@{plb[i-1][0]}> {plb[i-1][1]}", inline=False)
    await ctx.send(embed=embed)


@bot.event
async def on_member_join(meme):
    global last
    last = str(meme.id)
    print(f"last set to {meme.id}")

@bot.event
async def on_member_update(before, after):
    if len(before.roles) < len(after.roles):
        newRole = next(role for role in after.roles if role not in before.roles)
        inviter_id = ""
        if newRole.id == role1_id and not before.roles.count(role2_id):
            #TODO: add role1_pts to inviters count
            with closing(sqlite3.connect("data.db")) as dataconnection:
                with closing(dataconnection.cursor()) as cursor:
                    inviter_id = cursor.execute("SELECT inviter_id FROM invites WHERE id=?",[str(before.id)]).fetchone()[0]
                    cursor.execute("INSERT INTO members (id, points) VALUES(?, ?) ON CONFLICT(id) DO UPDATE SET points=points+? WHERE id=?", [str(inviter_id), role1_pts, role1_pts, str(inviter_id)])
                    #cursor.execute("INSERT INTO members (id, points) VALUES(?, ?)", [str(inviter_id), role1_pts])
                    dataconnection.commit()
                    print(f"added {role1_pts} to {inviter_id}")
                    return
        if newRole.id == role2_id and not before.roles.count(role1_id):
            #TODO: add role2_pts to inviters count
            with closing(sqlite3.connect("data.db")) as dataconnection:
                with closing(dataconnection.cursor()) as cursor:
                    inviter_id = cursor.execute("SELECT inviter_id FROM invites WHERE id=?",[str(before.id)]).fetchone()[0]
                    cursor.execute("INSERT INTO members (id, points) VALUES(?, ?) ON CONFLICT(id) DO UPDATE SET points=points+? WHERE id=?", [str(inviter_id), role2_pts, role2_pts, str(inviter_id)])
                    #cursor.execute("INSERT INTO members (id, points) VALUES(?, ?)", [str(inviter_id), role2_pts])
                    dataconnection.commit()
                    print(f"added {role2_pts} to {inviter_id}")
                    return
    return

bot.loop.create_task(fetch())

bot.run(token)