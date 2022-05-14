from discord.ext import commands
import discord
import gspread
from table2ascii import table2ascii as t2a, PresetStyle
import challonge

import string_commands
import config
import challonge_commands

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

def get_fom_sheet():
    gc = gspread.service_account(filename=config.SERVICE_ACCOUNT_FILE)
    return gc.open_by_url(config.FOM_SHEET)


class Player:
    def __init__(self, name, race, wins, losses, win_pct, seasons, s1_champ, s2_champ, s1_mp, s2_mp, total_mp, rank, bnet_name, w3c_tag, discord_name):
        self.name = name
        self.race = race
        self.wins = wins
        self.losses = losses
        self.win_pct = win_pct
        self.seasons = seasons
        self.s1_champ = s1_champ
        self.s2_champ = s2_champ
        self.s1_mp = s1_mp
        self.s2_mp = s2_mp
        self.total_mp = total_mp
        self.rank = rank
        self.bnet_name = bnet_name
        self.w3c_tag = w3c_tag
        self.discord_name = discord_name


def get_players_list():
    sheet = get_fom_sheet()
    ws = sheet.worksheet("Bot Stats")
    records = ws.get_all_records()

    players = []
    
    for record in records:
        players.append(
            Player(
                record.get('Player'),
                record.get('Race'),
                record.get('Wins'),
                record.get('Losses'),
                record.get('Win %'),
                record.get('Seasons'),
                record.get('S1 CHAMP'),
                record.get('S2 CHAMP'),
                record.get('s1 MP'),
                record.get('s2 MP'),
                record.get('MP'),
                record.get('Rank'),
                record.get('BNet Name'),
                record.get('W3C Tag'),
                record.get('Discord Name')
            )
        )
    
    return players


@bot.command(name='stats')
async def stats(ctx:commands.Context, user):
    players = get_players_list()
    for player in players:
        player_tags = [player.name.lower(), player.bnet_name.lower(), player.w3c_tag.lower, player.discord_name.lower()]
        if user.lower() in player_tags:
            content_string = f'**Name**: {player.name}\n**W3C**: {player.w3c_tag}\n**Discord**: {player.discord_name}\n**Rank**: {player.rank}\n**Race**: {player.race}\n**Wins**: {player.wins}\n**Losses**: {player.losses}\n**Win%**: {player.win_pct}\n**Seasons Played**: {player.seasons}\n**S1 MP**: {player.s1_mp}\n**S2 MP**: {player.s2_mp}\n**Total MP**: {player.total_mp}'
            embed = discord.Embed(
                title=f"{user} Stats",
                colour=0x0C2C55,
                description=content_string
            )

            fom_logo = 'https://s3.amazonaws.com/challonge_app/organizations/images/000/143/459/large/discord_icon.png'
            embed.set_author(name='Fountain of Manner', icon_url=fom_logo)
            champ_logo = None

            if player.s1_champ == 'YES':
                champ_logo = discord.File('./images/fom_s1_champ.png', filename='fom_s1_champ.png')
                embed.set_thumbnail(url='attachment://fom_s1_champ.png')
            if player.s2_champ == 'YES':
                champ_logo = discord.File('./images/fom_s2_champ.png', filename='fom_s2_champ.png')
                embed.set_thumbnail(url='attachment://fom_s2_champ.png')

            await ctx.reply(embed=embed, file=champ_logo)


@bot.command(name='mannerpoints', aliases=['mp'])
async def mannerpoints(ctx:commands.Context):
    await ctx.reply(string_commands.mannerpoints)


@bot.command(name='foml')
async def foml(ctx:commands.Context):
    await ctx.reply(string_commands.foml)


@bot.command(name='veto')
async def veto(ctx:commands.Context):
    await ctx.reply(string_commands.veto)


@bot.command(name='launcher')
async def launcher(ctx:commands.Context):
    await ctx.reply(string_commands.launcher)


@bot.command(name="leaderboard")
async def leaderboard(ctx:commands.Context, limit=15):
    if limit > 50:
        await ctx.reply("Leaderboard limited to 50 due to discord character limit")
        limit = 50
    elif limit < 1:
        await ctx.reply("Leaderboard limit must be greater than or equal to 1")
        limit = 1

    players = get_players_list()
    players.sort(key=lambda x: int(x.rank))
    top_n = players[0:limit]
    leaderboard_list = []
    for player in top_n:
        leaderboard_list.append([player.rank, player.name, player.race, player.total_mp])
    
    content = t2a(
        header=["Rank", "Name", "Race", "Total MP"],
        body=leaderboard_list,
        style=PresetStyle.thin_compact,
        first_col_heading=True
    )
    
    embed = discord.Embed(
        title=f"FoML Leaderboard - Top {limit}",
        colour=0x0C2C55,
        description=f"```\n{content}\n```"
    )
    fom_logo = 'https://s3.amazonaws.com/challonge_app/organizations/images/000/143/459/large/discord_icon.png'
    embed.set_author(name='Fountain of Manner', icon_url=fom_logo)

    await ctx.reply(embed=embed)


@bot.command(name="listmatches")
@commands.has_role('FoM League Admin')
async def listmatches(ctx:commands.Context, group, round, second_round=None):
    challonge.set_credentials("debaser19", config.CHALLONGE_KEY)
    tournament = challonge.tournaments.show(config.FOML_S3_ID)

    matches = challonge_commands.fetch_matches(tournament)
    member_list = get_members(guild)
    match_list = []
    for match in matches:
        if match.group.lower() == group.lower() and int(match.round) == int(round):
            match_list.append(match)
    
    reply_string = ""
    for match in match_list:
        for member in member_list:
            if str(member["member_name"]).lower() == str(match.p1_discord).lower():
                match.p1_discord_id = member["member_id"]
            elif str(member["member_name"]).lower() == str(match.p2_discord).lower():
                match.p2_discord_id = member["member_id"]
        reply_string += f"[Round {match.round}] [Group {match.group}] - <@!{match.p1_discord_id}> [{match.p1_race}] VS <@!{match.p2_discord_id}> [{match.p2_race}]"
        if match.state == 'complete':
            reply_string += f" [{match.state.upper()}: {match.score}]"
        reply_string += "\n"

    if second_round:
        match_list = []
        reply_string += f"\n\n **GROUP {match.group} - ROUND {second_round}**\n"
        for match in matches:
            if match.group.lower() == group.lower() and int(match.round) == int(second_round):
                match_list.append(match)
        
        for match in match_list:
            for member in member_list:
                if str(member["member_name"]).lower() == str(match.p1_discord).lower():
                    match.p1_discord_id = member["member_id"]
                elif str(member["member_name"]).lower() == str(match.p2_discord).lower():
                    match.p2_discord_id = member["member_id"]
            reply_string += f"[Round {match.round}] [Group {match.group}] - <@!{match.p1_discord_id}> [{match.p1_race}] VS <@!{match.p2_discord_id}> [{match.p2_race}]"
            if match.state == 'complete':
                reply_string += f" [{match.state.upper()}: {match.score}]"
            reply_string += "\n"

    await ctx.reply(f"**GROUP {match.group.upper()} - ROUND {round}**\n{reply_string}")


# @bot.command(name="getmembers")
# async def getmembers(ctx:commands.Context):
#     member_list = get_members(guild)
#     for member in member_list:
#         print(member["member_id"], member["member_name"])
#         await ctx.send(f"tagging <@!{member['member_id']}>")


def get_members(guild):
    member_list = []
    for member in guild.members:
        member_list.append({"member_name": member, "member_id": member.id})
    
    return member_list


def get_member_id(username):
    member_list = get_members(guild)
    for member in member_list:
        if username.lower() == member["mamber_name"].lower():
            return member["member_id"]


@bot.command(pass_context = True)
async def getserverid(ctx):
   serverId = ctx.message.guild.id
   await ctx.send(serverId)


@bot.event
async def on_ready():
    global guild
    guild = bot.get_guild(int(config.FOM_GUILD_ID))
    print(f'We have logged in as {bot.user}')


DISCORD_TOKEN = config.DISCORD_TOKEN
bot.run(DISCORD_TOKEN)