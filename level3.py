# -*- coding: utf-8 -*-
import json
import random
import sys
import math
import datetime
from datetime import datetime as dt

DATE_FORMAT = '%Y-%m-%d'


def get_args_validity(reviewee_id, lang, data):
    engineer_ids = map(lambda x: x["id"], data["engineers"])
    if reviewee_id not in engineer_ids:
        print(reviewee_id + " not in engineer list.")
        # not reccomend 突然死はよろしくない
        # 終わる場所は一箇所がいい。なにがあっても返る場所がある。
        # layered architecture
        # 良い設計のコードを読んでいく。それを読んで。ライブラリだったらある。
        # サービスレベルだと？マストドン設計。
        sys.exit()

    chottodekiru_langs = []
    for engineer in data["engineers"]:
        chottodekiru_langs.extend(engineer["chottodekiru"])

    if lang not in chottodekiru_langs:
        print("No one can review " + lang + ".")
        sys.exit()


def get_data_from_jsonpath(json_path):
    json_engineers = open(json_path)
    data = json.load(json_engineers)
    return data


def judge_business_day(datetime, data):
    not_weekend = datetime.weekday() is not 5 and datetime.weekday() is not 6
    not_holiday = str(datetime.date()) not in data["holidays"]

    if not_weekend and not_holiday:
        return True
    else:
        return False


def get_xth_next_business_day_from_date_str(date_str, x, data):
    date_datetime = dt.strptime(date_str, DATE_FORMAT)

    temp_datetime = date_datetime
    business_day_count = 0
    while business_day_count < math.fabs(x):
        # days=1 * x / math.fabs(x) ; matches plus/minus to x while keeping it's abs to 1.
        temp_datetime += datetime.timedelta(days=1 * x / math.fabs(x))

        if judge_business_day(temp_datetime, data):
            business_day_count += 1

    next_business_day_datetime = temp_datetime

    return next_business_day_datetime


def get_deadline_validity(earliest_deadline_datetime, deadline_date_str, data):
    deadline_datetime = dt.strptime(deadline_date_str, DATE_FORMAT)
    later_than_earliest_deadline = deadline_datetime >= earliest_deadline_datetime
    is_business_day = judge_business_day(deadline_datetime, data)
    validity = later_than_earliest_deadline and is_business_day

    return validity


def get_error_message_for_invalid_deadline(data, deadline_str, earliest_deadline_datetime):
    deadline_datetime = dt.strptime(deadline_str, DATE_FORMAT)
    deadline_is_weekend = deadline_datetime.weekday() == 5 or deadline_datetime.weekday() == 6
    msg = "Deadline is invalid. Please choose a business day later than " + str(earliest_deadline_datetime.date()) + "."

    if deadline_str in data["holidays"]:
        msg += "\nYou choosed a holiday."
    if deadline_is_weekend:
        msg += "\nYou choosed a weekend."
    return msg



def get_engineer_from_id(data, id):
    for engineer in data["engineers"]:
        if engineer['id'] == id:
            return engineer


def get_engineer_id(engineer):
    return engineer["id"]


def get_engineer_team(engineer):
    return engineer["team"]


def get_recent_reviewer_ids(data):
    recent_reviewer_ids = map(lambda log: log["reviewer"], data["recent_review_log"][:3])
    return recent_reviewer_ids


def get_recent_reviewer_from_ids(data, recent_reviewer_ids):
    recent_reviewers = map(lambda id: get_engineer_from_id(data, id), recent_reviewer_ids)
    return recent_reviewers


# below 4 defs are for choosing a teammate
def get_all_reviewee_teammates(reviewee, data):
    reviewee_team = get_engineer_team(reviewee)
    reviewee_id = get_engineer_id(reviewee)
    engineers = data["engineers"]
    teammate = [engineer for engineer in engineers if
                engineer["team"] == reviewee_team and engineer["id"] != reviewee_id]

    return teammate


# TODO: maybe change name to get_chottodekiru_filtered_reviewee_teammates
def get_filtered_reviewee_teammates(reviewee, teammates, lang):
    if lang not in reviewee["chottodekiru"]:
        filtered_teammates = [engineer for engineer in teammates if (lang in engineer["chottodekiru"])]
        return filtered_teammates
    else:
        return teammates


def get_vacation_filtered_candidates(data, candidate_engineers, deadline_str):
    candidate_ids = map(lambda x: x["id"], candidate_engineers)
    deadline_datetime = dt.strptime(deadline_str, DATE_FORMAT)

    for vacation in data["vacations"]:

        if vacation["engineer_id"] in candidate_ids:

            unreviewable_start_datetime = get_xth_next_business_day_from_date_str(vacation["start_day"], -1, data)
            unreviewable_end_datetime = get_xth_next_business_day_from_date_str(vacation["end_day"], 1, data)

            if unreviewable_start_datetime <= deadline_datetime <= unreviewable_end_datetime:
                engineer_in_vacation = get_engineer_from_id(data, vacation["engineer_id"])
                candidate_engineers.remove(engineer_in_vacation)

    return candidate_engineers


def choose_teammate_reviewer(teammates):
    if len(teammates) != 0:
        reviewer = random.choice(teammates)
    else:
        reviewer = {"id": "N/A", "team": "N/A"}

    return reviewer


# below 3defs are for choosing someone in another team member
def get_reviewee_other_team_members(reviewee, data):
    reviewee_team = get_engineer_team(reviewee)
    engineers = data["engineers"]
    other_team_members = [engineer for engineer in engineers if
                          engineer["team"] != reviewee_team]

    return other_team_members

# TODO: maybe change def name
def get_filtered_reviewee_other_team_members(other_team_members, lang):
    filtered_other_team_members = [engineer for engineer in other_team_members if (lang in engineer["chottodekiru"])]
    return filtered_other_team_members


def choose_other_teammember_reviewer(other_teammembers, lang):
    if len(other_teammembers) != 0:
        otherteam_reviewer_candidates = [engineer for engineer in other_teammembers \
                                         if (lang in engineer["chottodekiru"])]
        reviewer = random.choice(otherteam_reviewer_candidates)
    else:
        reviewer = {"id": "N/A", "team": "N/A"}

    return reviewer


def choose_random_reviewer(filtered_reviewee_teammates, filtered_reviewee_other_teammembers, \
                           teammate_reviewer, otherteam_reviewer):
    temp_candidates = filtered_reviewee_teammates + filtered_reviewee_other_teammembers

    for reviewer in [teammate_reviewer, otherteam_reviewer]:
        if reviewer["id"] != "N/A":
            temp_candidates.remove(reviewer)

    return random.choice(temp_candidates)


def main(argvs, run_date_str):
    reviewee_id = argvs[1].replace("reviewee=", '')
    jsonpath = argvs[2].replace("json=", '')
    lang = argvs[3].replace("lang=", '')
    deadline_str = argvs[4].replace("deadline=", '')

    data = get_data_from_jsonpath(jsonpath)
    get_args_validity(reviewee_id, lang, data)

    earliest_deadline_datetime = get_xth_next_business_day_from_date_str(run_date_str, 2, data)
    if get_deadline_validity(earliest_deadline_datetime, deadline_str, data) is False:
        print(get_error_message_for_invalid_deadline(data, deadline_str, earliest_deadline_datetime))
        sys.exit()

    reviewee = get_engineer_from_id(data, reviewee_id)
    data["engineers"].remove(reviewee)

    recent_reviewers_ids = get_recent_reviewer_ids(data)
    recent_reviewers = get_recent_reviewer_from_ids(data, recent_reviewers_ids)
    for reviewer in recent_reviewers:
        data["engineers"].remove(reviewer)

    reviewee_teammates = get_all_reviewee_teammates(reviewee, data)
    filtered_reviewee_teammates = get_filtered_reviewee_teammates(reviewee, reviewee_teammates, lang)
    filtered_reviewee_teammates = get_vacation_filtered_candidates(data, filtered_reviewee_teammates, deadline_str)
    teammate_reviewer = choose_teammate_reviewer(filtered_reviewee_teammates)

    reviewee_other_teammembers = get_reviewee_other_team_members(reviewee, data)
    filterd_reviewee_other_teammembers = get_filtered_reviewee_other_team_members(reviewee_other_teammembers, lang)
    filterd_reviewee_other_teammembers = get_vacation_filtered_candidates(data, filterd_reviewee_other_teammembers,
                                                                          deadline_str)
    otherteam_reviewer = choose_other_teammember_reviewer(filterd_reviewee_other_teammembers, lang)

    last_reviewer = choose_random_reviewer(filtered_reviewee_teammates, filterd_reviewee_other_teammembers, \
                                           teammate_reviewer, otherteam_reviewer)

    reviewer_list = [teammate_reviewer, otherteam_reviewer, last_reviewer]
    # reviewer_ids = map(lambda x: x["id"], reviewer_list)
    reviewer_ids = [reviewer['id'] for reviewer in reviewer_list]
    output_ids = ','.join(reviewer_ids)

    print(output_ids)

    return output_ids


if __name__ == '__main__':
    argvs = sys.argv
    main(argvs, "2017-04-26")