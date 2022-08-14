import challonge

import config


class Player:
    def __init__(
        self, id, name, discord_tag, bnet_tag, seed, group, race, w3c_link, region
    ):
        self.id = id
        self.name = name
        self.discord_tag = discord_tag
        self.bnet_tag = bnet_tag
        self.seed = seed
        self.group = group
        self.race = race
        self.w3c_link = w3c_link
        self.region = region


class Match:
    def __init__(
        self,
        id,
        group,
        round,
        p1_id,
        p1_name,
        p1_discord,
        p1_region,
        p1_race,
        p2_id,
        p2_name,
        p2_discord,
        p2_region,
        p2_race,
        state,
        score,
    ):
        self.id = id
        self.group = group
        self.round = round
        self.p1_id = p1_id
        self.p1_name = p1_name
        self.p1_discord = p1_discord
        self.p1_discord_id = None
        self.p1_region = p1_region
        self.p1_race = p1_race
        self.p2_id = p2_id
        self.p2_name = p2_name
        self.p2_discord = p2_discord
        self.p2_discord_id = None
        self.p2_region = p2_region
        self.p2_race = p2_race
        self.state = state
        self.score = score


def fetch_group(seed):
    if seed in range(1, 9):
        return "A"
    elif seed in range(9, 17):
        return "B"
    elif seed in range(17, 25):
        return "C"
    elif seed in range(25, 33):
        return "D"
    elif seed in range(33, 41):
        return "E"
    elif seed in range(41, 49):
        return "F"
    elif seed in range(49, 57):
        return "G"
    elif seed in range(57, 65):
        return "H"
    elif seed in range(65, 73):
        return "I"
    elif seed in range(73, 81):
        return "J"
    elif seed in range(81, 89):
        return "K"
    elif seed in range(89, 97):
        return "L"
    elif seed in range(97, 105):
        return "M"
    elif seed in range(105, 113):
        return "N"
    elif seed in range(113, 121):
        return "O"
    elif seed in range(121, 129):
        return "P"
    elif seed in range(129, 137):
        return "Q"
    else:
        return "WAITLIST"


def fetch_players(tournament):
    players = challonge.participants.index(tournament["id"])
    player_list = []
    for player in players:
        try:
            player_list.append(
                Player(
                    player["group_player_ids"][0],
                    player["name"],
                    player["custom_field_response"]["29915"],
                    player["custom_field_response"]["29916"],
                    player["seed"],
                    fetch_group(player["seed"]),
                    player["custom_field_response"]["29917"],
                    player["custom_field_response"]["29918"],
                    player["custom_field_response"]["29919"],
                )
            )
        except Exception as err:
            print(
                f"Missing info for player {player['name']} - adding blank values: {err}"
            )
            player_list.append(
                Player(
                    player["id"],
                    player["name"],
                    "fake_discord_tag",
                    "fake_bnet_tag",
                    "fake_seed",
                    "fake_group",
                    "fake_race",
                    "fake_w3c_link",
                    "fake_region",
                )
            )

    return player_list


def fetch_matches(tournament):
    players = fetch_players(tournament)
    matches = challonge.matches.index(tournament["id"])

    matches_list = []
    for match in matches:
        p1_discord_tag = (
            p1_name
        ) = (
            p1_race
        ) = p1_region = p2_discord_tag = p2_name = p2_race = p2_region = "blank"
        for player in players:
            # print(f"{match['player1_id']} - {player.id}")
            if match["player1_id"] == player.id:
                # print(f"{match['player1_id']} matches {player.id}")
                p1_id = player.id
                p1_name = player.name
                p1_group = player.group
                p1_discord_tag = player.discord_tag
                p1_race = player.race
                p1_region = player.region
            elif match["player2_id"] == player.id:
                p2_id = player.id
                p2_name = player.name
                p2_group = player.group
                p2_discord_tag = player.discord_tag
                p2_race = player.race
                p2_region = player.region

        matches_list.append(
            Match(
                match["id"],
                p1_group,
                match["round"],
                p1_id,
                p1_name,
                p1_discord_tag,
                p1_region,
                p1_race,
                p2_id,
                p2_name,
                p2_discord_tag,
                p2_region,
                p2_race,
                match["state"],
                match["scores_csv"],
            )
        )

    return matches_list


# def main():
#     challonge.set_credentials("debaser19", config.CHALLONGE_KEY)
#     tournament = challonge.tournaments.show(config.FOML_S4_ID)

#     # players = fetch_players(tournament)
#     # for player in players:
#     #     if 'hippo'.lower() in player.name.lower():
#     #         print(player.name, player.group, player.seed)
# #     print(tournament["id"])
# #     print(tournament["name"])
# #     print(tournament["started_at"])

# #     players = challonge.participants.index(tournament["id"])
# #     for player in players:
# #         print(player)
#     matches = fetch_matches(tournament)

#     for match in matches:
#         print(f"[{match.id}] Round {match.round} [{match.group}] - {match.p1_name} / {match.p1_discord} [{match.p1_race}] VS {match.p2_name} / {match.p2_discord} [{match.p2_race}] - [{match.state}] [{match.score}]")

# main()
