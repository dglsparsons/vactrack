# -*- coding: utf-8 -*-

# vactrack.py code by @thetafferboy

import requests
from datetime import date, timedelta

# You can change population of UK if you wish, which will change % calculations
population_of_uk = 52632729

# How many blocks you want in progress bar, 15 works well with Twitter ▓▓▓▓▓░░░░░░░░░░
bar_total = 15
perc_per_bar = 100/bar_total

# This sets date to 2 days ago, as there is a lag in government data reporting.
# API requests will fail if you request date which has no data yet
date_to_check = (date.today() - timedelta(2)).isoformat()
previous_date = (date.today() - timedelta(3)).isoformat()


def get_data():
    # GOV UK data source API:
    res = requests.get(
        'https://api.coronavirus.data.gov.uk/v2/data'
        '?areaType=overview'
        '&metric=cumPeopleVaccinatedFirstDoseByPublishDate'
        '&metric=cumPeopleVaccinatedSecondDoseByPublishDate'
    )
    res.raise_for_status()
    return res.json()


def get_count(field, data):
    date = next(d for d in data['body'] if d['date'] == date_to_check)
    previous = next(d for d in data['body'] if d['date'] == previous_date)

    return date[field], previous[field]


def calc_percent(dose, previous):
    percent = (dose / population_of_uk) * 100
    previous_percent = (previous / population_of_uk) * 100

    return round(percent, 2), round(percent - previous_percent, 2)


def create_bar(percent):
    solid_count = int(percent // perc_per_bar)
    empty_count = bar_total - solid_count

    return '▓'*solid_count + '░'*empty_count


def main():
    data = get_data()
    first_dose, first_dose_previous = get_count('cumPeopleVaccinatedFirstDoseByPublishDate', data)
    second_dose, second_dose_previous = get_count(
        'cumPeopleVaccinatedSecondDoseByPublishDate', data)

    first_dose_percent, increase = calc_percent(first_dose, first_dose_previous)
    second_dose_percent, second_dose_increase = calc_percent(second_dose, second_dose_previous)

    print(f"""
1st dose of vaccine progress:

{create_bar(first_dose_percent)} {first_dose_percent:.2f}% (+{increase:.2f}%)

2nd dose of vaccine progress:

{create_bar(second_dose_percent)} {second_dose_percent:.2f}% (+{second_dose_increase:.2f}%)


Total increase {increase + second_dose_increase:.2f}%
As of {date_to_check}

Using data from UK Gov API
#CovidVaccine
""")


main()
