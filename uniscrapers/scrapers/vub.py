import requests
import datetime
import lxml.html
from lxml.cssselect import CSSSelector

from . import UniScraper, DATE_FORMAT


# Months in Dutch, to allow the parsing of the (Dutch) site
MONTHS = ['januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli',
          'augustus', 'september', 'oktober', 'november', 'december']
LOCAL_MONTHS = {month: i for i, month in enumerate(MONTHS, 1)}


def clean_string(string):
    return string.replace(u'\xa0', u' ').strip()


def get_data(self, url, lang):
    data = []

    # Construct CSS Selectors
    sel_day_divs = CSSSelector('#content .views-row')
    sel_date_span = CSSSelector('.date-display-single')
    sel_tablerows = CSSSelector('table tr')
    sel_img = CSSSelector('img')

    # Request and build the DOM Tree
    r = requests.get(url)
    tree = lxml.html.fromstring(r.text)

    # Apply selector to get divs representing 1 day
    for day_div in sel_day_divs(tree):
        menus = []
        # Apply selector to get date span (contains date string of day)
        date_span = sel_date_span(day_div)
        if not date_span:
            continue  # No date = skip the day
        # date string should be format '29 september 2014', normally
        date_string = clean_string(
                        date_span[0].text_content()).lower()
        day, month_name, year = date_string.split()[1:]
        month = LOCAL_MONTHS.get(month_name.lower(), None)
        if month:
            date = datetime.date(int(year), month, int(day))
        else:
            # If we couldn't find a month, we try to use the previous date
            self.log.warning("Failed to get a month for "
                             "the month_name {}".format(month_name))
            try:
                year, month, day = map(int, data[-1]['date'].split('-'))
                prev_date = datetime.date(year, month, day)
                date = prev_date + datetime.timedelta(days=1)
            except Exception:
                # If we can't find any date, we'll skip the day
                self.log.warning("Couldn't derive date "
                                 "from previous dates")
                continue

        # Get the table rows
        for tr in sel_tablerows(day_div):
            tds = tr.getchildren()
            category = clean_string(tds[0].text_content())
            menu = clean_string(tds[1].text_content())
            # Sometimes there is no category,
            # but just an image (e.g., for "Veggiedag")
            if not category:
                img = sel_img(tds[0])
                if img and 'veggiedag' in img.get('src', ''):
                    category = 'Veggiedag'
                else:
                    category = 'Menu'
            if menu:
                menus.append({'name': menu,
                              'category': category,
                              'language': lang})
        data.append({'date': date.strftime(DATE_FORMAT), 'dishes': menus})
    return data


class VubEtterbeekScraper(UniScraper):

    def __init__(self):
        super(VubEtterbeekScraper, self).__init__()

        self.resto_name = 'VUB Etterbeek'
        self.remotes = [('https://my.vub.ac.be/resto/etterbeek', 'nl-BE'),
                        ('https://my.vub.ac.be/restaurant/etterbeek', 'en-US')]

    def get_data(self, url, lang):
        return get_data(self, url, lang)


class VubJetteScraper(UniScraper):

    def __init__(self):
        super(VubJetteScraper, self).__init__()

        self.resto_name = 'VUB Jette'
        self.remotes = [('https://my.vub.ac.be/resto/jette', 'nl-BE'),
                        ('https://my.vub.ac.be/restaurant/jette', 'en-US')]

    def get_data(self, url, lang):
        return get_data(self, url, lang)
