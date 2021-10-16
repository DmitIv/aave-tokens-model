from typing import Tuple

from aave_tokens_model.core.tokens.aerc20 import AERC20
from aave_tokens_model.core.tokens.erc20 import ERC20
from aave_tokens_model.core.tokens.steth import StETH
from aave_tokens_model.core.utilities.types import MSG, AddressT


class VDebtToken(ERC20):
    def __init__(self, steth: StETH):
        self._name = 'variableDebtStETH'
        self._borrowed_shares: float = 0.0
        self._underlaying_erc20 = AERC20()

        self._bor_index: float = 1.0
        self._steth = steth

    @property
    def name(self) -> str:
        """Get token name"""
        return self._name

    @property
    def symbol(self) -> str:
        """Get token symbol"""
        return self._name

    @property
    def bor_index(self) -> float:
        """Get borrow index"""
        return self._bor_index

    @bor_index.setter
    def bor_index(self, new_bor_index: float) -> None:
        """Set new borrow index."""
        if new_bor_index < 0:
            raise ValueError('borrow index should be a pos number.')

        self._bor_index = new_bor_index

    def _scaled_total_supply(self) -> float:
        """Get total supply without borrowing interest."""
        return self._underlaying_erc20.total_supply()

    def _scaled_balance_of(self, user: AddressT) -> float:
        """Get balance of user without borrowing interest"""
        return self._underlaying_erc20.balance_of(user)

    def total_supply(self) -> float:
        """Get total supply (with borrowing interest)"""
        return self._scaled_total_supply() * self._bor_index

    def balance_of(self, user: AddressT) -> float:
        """Get balance of user (with borrowing interest)"""
        return self._scaled_balance_of(user) * self._bor_index

    def transfer(self, msg: MSG, to: AddressT, value: int) -> bool:
        """Out of modeling"""
        raise NotImplementedError('out of modeling.')

    def transfer_from(
            self, msg: MSG, _from: AddressT, to: AddressT, value: int
    ) -> int:
        """Out of modeling"""
        raise NotImplementedError('out of modeling.')

    def allowance(self, owner: AddressT, spender: AddressT) -> int:
        """Out of modeling"""
        raise NotImplementedError('out of modeling.')

    def approve(self, msg: MSG, spender: AddressT, value: int) -> bool:
        """Out of modeling"""
        raise NotImplementedError('out of modeling.')

    def mint(self, user: AddressT, value: float) -> float:
        """Mint new debt tokens for user."""
        if value == 0:
            return self._underlaying_erc20.balance_of(user)
        value_scaled = value / self._bor_index
        self._underlaying_erc20.mint(user, value_scaled)
        self._borrowed_shares += self._steth.get_shares_by_pooled_steth(
            value_scaled
        )
        return self._underlaying_erc20.balance_of(user)

    def burn(self, user: AddressT, value: float) -> float:
        if value == 0:
            return self._underlaying_erc20.balance_of(user)

        value_scaled = value / self._bor_index
        self._underlaying_erc20.burn(user, value_scaled)
        self._borrowed_shares -= self._steth.get_shares_by_pooled_steth(
            value_scaled
        )

        return self._underlaying_erc20.balance_of(user)

    def get_borrowed_state(self) -> Tuple[float, float]:
        """Get borrowed shares and total supply of debt token"""
        return self._borrowed_shares, self._scaled_total_supply()
