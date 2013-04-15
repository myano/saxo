# Copyright 2013, Sean B. Palmer
# Source: http://inamidst.com/saxo/

path = None

if "__file__" in vars():
    if __file__:
        import os.path

        path = os.path.abspath(__file__)
        path = os.path.realpath(path)
        path = os.path.dirname(path)

        del os

if "__path__" in vars():
    if __path__:
        for directory in __path__:
            if path is None:
                path = directory
            elif path != directory:
                raise Exception("Can't create saxo.path")

        del directory

def command(function):
    # __name__ is "saxo"
    import resource
    import sys

    # Save PEP 3122!
    if "." in __name__:
        from . import generic
    else:
        import generic

    generic.exit_cleanly()
    resource.setrlimit(resource.RLIMIT_CPU, (6, 6))

    for line in sys.stdin:
        try: result = function(line.rstrip("\n"))
        except Exception as err:
            result = err.__class__.__name__ + ": " + str(err)
        break
    sys.stdout.write(result + "\n")

def event(command):
    def decorate(function):
        function.saxo_event = command
        return function
    return decorate

def script(argv):
    # Save PEP 3122!
    if "." in __name__:
        from .script import main
    else:
        from script import main
    main(argv)
