import asyncio
import inspect
from asyncio.events import AbstractEventLoop
from typing import Callable, List

from pydantic import BaseModel
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

EVENT_TYPE_ANY = "any"
EVENT_TYPE_MOVED = "moved"
EVENT_TYPE_DELETED = "deleted"
EVENT_TYPE_CREATED = "created"
EVENT_TYPE_MODIFIED = "modified"
VERSION = "0.0.0"


class FSCallback(BaseModel):
    """
    A dataclass that represents a callback to look for along with a callback_callable to run in that case.
    """

    event_type: str
    event_path: str
    callback_function: Callable[[FileSystemEvent], None]


class FSAsyncEventHandler(FileSystemEventHandler):
    def __init__(
        self,
        callback: FSCallback,
        loop: AbstractEventLoop = asyncio.get_event_loop(),
    ) -> None:
        self.callback_function = callback.callback_function
        self.loop = loop
        self.event_type_trigger = callback.event_type

    def dispatch(self, event: FileSystemEvent):
        if event.event_type == self.event_type_trigger:
            self.loop.call_soon_threadsafe(
                asyncio.create_task, self.callback_function(event)
            )


class FSWatcher(BaseModel):
    _observer: Observer = Observer()
    _callbacks: List[FSCallback] = []
    _loop: AbstractEventLoop = asyncio.get_event_loop()

    def watch(self):
        self._loop.run_until_complete(self.run_async())

    async def run_async(self):
        for callback in self._callbacks:
            if inspect.iscoroutinefunction(callback.callback_function):
                self._observer.schedule(
                    event_handler=FSAsyncEventHandler(callback=callback),
                    path=callback.event_path,
                    recursive=True,
                )
            else:
                raise Exception(
                    "FSWatcher only accepts coroutine functions as of version {}".format(
                        VERSION
                    )
                )
        self.start()
        for _ in range(20):
            await asyncio.sleep(1)
        self.stop()

    def start(self):
        self._observer.start()

    def stop(self):
        self._observer.stop()
        self._observer.join()

    def run(self):
        # if
        pass

    def on_any(self, path_to_watch: str) -> Callable[[Callable], Callable]:
        """
        A decorator that registers the function it decorates as a callback for on_any events related to path_to_watch.

        Arguments:
        - path_to_watch: The relative path to register the callable to.
        """

        def decorator(event_handler: Callable[[FileSystemEvent], None]) -> Callable:
            self._callbacks.append(
                FSCallback(
                    event_type=EVENT_TYPE_ANY,
                    event_path=path_to_watch,
                    callback_function=event_handler,
                )
            )
            return event_handler

        return decorator

    def on_moved(self, path_to_watch: str) -> Callable[[Callable], Callable]:
        """
        A decorator that registers the function it decorates as a callback for on_moved events related to path_to_watch.

        Arguments:
        - path_to_watch: The relative path to register the callable to.
        """

        def decorator(event_handler: Callable[[FileSystemEvent], None]) -> Callable:
            self._callbacks.append(
                FSCallback(
                    event_type=EVENT_TYPE_MOVED,
                    event_path=path_to_watch,
                    callback_function=event_handler,
                )
            )
            return event_handler

        return decorator

    def on_created(self, path_to_watch: str) -> Callable[[Callable], Callable]:
        """
        A decorator that registers the function it decorates as a callback for on_created events related to path_to_watch.

        Arguments:
        - path_to_watch: The relative path to register the callable to.
        """

        def decorator(event_handler: Callable[[FileSystemEvent], None]) -> Callable:
            self._callbacks.append(
                FSCallback(
                    event_type=EVENT_TYPE_CREATED,
                    event_path=path_to_watch,
                    callback_function=event_handler,
                )
            )
            return event_handler

        return decorator

    def on_deleted(self, path_to_watch: str) -> Callable[[Callable], Callable]:
        """
        A decorator that registers the function it decorates as a callback for on_deleted events related to path_to_watch.

        Arguments:
        - path_to_watch: The relative path to register the callable to.
        """

        def decorator(event_handler: Callable[[FileSystemEvent], None]) -> Callable:
            self._callbacks.append(
                FSCallback(
                    event_type=EVENT_TYPE_DELETED,
                    event_path=path_to_watch,
                    callback_function=event_handler,
                )
            )
            return event_handler

        return decorator

    def on_modified(self, path_to_watch: str) -> Callable[[Callable], Callable]:
        """
        A decorator that registers the function it decorates as a callback for on_modified events related to path_to_watch.

        Arguments:
        - path_to_watch: The relative path to register the callable to.
        """

        def decorator(event_handler: Callable[[FileSystemEvent], None]) -> Callable:
            self._callbacks.append(
                FSCallback(
                    event_type=EVENT_TYPE_MODIFIED,
                    event_path=path_to_watch,
                    callback_function=event_handler,
                )
            )
            return event_handler

        return decorator
