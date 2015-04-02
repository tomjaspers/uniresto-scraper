from setuptools import setup

setup(
    name='uniresto-scraper',
    version='0.1.0',
    description='music tagger and library organizer',
    author='Tom Jaspers',
    author_email='contact@tomjaspers.be',
    url='https://github.com/tomjaspers/uniresto-scraper',
    license='GPLv3',
    platforms='ALL',
    # long_description=_read('README.rst'),

    packages=[
        'uniscrapers',
        ],

    entry_points={
        'console_scripts': [
            'uniresto-scraper = uniscrapers:cli',
            ],
        },

    install_requires=[
        'requests',
        'lxml',
        'cssselect'
        ],
    )
