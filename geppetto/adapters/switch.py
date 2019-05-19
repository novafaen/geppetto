"""Adapter to abstract REST to functions for switches."""

import logging

from smrt.make_request import put

log = logging.getLogger('geppetto')


class SwitchAdapter:
    """Switch adapter class."""

    def __init__(self, base_url):
        """Create and initiate SwitchAdapter."""
        self._url = base_url

    def power_on(self, name):
        """Turn on switch based on name.

        :param name: ``String`` name
        """
        self._power(name, True)

    def power_off(self, device):
        """Turn off switch based on name.

        :param name: ``String`` name
        """
        self._power(device, False)

    def _power(self, device, on_off):
        logging.debug('[switch] calling %s, power=%s', device, on_off)

        power = 'off'
        if on_off:
            power = 'on'

        response = put(
            self._url + 'device/%s/power/%s' % (device, power),
            headers={'Accept': 'application/se.novafaen.stick.device.v1+json'}
        )

        log.debug('set device state successful=%s', response.status_code == 200)
