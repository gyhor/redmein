from __future__ import print_function
import json
import os
import yaml
import helpers


def load_config():
    """Return configuration, from YAML file, for this application.
    Raises:
        Exception: If not able to read or parse the configuration file for any
                   reason or if "base branch" isn't set in the configuration
                   file.
    Returns:
        dict: Configuration information.
    """
    config_filename = '.redmein.yml'

    # Attempt to load configuration file from user's home directory
    config_path = os.path.join(os.path.expanduser('~'), config_filename)

    try:
        config = yaml.safe_load(open(config_path))
    except IOError:
        raise Exception('Unable to load ~/{}: does it exist (or is there a YAML error)?'.format(config_filename))

    # Verify Redmine URL has been set in the config file
    if 'url' not in config:
        raise Exception('Please set Redmine site as "url" in {}.'.format(config_filename))

    # Verify Redmine key has been set in the config file
    if 'redmine_key' not in config:
        raise Exception('Please set Redmine api key as "redmine_key" in {}.'.format(config_filename))

    # Verify default activity has been set in the config file
    if 'default activity' not in config:
        raise Exception('Please set default acitivity as "default activity" in {}.'.format(config_filename))

    return config


def get_activities(redmine):
    activities_cache_filename = helpers.get_cache_filename('activities')

    if os.path.isfile(activities_cache_filename):
        with open(activities_cache_filename, "r") as activities_file:
            return json.loads(activities_file.read())
    else:
        activities = {}

        enumerations = redmine.enumeration.filter(resource='time_entry_activities')
        for enum in enumerations:
            activities[enum.name] = enum.id

        with open(activities_cache_filename, "w") as activities_file:
            activities_file.write(json.dumps(activities))

        return activities


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
            report += helpers.entry_bullet_point(entry)
            sum += entry.hours

        report += "\n" + str(sum) + " hours.\n"
    else:
        report = "No time entries.\n"

    print(report)
