"""The makemsmessages command."""

from django.core.management.commands import makemessages


class Command(makemessages.Command):
    """Implement the makemsmessages command, which supports the `getText` keyword."""

    xgettext_options = makemessages.Command.xgettext_options + ["--keyword=getText"]
