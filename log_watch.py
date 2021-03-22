#!/usr/bin/env python3
import sys
import os
from inotify_simple import INotify, flags

SERVER_NAME = os.environ['server_name'].replace(' ', '_')
LOG_DIR = f'/srv/{SERVER_NAME}/logs'
LATEST_LOG = f'{LOG_DIR}/latest.log'

class McDirWatcher:
    def __init__(self):
        self.inotify = INotify()

        watch_flags = flags.CREATE | flags.MODIFY
        self.inotify.add_watch(LOG_DIR, watch_flags)

    def events(self):
        while True:
            yield from self.inotify.read()

    def close(self):
        self.inotify.close()

class McLatestLog:
    def __init__(self):
        self.dir_watcher = McDirWatcher()
        self.cur_log = open(LATEST_LOG)
        self.cur_log.seek(0, 2) # Seek to end

    def close(self):
        self.cur_log.close()
        self.dir_watcher.close()

    def __enter__(self):
        return self

    def __exit__(self, _1, _2, _3):
        self.close()

    def __iter__(self):
        return self.lines()

    def lines(self):
        # let's assume we don't read partial lines. lol
        for event in self.dir_watcher.events():
            if event.mask & flags.CREATE:
                self.cur_log.close()
                self.cur_log = open(LATEST_LOG)
            if event.mask & flags.MODIFY:
                yield from self.cur_log

def main():
    print('Log watcher starting...', file=sys.stderr)
    with McLatestLog() as log:
        for line in log:
            print(line, end='', flush=True)


if __name__ == '__main__':
    main()
