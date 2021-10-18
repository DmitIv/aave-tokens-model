from typing import Dict
from collections import defaultdict

from loguru import logger

from aave_tokens_model.core.utilities import (
    AddressT,
    require, generate_address
)
from aave_tokens_model.core.utilities.restriction import (
    NOT_ENOUGH_BALANCE
)


class ERC20:
    def __init__(self, name: str, symbol: str, verbose: bool = False) -> None:
        """Prepare new token."""
        self._name = name
        self._symbol = symbol
        self._verbose = verbose
        self._address = generate_address()

        self._balances: Dict[AddressT, float] = defaultdict(lambda: 0)
        self._total_supply: float = 0

    def _log(action):
        def _handler(self, *args, **kwargs):
            if self._verbose:
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
        cls_name = type(self)
        name = getattr(action, '__name__', 'action')
        logger.debug(
            f'class: {cls_name} '
            f'run {name} with '
            f'args: {args}; '
            f'kwargs: {kwargs}'
        )

    def on_logging(self) -> None:
        """Switch-on logging"""
        self._verbose = True

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
