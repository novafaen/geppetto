import logging

from smrt import SMRT as app


class Geppetto():
    def __init__(self):
        logging.debug('Geppetto spinning up...')

    def version(self):
        logging.debug('troll')
        return {
            'app_version': '0.0.1'
        }


geppetto = Geppetto()

app.register_client(geppetto)
