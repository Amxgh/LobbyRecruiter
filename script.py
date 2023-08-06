import os
import random
import re
import threading

import requests

# To get an api key, go to https://developer.hypixel.net/ and follow the instructions.
# For badlion the Chat logs can be found under `.minecraft/logs/blclient/minecraft/latest.log` (untested)

# CONSTANTS
API_KEYS = []
USER_PROFILE = os.getenv('USERPROFILE')
PATH = fr'{USER_PROFILE}\.lunarclient\offline\multiver\logs\latest.log'

REQUIRED_GEXP = 100000
MAX_GUILD_LEVEL_TO_INVITE = 150

# ! Below are constant variables, do not touch.
# The below is used to calculate the guild's level.
LEVEL_UP_EXP_NEEDED = [
    100000,
    150000,
    250000,
    500000,
    750000,
    1000000,
    1250000,
    1500000,
    2000000,
    2500000,
    2500000,
    2500000,
    2500000,
    2500000,
    3000000]


class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def get_hyapi_key():
    return random.choice(API_KEYS)


def get_weekly_gexp(uuid, guild_data):
    for member in guild_data["members"]:
        if member["uuid"] == uuid:
            return sum(member["expHistory"].values())
    return None


def get_guild_level_from_exp(exp):
    level = 0

    for req in LEVEL_UP_EXP_NEEDED:

        if exp >= req:
            exp -= req
            level += 1

    level += int(exp / LEVEL_UP_EXP_NEEDED[-1])

    return level


def check_stats(player):
    res = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{player}?').json()
    try:
        uuid = res['id']
    except KeyError:
        return False

    API_KEY = get_hyapi_key()

    # Getting data from hypixel
    headers = {"API-Key": API_KEY}
    guild_data = requests.get(
        f'https://api.hypixel.net/guild?player={uuid}',
        headers=headers).json()
    if guild_data and "guild" in guild_data:
        if guild_data["guild"]:
            guild_data = guild_data['guild']
            guild_level = get_guild_level_from_exp(guild_data['exp'])
            weekly_gexp = get_weekly_gexp(uuid, guild_data)

            if (guild_level < MAX_GUILD_LEVEL_TO_INVITE) and (weekly_gexp > REQUIRED_GEXP):
                print(f"Message and recruit: {colors.OKBLUE} {player} {colors.ENDC} ({weekly_gexp})\n")
                return True
            return False

        print(f"Send an invite to: {colors.OKGREEN} {player} {colors.ENDC}\n")
        return True


def find_players():
    print(colors.BOLD + 'Starting..\n')

    # Opening the logs file
    with open(PATH, 'r+b') as file:
        for line_bytes in file.readlines():
            line = str(line_bytes).split('[CHAT] ')[-1]  # Only message content
            line = re.sub(r'\\[nrt]', '', line)  # Remove all escape characters

            if line.startswith('Online Players'):
                line = line.split(': ')[-1]  # Players only in message
                players = line.split(', ')  # Split at comma and remove whitespace before name

        for player in players:
            # Split name at end of rank and get last element (works for every rank including non)
            player = player.split('] ')[-1]

            threading.Thread(target=check_stats, args=(player,)).start()


try:
    find_players()
except KeyboardInterrupt:
    exit(0)
