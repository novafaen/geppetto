import datetime
import json
import logging

from pysolar.solar import get_altitude

from smrt import SMRTApp, app, make_response

from geppetto.adapters.lights import LightAdapter
from geppetto.adapters.switch import SwitchAdapter
from geppetto.scheduler import Scheduler


class Geppetto(SMRTApp):
    def __init__(self):
        logging.debug('Geppetto spinning up...')

        SMRTApp.__init__(self)

        self.light_adapter = LightAdapter(self.config['smrt']['light'])
        self.switch_adapter = SwitchAdapter(self.config['smrt']['switch'])

        self.listen(self.recv_broadcast)

        self.scheduler = Scheduler(self.config)
        self.scheduler.event_power_on = self.action_power_on
        self.scheduler.event_power_off = self.action_power_off
        self.scheduler.schedule_bright = self.action_bright
        self.scheduler.schedule_sunlight = self.action_sunlight

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

    def action_power_on(self, devices):
        self._power(devices, True)

    def action_power_off(self, devices):
        self._power(devices, False)

    def _power(self, devices, on_off):
        logging.debug('[geppetto] event power_on for %s', devices)
        for device in devices:
            if device in self.config['lights']:
                adapter = self.light_adapter
            elif device in self.config['switches']:
                adapter = self.switch_adapter
            else:
                logging.error('[geppetto] failed, %s is not configured')
                return  # graceful error

            if on_off:
                adapter.power_on(device)
            else:
                adapter.power_off(device)

    def action_bright(self, lights):
        logging.debug('[geppetto] event bright for bulbs: %', lights)

        # kelvin range: sun 1850-6500
        # lifx 2500-9000
        # yeelight ?-?
        for light in lights:
            self.light_adapter.set_state(light, brightness=1.0, kelvin=2500)

    def action_sunlight(self, lights):
        logging.debug('[geppetto] event sunlight for bulbs: %s', lights)

        now_utc = datetime.datetime.now(tz=datetime.timezone.utc)
        midday_utc = datetime.datetime.now(tz=datetime.timezone.utc)\
            .replace(hour=12, minute=0)
        longitude = self.config['location']['longitude']
        latitude = self.config['location']['latitude']

        sun_angle = get_altitude(longitude, latitude, now_utc)
        sun_angle_max = get_altitude(longitude, latitude, midday_utc)

        # angle
        if sun_angle < 0:
            sun_angle = 0.01  # avoid division by zero
        elif sun_angle > 180:
            sun_angle = 180

        kelvin = 2500 + int(2000 * (sun_angle / sun_angle_max))

        # brightness range, 0.5-1.0, cast to 2 decimals
        brightness = 0.5 + 0.5 * (sun_angle / sun_angle_max)
        brightness = float('{0:.2f}'.format(brightness))

        # handle if sun is not at top at noon
        if kelvin > 6500:
            kelvin = 6500
        if brightness > 1.0:
            brightness = 1.0

        logging.debug('[geppetto] sun angle %s', sun_angle)


geppetto = Geppetto()
app.register_client(geppetto)
