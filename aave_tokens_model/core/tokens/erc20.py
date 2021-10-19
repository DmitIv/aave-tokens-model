"""
ERC20 token.
"""
from collections import defaultdict
from typing import Dict, Any, List

from aave_tokens_model.core.logging import Logged
from aave_tokens_model.core.utilities import (
    AddressT, require, generate_address
)
from aave_tokens_model.core.utilities.restriction import NOT_ENOUGH_BALANCE


class ERC20(Logged):
    """
    The most common ERC20 implementation.
    """

    def __init__(self, name: str, symbol: str, verbose: bool = False) -> None:
        """Prepare new token."""
        super().__init__(verbose)
        self._name = name
        self._symbol = symbol
        self._verbose = verbose
        self._address = generate_address()

        self._balances: Dict[AddressT, float] = defaultdict(lambda: 0)
        self._total_supply: float = 0

    def _get_context(self, function: str, stage: str) -> Dict[str, Any]:
        context = super()._get_context(function, stage)
        context['symbol'] = self._symbol
        return context

    def _prepare_log_before(self, action, *args, **kwargs) -> List[str]:
        base_msg = super()._prepare_log_before(action, *args, **kwargs)
        base_msg.append(base_msg[-1])
        base_msg[-2] = f'total supply = {self._total_supply}'
        return base_msg

    def _prepare_log_after(self, action, *args, **kwargs) -> List[str]:
        base_msg = super()._prepare_log_after(action, *args, **kwargs)
        base_msg.append(base_msg[-1])
        base_msg[-2] = f'new total supply = {self._total_supply}'
        return base_msg

    @staticmethod
    def _format_log_msg(record) -> str:
        msg = Logged._format_log_msg(record)
        extra = record.get('extra', {})
        token_symbol = extra.get('symbol', 'unknown-token')
        start = msg.find('>')
        return msg[:start + 1] + f'{token_symbol}:' + msg[start + 1:]

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

    def total_supply(self) -> float:
        """Get total amount of minted tokens."""
        return self._total_supply

    def balance_of(self, user: AddressT) -> float:
        """Get amount of tokens held by the specific user."""
        return self._balances[user]

    @Logged.with_log
    def transfer(self, user: AddressT, to: AddressT, value: float) -> bool:
        """
        Transfer an amount from user to the specific address.

        Return an indicator of transfer success.
        """
        require(self._balances[user] >= value, NOT_ENOUGH_BALANCE)
        self._balances[user] -= value
        self._balances[to] += value

        return True

    @Logged.with_log
    def mint(self, user: AddressT, value: float) -> float:
        """Mint new tokens for user; return new balance."""
        self._balances[user] += value
        self._total_supply += value
        return self._balances[user]

    @Logged.with_log
    def burn(self, user: AddressT, value: float) -> float:
        """Burn tokens for user; return new balance."""
        require(self._balances[user] >= value, NOT_ENOUGH_BALANCE)
        self._balances[user] -= value
        self._total_supply -= value
        return self._balances[user]
