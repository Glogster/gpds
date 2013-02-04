import sys

from os.path import abspath, join, splitext, isfile, getsize, isdir
from os import makedirs, unlink, getcwd

from string import hexdigits
from hashlib import sha1

from gunicorn.app.wsgiapp import WSGIApplication

from sh import file

class GPDS(object):
    basepath = '.'

    def __init__(self, environ):
        self.environ = environ

    def process(self, start_response):
        http_method = self.environ['REQUEST_METHOD']
        method = 'method_%s' % http_method

        if hasattr(self, method):
            return getattr(self, method)(start_response)

    def _check_path(self, input):
        parts = input.split('/')
        hash, ext = splitext(parts[-1])
        output = join(self.basepath, input[1:])

        return len(parts) == 4 and hash.startswith(''.join(parts[1:2])) and \
           all(c in hexdigits for c in hash) and len(hash) == 40 and isfile(output)

    def _respond_error(self, start_response, error='404 Not Found'):
        start_response(error, [
            ('Content-Length', 0)
        ])

    def method_PUT(self, start_response):
        input = self.environ['PATH_INFO']
        buffer = self.environ['wsgi.input'].read()
        hash = sha1(buffer).hexdigest()

        if not buffer:
            return self._respond_error(start_response, error='400 Bad Request')

        filename = ''.join([hash, splitext(input)[1]])
        directory = join(self.basepath, hash[0:2], hash[2:4])
        if not isdir(directory):
            makedirs(directory, 0755)
        output = join(directory, filename)

        response = '201 Created'
        if not isfile(output):
            id = open(output, 'wb')
            id.write(buffer)
            id.close()
        else:
            response = '200 OK'

        del buffer

        start_response(response, [
            ('Location', output.replace(self.basepath, '')),
            ('Content-Length', 0)
        ])

    def method_GET(self, start_response):
        input = self.environ['PATH_INFO']
        output = join(self.basepath, input[1:])

        if not self._check_path(input):
            return self._respond_error(start_response)

        mime = file("-b", "--mime-type", output)
        start_response('200 OK', [
            ('Content-Length', getsize(output)),
            ('Content-Type', mime)
        ])

        return open(output, 'rb')

    def method_DELETE(self, start_response):
        input = self.environ['PATH_INFO']
        output = join(self.basepath, input[1:])

        response = '404 Not Found'
        if self._check_path(input):
            unlink(output)
            response = '204 No Content'

        start_response(response, [
            ('Content-Length', 0)
        ])

def main(environ, start_response):
    return GPDS(environ).process(start_response) or iter([''])

class GpdsApplication(WSGIApplication):
    def init(self, parser, opts, args):
        if len(args) != 1:
            parser.error("No working directory specified.")

        if not isdir(args[0]):
            makedirs(args[0], 0755)

        GPDS.basepath = abspath(args[0])

        proc = "gpds:main"
        self.cfg.set("default_proc_name", proc)
        self.app_uri = proc

        sys.path.insert(0, getcwd())

def run():
    GpdsApplication("%(prog)s [OPTIONS] DIRECTORY").run()
