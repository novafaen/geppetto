from time import localtime, strftime
import logging
from threading import Thread
import time

import schedule

logging.getLogger('schedule').setLevel(logging.WARNING)


class Scheduler(Thread):
    def __init__(self, config):
        super().__init__()

        logging.debug('[scheduler] initiating')

        self._config = config

        for event in config['events']:
            for event_day in event['days']:
                day, time = event_day['day'], event_day['time']
                self.schedule_event(event['type'], day, time, event['lights'])

        for schedule_day in config['schedule']:
            start, end = schedule_day['start'], schedule_day['end']
            self.add_schedule(schedule_day['type'], start, end, schedule_day['lights'])

        logging.debug('[scheduler] initiation done')

    def add_schedule(self, schedule_name, start, end, lights):
        if schedule_name == 'bright':
            schedule_function = self._schedule_bright
        elif schedule_name == 'sunlight':
            schedule_function = self._schedule_sunlight
        else:
            logging.warning('[scheduler] unknown schedule %s, for %s-%s with %s', schedule_name, start, end, lights)
            return

        schedule.every(1).minute.do(schedule_function, start, end, lights)

    def schedule_event(self, event_name, day, time, lights):
        if event_name == 'power_on':
            event_function = self._event_power_on
        elif event_name == 'wakeup':
            event_function = self._event_wakeup
        else:
            logging.warning('[scheduler] unknown event %s, for %s %s with %s', event_name, day, time, lights)
            return

        if day == 'monday':
            schedule.every().monday.at(time).do(event_function, lights)
        elif day == 'tuesday':
            schedule.every().tuesday.at(time).do(event_function, lights)
        elif day == 'wednesday':
            schedule.every().wednesday.at(time).do(event_function, lights)
        elif day == 'thursday':
            schedule.every().thursday.at(time).do(event_function, lights)
        elif day == 'friday':
            schedule.every().friday.at(time).do(event_function, lights)
        elif day == 'saturday':
            schedule.every().saturday.at(time).do(event_function, lights)
        elif day == 'sunday':
            schedule.every().sunday.at(time).do(event_function, lights)

    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

    def _schedule_bright(self, start, end, lights):
        now = strftime("%H:%M", localtime())
        if start < end and start <= now <= end \
                or start > end and now > start > end \
                or start > end and now < end < start:
            logging.debug('[scheduler] event bright on for %s', lights)
            try:
                self.schedule_bright(lights)
            except Exception as err:
                logging.error('[scheduler] Unexpected bright schedule crash: %s', err)
        else:
            logging.debug('[scheduler] event bright outside time %s', now)

    @staticmethod
    def schedule_bright(lights):
        raise NotImplementedError('missing implementation schedule function: bright')

    def _schedule_sunlight(self, start, end, lights):
        now = strftime("%H:%M", localtime())
        if start < end and start <= now <= end \
                or start > end and now > start > end \
                or start > end and now < end < start:
            logging.debug('[scheduler] event sunlight on for %s', lights)
            try:
                self.schedule_sunlight(lights)
            except Exception as err:
                logging.error('[scheduler] Unexpected sunlight schedule crash: %s', err)
        else:
            logging.debug('[scheduler] event sunlight outside time %s', now)

    @staticmethod
    def schedule_sunlight(lights):
        raise NotImplementedError('missing implementation schedule function: sunlight')

    def _event_power_on(self, lights):
        logging.debug('[scheduler] event power on for %s', lights)
        try:
            self.event_power_on(lights)
        except Exception as err:
            logging.error('[scheduler] Unexpected power_on event crash: %s', err)

    def event_power_on(self, lights):
        raise NotImplementedError('missing implementation event function: power_on')

    def _event_wakeup(self, lights):
        logging.debug('[scheduler] event wake up for %s', lights)

        try:
            self.event_wakeup(lights)
        except Exception as err:
            logging.error('[scheduler] Unexpected wakeup event crash: %s', err)

    def event_wakeup(self, lights):
        raise NotImplementedError('missing implementation event function: wakeup')


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.DEBUG
    )

    import json
    fh = open('../configuration.json', 'rb')
    config = json.loads(fh.read())
    fh.close()

    removeme = Scheduler(config)

    removeme.start()