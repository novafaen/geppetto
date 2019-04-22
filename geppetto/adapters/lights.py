import logging
import requests

class LightAdapter:

    def __init__(self, base_url):
        self._url = base_url

    def power_on(self, light):
        logging.debug('[light] trying to power on %s', light)
        response = requests.put(
            self._url + 'light/' + light + '/state/power/on',
            headers={'Accept': 'application/se.novafaen.prism.light.v1+json'}
        )

        logging.debug(response.status_code)
        logging.debug(response.text)

    def power_off(self, light):
        pass

    def set_state(self, light, brightness=None, kelvin=None):
        logging.debug('[light] trying change state on %s', light)

        body = {}
        if brightness is not None:
            body['brightness'] = brightness
        if kelvin is not None:
            body['kelvin'] = kelvin

        response = requests.put(
            self._url + 'light/' + light + '/state',
            headers={
                'Content-Type': 'application/se.novafaen.prism.lightstate.v1+json',
                'Accept': 'application/se.novafaen.prism.light.v1+json'
            },
            json=body
        )

        logging.debug(response.status_code)
        logging.debug(response.text)