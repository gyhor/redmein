from __future__ import print_function
from datetime import date, datetime
import helpers
import os
import redminelib


def list_entries(args, config, app_data):
    today_raw = date.today()
    today = today_raw.strftime('%Y-%m-%d')

    if args.start or args.end:
        # Handle --start and --end
        if args.start and not args.end:
            from_date = args.start

            if from_date < today:
                to_date = today
            else:
                to_date = from_date
        elif not args.start and args.end:
            to_date = args.end

            if to_date > today:
                from_date = today
            else:
                from_date = to_date
        else:
            from_date = args.start
            to_date = args.end

        # Handle +/- values
        from_date = helpers.handle_date_calculation_value(from_date)
        to_date = helpers.handle_date_calculation_value(to_date)
    else:
        # List defaults to current day
        from_date = today
        to_date = today

    # Periods will override --from and --to
    if args.period and helpers.resolve_period(args.period):
        period = helpers.resolve_period(args.period)
        from_date = period['start']
        to_date = period['end']

    helpers.time_entry_list(from_date, to_date, app_data['user'], app_data['redmine'])


def new_entry(args, config, app_data):
    if args.id:
        # Warn user is issue isn't assigned or is assigned to another user
        issue = app_data['redmine'].issue.get(args.id)
        if not hasattr(issue, 'assigned_to'):
            print("*** Note: Issue is unassigned. ***\n")
        elif issue.assigned_to.id != app_data['user'].id:
            print("*** Note: Issue is not assigned to you. ***\n")

        entry = app_data['redmine'].time_entry.new()
        entry.issue_id = args.id
        entry.spent_on = date.today()

        if args.date:
            entry.spent_on = datetime.strptime(helpers.handle_date_calculation_value(args.date), '%Y-%m-%d').date()

        if args.comments:
            entry.comments = args.comments

        if args.hours:
            entry.hours = args.hours

        if not args.activity and 'default activity' in config:
            args.activity = helpers.resolve_activity_alias(config['default activity'], config['activities'])

        if args.activity:
            entry.activity_id = app_data['activities'][args.activity]

        entry.save()

        print(helpers.entry_bullet_point(entry))

        print("Time entry created.")

    else:
        print("Specify an issue ID using the --id option.")


def update_entry(args, config, app_data):
    if args.id:
        changed = False

        try:
            entry = app_data['redmine'].time_entry.get(args.id)
            if entry.user.id != app_data['user'].id:
                print("Entry was created by {}. Update skipped.".format(str(entry.user)))
                return
        except redminelib.exceptions.ResourceNotFoundError:
            print("Entry not found.")
            return

        print(helpers.entry_bullet_point(entry))

        if args.comments and entry.comments != args.comments:
            changed = True
            entry.comments = args.comments
            print('Changing comments to: ' + args.comments)

        if args.hours and (args.hours[:1] == '+' or args.hours[:1] == '-' or entry.hours != float(args.hours)):
            changed = True
            original_hours = entry.hours

            if args.hours[:1] == '+':
                entry.hours += float(args.hours[1:])
            elif args.hours[:1] == '-':
                entry.hours -= float(args.hours[1:])
            else:
                entry.hours = float(args.hours)
            print('Changing hours from ' + str(original_hours) + ' to: ' + str(entry.hours))

        if args.date:
            changed = True
            original_date = entry.spent_on
            entry.spent_on = helpers.handle_date_calculation_value(args.date)
            print('Changing activies from ' + str(original_date) + ' to ' + str(entry.spent_on))

        # share code with new_entry?
        if args.activity:
            changed = True
            original_activity = str(entry.activity)
            entry.activity_id = app_data['activities'][args.activity]
            print('Changing activity from ' + original_activity + ' to ' + args.activity)

        if changed:
            entry.save()

    else:
        print("Specify a time entry ID using the --id option.")


def delete_entry(args, config, app_data):
    app_data['redmine'].time_entry.delete(args.id)
    print('Time entry deleted.')


def list_periods(args, config, app_data):
    for abbreviation, period in helpers.PERIODS.items():
        print('* {} [{}]: {}'.format(period['name'], abbreviation, period['description']))


def flush(args, config, app_data):
    cache_filename = helpers.get_cache_filename('activities')

    if os.path.isfile(cache_filename):
        os.remove(cache_filename)

    print('Flushed.')
