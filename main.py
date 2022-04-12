from discord.ext import commands
import discord
import gspread

import config

bot = commands.Bot(command_prefix="!")

def get_fom_sheet():
    gc = gspread.service_account(filename=config.SERVICE_ACCOUNT_FILE)
    return gc.open_by_url(config.FOM_SHEET)


class Player:
    def __init__(self, name, race, wins, losses, win_pct, seasons, s1_champ, s2_champ, s1_mp, s2_mp, total_mp, rank):
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
                record.get('Rank')
            )
        )
    
    return players


@bot.command(name='stats')
async def stats(ctx:commands.Context, user):
    players = get_players_list()
    for player in players:
        if user.lower() == player.name.lower():
            content_string = f"""
            **Player Name**: {player.name}
            **Rank**: {player.rank}
            **Race**: {player.race}
            **Wins**: {player.wins}
            **Losses**: {player.losses}
            **Win Pct**: {player.win_pct}
            **Seasons Played**: {player.seasons}
            **Season 1 Manner Points**: {player.s1_mp}
            **Season 2 Manner Points**: {player.s2_mp}
            **Total Manner Points**: {player.total_mp}
            """
            embed = discord.Embed(
                title=f"{player.name} Stats",
                colour=0x0C2C55,
                description=content_string
            )

            fom_logo = 'https://s3.amazonaws.com/challonge_app/organizations/images/000/143/459/large/discord_icon.png'
            embed.set_author(name='Fountain of Manner', icon_url=fom_logo)

            if player.s1_champ == 'YES':
                embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/963256852613832734/963258532847845476/trophy_1.png')
            if player.s2_champ == 'YES':
                embed.set_thumbnail(url='https://i.imgur.com/txh9BQm.png')

            await ctx.reply(embed=embed)


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

DISCORD_TOKEN = config.DISCORD_TOKEN
bot.run(DISCORD_TOKEN)