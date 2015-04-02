DATE_FORMAT = '%m/%d/%Y'


class UniScraper(object):

    def __init__(self):
        self.resto_name = None
        self.remotes = []
        self.maintainer = None
        self.log = None

    def get_data(self, url, lang):
        raise NotImplementedError('')
