CoffeePy
========

Want to compile CoffeeScript on Windows or without running Node.js? Now it's easy. 

Uses the excellent PyV8 module to execute CoffeeScript's js compiler inside python.

Usage:
------

<pre>
Usage: coffee_watch.py [options] watch_directory

Options:
  -h, --help            show this help message and exit
  -b, --bare            compile without the top-level function wrapper
  -o DIR, --output=DIR  set the output directory for the compiled JavaScript
  -i SECONDS, --interval=SECONDS
                        set the poll interval in seconds (default: 2)
</pre>