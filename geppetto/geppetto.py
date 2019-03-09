import json
import logging

from smrt import SMRTApp, app, make_response

from geppetto.scheduler import Scheduler


class Geppetto(SMRTApp):
    def __init__(self):
        logging.debug('Geppetto spinning up...')

        SMRTApp.__init__(self)

        self.listen(self.recv_broadcast)

        self.scheduler = Scheduler(self.config)
        self.scheduler.run()

        logging.debug('Geppetto initiated!')

    def status(self):
        return {
            'name': 'Geppetto',
            'status': 'OK',
            'version': '0.0.1'
        }

    @staticmethod
    def client_name():
        return 'Geppetto'

    def recv_broadcast(self, data):
        data = json.loads(data)


geppetto = Geppetto()

app.register_client(geppetto)
