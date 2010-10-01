django_shell
------------

From time to time I use the `manage.py shell` command to launch simple one-time
tasks within my Django projects in the non-interactive mode. For example:

    $ echo 'from django_app.tasks import procmail; procmail()' | ./manage.py shell

It's possible to run python scripts too:

    $ echo 'execfile("/path/to/migrations/01-fix-stupid-bug.py")' | ./manage.py shell

It is fast and easy, than write real application management commands. But now I
have some restrictions:

1. Annoying syntax for a command execution.
2. I can't pass additional command line arguments because `shell` refuses them:

       $ echo 'import sys; print sys.argv' | ./manage.py shell --foo
       ...
       manage.py: error: no such option: --foo

3. The `shell` pollutes both stdin and stdout with banners from interactive
   python:

       $ echo '' | ./manage.py shell
       Python 2.5.2 (r252:60911, Jan 20 2010, 23:14:04) 
       [GCC 4.2.4 (Ubuntu 4.2.4-1ubuntu3)] on linux2
       Type "help", "copyright", "credits" or "license" for more information.
       (InteractiveConsole)

       >>> >>> 

I suppose the `manage.py shell` command line interface should be similar to
regular `python`.

Should execute python code:

    $ ./manage.py shell -c 'from django.db.models.loading import get_models; print get_models()'

Should execute python files:

    $ ./manage.py shell /path/to/migrations/01-fix-stupid-bug.py

Should execute python modules:

    $ ./manage.py shell -m smtpd -n -c DebuggingServer localhost:1025

Should execute python code from stdin:

    $ echo 'from django.db.models.loading import get_models; print get_models()' | ./manage.py shell -

Under \*nix-like environments it's possible to use `manage.py shell` as
interpreter. Just put `manage.py` into the `PATH`:

    #!manage.py shell

    from django.db.models.loading import get_models, get_apps
    print "Models", get_models()
    print "Applications", get_apps()

-- 
Will, whether the work in this area helpful for Django?

