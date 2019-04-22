import logging
import requests


class SwitchAdapter:

    def __init__(self, base_url):
        self._url = base_url

    def power_on(self, device):
        self._power(device, True)

    def power_off(self, device):
        self._power(device, False)

    def _power(self, device, on_off):
        logging.debug('[switch] calling %s, power=%s', device, on_off)

        power = 'off'
        if on_off:
            power = 'on'

        response = requests.put(
            self._url + '/device/%s/power/%s' % (device, power),
            headers={'Accept': 'application/se.novafaen.stick.device.v1+json'}
        )

        logging.debug(response.status_code)
        logging.debug(response.text)
