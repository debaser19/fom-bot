from pstats import Stats
from pydoc import describe
from discord.ext import commands
import discord
import requests
import gspread
import pandas as pd
from datetime import datetime
import json

import config

bot = commands.Bot(command_prefix="!")

def get_fom_sheet():
    gc = gspread.service_account(filename=config.SERVICE_ACCOUNT_FILE)
    return gc.open_by_url(config.FOM_SHEET)


class Player:
    def __init__(self, challonge_name, bnet_tag, discord_tag, race):
        self.challonge_name = challonge_name
        self.bnet_tag = bnet_tag
        self.discord_tag = discord_tag
        self.race = race


def get_players_list():
    sheet = get_fom_sheet()
    ws = sheet.worksheet("player api")
    records = ws.get_all_records()

    players = []
    
    for record in records:
        players.append(
            Player(
                record.get('challonge name'),
                record.get('battlenet tag'),
                record.get('discord name'),
                record.get('race')
            )
        )
    
    return players


@bot.command(name='players')
async def players(ctx:commands.Context):
    players = get_players_list()
    for player in players:
        print(player)


@bot.command(name='s2')
async def s2(ctx: commands.Context, username=None):
    worksheet = get_fom_sheet().get_worksheet("player api")
    if username:
        if username.lower() in worksheet.get_all_records():
            for user in worksheet.get_all_records():
                if username.lower() in user['Player'].lower():
                    print(f'found {user["Player"]}')
                else:
                    print(f'Username not found - {user["Player"]}')
    else:
        print('Dumping stats list')
        df = pd.DataFrame(data=worksheet.get_all_values())
        df.columns = df.iloc[0]
        df = df.reindex(df.index.drop(0)).reset_index(drop=True)
        df.columns.name = None
        print(df)

        embed=discord.Embed(
            title='Season 2 Stats',
            colour=0xE45B9D,
            description=df
        )
        fom_logo = 'https://s3.amazonaws.com/challonge_app/organizations/images/000/143/459/large/discord_icon.png'
        embed.set_author(name='Fountain of Manner', icon_url=fom_logo)

        await ctx.reply(embed=embed)


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

DISCORD_TOKEN = config.DISCORD_TOKEN
bot.run(DISCORD_TOKEN)