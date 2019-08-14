"""Adapter to abstract REST to functions for switches."""

import logging

from smrt.make_request import put

log = logging.getLogger('geppetto')


class SwitchAdapter:
    """Switch adapter class."""

    def __init__(self, base_url):
        """Create and initiate SwitchAdapter."""
        self._url = base_url

    def toggle_power(self, name):
        """Toggle power based on name.

        :param light: ``String`` name
        """
        response = put(
            self._url + 'device/' + name + '/power/toggle',
            headers={'Accept': 'application/se.novafaen.stick.device.v1+json'}
        )

        log.debug('set state, device=%s, power=toggle, successful=%s', name, response.status_code == 200)

    def power_on(self, name):
        """Turn on switch based on name.

        :param name: ``String`` name
        """
        self._power(name, True)

    def power_off(self, name):
        """Turn off switch based on name.

        :param name: ``String`` name
        """
        self._power(name, False)

    def _power(self, name, on_off):
        power = 'off'
        if on_off:
            power = 'on'

        response = put(
            self._url + 'device/%s/power/%s' % (name, power),
            headers={'Accept': 'application/se.novafaen.stick.device.v1+json'}
        )

        log.debug('set state, device=%s, power=%s, successful=%s', name, on_off, response.status_code == 200)
