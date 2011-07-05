import PyV8 as v8
import time
import sys
import os
import codecs
import urllib
import optparse

COMPILER_URL = 'https://github.com/jashkenas/coffee-script/raw/master/extras/coffee-script.js'
POLL_INTERVAL = 2

# keep track of when files were last compiled
compiled = {}

def start_watching():
    print "Checking %s and subdirectories every %d seconds" % (opts.watch.folder,
                                                               opts.interval)
    while True:
        try:
            _check_folder(opts.watch.folder)
            time.sleep(opts.interval)
        except KeyboardInterrupt:
            # allow graceful exit (no stacktrace output)
            sys.exit(0)
        
def _check_folder(watch_path):
    for dirpath, dirnames, filenames in os.walk(watch_path):
        filepaths = (os.path.join(dirpath, filename) 
                     for filename in filenames if filename.endswith('.coffee'))
        for filepath in filepaths:
            mtime = os.stat(filepath).st_mtime
            compiled_path = _compiled_path(filepath)
            if (not filepath in compiled or compiled[filepath] < mtime or
                not os.path.isfile(compiled_path)):
                _compile_file(filepath, compiled_path)
                compiled[filepath] = mtime

def _compiled_path(filepath):
    if opts.output:
        # make a compiled path that is output_path + source file path relative
        # to watch folder
        output_path = opts.output.folder
        filename = os.path.split(filepath)[1]
        compiled_filename = filename[:filename.rfind('.')] + '.js'
        rel_path = os.path.relpath(os.path.split(filepath)[0], opts.watch.folder)
        return os.path.join(output_path, rel_path, compiled_filename)
    else:
        return filepath[:filepath.rfind('.')] + '.js'

def _compile_file(path, compiled_path):
    # if using --output the destination folder may not yet exist
    compiled_folder = os.path.split(compiled_path)[0]
    if not os.path.exists(compiled_folder):
        os.makedirs(compiled_folder)
    try:
        codecs.open(compiled_path, 'w', encoding='utf-8')\
              .write(_convert(codecs.open(path, 'r', encoding='utf-8').read()))
        print "compiled %s" % (os.path.relpath(path, opts.watch.folder),)
    except Exception, e:
        msg = "Error parsing %s: %s" % (os.path.relpath(path, opts.watch.folder),
                                                       str(e))
        print msg
        codecs.open(compiled_path, 'w', encoding='utf-8').write(str(e))
               
def _convert(coffee):
    return compiler.compile(coffee, {'bare': opts.bare})

class Path(object):
    """Object represeting a path.

    Contains the full path, the folder path and the name of the file if relevant.

    Attributes:
        path -- the full path.
        folder -- the folder path (not including filename).
        file -- the filename (or undefined).

    """
    def __init__(self, path):
        self.path = os.path.realpath(path)
        head, tail = os.path.split(path)
        if head:
            self.folder = os.path.realpath(head)
            self.file = tail
        else:
        # if the path is a single word, it could be a file or a folder
            if os.path.isdir(tail):
                self.folder = os.path.realpath(tail)
            else:
                self.folder = os.path.realpath(os.getcwd())
                self.file = tail

def _check_folder_exists(folder_path):
    if not os.path.isdir(folder_path):
        parser.error("%s is not a valid path to an existing folder." % (folder_path,))

def _store_path(option, opt_str, value, parser):
    path = Path(value)

    _check_folder_exists(path.folder)

    setattr(parser.values, option.dest, path)

def _process_args(args):
    if len(args) > 1:
        op.error('please specify a single folder to be watched')
    elif len(args) == 0:
        op.error('please specify a folder to be watched')
    else:
        path = Path(args[0])
        _check_folder_exists(path.folder)
        setattr(opts, 'watch', path)

if __name__ == '__main__':
    op = optparse.OptionParser(usage='Usage: %prog [options] <watch_directory>')
    op.add_option('-b', '--bare', action='store_true', default=False, 
        dest='bare', help='compile without the top-level function wrapper')
    op.add_option('-o', '--output', action='callback', callback=_store_path,
        dest='output', help='set the output directory for the compiled JavaScript',
        metavar='DIR', type='str')
    op.add_option('-i', '--interval', action='store', dest='interval',
        type='int', default=POLL_INTERVAL, metavar='SECONDS',
        help='set the poll interval in seconds (default: 2)')

    opts, args = op.parse_args()

    _process_args(args)

    # create compiler with latest browser js coffeescript compiler from github
    ct = v8.JSContext()
    ct.enter()
    compiler = ct.eval(urllib.urlopen(COMPILER_URL).read())

    start_watching()