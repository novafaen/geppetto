"""Adapter to abstract REST to functions for lights."""

import logging as loggr
from uuid import uuid4

from smrt.make_request import put

log = loggr.getLogger('smrt')


class LightAdapter:
    """Light adapter class."""

    def __init__(self, base_url):
        """Create and initiate LightAdapter."""
        self._url = base_url

    def toggle_power(self, name):
        """Toggle power based on name.

        :param name: ``String`` name
        """
        response = put(
            self._url + 'light/' + name + '/state/power/toggle',
            headers={'Accept': 'application/se.novafaen.prism.light.v1+json'}
        )

        log.debug('set state, light=%s, power=toggle, successful=%s', name, response.status_code == 200)

    def power_on(self, name):
        """Turn on light based on name.

        :param name: ``String`` name
        """
        self._power(name, True)

    def power_off(self, name):
        """Turn off light based on name.

        :param name: ``String`` name
        """
        self._power(name, False)

    def _power(self, name, on_off):
        response = put(
            self._url + 'light/' + name + '/state/power/' + ('on' if on_off else 'off'),
            headers={'Accept': 'application/se.novafaen.prism.light.v1+json'}
        )

        log.debug('set state, light=%s, power=%s, successful=%s', name, on_off, response.status_code == 200)

    def set_state(self, name, color=None, brightness=None, kelvin=None, duration=None):
        """Set state for light.

        :param name: ``String`` name
        :param brightness: ``Integer``, default not included
        :param kelvin: ``Integer``, default not included
        :param duration: ``Integer``, default not included
        """
        body = {}
        if brightness is not None:
            body['brightness'] = brightness
        if kelvin is not None:
            body['kelvin'] = kelvin
        if duration is not None:
            body['duration'] = duration
        if color is not None:
            body['color'] = color

        try:
            response = put(
                self._url + 'light/' + name + '/state',
                headers={
                    'Content-Type': 'application/se.novafaen.prism.lightstate.v1+json',
                    'Accept': 'application/se.novafaen.prism.light.v1+json'
                },
                body=body
            )
        except Exception as err:
            log.warning('failed to set state for %s: %s', name, err)
            return

        log.debug('set state, light=%s, state=%s, successful=%s', name, body, response.status_code == 200)
