"""Adapter to abstract REST to functions for lights."""

import logging
import requests

log = logging.getLogger('geppetto')


class LightAdapter:
    """Light adapter class."""

    def __init__(self, base_url):
        """Create and initiate LightAdapter."""
        self._url = base_url

    def power_on(self, light):
        """Turn on light based on name.

        :param light: ``String`` name
        """
        self._power(light, True)

    def power_off(self, light):
        """Turn off light based on name.

        :param light: ``String`` name
        """
        self._power(light, True)

    def _power(self, light, on_off):
        response = requests.put(
            self._url + 'light/' + light + '/state/power/' + 'on' if on_off else 'off',
            headers={'Accept': 'application/se.novafaen.prism.light.v1+json'}
        )

        log.debug('set light state successful=%s', response.status_code == 200)

    def set_state(self, light, brightness=None, kelvin=None, duration=None):
        """Set state for light.

        :param light: ``String`` name
        :param brightness: ``Integer``, default not included
        :param kelvin: ``Integer``, default not included
        :param duration: ``Integer``, default not included
        """
        log.debug('[light] trying change state on %s', light)

        body = {}
        if brightness is not None:
            body['brightness'] = brightness
        if kelvin is not None:
            body['kelvin'] = kelvin
        if duration is not None:
            body['duration'] = duration

        response = requests.put(
            self._url + 'light/' + light + '/state',
            headers={
                'Content-Type': 'application/se.novafaen.prism.lightstate.v1+json',
                'Accept': 'application/se.novafaen.prism.light.v1+json'
            },
            json=body
        )

        log.debug('set light state successful=%s', response.status_code == 200)
