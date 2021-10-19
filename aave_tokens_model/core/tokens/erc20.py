"""
ERC20 token.
"""
import sys
from collections import defaultdict
from functools import wraps
from typing import Dict

from loguru import logger

from aave_tokens_model.core.utilities import (
    AddressT, require, generate_address
)
from aave_tokens_model.core.utilities.restriction import NOT_ENOUGH_BALANCE


class ERC20:
    """
    The most common ERC20 implementation.
    """

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
                f'<r>{msg}</r>'
            )

        token_name = record['extra'].get('symbol', 'unknown-token')
        function = record['function']
        msg = record['message']

        return (
            f'{token_name}:{function}::\n'
            f'{msg}'
        )

    @staticmethod
    def _filter_log_msg(record) -> bool:
        """Filter log message."""
        return record['level'] == 'INFO'

    def __init__(self, name: str, symbol: str, verbose: bool = False) -> None:
        """Prepare new token."""
        self._name = name
        self._symbol = symbol
        self._verbose = verbose
        self._address = generate_address()

        self._balances: Dict[AddressT, float] = defaultdict(lambda: 0)
        self._total_supply: float = 0
        self._logger = logger
        self._setup_logger()

    def _setup_logger(self) -> None:
        self._logger.remove()
        if self._verbose:
            self._logger.add(
                sys.stdout, level='INFO',
                format=self._format_log_msg,
                filter=self._filter_log_msg
            )
            self._logger.bind(name=self._name, symbol=self._symbol)

    def _log(action):
        @wraps(action)
        def _handler(self, *args, **kwargs):
            self._print_log(action, *args, **kwargs)
            return action(self, *args, **kwargs)

        return _handler

    @property
    def name(self) -> str:
        """Get name of token."""
        return self._name

    @property
    def symbol(self) -> str:
        """Get symbol of token."""
        return self._symbol

    @property
    def address(self) -> AddressT:
        """Get address of token."""
        return self._address

    def _print_log(self, action, *args, **kwargs) -> None:
        args = ' '.join([str(arg) for arg in args])
        kwargs = ' '.join([
            f'{str(key)} = {str(value)}'
            for key, value in kwargs.items()
        ])
        delimiter = '=' * 10
        self._logger.info(
            f'args: {args}\n'
            f'kwargs: {kwargs}\n'
            f'{delimiter}'
        )

    def switch_up_logger(self, with_logging: bool) -> None:
        """Switch-up logging"""
        self._verbose = with_logging
        self._setup_logger()

    def total_supply(self) -> float:
        """Get total amount of minted tokens."""
        return self._total_supply

    def balance_of(self, user: AddressT) -> float:
        """Get amount of tokens held by the specific user."""
        return self._balances[user]

    @_log
    def transfer(self, user: AddressT, to: AddressT, value: float) -> bool:
        """
        Transfer an amount from user to the specific address.

        Return an indicator of transfer success.
        """
        require(self._balances[user] >= value, NOT_ENOUGH_BALANCE)
        self._balances[user] -= value
        self._balances[to] += value

        return True

    @_log
    def mint(self, user: AddressT, value: float) -> float:
        """Mint new tokens for user; return new balance."""
        self._balances[user] += value
        self._total_supply += value
        return self._balances[user]

    @_log
    def burn(self, user: AddressT, value: float) -> float:
        """Burn tokens for user; return new balance."""
        require(self._balances[user] >= value, NOT_ENOUGH_BALANCE)
        self._balances[user] -= value
        self._total_supply -= value
        return self._balances[user]
