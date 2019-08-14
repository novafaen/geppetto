"""Scheduler for Geppetto.

Will schedule and handle event callbacks.
"""


from time import localtime, strftime
import logging
from threading import Thread
import time

import schedule

# supress logging from third party library
logging.getLogger('schedule').setLevel(logging.WARNING)

log = logging.getLogger('geppetto')


class Scheduler(Thread):
    """Scheduler handles events, in a threaded way."""

    def __init__(self, config):
        """Create and initiate ``Stick`` application."""
        Thread.__init__(self)

        log.debug('scheduler initiating')

        for event in config['events']:
            for event_day in event['days']:
                day, time = event_day['day'], event_day['time']
                self.schedule_event(event['type'], day, time,
                                    lights=event['lights'],
                                    switches=event['switches'])

        for schedule_day in config['schedule']:
            start, end = schedule_day['start'], schedule_day['end']
            self.add_schedule(schedule_day['type'], start, end, schedule_day['lights'])

        log.debug('scheduler initiation done')

    def add_schedule(self, schedule_name, start, end, lights):
        """Add a schedule to the scheduler.

        :param schedule_name: ``String`` name or "type" of schedule
        :param start: ``String`` in HH:MM format
        :param end: ``String`` in HH:MM format
        :param lights: ``[String]`` list of lights
        """
        if schedule_name == 'bright':
            schedule_function = self._schedule_bright
        elif schedule_name == 'sunlight':
            schedule_function = self._schedule_sunlight
        else:
            log.warning('unknown schedule %s, for %s-%s with %s', schedule_name, start, end, lights)
            return

        log.debug('registered schedule %s, %s-%s', schedule_name, start, end)
        schedule.every(1).minute.do(schedule_function, start, end, lights)

    def schedule_event(self, event_name, day, time, lights=None, switches=None):
        """Add scheduled events to scheduler.

        :param event_name: ``String`` name or "type" of events
        :param day: ``String`` weekday in English
        :param time: ``String`` in HH:MM format
        :param lights: ``[String]`` list of light names
        :param switches: ``[String]`` list of on-off devices
        """
        if event_name == 'power_on':
            event_function = self._event_power_on
        elif event_name == 'power_off':
            event_function = self._event_power_off
        elif event_name == 'wakeup':
            event_function = self._event_wakeup
        else:
            log.warning('unknown event %s, for %s %s with %s', event_name, day, time, lights)
            return

        if day == 'monday':
            schedule.every().monday.at(time).do(event_function, lights + switches)
        elif day == 'tuesday':
            schedule.every().tuesday.at(time).do(event_function, lights + switches)
        elif day == 'wednesday':
            schedule.every().wednesday.at(time).do(event_function, lights + switches)
        elif day == 'thursday':
            schedule.every().thursday.at(time).do(event_function, lights + switches)
        elif day == 'friday':
            schedule.every().friday.at(time).do(event_function, lights + switches)
        elif day == 'saturday':
            schedule.every().saturday.at(time).do(event_function, lights + switches)
        elif day == 'sunday':
            schedule.every().sunday.at(time).do(event_function, lights + switches)

        log.debug('registered event %s, %s at %s', event_name, day, time)

    def run(self):
        """Start the thread."""
        while True:
            schedule.run_pending()
            time.sleep(1)

    def _schedule_bright(self, start, end, lights):
        """Action, internal schedule fuction."""
        now = strftime("%H:%M", localtime())
        if start < end and start <= now <= end \
                or start > end and now > start > end \
                or start > end and now < end < start:
            log.debug('scheduled bright on for %s', lights)
            try:
                self.schedule_bright(lights)
            except Exception as err:
                log.error('Unexpected bright schedule crash: %s', err)

    @staticmethod
    def schedule_bright(lights):
        """Abstract callback function, must be overridden."""
        raise NotImplementedError('missing implementation schedule function: bright')

    def _schedule_sunlight(self, start, end, lights):
        """Action, internal schedule fuction."""
        now = strftime("%H:%M", localtime())
        if start < end and start <= now <= end \
                or start > end and now > start > end \
                or start > end and now < end < start:
            log.debug('scheduled sunlight on for %s', lights)
            try:
                self.schedule_sunlight(lights)
            except Exception as err:
                log.error('Unexpected sunlight schedule crash: %s', err)

    @staticmethod
    def schedule_sunlight(lights):
        """Abstract callback function, must be overridden."""
        raise NotImplementedError('missing implementation schedule function: sunlight')

    def _event_power_on(self, devices):
        log.debug('event power on for %s', devices)
        try:
            self.event_power_on(devices)
        except Exception as err:
            log.error('Unexpected power_on event crash: %s', err)

    def event_power_on(self, devices):
        """Abstract callback function, must be overridden."""
        raise NotImplementedError('missing implementation event function: power_on')

    def _event_power_off(self, devices):
        """Action, internal schedule fuction."""
        log.debug('event power off for %s', devices)
        try:
            self.event_power_off(devices)
        except Exception as err:
            log.error('Unexpected power_on event crash: %s', err)

    def event_power_off(self, devices):
        """Abstract callback function, must be overridden."""
        raise NotImplementedError('missing implementation event function: power_off')

    def _event_wakeup(self, lights):
        """Action, internal schedule fuction."""
        log.debug('event wake up for %s', lights)

        try:
            self.event_wakeup(lights)
        except Exception as err:
            log.error('Unexpected wakeup event crash: %s', err)

    def event_wakeup(self, lights):
        raise NotImplementedError('missing implementation event function: wakeup')
