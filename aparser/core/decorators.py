from functools import wraps
import inspect
import logging
from pathlib import Path
import time
from typing import Any
from typing import Callable
from typing import TypeVar


T = TypeVar("T")


def log_execution(
    level: int = logging.INFO, track_time: bool = True, show_args: bool = False
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to log function execution with timing and error handling.

    Args:
        level: Logging level (e.g., logging.INFO)
        track_time: If True, logs execution duration
        show_args: If True, logs function arguments

    Returns:
        A decorator that wraps the target function

    Example:
        >>> @log_execution(level=logging.DEBUG, track_time=True)
        >>> def fetch_data(url):
        ...     pass
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            """Actual wrapper that instruments the function call.

            Logs:
            - Start/end of execution (with source location)
            - Duration if track_time=True
            - Arguments if show_args=True
            - Full traceback on errors

            Returns:
                The original function's return value

            Raises:
                Original function's exceptions with added logging
            """
            logger = logging.getLogger(func.__module__)

            filename = "unknown"
            lineno = 0
            try:
                current_frame = inspect.currentframe()
                if current_frame is not None and current_frame.f_back is not None:
                    frame = current_frame.f_back
                    filename = Path(frame.f_code.co_filename).name
                    lineno = frame.f_lineno
            except Exception as e:
                logger.debug(f"Could not get frame information: {e}")

            func_name = func.__name__
            arg_str = f"({', '.join(map(repr, args))})" if show_args else ""

            logger.log(level, f"START {filename}:{lineno} - {func_name}{arg_str}")
            start = time.perf_counter()

            try:
                result = func(*args, **kwargs)
                if track_time:
                    elapsed = time.perf_counter() - start
                    logger.log(
                        level,
                        f"FINISH {filename}:{lineno} - {func_name}{arg_str}"
                        f" in {elapsed:.4f}s",
                    )
                return result
            except Exception as e:
                elapsed = time.perf_counter() - start
                logger.error(
                    f"ERROR {filename}:{lineno} - {func_name}{arg_str}"
                    f" after {elapsed:.4f}s: {e}",
                    exc_info=True,
                )
                raise

        return wrapper

    return decorator
