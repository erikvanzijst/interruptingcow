Interrupting Cow
================

Interruptingcow is a generic utility can relatively gracefully interrupt your
Python code when it doesn't execute within a specific number of seconds::

    from interruptingcow import timeout

    try:
        with timeout(5, exception=RuntimeError):
            # perform a potentially very slow operation
            pass
    except RuntimeError:
        print "didn't finish within 5 seconds"

Timeouts are specified in seconds (as floats with theoretical microsecond
precision).


Installation
------------
::

    $ pip install interruptingcow


Reentrant
---------

Interruptingcow is fully reentrant, which means that you can have nested
timeouts::

    from interruptingcow import timeout

    class Outer(RuntimeError): pass

    class Inner(RuntimeError): pass

    try:
        with timeout(20.0, Outer):
            try:
                with timeout(1.0, Inner):
                    # some expensive operation
                    try_the_expensive_thing()
            except Inner:
                do_the_cheap_thing_instead()

    except Outer:
        print 'Program as a whole failed to return in 20 secs'

Nested timeouts allow a large outer timeout to contain smaller timeouts. If the
inner timeout is larger than the outer timeout, it is treated as a no-op.


Function Decorators
-------------------

Interruptingcow can be used both as inline with-statements, as shown in the
above examples, as well as function decorator::

    from interruptingcow import timeout

    @timeout(.5)
    def foo():
        with timeout(.3):
            # some expensive operation
            pass


Caveats
-------

Interruptingcow uses ``signal(SIGALRM)`` to let the operating system interrupt
program execution. This has the following limitations:

1. Python signal handlers only apply to the main thread, so you cannot use this
   from other threads
2. You must not use this in a program that uses ``SIGALRM`` itself (this
   includes certain profilers)
