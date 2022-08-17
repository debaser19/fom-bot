from discord.ext import commands, tasks
import discord
import gspread
from table2ascii import table2ascii as t2a, PresetStyle
import challonge
from fom_logger import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

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
    def __init__(
        self,
        name,
        race,
        wins,
        losses,
        win_pct,
        seasons,
        s1_champ,
        s2_champ,
        s3_champ,
        aliases,
        s1_mp,
        s2_mp,
        s3_mp,
        total_mp,
        rank,
        bnet_name,
        w3c_tag,
        discord_name,
    ):
        self.name = name
        self.race = race
        self.wins = wins
        self.losses = losses
        self.win_pct = win_pct
        self.seasons = seasons
        self.s1_champ = s1_champ
        self.s2_champ = s2_champ
        self.s3_champ = s3_champ
        self.aliases = aliases
        self.s1_mp = s1_mp
        self.s2_mp = s2_mp
        self.s3_mp = s3_mp
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
                record.get("Player"),
                record.get("Race"),
                record.get("Wins"),
                record.get("Losses"),
                record.get("Win %"),
                record.get("Seasons"),
                record.get("S1 CHAMP"),
                record.get("S2 CHAMP"),
                record.get("S3 CHAMP"),
                record.get("Aliases").split(","),
                record.get("s1 MP"),
                record.get("s2 MP"),
                record.get("s3 MP"),
                record.get("MP"),
                record.get("Rank"),
                record.get("BNet Name"),
                record.get("W3C Tag"),
                record.get("Discord Name"),
            )
        )

    return players


@bot.command(name="stats")
async def stats(ctx: commands.Context, user):
    logger.info(f"Discord user {ctx.author} requested stats for {user}")
    channel_stats_check = 975799340733984838
    channel_bot_test = 963256852613832734
    if ctx.channel.name == ("stats-check") or ctx.channel.id == channel_bot_test:
        players = get_players_list()
        for player in players:
            player_tags = [
                player.name.lower(),
                player.bnet_name.lower(),
                player.w3c_tag.lower,
                player.discord_name.lower(),
            ]
            for alias in player.aliases:
                player_tags.append(alias.lower())
            if user.lower() in player_tags:
                content_string = f"**Name**: {player.name}\n**W3C**: {player.w3c_tag}\n**Discord**: {player.discord_name}\n**Rank**: {player.rank}\n**Race**: {player.race}\n**Wins**: {player.wins}\n**Losses**: {player.losses}\n**Win%**: {player.win_pct}\n**Seasons Played**: {player.seasons}\n**S1 MP**: {player.s1_mp}\n**S2 MP**: {player.s2_mp}\n**S3 MP**: {player.s3_mp}\n**Total MP**: {player.total_mp}"
                embed = discord.Embed(
                    title=f"{user} Stats", colour=0x0C2C55, description=content_string
                )

                fom_logo = "https://s3.amazonaws.com/challonge_app/organizations/images/000/143/459/large/discord_icon.png"
                embed.set_author(name="Fountain of Manner", icon_url=fom_logo)
                champ_logo = None

                if player.s1_champ == "YES":
                    champ_logo = discord.File(
                        "./images/fom_s1_champ.png", filename="fom_s1_champ.png"
                    )
                    embed.set_thumbnail(url="attachment://fom_s1_champ.png")
                if player.s2_champ == "YES":
                    champ_logo = discord.File(
                        "./images/fom_s2_champ.png", filename="fom_s2_champ.png"
                    )
                    embed.set_thumbnail(url="attachment://fom_s2_champ.png")
                if player.s3_champ == "YES":
                    champ_logo = discord.File(
                        "./images/fom_s3_champ.png", filename="fom_s3_champ.png"
                    )
                    embed.set_thumbnail(url="attachment://fom_s3_champ.png")

                await ctx.reply(embed=embed, file=champ_logo)

    else:
        await ctx.reply(
            f"Please use the <#{channel_stats_check}> channel for this command"
        )


@bot.command(name="mannerpoints", aliases=["mp"])
async def mannerpoints(ctx: commands.Context):
    await ctx.reply(string_commands.mannerpoints)


@bot.command(name="foml")
async def foml(ctx: commands.Context):
    await ctx.reply(string_commands.foml)


@bot.command(name="veto")
async def veto(ctx: commands.Context):
    await ctx.reply(string_commands.veto)


@bot.command(name="launcher")
async def launcher(ctx: commands.Context):
    await ctx.reply(string_commands.launcher)


@bot.command(name="leaderboard")
async def leaderboard(ctx: commands.Context, limit=15):
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
        leaderboard_list.append(
            [player.rank, player.name, player.race, player.total_mp]
        )

    content = t2a(
        header=["Rank", "Name", "Race", "Total MP"],
        body=leaderboard_list,
        style=PresetStyle.thin_compact,
        first_col_heading=True,
    )

    embed = discord.Embed(
        title=f"FoML Leaderboard - Top {limit}",
        colour=0x0C2C55,
        description=f"```\n{content}\n```",
    )
    fom_logo = "https://s3.amazonaws.com/challonge_app/organizations/images/000/143/459/large/discord_icon.png"
    embed.set_author(name="Fountain of Manner", icon_url=fom_logo)

    await ctx.reply(embed=embed)


@bot.command(name="listmatches")
@commands.has_role("FoM League Admin")
async def listmatches(ctx: commands.Context, group, round, second_round=None):
    challonge.set_credentials("debaser19", config.CHALLONGE_KEY)
    tournament = challonge.tournaments.show(config.FOML_S4_ID)

    matches = challonge_commands.fetch_matches(tournament)
    member_list = get_members(guild)
    match_list = []
    for match in matches:
        if match.group.lower() == group.lower() and int(match.round) == int(round):
            match_list.append(match)

    channel_links_and_info = 879207158477127702
    channel_rules_and_faq = 879208033417330709
    channel_report_results = 879209532100857856
    channel_scheduled_games = 938137398565556224
    info_string = f"**MATCHUPS FOR THIS WEEK** (Round {round} {'+ ' + second_round if second_round else ''} in Challonge)\n\nPlease complete these games (BO3) by the end of Sunday. Check <#{channel_rules_and_faq}> and <#{channel_links_and_info}> for more information on the veto process (or type `!veto` in this server for veto rules), map pool, and more.\n\n**PLAYER ON LEFT IS PLAYER A**\n\n"
    reply_string = ""
    for match in match_list:
        for member in member_list:
            if str(member["member_name"]).lower() == str(match.p1_discord).lower():
                match.p1_discord_id = member["member_id"]
            elif str(member["member_name"]).lower() == str(match.p2_discord).lower():
                match.p2_discord_id = member["member_id"]
        reply_string += f"<@!{match.p1_discord_id}> [{match.p1_race}] VS <@!{match.p2_discord_id}> [{match.p2_race}]"
        if match.state == "complete":
            reply_string += f" [{match.state.upper()}: {match.score}]"
        reply_string += "\n"

    if second_round:
        match_list = []
        reply_string += f"\n\n **GROUP {match.group} - ROUND {second_round}**\n"
        for match in matches:
            if match.group.lower() == group.lower() and int(match.round) == int(
                second_round
            ):
                match_list.append(match)

        for match in match_list:
            for member in member_list:
                if str(member["member_name"]).lower() == str(match.p1_discord).lower():
                    match.p1_discord_id = member["member_id"]
                elif (
                    str(member["member_name"]).lower() == str(match.p2_discord).lower()
                ):
                    match.p2_discord_id = member["member_id"]
            reply_string += f"<@!{match.p1_discord_id}> [{match.p1_race}] VS <@!{match.p2_discord_id}> [{match.p2_race}]"
            if match.state == "complete":
                reply_string += f" [{match.state.upper()}: {match.score}]"
            reply_string += "\n"

    post_string = f"\n\nWhen you and your opponent decide on a match time post the times here and in <#{channel_scheduled_games}>.\n\nOnce your match is completed, please post your replays in <#{channel_report_results}> and report your results on Challonge: http://challonge.com/FOMLS4"

    await ctx.reply(
        f"{info_string}**GROUP {match.group.upper()} - ROUND {round}**\n{reply_string}{post_string}"
    )


@bot.command(name="incomplete")
@commands.has_role("FoM League Admin")
async def incomplete(ctx: commands.Context, group, round, second_round=None):
    challonge.set_credentials("debaser19", config.CHALLONGE_KEY)
    tournament = challonge.tournaments.show(config.FOML_S4_ID)

    matches = challonge_commands.fetch_matches(tournament)
    member_list = get_members(guild)
    match_list = []
    for match in matches:
        if (
            match.group.lower() == group.lower()
            and int(match.round) == int(round)
            and match.state != "complete"
        ):
            match_list.append(match)

    channel_links_and_info = 879207158477127702
    channel_rules_and_faq = 879208033417330709
    info_string = f"**INCOMPLETE MATCHES** (Round {round} {'+ ' + second_round if second_round else ''} in Challonge)\n\nThe following matches have **NOT** yet been completed. Please reach out to your opponent ASAP to get these matches completed. If you are having trouble scheduling, please message an admin. Check <#{channel_rules_and_faq}> and <#{channel_links_and_info}> for more information on the veto process (or type `!veto` in this server for veto rules), map pool, and more.\n\n**PLAYER ON LEFT IS PLAYER A**\n\n"
    reply_string = ""
    for match in match_list:
        for member in member_list:
            if str(member["member_name"]).lower() == str(match.p1_discord).lower():
                match.p1_discord_id = member["member_id"]
            elif str(member["member_name"]).lower() == str(match.p2_discord).lower():
                match.p2_discord_id = member["member_id"]
        reply_string += f"<@!{match.p1_discord_id}> [{match.p1_race}] VS <@!{match.p2_discord_id}> [{match.p2_race}]"
        if match.state == "complete":
            reply_string += f" [{match.state.upper()}: {match.score}]"
        reply_string += "\n"

    if second_round:
        match_list = []
        reply_string += f"\n\n **GROUP {match.group} - ROUND {second_round}**\n"
        for match in matches:
            if (
                match.group.lower() == group.lower()
                and int(match.round) == int(second_round)
                and match.state != "complete"
            ):
                match_list.append(match)

        for match in match_list:
            for member in member_list:
                if str(member["member_name"]).lower() == str(match.p1_discord).lower():
                    match.p1_discord_id = member["member_id"]
                elif (
                    str(member["member_name"]).lower() == str(match.p2_discord).lower()
                ):
                    match.p2_discord_id = member["member_id"]
            reply_string += f"<@!{match.p1_discord_id}> [{match.p1_race}] VS <@!{match.p2_discord_id}> [{match.p2_race}]"
            if match.state == "complete":
                reply_string += f" [{match.state.upper()}: {match.score}]"
            reply_string += "\n"

    await ctx.reply(
        f"{info_string}**GROUP {match.group.upper()} - ROUND {round}**\n{reply_string}"
    )


# Veto commands
# TODO: Add a way to start veto process between two players
@bot.command(name="startveto")
async def startveto(
    ctx: commands.Context, player1: discord.User, player2: discord.User
):
    logger.info(f"{ctx.author} started a veto between {player1} and {player2}")

    # make sure both players are valid users on the server
    if not ctx.guild.get_member(int(player1.id)):
        logger.warning(f"{player1} is not a valid user on this server")
        await ctx.reply(f"{player1} is not a valid user on this server.")
        return
    if not ctx.guild.get_member(int(player2.id)):
        logger.warning(f"{player2} is not a valid user on this server")
        await ctx.reply(f"{player2} is not a valid user on this server.")
        return

    # ask who will be player A
    player_a_message = await ctx.reply(
        f"Which player will be player A?\n:regional_indicator_a: - {player1}\n:regional_indicator_b: - {player2}"
    )
    await player_a_message.add_reaction("🇦")
    await player_a_message.add_reaction("🇧")

    # wait for reaction from player_a or player_b
    def check(reaction, user):
        return user == player1 or user == player2

    reaction = await bot.wait_for("reaction_add", check=check)
    await ctx.send(f"{reaction[0]} was selected")


@bot.command(name="upcoming")
async def upcoming(ctx: commands.Context):
    logger.info(f"{ctx.author} requested upcoming matches")
    message = await ctx.reply("Looking for upcoming matches...")
    import matchups

    upcoming_matches = matchups.get_upcoming_matches()
    if len(upcoming_matches) > 0:
        result = ""
        for match in upcoming_matches:
            # convert match["datetime"] to string containing date and time
            # match_date = match["datetime"].strftime("%a %d %b @ %I:%M %p EST")
            # convert match["datetime"] to unix timestamp
            match_date = int(match.datetime.timestamp())
            match_date = f"<t:{match_date}:f>"
            result += f"[ID: {match.id}] [GROUP: {match.group}] **{match.p1_name} [{match.p1_race}]** vs **{match.p2_name} [{match.p2_race}]** - {match_date}"

            if match.stream != "":
                result += f" - <https://twitch.tv/{match.stream}>\n"
            else:
                result += (
                    f" - No caster scheduled yet - `!claim {match.id} <twitch_name>`\n"
                )

        await message.delete()
        await ctx.reply(
            f"**Matches scheduled in the next 24 hours**:\nMatch times should be automatically converted to your timezone\n\n{result}"
        )
    else:
        await message.delete()
        await ctx.reply("No matches scheduled in the next 24 hours")
        logger.info("No upcoming matches without caster")


@bot.command(name="claim")
async def claim(ctx: commands.Context, match_id, twitch_name):
    logger.info(f"{ctx.author} is trying to claim match id {match_id}")
    role = discord.utils.find(lambda r: r.name == "FoM League Admin", ctx.guild.roles)
    if role in ctx.author.roles:
        fom_admin = True
        logger.info(f"{ctx.author} is an admin, user is able to claim any match")
    else:
        fom_admin = False
        logger.info(
            f"{ctx.author} is not an admin, user is not able to claim matches claimed by other casters"
        )

    # check to make sure twitch_name is valid
    illegal_characters = ["<", ">", ":", ";", "!", '"', "|", "\\", "/", "?", "*"]
    if any(char in illegal_characters for char in twitch_name):
        logger.warning(f"{twitch_name} contains illegal characters")
        await ctx.reply(
            "Illegal characters in twitch name, please enter a valid twitch username "
        )
        return

    import matchups

    matchups_list = matchups.get_all_matches()
    for match in matchups_list:
        if int(match.id) == int(match_id):
            if match.stream != "":
                if fom_admin == False:
                    logger.warning(
                        f"Match {match_id} is already claimed by {match.stream}"
                    )
                    await ctx.reply(
                        f"Match {match.id} already claimed by {match.stream}"
                    )
                    return
            try:
                # find game id in ID column of google sheet
                gc = gspread.service_account(filename=config.SERVICE_ACCOUNT_FILE)
                sh = gc.open_by_url(config.MATCHUPS_SHEET)
                sheet = sh.worksheet("s4")
                game_id_row = sheet.find(str(match.id)).row
                match.stream = twitch_name
                # update stream column in google sheet with twitch name
                sheet.update_cell(game_id_row, 10, twitch_name)
                logger.info(f"{twitch_name} claimed match {match.id}")
                await ctx.reply(f"Match {match_id} claimed by {twitch_name}")
                return
            except Exception as e:
                logger.error(f"Error claiming match {match_id} - {e}")
                await ctx.reply(f"Error claiming match: {e}")
                return


async def check_scheduled_matches():
    channel = bot.get_channel(881917059905253386)  # gym-newbie-league
    caster_role = "<@&931627673225138177>"
    import matchups

    upcoming_matches = matchups.get_upcoming_matches()
    if len(upcoming_matches) > 0:
        logger.info("Checking for matches scheduled in the next 24 hours")
        result = ""
        for match in upcoming_matches:
            match_date = int(match.datetime.timestamp())
            match_date = f"<t:{match_date}:f>"
            result += f"[ID: {match.id}] [GROUP: {match.group}] **{match.p1_name} [{match.p1_race}]** vs **{match.p2_name} [{match.p2_race}]** - {match_date}"

            if match.stream != "":
                result += f" - <https://twitch.tv/{match.stream}>\n"
            else:
                result += f" - No {caster_role} scheduled yet - claim match with `!claim {match.id} <twitch_name>`\n"

        await channel.send(
            f"**Matches scheduled in the next 24 hours**:\nMatch times should be automatically converted to your timezone\n\n{result}"
        )
    else:
        logger.info("No upcoming matches without caster")


async def update_stream_schedule():
    logger.info("Updating stream schedule...")

    # get last message id
    channel = bot.get_channel(879207644399816704)
    message_id = channel.last_message_id
    message = await channel.fetch_message(message_id)

    # fetch list of scheduled matches
    import matchups
    from datetime import datetime

    last_update_time = int(datetime.now().timestamp())
    last_update_time_string = f"<t:{last_update_time}:f>"

    upcoming_matches = matchups.get_weekly_matches()
    if len(upcoming_matches) > 0:
        count = 0
        result = ""
        for match in upcoming_matches:
            # check if day of current match is different from previous match
            if match.datetime.strftime("%a %b %d") != upcoming_matches[
                count - 1
            ].datetime.strftime("%a %b %d"):
                result += f"\n**{match.datetime.strftime('%a %b %d')}**\n"
            match_date = int(match.datetime.timestamp())
            match_date = f"<t:{match_date}:f>"
            if match.datetime < datetime.now():
                result += f"_[{match.group}] **{match.p1_name} [{match.p1_race}]** vs **{match.p2_name} [{match.p2_race}]** - {match_date}_"
            else:
                result += f"[{match.group}] **{match.p1_name} [{match.p1_race}]** vs **{match.p2_name} [{match.p2_race}]** - {match_date}"

            if match.stream != "":
                result += f" - <https://twitch.tv/{match.stream}>\n"
            else:
                result += f" - `[{match.id}]`\n"

            count += 1

        result += "\n**Claim matches with `!claim <match_id> <twitch_name>`**"
        result += "\n**For full schedule check out <https://warcraft-gym.com/>**"
        result += f"\n *Updated: {last_update_time_string}*"

    # convert result to discord embed
    embed = discord.Embed(
        title="FoM League Season 4 Stream Schedule", description=result, color=0x00FF00
    )
    # edit message with new embed
    try:
        logger.info(f"Editing stream schedule message... Characters: {len(result)}")
        await message.edit(embed=embed)
    except discord.errors.HTTPException as e:
        logger.error(f"Error updating stream schedule - {e}")
    # await message.edit(content=result)


@bot.command(name="hotdog")
async def hotdog(ctx: commands.Context):
    await ctx.reply(file=discord.File("assets/hotdog.gif"))


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


@bot.command(pass_context=True)
async def getserverid(ctx):
    serverId = ctx.message.guild.id
    await ctx.send(serverId)


@bot.event
async def on_ready():
    global guild
    guild = bot.get_guild(int(config.FOM_GUILD_ID))
    logger.info(f"We have logged in as {bot.user}")

    # initialize the scheduler
    scheduler = AsyncIOScheduler()

    # add scheduled matches job to scheduler
    scheduler.add_job(check_scheduled_matches, CronTrigger(hour="0,6,12,18"))
    # add update stream schedule job to scheduler to run at every 5th minute
    scheduler.add_job(update_stream_schedule, CronTrigger(minute="*/5"))

    scheduler.start()


DISCORD_TOKEN = config.DISCORD_TOKEN
bot.run(DISCORD_TOKEN)
