"""Geppetto is a scheduler and event service built on SMRT framework.

The scheduler uses adapters to talk to other micro services.
"""

import datetime
import logging

from pysolar.solar import get_altitude

from smrt import SMRTApp, app

from geppetto.adapters.lights import LightAdapter
from geppetto.adapters.switch import SwitchAdapter
from geppetto.scheduler import Scheduler

log = logging.getLogger('geppetto')


class Geppetto(SMRTApp):
    """Geppetto is a ``SMRTApp`` that is to be registered with SMRT."""

    def __init__(self):
        """Create and initiate ````Geppetto`` application."""
        log.debug('%s (%s) spinning up...', self.application_name(), self.version())

        SMRTApp.__init__(self)

        self.light_adapter = LightAdapter(self.config['smrt']['light'])
        self.switch_adapter = SwitchAdapter(self.config['smrt']['switch'])

        self.scheduler = Scheduler(self.config)
        self.scheduler.event_power_on = self.action_power_on
        self.scheduler.event_power_off = self.action_power_off
        self.scheduler.schedule_bright = self.action_bright
        self.scheduler.schedule_sunlight = self.action_sunlight

        self.scheduler.run()

        log.debug('%s initiated!', self.application_name())

    def status(self):
        """See ``SMRTApp`` documentation."""
        return {
            'name': self.application_name(),
            'status': 'OK',
            'version': self.version()
        }

    @staticmethod
    def version():
        """See ``SMRTApp`` documentation."""
        return '0.0.1'

    @staticmethod
    def application_name():
        """See ``SMRTApp`` documentation."""
        return 'Geppetto'

    def action_power_on(self, devices):
        """Take action, power on devices identified by name.

        :param devices: ``[String]`` device names
        """
        self._power(devices, True)

    def action_power_off(self, devices):
        """Take action; power off devices identified by name.

        :param devices: ``[String]`` device names
        """
        self._power(devices, False)

    def _power(self, devices, on_off):
        """Action, internal function to toggle power."""
        log.debug('event power_on for %s', devices)
        for device in devices:
            if device in self.config['lights']:
                adapter = self.light_adapter
            elif device in self.config['switches']:
                adapter = self.switch_adapter
            else:
                log.error('failed, %s is not configured')
                return  # graceful error

            if on_off:
                adapter.power_on(device)
            else:
                adapter.power_off(device)

    def action_bright(self, lights):
        """Take action; set light sources to bright.

        :param lights: ``[String]`` light names
        """
        log.debug('event bright for lights: %', lights)

        # kelvin range: sun 1850-6500
        # lifx 2500-9000
        # yeelight ?-?
        for light in lights:
            self.light_adapter.set_state(light, brightness=1.0, kelvin=2500, duration=60)

    def action_sunlight(self, lights):
        """Take action; set light source to match sun.

        :param lights: ``[String]`` light names
        """
        log.debug('event sunlight for lights: %s', lights)

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

        # brightness range, 50-100, cast to 2 decimals
        brightness = int(50 + 50 * (sun_angle / sun_angle_max))

        log.debug('max=%s, current=%s, brightness=%s', sun_angle_max, sun_angle, brightness)

        # handle if sun is not at top at noon
        if kelvin > 6500:
            kelvin = 6500
        if brightness > 100:
            brightness = 100

        for light in lights:
            self.light_adapter.set_state(light, brightness=brightness, kelvin=kelvin, duration=45)


geppetto = Geppetto()
app.register_application(geppetto)
