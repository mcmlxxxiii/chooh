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
                changes = EventBunchDelayedHandler.extract_changes(self._events_collected)
                self._callback(changes)
                self._events_collected = []
        return cb

    def on_any_event(self, event):
        self._events_collected.append(event)
        self._counter += 1
        timer = threading.Timer(
                self._delay, self.make_real_callback(self._counter))
        timer.start()

    @classmethod
    def extract_changes(cls, event_list):
        changes = {
            'created_files': [],
            'modified_files': [],
            'moved_files': [],
            'deleted_files': [],
            'created_dirs': [],
            'moved_dirs': [],
            'deleted_dirs': []
        }

        for e in event_list:
            if isinstance(e, events.FileDeletedEvent):
                changes['deleted_files'].append(e.src_path)

            elif isinstance(e, events.FileCreatedEvent):
                if e.src_path in changes['deleted_files']:
                    changes['modified_files'].append(e.src_path)
                    changes['deleted_files'].remove(e.src_path)
                else:
                    changes['created_files'].append(e.src_path)

            elif isinstance(e, events.FileModifiedEvent):
                changes['modified_files'].append(e.src_path)

            elif isinstance(e, events.FileMovedEvent):
                changes['moved_files'].append([e.src_path, e.dest_path])

            elif isinstance(e, events.DirDeletedEvent):
                changes['deleted_dirs'].append(e.src_path)

            elif isinstance(e, events.DirCreatedEvent):
                changes['created_dirs'].append(e.src_path)

            elif isinstance(e, events.DirMovedEvent):
                changes['moved_dirs'].append([e.src_path, e.dest_path])

            # DirModifiedEvent is triggered at all times, so it is not
            # very useful and is not being handled.

        return changes

def observe_directory_changes(path, callback, delay=0.5):
    observer = observers.Observer()
    observer.schedule(
            EventBunchDelayedHandler(delay, callback), path, recursive=True)
    observer.start()
    return observer
