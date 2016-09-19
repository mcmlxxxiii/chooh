# -*- coding: utf-8 -*-

import threading
from watchdog import events, observers


class EventBunchDelayedHandler(events.FileSystemEventHandler):
    def __init__(self, delay, callback):
        self._counter = 0
        self._callback = callback
        self._delay = delay
        self._events_collected = []
    def process_events(self):
        #TODO Process events to understand whether any of them and so maybe
        # a whole bunch should be ignored. And to be able to pretty print
        # the changes done to console.
        pass
    def make_real_callback(self, c):
        def cb():
            if c == self._counter:
                self._callback(self._events_collected)
                self._events_collected = []
        return cb
    def on_any_event(self, event):
        self._events_collected.append(event)
        self._counter += 1
        timer = threading.Timer(self._delay, self.make_real_callback(self._counter))
        timer.start()

def observe_directory_changes(path, callback, delay=0.5):
    observer = observers.Observer()
    observer.schedule(EventBunchDelayedHandler(delay, callback), path, recursive=True)
    observer.start()
    return observer
