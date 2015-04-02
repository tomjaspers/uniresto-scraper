from __future__ import print_function
import json
import requests
import logging
import click
import pkgutil
from importlib import import_module
from multiprocessing import Pool, cpu_count
from multiprocessing.dummy import Pool as ThreadPool

import config
from util.mplog import MultiProcessingLog


SCRAPERS_MODULE = 'uniscrapers.scrapers'

mplog = MultiProcessingLog(config.LOG_FILENAME, 'a', 0, 0)
mplog.setFormatter(logging.Formatter(config.LOG_FORMAT))
logging.getLogger().addHandler(mplog)


def find_all_scraper_names():
    """ Returns a list of all modules containing scrapers
    """
    return [name for _, name, _ in
            pkgutil.walk_packages(import_module(SCRAPERS_MODULE).__path__)]


def send_to_server(resto_name, data):
    print('im pretending to send to server')
    # r = requests.post(config.SERVER_URL,
    #                   json=data,
    #                   params={'passPhrase': config.SERVER_AUTH_TOKEN})
    # logging.info(r)


dump = send_to_server


def run_scraper((scraper_name, scraper)):
    """ Runs the Scraper to get the data and dump it somewhere (db, json, ...)
    """
    def get_data_and_dump((url, lang)):
        try:
            data = scraper.get_data(url, lang)
            dump(scraper.resto_name, data)
        except Exception as e:
            # TODO: avoid doing catch-all
            logging.error('Failed to get_data_and_dump {}, '
                          'we need to reschedule!'.format(scraper_name))
            logging.exception(e)

    scraper.log = logging
    pool = ThreadPool()
    pool.map(get_data_and_dump, scraper.remotes)


def get_scrapers(scraper_names):
    """ Return instantiated UniScrapers from their fully qualified names
        (e.g., 'vub.VubEtterbeek'), or their high-level name (e.g., 'vub')
    """
    scrapers = {}
    for name in scraper_names:
        try:
            module_name, class_identifier = name.split('.')
        except ValueError:
            module_name, class_identifier = name, 'Scraper'
        try:
            module = import_module(SCRAPERS_MODULE + '.' + module_name)
            class_names = [a for a in dir(module) if
                           class_identifier in a and a != 'UniScraper']

            for class_name in class_names:
                fqn = module_name + '.' + class_name
                scrapers[fqn] = getattr(module, class_name)()

        except ImportError:
            logging.warning("Could not find scraper {}".format(module_name))
        except AttributeError:
            logging.warning("Could not get scraper "
                            "classes for {}".format(name))

    return scrapers


def do_scraping(scraper_names):
    scrapers = get_scrapers(scraper_names)
    if scrapers:
        logging.info("Starting {} scrapers".format(len(scrapers)))

        pool = Pool(cpu_count() // 2)
        pool.map(run_scraper, scrapers.items())

        logging.info("Finished scraping")
    else:
        logging.warning("No scrapers found.")


@click.command()
@click.argument('scraper_names', nargs=-1)
@click.option('-t', '--test', is_flag=True,
              help='Test the scraper')
@click.option('-v', '--verbose', is_flag=True,
              help='Enables verbose mode.')
def main(scraper_names, test, verbose):
    logging_level = logging.INFO if verbose else logging.WARNING
    logging.basicConfig(level=logging_level)

    # TODO: find a less icky way to do this
    if test:
        global dump
        dump = lambda x, y: print(x, '\n', json.dumps(y, indent=2))

    scraper_names = scraper_names or find_all_scraper_names()

    do_scraping(scraper_names)
