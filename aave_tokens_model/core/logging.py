import inspect
import sys
from functools import wraps, lru_cache
from itertools import zip_longest, chain
from typing import List, Callable, Dict, Any, Tuple

from loguru import logger


def get_function_signature(func: Callable) -> str:
    """Get function signature as string."""
    full_spec = inspect.getfullargspec(func)
    arguments = full_spec.args
    if arguments is None:
        arguments = []
    invert_arguments = arguments[::-1]
    defaults = full_spec.defaults
    if defaults is None:
        defaults = []
    invert_defaults = defaults[::-1]

    def _make_arg_repr(arg: Tuple) -> str:
        arg_name, default_value = arg
        value_type = full_spec.annotations.get(arg_name, None)

        if default_value is not None:
            default_value = f' = {default_value}'
        else:
            default_value = ''

        if value_type is not None:
            value_type = getattr(value_type, '__name__', value_type)
            value_type = f': {value_type}'
        else:
            value_type = ''

        return f'{arg_name}{value_type}{default_value}'

    varargs = full_spec.varargs
    if varargs is not None:
        varargs = [f'*{varargs}']
    else:
        varargs = []

    varkw = full_spec.varkw
    if varkw is not None:
        varkw = [f'**{varkw}']
    else:
        varkw = []

    arguments = ', '.join(chain(list(map(
        _make_arg_repr, zip_longest(invert_arguments, invert_defaults))
    )[::-1], varargs, varkw))

    func_name = getattr(func, '__name__', 'function')

    return f'{func_name}({arguments})'


class Logged:
    LOG_BEFORE = 'BEFORE'
    LOG_AFTER = 'AFTER'
    LOG_INTERNAL = 'INTERNAL'

    COLORIZE_PER_STAGE = {
        LOG_AFTER: 'green',
        LOG_BEFORE: 'blue',
        LOG_INTERNAL: 'red'
    }

    def __init__(self, verbose: bool = False):
        self._verbose = verbose

        self._logger = logger
        self._setup_logger()

    def function_log(self, func):
        @wraps(func)
        def _log(*args, **kwargs) -> Any:
            function = func.__qualname__
            base_message = self._prepare_base_message(func, *args, *kwargs)
            with self._logger.contextualize(
                    function=function, stage=self.LOG_BEFORE, symbol='func'
            ):
                self._logger.info('\n'.join(base_message))
            result = func(*args, **kwargs)
            with self._logger.contextualize(
                    function=function, stage=self.LOG_AFTER, symbol='func'
            ):
                self._logger.info('\n'.join(base_message))
            return result

        return _log

    @staticmethod
    def _format_log_msg(record) -> str:
        """Format log message for using it with Loguru."""
        if record.get('exception', None):
            file_name = record['file'].name
            line = record['line']
            time = record['time']
            msg = record['message']

            return (
                f'{time:HH:mm:ss} '
                f'<b>{file_name}:{line}</b>::\n'
                f'<r>{msg}</r>\n'
            )

        extra = record.get('extra', {})
        stage = extra.get('stage', Logged.LOG_BEFORE)
        color = Logged.COLORIZE_PER_STAGE[stage]
        function = extra.get('function', 'unknown-function')
        msg = record['message']

        return (
            f'<{color}>{function}:{stage}</{color}>\n'
            f'{msg}\n'
        )

    def _setup_logger(self) -> None:
        self._logger.remove()
        if self._verbose:
            self._logger.add(
                sys.stdout, level='INFO',
                format=self._format_log_msg
            )

    def _prepare_base_message(
            self, action: Callable, *args, **kwargs
    ) -> List[str]:
        signature = get_function_signature(action)
        args = ' '.join([str(arg) for arg in args])
        kwargs = ' '.join([
            f'{str(key)} = {str(value)}'
            for key, value in kwargs.items()
        ])
        delimiter = '=' * 20
        return [
            f'signature: {signature}',
            f'args: {args}',
            f'kwargs: {kwargs}',
            f'{delimiter}',
        ]

    def _prepare_log_before(self, action, *args, **kwargs) -> List[str]:
        return self._prepare_base_message(action, *args, **kwargs)

    def _prepare_log_after(self, action, *args, **kwargs) -> List[str]:
        return self._prepare_base_message(action, *args, **kwargs)

    def _get_context(self, function: str, stage: str) -> Dict[str, Any]:
        return {
            'function': function,
            'stage': stage
        }

    def with_log(action):
        @wraps(action)
        def _handler(self, *args, **kwargs):
            function = action.__qualname__
            with self._logger.contextualize(**self._get_context(
                    function=function,
                    stage=self.LOG_BEFORE,
            )):
                self._logger.info('\n'.join(
                    self._prepare_log_before(action, *args, **kwargs)
                ))
            result = action(self, *args, **kwargs)
            with self._logger.contextualize(**self._get_context(
                    function=function,
                    stage=self.LOG_AFTER,
            )):
                self._logger.info('\n'.join(
                    self._prepare_log_after(action, *args, **kwargs)
                ))
            return result

        return _handler

    def log(self, act: Callable, message: str) -> None:
        with self._logger.contextualize(**self._get_context(
                function=act.__qualname__,
                stage=Logged.LOG_INTERNAL,
        )):
            self._logger.info(message)

    def switch_up_logger(self, with_logging: bool) -> None:
        """Switch-up logging"""
        self._verbose = with_logging
        self._setup_logger()


@lru_cache(1)
def get_logger() -> Logged:
    return Logged(True)
