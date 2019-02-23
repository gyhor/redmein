from __future__ import print_function
from datetime import date, datetime, timedelta
import os
import tempfile


PERIODS = {
  'y': {'name': 'yesterday', 'description': 'Yesterday'},
  'lw': {'name': 'lastweek', 'description': 'Last work week'},
  'cw': {'name': 'currentweek', 'description': 'Current work week'},
  'flw': {'name': 'fulllastweek', 'description': 'Last full week'},
  'fcw': {'name': 'fullcurrentweek', 'description': 'Current full week'}
}


def time_entry_list(from_date, to_date, user, redmine):
    print("Fetching time entries from {} to {} for {}...".format(from_date, to_date, user))
    print()

    # Get yesterday's time entries
    time_entries = redmine.time_entry.filter(user_id=user.id, from_date=from_date, to_date=to_date, sort='hours:desc')

    if time_entries:
        sum = 0

        # Print scrum update template
        report = "Time entries:\n"

        for entry in time_entries:
            report += entry_bullet_point(entry)
            sum += entry.hours

        report += "\n" + str(sum) + " hours.\n"
    else:
        report = "No time entries.\n"

    print(report)


def entry_bullet_point(entry):
    if hasattr(entry, 'issue'):
        issue_id = '#' + str(entry.issue.id)
    else:
        issue_id = 'none'

    item = '* {} / {} hours ({})'.format(entry.comments, str(entry.hours),  issue_id)

    item = item + ' [' + str(entry.id) + ']'

    item = item + ' ' + str(entry.activity)

    return item + "\n"


def handle_date_calculation_value(date_value):
    if date_value[:1] == '+' or date_value[:1] == '-':
        date_value_raw = date.today() + timedelta(int(date_value))
        date_value = date_value_raw.strftime('%Y-%m-%d')

    return date_value


def weekday_of_week(day_of_week, weeks_previous=0):
    days_ahead_of_weekday_last_week = date.today().weekday() + (weeks_previous * 7) - day_of_week
    last_weekday = datetime.now() - timedelta(days=days_ahead_of_weekday_last_week)
    return last_weekday.strftime("%Y-%m-%d")


def weekday_last_week(day_of_week):
    return weekday_of_week(day_of_week, 1)


def resolve_period_abbreviation(period):
    period = period.lower()

    if period in PERIODS:
        return PERIODS[period]['name']

    if period in {abbr: item.get('name') for abbr, item in PERIODS.items()}.values():
        return period

    return None


def resolve_period(period):
    if period == 'yesterday':
        yesterday = handle_date_calculation_value('-1')
        return {'start': yesterday, 'end': yesterday}

    if period == 'lastweek':
        start_date = weekday_last_week(0)  # last Monday
        end_date = weekday_last_week(4)  # last Friday
        return {'start': start_date, 'end': end_date}

    if period == 'currentweek':
        start_date = weekday_of_week(0)  # this Monday
        end_date = weekday_of_week(4)  # this Friday
        return {'start': start_date, 'end': end_date}

    if period == 'fulllastweek':
        start_date = weekday_of_week(6, 2)  # last Sunday
        end_date = weekday_of_week(5, 1)  # last Saturday
        return {'start': start_date, 'end': end_date}

    if period == 'fullcurrentweek':
        start_date = weekday_last_week(6)  # this Sunday
        end_date = weekday_of_week(5)  # this Saturday
        return {'start': start_date, 'end': end_date}


def resolve_activity_alias(activity_name, aliases):
    if activity_name in aliases:
        return resolve_activity_alias(aliases[activity_name], aliases)
    else:
        return activity_name


def resolve_issue_template(issue_name, templates):
    if issue_name in templates:
        return templates[issue_name]


def template_field(issue_name, field, templates):
    template = resolve_issue_template(issue_name, templates)
    if template and field in template:
        return template[field]


def resolve_issue_alias(issue_id, templates):
    resolved_id = template_field(issue_id, 'id', templates)

    if resolved_id:
        return resolve_issue_alias(resolved_id, templates)
    else:
        return issue_id


def get_cache_filename(type_name):
    return os.path.join(tempfile.gettempdir(), 'redmein-{}'.format(type_name))
