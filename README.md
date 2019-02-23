# redmein
CLI client for Redmine

Example list of today's time entries:

    $ redmein

Examples of listing yesterday's time entries:

    $ redmein y
    $ redmein l y
    $ redmein l -s -1 -e -1

Example addition of a time entry:

    redmein new 20 --comments="Email." --hours=.25

Example update of a time entry, increasing hours by .25:

    redmein u 91807 --hours=+.25


Commands
--------

Remein allows you to list, create, update and delete Redmine time entries.


### Creating a time entry

When creating a time entry the `--id` option is used to specify the issue ID.

Here's an example of creating a time entry:

    $ redmein new 100 --comments="Checking email." --hours=.25 --activity=Administration

Here's the same example in a briefer form.

    $ redmein new 100 -c "Checking email." -t .25 -a Administration


### Updating a time entry

When updating a time entry the `--id` option is used to specify the time entry
ID.

Here's a example of updating a time entry, changing the time spent to half an hour:

    $ redmein update 92312 -t .5

If you'd like to decrement or increment, rather than set, hours spent you can
precede the value for the `--hours` option with `-` or `+`.

For example:

    $ redmein update 92312 -t +.25


### Deleting a time entry

When deleting a time entry the `--id` option is used to delete the time entry.

Here's an example of deleting a time entry:

    $ redmain delete 92312


### Listing available time periods

To list available time periods use the "periods" command:

    $ remein periods

Configuration
-------------

Redmein's configuration file is YAML-formatted and should be created in
`$HOME/.redmein.yml`.

Access to Redmine's API is configured via the `url`, `username`, and `password`
parameters:

    url: https://projects.example.com
    username: bob_dobbs
    password: supersekret


### Activity aiases and default

When specifying an activity you can either use the full name of the activity or
you can refer to an alias specifed in your configuration file. You can also
create aliases for aliases.

Example:

    activities:
      admin: Administration
      dev: Development
      a: admin
      d: dev

When creating a time entry a default activity, if specified in your
configuration, will be used if no activity has been specified.

    default activity: dev


### Issue aliases

When specifying an issue you can either use ID of the issue or you can refer to
an alias specifed in your configuration file. You can also create aliases for
aliases.

Example:

    issues:
      meet:
        id: 100
      meeting:
        id: meet


### Issue templates

In addition to using an alias to specify an ID, you can use the alias to, when
creating a time entry, automatically set the comments, hours spent, and/or
activity for the new time entry.

Example:

    issues:
      meet:
        id: 100
      meeting:
        id: meet
      scrum:
        id: meet
        comments: "Daily scrum."
        hours: .25
        activity: admin

These values can be overridden by command-line options so if, building on the
previous example, you had a scrum meeting that lasted a half hour, instead of
15 minutes, you could add a time entry using the "scrum" alias and just
overrride the --time command-line option.

Example:

    $ redmein n scrum -t .5


Shortcuts and abbreviations
---------------------------

Example of quick addition of a time entry using a template:

    $ redmein +scrum
