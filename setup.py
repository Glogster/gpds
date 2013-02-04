from distutils.core import setup

setup(
    name='gpds',
    version='0.2',
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
    description='Simple GET-PUT-DELETE service to (temporary) store your files as an alternative to NFS shared folders.'
)
