from typing import Tuple
from functools import lru_cache

from aave_tokens_model.core.tokens.erc20 import ERC20
from aave_tokens_model.core.tokens.steth import StETH, get_steth
from aave_tokens_model.core.utilities.types import AddressT


class VDebtStETH(ERC20):
    def __init__(self, steth: StETH):
        super().__init__('variable debt stETH token', 'VDebtStETH')
        self._borrowed_shares: float = 0.0
        self._bor_index: float = 1.0
        self._steth: StETH = steth

    @property
    def bor_index(self) -> float:
        """Get borrow index"""
        return self._bor_index

    def _scaled_total_supply(self) -> float:
        """Get total supply without borrowing interest."""
        return super().total_supply()

    def _scaled_balance_of(self, user: AddressT) -> float:
        """Get balance of user without borrowing interest"""
        return super().balance_of(user)

    def _scale_value(self, value: float) -> float:
        return value / self._bor_index

    def total_supply(self) -> float:
        """Get total supply (with borrowing interest)"""
        return self._scaled_total_supply() * self._bor_index

    def balance_of(self, user: AddressT) -> float:
        """Get balance of user (with borrowing interest)"""
        return self._scaled_balance_of(user) * self._bor_index

    def transfer(self, user: AddressT, to: AddressT, value: int) -> bool:
        """Out of modeling"""
        raise NotImplementedError('out of modeling.')

    def mint(self, user: AddressT, value: float) -> float:
        """Mint new debt tokens for user."""
        scaled_value = self._scale_value(value)
        new_shares = self._steth.get_shares_by_pooled_steth(scaled_value)
        self._borrowed_shares += new_shares
        return super().mint(user, scaled_value)

    def burn(self, user: AddressT, value: float) -> float:
        """Burn tokens for user."""
        scaled_value = self._scale_value(value)
        remains = super().burn(user, scaled_value)
        burned_shares = self._steth.get_shares_by_pooled_steth(scaled_value)
        self._borrowed_shares -= burned_shares

        return remains

    def get_borrowed_state(self) -> Tuple[float, float]:
        """Get borrowed shares and total supply of debt token"""
        return self._borrowed_shares, self._scaled_total_supply()


@lru_cache(1)
def get_debtsteth() -> VDebtStETH:
    """Get cached instance of VDebtStETH"""
    return VDebtStETH(get_steth())
