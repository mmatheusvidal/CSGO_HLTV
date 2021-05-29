import json
import pandas as pd
from time import sleep
from typing import Dict, List
from selenium.webdriver import Chrome
from selenium.common.exceptions import NoSuchElementException


def print_error(err, text: str = "Error."):
    """Print error given Exception"""
    print(
        "["
        + "\033[91m"
        + f"{err}"
        + "\033[0m"
        + "]"
        + "\033[91m"
        + " -> "
        + "\033[0m"
        + f"{text}"
    )


def get_pages(browser, data: pd.DataFrame):
    """Return a list with matches url"""
    return list(data["match_url"])


def get_date(browser):
    """Return the date in the top of the page"""
    return {"date": browser.find_element_by_class_name("date").text}


def get_flexbox(browser) -> Dict[str, str]:
    """Return Dict with teamnames, total scores, scores per side, mapnames and sides"""
    flexbox_dict = {}

    box = browser.find_element_by_class_name("flexbox-column")

    # Team names
    team_names = box.find_elements_by_class_name("results-teamname")
    flexbox_dict["first_team"] = team_names[0].text
    flexbox_dict["second_team"] = team_names[1].text

    ranks = browser.find_elements_by_class_name("teamRanking")

    for idx_rank, rank in enumerate(ranks):
        rank_value = rank.get_attribute("textContent").split("#")[-1]
        try:
            rank_value = int(rank_value)

        except ValueError:
            rank_value = rank_value.split("\n")[1].lstrip().rstrip()

        flexbox_dict[f"{['first','second'][idx_rank]}_team_world_rank_#"] = rank_value

    # Total Score
    t1 = browser.find_element_by_class_name("team1-gradient")
    flexbox_dict["first_team_total_score"] = int(
        t1.get_attribute("textContent").split("\n")[-2]
    )
    t2 = browser.find_element_by_class_name("team2-gradient")
    flexbox_dict["second_team_total_score"] = int(
        t2.get_attribute("textContent").split("\n")[-2]
    )

    if flexbox_dict["first_team_total_score"] > flexbox_dict["second_team_total_score"]:
        flexbox_dict["first_team_won"] = 1
    else:
        flexbox_dict["first_team_won"] = 0

    # Scores and Maps
    maps = box.find_elements_by_class_name("mapname")
    scores = box.find_elements_by_class_name("results-team-score")

    flexbox_dict["M1"] = maps[0].text
    flexbox_dict["first_team_score_M1"] = scores[0].text
    flexbox_dict["second_team_score_M1"] = scores[1].text

    flexbox_dict["M2"] = maps[1].text
    flexbox_dict["first_team_score_M2"] = scores[2].text
    flexbox_dict["second_team_score_M2"] = scores[3].text

    flexbox_dict["M3"] = maps[2].text
    flexbox_dict["first_team_score_M3"] = scores[4].text
    flexbox_dict["second_team_score_M3"] = scores[5].text

    flexbox_dict = get_sides(box, flexbox_dict)

    return flexbox_dict


def get_sides(box, flexbox_dict: Dict[str, str]) -> Dict[str, str]:
    """Return the side played by each team"""
    sides = box.find_elements_by_class_name("results-center-half-score")

    for idx, side in enumerate(sides):
        ct = int(side.find_element_by_class_name("ct").text)
        score_first_team = int(side.text.strip("(").split(";")[0].split(":")[0])
        if ct == score_first_team:
            flexbox_dict[f"side_first_team_M{idx+1}"] = "CT"
            flexbox_dict[f"side_second_team_M{idx+1}"] = "T"
        else:
            flexbox_dict[f"side_first_team_M{idx+1}"] = "T"
            flexbox_dict[f"side_second_team_M{idx+1}"] = "CT"

        scores = side.text.split("(")[1]
        scores = scores.split(":")
        flexbox_dict[f"score_first_team_t1_M{idx+1}"] = int(scores[0])
        flexbox_dict[f"score_first_team_t2_M{idx+1}"] = int(scores[1].split("; ")[1])
        flexbox_dict[f"score_second_team_t1_M{idx+1}"] = int(scores[1].split("; ")[0])
        flexbox_dict[f"score_second_team_t2_M{idx+1}"] = int(scores[-1].strip(")")[0])

    if len(sides) < 3:
        flexbox_dict["side_first_team_M3"] = "-"
        flexbox_dict["side_second_team_M3"] = "-"
        flexbox_dict["score_first_team_t1_M3"] = "-"
        flexbox_dict["score_first_team_t2_M3"] = "-"
        flexbox_dict["score_second_team_t1_M3"] = "-"
        flexbox_dict["score_second_team_t2_M3"] = "-"

    return flexbox_dict


def get_picks_bans(browser, first_team: str) -> Dict[str, str]:
    """Return picks and bans"""
    picks_bans_dict = {}

    lcolumn = browser.find_element_by_class_name("col-6")
    picks_bans = lcolumn.find_elements_by_class_name("padding")[1]
    picks_bans = picks_bans.text.split("\n")

    first_ban = picks_bans[0].split(".")[-1].lstrip().split(" ")[0].lower()

    if first_ban == first_team.lower():
        picks_bans_dict["first_pick_by_first_team"] = 1
    else:
        picks_bans_dict["first_pick_by_first_team"] = 0

    picks_bans_dict["ban 1"] = picks_bans[0].split(" ")[-1]
    picks_bans_dict["ban 2"] = picks_bans[1].split(" ")[-1]
    picks_bans_dict["pick 1"] = picks_bans[2].split(" ")[-1]
    picks_bans_dict["pick 2"] = picks_bans[3].split(" ")[-1]
    picks_bans_dict["ban 3"] = picks_bans[4].split(" ")[-1]
    picks_bans_dict["ban 4"] = picks_bans[5].split(" ")[-1]
    picks_bans_dict["pick 3"] = picks_bans[6].split(" ")[1]

    return picks_bans_dict


def get_stats(
    browser, lineup_dict: Dict[str, str], idx_team: int, idx_player: int
) -> Dict[str, str]:
    """Return stats"""
    stats = browser.find_element_by_class_name("stats-content")
    tables = stats.find_elements_by_class_name("table")

    if idx_team == 0:
        tables = tables[1:3]
    else:
        tables = tables[4:]

    nicks_element = tables[0].find_elements_by_xpath('.//span[@class="player-nick"]')
    nicks = [n.get_attribute("textContent").lstrip().rstrip() for n in nicks_element]

    lineup_dict[f"{['first','second'][idx_team]}_team_P{idx_player+1}"] = nicks[
        idx_player
    ]

    for tab_idx, table in enumerate(tables):
        nicks_element = table.find_elements_by_xpath('.//span[@class="player-nick"]')
        nicks = [
            n.get_attribute("textContent").lstrip().rstrip() for n in nicks_element
        ]

        # Locate Player
        nicks_idx_locate = nicks.index(
            lineup_dict[f"{['first','second'][idx_team]}_team_P{idx_player+1}"]
        )

        # Kills - Deaths
        kds = table.find_elements_by_class_name("kd")
        del kds[0]
        lineup_dict[
            f"{['first','second'][idx_team]}_team_P{idx_player+1}_{['CT','T'][tab_idx]}_KD"
        ] = kds[nicks_idx_locate].get_attribute("textContent")

        # +/-
        plus_minus = table.find_elements_by_class_name("plus-minus")
        del plus_minus[0]
        lineup_dict[
            f"{['first','second'][idx_team]}_team_P{idx_player+1}_{['CT','T'][tab_idx]}_+/-"
        ] = plus_minus[nicks_idx_locate].get_attribute("textContent")

        # ADR
        adr = table.find_elements_by_class_name("adr")
        del adr[0]
        lineup_dict[
            f"{['first','second'][idx_team]}_team_P{idx_player+1}_{['CT','T'][tab_idx]}_ADR"
        ] = adr[nicks_idx_locate].get_attribute("textContent")

        # Kast
        kast = table.find_elements_by_class_name("kast")
        del kast[0]
        lineup_dict[
            f"{['first','second'][idx_team]}_team_P{idx_player+1}_{['CT','T'][tab_idx]}_Kast"
        ] = kast[nicks_idx_locate].get_attribute("textContent")

        # Rating
        rating = table.find_elements_by_class_name("rating")
        del rating[0]
        lineup_dict[
            f"{['first','second'][idx_team]}_team_P{idx_player+1}_{['CT','T'][tab_idx]}_Rating"
        ] = rating[nicks_idx_locate].get_attribute("textContent")

    return lineup_dict


def get_lineup(browser) -> Dict[str, str]:
    """Return lineups, player names and stats"""
    lineup_dict = {}

    # Lineup
    lu = browser.find_element_by_class_name("lineups")
    lineups = lu.find_elements_by_class_name("players")

    for idx_team, lineup in enumerate(lineups):
        players = lineup.find_elements_by_class_name("text-ellipsis")

        for idx_player in range(len(players)):
            lineup_dict = get_stats(browser, lineup_dict, idx_team, idx_player)

    return lineup_dict


def get_details(browser, url_list: List, details: List):
    """Return details from the page"""
    for url in url_list:
        try:
            details_dict = {}
            browser.get(url)
            sleep(1)
            date_dict = get_date(browser)
            flexbox_dict = get_flexbox(browser)
            lineup_dict = get_lineup(browser)
            picks_bans_dict = get_picks_bans(browser, flexbox_dict["first_team"])

            details_dict = {
                **date_dict,
                **flexbox_dict,
                **lineup_dict,
                **picks_bans_dict,
            }
            details_dict["url"] = url
            details.append(details_dict)

        except KeyboardInterrupt:
            print_error(KeyboardInterrupt, "Saving data")

            return details

        except NoSuchElementException:
            print_error(NoSuchElementException, "Saving data")

            return details

    return details


def write_file(details):
    """Write collected results in JSON file"""
    f = open(
        "teste_details_1.json",
        "w",
    )
    f.write("[")
    for i in range(len(details)):
        json.dump(details[i], f)
        if i < len(details) - 1:
            f.write(",\n")
        else:
            f.write("\n")
    f.write("]")
    f.close()


def extract_players(csv_filename="HTLV_results.csv", sep=";"):
    """Return player details for each match"""
    details = []
    browser = Chrome()

    data = pd.read_csv(csv_filename, sep=sep, index_col=0)

    url_list = get_pages(browser, data[data["type_of_match"] == "bo3"])
    details = get_details(browser, url_list, details)
    write_file(details)


if __name__ == "__main__":
    extract_players()
