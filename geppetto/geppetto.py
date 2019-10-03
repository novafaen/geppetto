"""Geppetto is a scheduler and event service built on SMRT framework.

The scheduler uses adapters to talk to other micro services.
"""

import datetime
import logging as loggr
import os

from pysolar.solar import get_altitude

from smrt import SMRTApp, app, smrt, make_response
from smrt import ResouceNotFound

from geppetto.adapters.lights import LightAdapter
from geppetto.adapters.switch import SwitchAdapter
from geppetto.scheduler import Scheduler

log = loggr.getLogger('smrt')


class Geppetto(SMRTApp):
    """Geppetto is a ``SMRTApp`` that is to be registered with SMRT."""

    def __init__(self):
        """Create and initiate ````Geppetto`` application."""
        log.debug('%s (%s) spinning up...', self.application_name(), self.version())

        self._schemas_path = os.path.join(os.path.dirname(__file__), 'schemas')

        SMRTApp.__init__(self, self._schemas_path, 'configuration.geppetto.schema.json')

        self.light_adapter = LightAdapter(self._config['smrt']['light'])
        self.switch_adapter = SwitchAdapter(self._config['smrt']['switch'])

        self.scheduler = Scheduler(self._config)
        self.scheduler.event_power_on = self.action_power_on
        self.scheduler.event_power_off = self.action_power_off
        self.scheduler.schedule_bright = self.action_bright
        self.scheduler.schedule_sunlight = self.action_sunlight

        self.scheduler.start()

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
            if device in self._config['lights']:
                adapter = self.light_adapter
            elif device in self._config['switches']:
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
        log.debug('event bright for lights: %s', lights)

        # kelvin range: sun 1850-6500
        # lifx 2500-9000
        # yeelight ?-?
        for light in lights:
            self.light_adapter.set_state(light, brightness=100, kelvin=2500, duration=60)

    def action_sunlight(self, lights):
        """Take action; set light source to match sun.

        :param lights: ``[String]`` light names
        """
        log.debug('event sunlight for lights: %s', lights)

        now_utc = datetime.datetime.now(tz=datetime.timezone.utc)
        midday_utc = datetime.datetime.now(tz=datetime.timezone.utc)\
            .replace(hour=12, minute=0)
        longitude = self._config['location']['longitude']
        latitude = self._config['location']['latitude']

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
            self.light_adapter.set_state(light, color=[255, 255, 255], brightness=brightness, kelvin=kelvin, duration=45)

    def action(self, name):
        """Action; run configured action.

        If action is not configured, raise ``ResouceNotFound`` error.

        :param lights: ``String`` configured action.
        """
        action = None
        for config_action in self._config['actions']:
            if name == config_action['name']:
                action = config_action
                break

        if action is None:
            raise ResouceNotFound('Action \'{}\' is not configured.'.format(name))

        if action['type'] == 'toggle':
            light_action_function = self.light_adapter.toggle_power
            switch_action_function = self.switch_adapter.toggle_power
        elif action['type'] == 'power_on':
            light_action_function = self.light_adapter.power_on
            switch_action_function = self.switch_adapter.power_on
        elif action['type'] == 'power_off':
            light_action_function = self.light_adapter.power_off
            switch_action_function = self.switch_adapter.power_off

        for light in action['lights']:
            light_action_function(light)
        for switch in action['switches']:
            switch_action_function(switch)


geppetto = Geppetto()
app.register_application(geppetto)


@smrt('/action/<string:name>',
      methods=['POST'])
def action(name):
    """Endpoint to perform an action.

    :returns: ``202 Accepted``
    """
    geppetto.action(name)

    return make_response('', 202)
