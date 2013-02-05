from setuptools import setup

long_description = open('README.rst', 'rt').read()
project = long_description.split("\n")[1]
version = project.split(' ')[-1]

setup(
    name='gpds',
    version=version,
    py_modules=['gpds'],
    install_requires=[
        'gunicorn',
        'sh'
    ],
    entry_points = {
    'console_scripts': [
            'gpds = gpds:run',
        ],
    },
    url='https://github.com/rembish/gpds',
    license='BSD',
    author='Alex Rembish',
    author_email='alex@rembish.org',
    description='Simple GET-PUT-DELETE service to (temporary) store your files as an alternative to NFS shared folders.',
    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application'
    ]
)
