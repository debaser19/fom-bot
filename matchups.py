import gspread

import config


class Matchup:
    def __init__(self, id, datetime, p1_name, p1_race, p2_name, p2_race, group, stream):
        self.id = id
        self.datetime = datetime
        self.p1_name = p1_name
        self.p1_race = p1_race
        self.p2_name = p2_name
        self.p2_race = p2_race
        self.group = group
        self.stream = stream


def get_upcoming_matches():
    gc = gspread.service_account(filename=config.SERVICE_ACCOUNT_FILE)
    sh = gc.open_by_url(config.MATCHUPS_SHEET)
    sheet = sh.worksheet("s4")
    print(f"Grabbing all matchups")
    records = sheet.get_all_records()
    matchups_list = []
    from datetime import datetime, timedelta

    for record in records:
        match_date = record.get("DATE")
        match_date = match_date.strip()
        match_time = record.get("START TIME (EDT)")
        match_time = match_time.strip()

        # convert match_date and match_time to datetime object
        match_datetime = datetime.strptime(
            f"{match_date} {match_time}", "%m/%d/%Y %I:%M %p"
        )
        matchups_list.append(
            Matchup(
                record.get("id"),
                match_datetime,
                record.get("PLAYER 1"),
                record.get("RACE 1"),
                record.get("PLAYER 2"),
                record.get("RACE 2"),
                record.get("GROUP"),
                record.get("STREAM"),
            )
        )

    new_matchups_list = []
    for matchup in matchups_list:
        # remove matchups that have no date, are in the past, or more than one hour away
        if (
            matchup.datetime is not None
            and matchup.datetime > datetime.now()
            and matchup.datetime < datetime.now() + timedelta(hours=24)
        ):
            # print(f"Removing matchup: {matchup}")
            print(f"Adding matchup: {matchup}")
            new_matchups_list.append(matchup)

    # sort list based on datetime value
    new_matchups_list.sort(key=lambda x: x.datetime)
    print("List of upcoming matches in the next 24 hours:")
    for matchup in new_matchups_list:
        print(
            matchup.id,
            matchup.datetime,
            matchup.p1_name,
            matchup.p1_race,
            matchup.p2_name,
            matchup.p2_race,
            matchup.group,
            matchup.stream,
        )
    return new_matchups_list


get_upcoming_matches()
