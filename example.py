from watchdog.events import FileSystemEvent
from decorated_watchdog import FSWatcher

watcher = FSWatcher()

@watcher.on_any("README.md")
async def say_hello(event: FileSystemEvent):
    print("Modified README file.")

watcher.watch()
