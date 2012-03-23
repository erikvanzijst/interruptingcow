Interrupting Cow
================

MOOOOO!


Overview
--------

Interruptingcow is a generic utility can relatively gracefully interrupt your
Python code when it doesn't execute within a specific number of seconds:

    :::python
    from interruptingcow import interruptingcow, InterruptedException

    try:
        with interruptingcow(timeout=5):
            # perform a potentially very slow operation
            pass
    except InterruptedException:
        print "didn't finish within 5 seconds"


Installation
------------

  $ pip install interruptingcow

Caveats
-------

Interruptingcow uses ``signal(SIGALRM)`` to let the operating system interrupt
program execution. This has the following limitations:

* ``SIGALRM`` is not reentrant so you can not nest timeouts
* Python signal handlers only apply to the main thread, so you cannot use this
  from other threads
* You must not use this in a program that uses ``SIGALRM`` itself
