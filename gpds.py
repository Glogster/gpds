from datetime import datetime
from errno import EEXIST
from os import makedirs, unlink, getcwd
from os.path import abspath, join, splitext, isfile, getsize, isdir
from sh import file
from shutil import move
import sys
from tempfile import NamedTemporaryFile
from uuid import uuid4

import gunicorn
from gunicorn.app.wsgiapp import WSGIApplication

version_info = (0, 4, 1)
__version__ = '.'.join(map(str, version_info))
__server__ = '%s/%s' % (__name__, __version__)

gunicorn.SERVER_SOFTWARE = __server__


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
        path = join(self.basepath, input[1:])
        return isfile(path)

    def _get_dir(self):
        now = datetime.utcnow()
        date = now.strftime('%Y-%m-%d')
        hour = now.strftime('%H')
        return join(self.basepath, date, hour)

    def _respond_error(self, start_response, error='404 Not Found'):
        start_response(error, [
            ('Content-Length', 0)
        ])

    def method_PUT(self, start_response):
        input = self.environ['PATH_INFO']
        ext = splitext(input)[1]

        temporary = NamedTemporaryFile('wb', suffix=ext, dir=self.basepath,
                                       delete=False)
        for chunk in iter(lambda: self.environ['wsgi.input'].read(32768), b''):
            temporary.write(chunk)
        temporary.close()

        if not getsize(temporary.name):
            unlink(temporary.name)
            return self._respond_error(start_response, error='400 Bad Request')

        filename = ''.join([str(uuid4()), ext])
        directory = self._get_dir()
        if not isdir(directory):
            try:
                makedirs(directory, 0755)
            except OSError as e:
                if not isdir(directory) or e.errno != EEXIST:
                    raise
                # Some other thread already created the directory

        output = join(directory, filename)

        response = '201 Created'
        if not isfile(output):
            move(temporary.name, output)
        else:
            unlink(temporary.name)
            response = '200 OK'

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

        working_dir = args[0]
        if not isdir(working_dir):
            try:
                makedirs(working_dir, 0755)
            except OSError:
                parser.error('Can create working directory "%s"' % working_dir)
        else:
            try:
                NamedTemporaryFile(dir=working_dir).close()
            except OSError:
                msg = 'Can\'t write any data to the working directory "%s"'
                parser.error(msg % working_dir)

        GPDS.basepath = abspath(working_dir)

        proc = "%s:main" % __name__
        self.cfg.set("default_proc_name", proc)
        self.app_uri = proc

        sys.path.insert(0, getcwd())


def run():
    GpdsApplication("%(prog)s [OPTIONS] DIRECTORY").run()
