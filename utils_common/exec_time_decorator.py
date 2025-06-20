import asyncio
from typing import Callable
from datetime import datetime


def execution_time_decorator(in_seconds: bool = False,
                             note: str = None,
                             exec_time_logging: bool = False,
                             new_line_after: bool = False) -> Callable:
    def decorator(func: Callable):
        if not exec_time_logging:
            return func

        if asyncio.iscoroutinefunction(func):  # Async func
            async def async_wrapper(*args, **kwargs):
                start_time = datetime.now()
                result = await func(*args, **kwargs)
                end_time = datetime.now()
                time_delta = (end_time - start_time).total_seconds()

                if in_seconds:
                    time_delta = round(time_delta, 3)
                    units = "seconds"
                else:
                    time_delta = int(time_delta * 1e6)
                    units = "microseconds"

                note_text = f"[{note}]" if note else None
                print(f"### EXECUTION TIME {note_text}: "
                      f"{time_delta} {units}")
                print() if new_line_after else None
                return result
            return async_wrapper
        else:  # Sync func
            def sync_wrapper(*args, **kwargs):
                start_time = datetime.now()
                result = func(*args, **kwargs)
                end_time = datetime.now()
                time_delta = (end_time - start_time).total_seconds()

                if in_seconds:
                    time_delta = round(time_delta, 3)
                    units = "seconds"
                else:
                    time_delta = int(time_delta * 1e6)
                    units = "microseconds"

                note_text = f"[{note}]" if note else None
                print(f"### EXECUTION TIME {note_text}: "
                      f"{time_delta} {units}")
                print() if new_line_after else None
                return result
            return sync_wrapper
    return decorator
