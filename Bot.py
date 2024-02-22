import nextcord
from nextcord.ext import commands, tasks
from json import loads
from pathlib import Path
import psutil
import urllib
import json

ts = 0
tm = 0
th = 0
td = 0

# Load the token from the config file
config = loads(Path('config.json').read_text())
Token = config['Token']
WetterAPI = config['WetterAPI']

intents = nextcord.Intents.all()

# Load the prefix from the prefixes.json file
def get_prefix(client, message):
    with open('prefixes.json', 'r') as f:
        prefixes = loads(f.read())

    return prefixes[str(message.guild.id)] if str(message.guild.id) in prefixes else "!"


client = commands.AutoShardedBot(shard_count=3, command_prefix = get_prefix, intents=intents)
client.remove_command('help')

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')
    print(f'Bot ID: {client.user.id}')
    print(f'Nextcord Version: {nextcord.__version__}')
    print(f'shards: {client.shard_count}')
    print(f'Latency: {round(client.latency * 1000)}ms')
    print(f'Uptime: {td}d {th}h {tm}m {ts}s')
    print("BOT IS READY")

    Status.start()

def admin(ctx):
    if ctx.author.guild_permissions.administrator == True:
        return True
    else:
        return False
    
#Prefix Command
@client.command(description="Changes the Prefix of the Bot",)
async def on_guild_join(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = '!'

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

#Prefix Command
@client.command(description="Changes the Prefix of the Bot",)
async def on_guild_remove(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes.pop(str(guild.id))

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

@tasks.loop(seconds=5.0)
async def Status():
    global ts, tm, th, td
    ts += 5
    if ts == 60:
        ts = 0
        tm += 1
    if tm == 60:
        tm = 0
        th += 1
    if th == 24:
        th = 0
        td += 1
    await client.change_presence(activity=nextcord.Game(name=f"Uptime: {td}d {th}h {tm}m {ts}s"))

@Status.before_loop
async def BeforeStatus():
    await client.wait_until_ready()

#Shows the Status of the Bot
@client.command(description="Status Command for the Bot",)
async def status(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You are not allowed to see the status of the bot")
        return
    global ts, tm, th, td
    embed = nextcord.Embed(title="Status", color=0xe74c3c)
    embed.add_field(name="Bot Name", value=client.user.name, inline=True)
    embed.add_field(name="Bot Version", value="1.0", inline=True)
    embed.add_field(name="Uptime", value=f"{td}d {th}h {tm}m {ts}s", inline=True)
    embed.add_field(name="Memory Usage", value=f"{psutil.virtual_memory().percent}%", inline=True)
    embed.add_field(name="CPU Usage", value=f"{psutil.cpu_percent()}%", inline=True)
    embed.add_field(name="RAM Usage", value=f"{round(psutil.virtual_memory().used / 1024**3, 2)}GB", inline=True)
    await ctx.send(embed=embed)

#Ping Command
@client.command(description="Ping Test",)
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency * 1000)}ms')



#Moderation Commands
@client.command(description="kicks a user from the Server",)
async def kick(ctx, member : nextcord.Member, *, reason=None):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You are not allowed to kick people")
        return
    await member.kick(reason=reason)
    await ctx.send(f'{member.mention} has been kicked')

@client.command(description="Bonk a User from the Server",)
async def ban(ctx, member : nextcord.Member, *, reason=None):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You are not allowed to ban people")
        return
    await member.ban(reason=reason)
    await ctx.send(f'{member.mention} has been banned')

@client.command(description='unban a User',)
async def unban(ctx, *, member):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You are not allowed to unban people")
        return
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'{user.mention} has been unbanned')
            return
        
@client.command(description="Clears all Messages", aliases=['purge'])
async def clear(ctx, amount=5):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You are not allowed to clear messages")
        return
    await ctx.channel.purge(limit=amount)

@client.command(description="Mutes a User",)
async def mute(ctx, member : nextcord.Member, *, reason=None):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You are not allowed to mute people")
        return
    role = nextcord.utils.get(ctx.guild.roles, name="Muted")
    if role is None:
        role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.text_channels:
            await channel.set_permissions(role, send_messages=False)
    await member.add_roles(role, reason=reason)
    await ctx.send(f'{member.mention} has been muted')

@client.command(description="Unmutes a User",)
async def unmute(ctx, member : nextcord.Member):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You are not allowed to unmute people")
        return
    role = nextcord.utils.get(ctx.guild.roles, name="Muted")
    await member.remove_roles(role)
    await ctx.send(f'{member.mention} has been unmuted')

@client.command(description="Enables or Disables a Command")
async def toggle(ctx, *, command):
    command = client.get_command(command)
    if command == None:
        await ctx.send("Command not found")
    elif ctx.command == command:
        await ctx.send("You cannot disable this command")
    else:
        command.enabled = not command.enabled
        ternary = "enabled" if command.enabled else "disabled"
        await ctx.send(f"{command.qualified_name} has been {ternary}")

#Help Command
@client.command(description="List of all Commands")
async def help(ctx):
    embed = nextcord.Embed(title="Commands", color=0xe74c3c)
    for command in client.walk_commands():
        description = command.description
        if description or description is None or description == "":
            description = "No description available"
        embed.add_field(name=f"!{command.name}{command.signature if command.signature is not None else ""}", value=description)
    await ctx.send(embed=embed)

#A Command to change the Prefix
@client.command()
async def prefix(ctx, prefixset = None):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You are not allowed to change the prefix")
        return
    
    if (prefixset == None):
        prefixset = "!"
        
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = prefixset

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

    await ctx.send(f"Prefix has been set to {prefixset}")

#Lockdown and Unlock Commands

@client.command(description="Shutsdown the Chat in a Channel and in the Server ",)
async def lockdown(ctx, channel: nextcord.TextChannel=None, setting = None):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You are not allowed to lock the Chat in the Server or in a Channel")
        return
    if setting == "--server":
        for channel in ctx.guild.text_channels:
            await channel.set_permissions(ctx.guild.default_role, send_messages=False, read_message_history=False, reason=f"{ctx.author.name} has disabled the Chatting in whole server")
        await ctx.send(f"Chatting has been disabled in all channels")
    if channel is None:
        channel = ctx.message.channel
    await channel.set_permissions(ctx.guild.default_role, reason=f"{ctx.author.name} has disabled the Chatting in {channel.name}", send_messages=False, read_message_history=False)
    await ctx.send(f"Chatting has been disabled in {channel.mention}")

@client.command(description="unlocks the Chat in the Channel and in the Server",)
async def unlock(ctx, channel: nextcord.TextChannel=None, setting = None):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You are not allowed to unlock the Chat in the Server or in a Channel")
        return
    if setting == "--server":
        for channel in ctx.guild.text_channels:
            await channel.set_permissions(ctx.guild.default_role, send_messages=True, read_message_history=True , reason=f"{ctx.author.name} has enabled the Chatting in whole server")
        await ctx.send(f"Chatting has been enabled in all channels")
    if channel is None:
        channel = ctx.message.channel
    await channel.set_permissions(ctx.guild.default_role, send_messages=True, read_message_history=True, reason=f"{ctx.author.name} has enabled the Chatting in {channel.name}")
    await ctx.send(f"Chatting has been enabled in {channel.mention}")

#Server and User Info Commands

@client.command(description="Shows the Server Info",)
async def serverinfo(ctx):
    embed = nextcord.Embed(title=f"{ctx.guild.name}", color=0xe74c3c)
    embed.set_thumbnail(url=ctx.guild.icon_url)
    embed.add_field(name="Owner", value=ctx.guild.owner, inline=True)
    embed.add_field(name="Region", value=ctx.guild.region, inline=True)
    embed.add_field(name="Members", value=ctx.guild.member_count, inline=True)
    embed.add_field(name="Created At", value=ctx.guild.created_at.strftime("%d-%m-%Y %H:%M:%S"), inline=True)
    await ctx.send(embed=embed)

@client.command(description="Shows the User Info",)
async def userinfo(ctx, member : nextcord.Member):
    embed = nextcord.Embed(title=f"{member.name}", color=0xe74c3c)
    embed.set_thumbnail(url=member.avatar_url)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Created At", value=member.created_at.strftime("%d-%m-%Y %H:%M:%S"), inline=True)
    embed.add_field(name="Joined At", value=member.joined_at.strftime("%d-%m-%Y %H:%M:%S"), inline=True)
    await ctx.send(embed=embed)

@client.command(description="Shows the Avatar of the User",)
async def avatar(ctx, member : nextcord.Member):
    embed = nextcord.Embed(title=f"{member.name}'s Avatar", color=0xe74c3c)
    embed.set_image(url=member.avatar_url)
    await ctx.send(embed=embed)


#API Section
#Current API's: Openweathermap, League of Legends, Memes
#still WIP some functions are not working properly or are broken APIs not working anymore

@client.command(description="Shows a Meme",)
async def meme(ctx):
    memeApi = urllib.request.urlopen("https://meme-api.com/gimme")
    meme = loads(memeApi.read())

    memeUrl = meme['url']
    memeTitle = meme['title']
    memeSubreddit = meme['subreddit']
    memeLink = meme['postLink']
    memeAuthor = meme['author']

    embed = nextcord.embed(title=f"{memeTitle}", color=0xe74c3c)
    embed.set_image(url=memeUrl)
    embed.set_author(text=f"Meme by {memeAuthor} from r/{memeSubreddit} Link: {memeLink}")
    await ctx.send(embed=embed)

@client.command(description="Shows the Weather of the City",)
async def wetter(ctx, city):
    weatherApi = urllib.request.urlopen(f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WetterAPI}")
    weather = loads(weatherApi.read())

    weatherDescription = weather['weather'][0]['description']
    weatherTemp = weather['main']['temp']
    weatherFeelsLike = weather['main']['feels_like']
    weatherHumidity = weather['main']['humidity']
    weatherWindSpeed = weather['wind']['speed']

    embed = nextcord.Embed(title=f"Weather in {city}", color=0xe74c3c)
    embed.add_field(name="Description", value=weatherDescription, inline=True)
    embed.add_field(name="Temperature", value=f"{round(weatherTemp - 273.15, 2)}°C", inline=True)
    embed.add_field(name="Feels Like", value=f"{round(weatherFeelsLike - 273.15, 2)}°C", inline=True)
    embed.add_field(name="Humidity", value=f"{weatherHumidity}%", inline=True)
    embed.add_field(name="Wind Speed", value=f"{weatherWindSpeed}m/s", inline=True)
    await ctx.send(embed=embed)

@client.command()
async def league(ctx, summoner):#
    leagueApi = urllib.request.urlopen(f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner}?api_key={config['LeagueAPI']}")
    league = loads(leagueApi.read())

    leagueId = league['id']
    leagueName = league['name']
    leagueLevel = league['summonerLevel']
    leagueIconId = league['profileIconId']

    embed = nextcord.Embed(title=f"{leagueName}", color=0xe74c3c)
    embed.set_thumbnail(url=f"http://ddragon.leagueoflegends.com/cdn/11.16.1/img/profileicon/{leagueIconId}.png")
    embed.add_field(name="Level", value=leagueLevel, inline=True)

    leagueMasteryApi = urllib.request.urlopen(f"https://euw1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{leagueId}?api_key={config['LeagueAPI']}")
    leagueMastery = loads(leagueMasteryApi.read())

    leagueMasteryChampionId = leagueMastery[0]['championId']
    leagueMasteryChampionPoints = leagueMastery[0]['championPoints']
    leagueMasteryChampionLevel = leagueMastery[0]['championLevel']

    embed.add_field(name="Mastery", value=f"Champion: {leagueMasteryChampionId} Points: {leagueMasteryChampionPoints} Level: {leagueMasteryChampionLevel}", inline=True)

    leagueRankApi = urllib.request.urlopen(f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{leagueId}?api_key={config['LeagueAPI']}")
    leagueRank = loads(leagueRankApi.read())

    leagueRankTier = leagueRank[0]['tier']
    leagueRankRank = leagueRank[0]['rank']
    leagueRankLP = leagueRank[0]['leaguePoints']
    leagueRankWins = leagueRank[0]['wins']
    leagueRankLosses = leagueRank[0]['losses']

    embed.add_field(name="Rank", value=f"{leagueRankTier} {leagueRankRank} {leagueRankLP}LP Wins: {leagueRankWins} Losses: {leagueRankLosses}", inline=True)
    await ctx.send(embed=embed)




#Error Handling very basic not the finished Error Handler but it works

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please pass in all required arguments")
        return
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Nuh Uh you are not allowed to use this command")
        return
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found use !help to see all commands available to you")
        return
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds")
        return
    if isinstance(error, commands.MissingRole):
        await ctx.send("You are missing the required role to use this command")
        return
    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send("I am missing the required permissions to run this command")
        return
    if isinstance(error, commands.BadArgument):
        await ctx.send("Bad Argument")
        return
    if isinstance(error, commands.CheckFailure):
        await ctx.send("You are not allowed to use this command")
        return
    if isinstance(error, commands.CommandInvokeError):
        await ctx.send("An error occured while running the command if the error persists contact the developer of the bot")
        return
    if isinstance(error, commands.CommandError):
        await ctx.send("Something is Wrong here please check the command and try again if the error persists contact the developer of the bot")
        return
    if isinstance(error, commands.DisabledCommand):
        await ctx.send("This command is disabled you cannot use it")
        return

client.run(Token)