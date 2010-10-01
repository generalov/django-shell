import os
import sys
from django.core.management.base import BaseCommand
from optparse import make_option


def parse_command(option, opt_str, value, parser):
    value = parser.rargs[0]
    parser.largs.extend(parser.rargs[:])
    del parser.rargs[:]
    setattr(parser.values, option.dest, value)

class Command(BaseCommand):
    args = '[-c cmd | -m mod | file | -] [arg]'
    option_list = BaseCommand.option_list + (
        make_option('--plain', action='store_true', dest='plain',
            help='Tells Django to use plain Python, not IPython.'),
        make_option('-c', dest='command', action='callback', callback=parse_command,
            help='''Program passed in as string (terminates option list)'''),
        make_option('-m', dest='module', action='callback', callback=parse_command,
            help='''Run library module as a script (terminates option list)'''),
    )
    help = "Runs a Python interactive interpreter. Tries to  use IPython, if it's available."

    requires_model_validation = False

    def handle(self, *args, **options):
        # XXX: (Temporary) workaround for ticket #1796: force early loading of all
        # models from installed apps.
        from django.db.models.loading import get_models
        loaded_models = get_models()

        if options.get('command', False):
            self.handle_command(args)
        elif options.get('module', False):
            self.hande_module(args)
        elif args and args[0] == '-':
            self.handle_stdin(args)
        elif args:
            self.handle_file(args)
        else:
            self.handle_interactive(**options)

    def handle_interactive(self, **options):
        use_plain = options.get('plain', False)

        try:
            if use_plain:
                # Don't bother loading IPython, because the user wants plain Python.
                raise ImportError
            import IPython
            # Explicitly pass an empty list as arguments, because otherwise IPython
            # would use sys.argv from this script.
            shell = IPython.Shell.IPShell(argv=[])
            shell.mainloop()
        except ImportError:
            import code
            # Set up a dictionary to serve as the environment for the shell, so
            # that tab completion works on objects that are imported at runtime.
            # See ticket 5082.
            imported_objects = {}
            try: # Try activating rlcompleter, because it's handy.
                import readline
            except ImportError:
                pass
            else:
                # We don't have to wrap the following import in a 'try', because
                # we already know 'readline' was imported successfully.
                import rlcompleter
                readline.set_completer(rlcompleter.Completer(imported_objects).complete)
                readline.parse_and_bind("tab:complete")

            # We want to honor both $PYTHONSTARTUP and .pythonrc.py, so follow system
            # conventions and get $PYTHONSTARTUP first then import user.
            if not use_plain: 
                pythonrc = os.environ.get("PYTHONSTARTUP") 
                if pythonrc and os.path.isfile(pythonrc): 
                    try: 
                        execfile(pythonrc) 
                    except NameError: 
                        pass
                # This will import .pythonrc.py as a side-effect
                import user
            code.interact(local=imported_objects)

    def hande_module(self, argv):
        from runpy import run_module
        self.non_interactive_prepare(argv)
        run_module(sys.argv[0], run_name="__main__", alter_sys=True)
        self.non_interactive_done()

    def handle_file(self, argv):
        self.non_interactive_prepare(argv)
        execfile(argv[0], dict(__file__=argv[0], __name__='__main__'))
        self.non_interactive_done()

    def handle_command(self, argv):
        command = argv[0]
        argv = ('-c', ) + argv[1:]
        self.non_interactive_prepare(argv)
        exec(command, dict(__name__='__main__'))
        self.non_interactive_done()

    def handle_stdin(self, argv):
        self.handle_command((sys.stdin.read(), ) + argv[1:])

    def non_interactive_prepare(self, argv):
        # patch sys.argv with new argv
        # altering `sys` is not thread safe
        self._old_argv = sys.argv[:]
        del sys.argv[:]
        sys.argv.extend(argv)

    def non_interactive_done(self):
        del sys.argv[:]
        sys.argv.extend(self._old_argv)
        del self._old_argv

    def create_parser(self, prog_name, subcommand):
        parser = super(Command, self).create_parser(prog_name, subcommand)
        parser.disable_interspersed_args()
        return parser

