import argparse
import sys
import helpers


def preprocess_argv():
    # Remove script from argv
    argv = sys.argv[1:]

    if len(argv):
        command_abbreviations = {
            'l': 'list',
            'u': 'update',
            'n': 'new',
            'd': 'delete',
            'p': 'periods'
        }

        if argv[0] in command_abbreviations:
            # Expand command abbreviation
            argv[0] = command_abbreviations[argv[0]]
        elif argv[0][0:1] == '+':
            # "+<issue>" is shorthand for "new <issue>"
            argv = ['new', argv[0][1:]] + argv[1:]
        elif len(argv) == 1 and helpers.resolve_period_abbreviation(argv[0]):
            # If time period given, not command, use as basis for list command
            argv = ['list', argv[0]]
    else:
        # Default to "list" command
        argv = ['list']

    return argv


def arg_parser():
    """Return ArgumentParser for this application."""
    parser = argparse.ArgumentParser(description='Redmine client.')
    subparsers = parser.add_subparsers(dest='command')

    # Parent parser for new and update commands (with options common to both)
    entry_parser = argparse.ArgumentParser(add_help=False)
    entry_parser.add_argument('-c', '--comments', metavar='comments', action='store')
    entry_parser.add_argument('-t', '--hours', metavar='hours spent', action='store')
    entry_parser.add_argument('-a', '--activity', metavar='activity', action='store')
    entry_parser.add_argument('-d', '--date', metavar='date', action='store', help='defaults to today')

    # New entry command
    parser_new = subparsers.add_parser('new', help='Create new time entry', parents=[entry_parser])
    parser_new.add_argument('id', nargs='?', metavar='issue ID', help='ID of issue')
    parser_new.set_defaults(func='new_entry')

    # Update entry command
    parser_update = subparsers.add_parser('update', help='Update time entry', parents=[entry_parser])
    parser_update.add_argument('id', nargs='?', metavar='time entry ID', help='ID of time entry')
    parser_update.set_defaults(func='update_entry')

    # List command
    parser_list = subparsers.add_parser('list', help='List time entries')
    parser_list.add_argument('period', nargs='?', metavar='period', help='time period')
    parser_list.add_argument('-s', '--start', metavar='start date', action='store')
    parser_list.add_argument('-e', '--end', metavar='end date', action='store')
    parser_list.set_defaults(func='list_entries')

    # Delete command
    parser_delete = subparsers.add_parser('delete', help='Delete time entry')
    parser_delete.add_argument('id', nargs='?', metavar='time entry ID', help='ID of time entry')
    parser_delete.set_defaults(func='delete_entry')

    # Periods command
    parser_periods = subparsers.add_parser('periods', help='List periods')
    parser_periods.set_defaults(func='list_periods')

    # Flush command
    parser_flush = subparsers.add_parser('flush', help='Flush cache')
    parser_flush.set_defaults(func='flush')

    return parser


def validate_args(parser, args, config, activities):
    # Normalize and validate period
    if 'period' in args and args.period:
        args.period = helpers.resolve_period_abbreviation(args.period)
        if not args.period:
            parser.error('Invalid period.')

    # Normalize and validate issue/entry ID
    if 'id' in args and args.id:
        if args.command == 'new':
            default_comments = helpers.template_field(args.id, 'comments', config['issues'])
            default_hours = helpers.template_field(args.id, 'hours', config['issues'])
            default_activity = helpers.template_field(args.id, 'activity', config['issues'])

            if default_comments and not args.comments:
                args.comments = default_comments

            if default_hours and not args.hours:
                args.hours = default_hours

            if default_activity and not args.activity:
                args.activity = default_activity

        args.id = helpers.resolve_issue_alias(args.id, config['issues'])
        if not str(args.id).isdigit():
            parser.error('Invalid ID.')

    if 'activity' in args and args.activity:
        args.activity = helpers.resolve_activity_alias(args.activity, config['activities'])
        if args.activity not in activities:
            parser.error('Invalid activity.')

    return args
