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

def watch_folder(watch_path, interval = POLL_INTERVAL):
    watch_path = os.path.realpath(watch_path)
    if opts.output_path:
        output_path = os.path.realpath(opts.output_path)

    print "Checking %s and subdirectories every %d seconds" % (watch_path,
                                                               interval)
    while True:
        try:
            _check_folder(watch_path)
            time.sleep(interval)
        except KeyboardInterrupt:
            # allow graceful exit (no stacktrace output)
            sys.exit(0)
        
def _check_folder(watch_path):

    for dirpath, dirnames, filenames in os.walk(watch_path):
        filepaths = (os.path.join(dirpath, filename) 
                     for filename in filenames if filename.endswith('.coffee')
                     )
        for filepath in filepaths:
            mtime = os.stat(filepath).st_mtime
            compiled_path = _compiled_path(filepath)
            if (not filepath in compiled or compiled[filepath] < mtime or
                not os.path.isfile(compiled_path)):
                _compile_file(filepath, compiled_path)
                compiled[filepath] = mtime

def _compiled_path(filepath):
    if opts.output_path:
        # make a compiled path that is output_path + source file path relative
        # to watch folder
        output_path = os.path.realpath(opts.output_path)
        filename = os.path.split(filepath)[1]
        compiled_filename = filename[:filename.rfind('.')] + '.js'
        rel_path = os.path.relpath(os.path.split(filepath)[0], watch_path)
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
        print "compiled %s" % (os.path.split(path)[1],)
    except Exception, e:
        msg = "Error parsing CoffeScript in %s: %s" % (path, str(e))
        print msg
        codecs.open(compiled_path, 'w', encoding='utf-8').write(str(e))
               
def _convert(coffee):
    return compiler.compile(coffee, {'bare': opts.bare})

if __name__ == '__main__':
    op = optparse.OptionParser(usage='Usage: %prog [options] <watch_directory>')
    op.add_option('-b', '--bare', action='store_true', default=False, 
        dest='bare', help='compile without the top-level function wrapper')
    op.add_option('-o', '--output', action='store', dest='output_path', metavar='DIR',
        help='set the output directory for the compiled JavaScript')

    (opts, args) = op.parse_args()

    if len(args) >= 1:
        watch_path = args[0]
    else: op.error('please specify a folder to be watched')

    if not os.path.isdir(watch_path):
        op.error("%s is not a valid path to a folder" % (watch_path,))
    
    if opts.output_path:
        if not os.path.isdir(opts.output_path):
            op.error("%s is not a valid path to a folder" % (opts.output_path,))

    # create compiler with latest browser js coffeescript compiler from github
    ct = v8.JSContext()
    ct.enter()
    compiler = ct.eval(urllib.urlopen(COMPILER_URL).read())

    watch_folder(watch_path)