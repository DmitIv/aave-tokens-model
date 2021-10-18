from functools import lru_cache

from aave_tokens_model.core.tokens.erc20 import ERC20
from aave_tokens_model.core.utilities.types import (
    AddressT
)


class StETH(ERC20):
    """
    StETH token.

    self._total_supply == total shares
    underlaying ERC20 token is equal to shares from contract.
    """

    def __init__(self):
        super().__init__('stETH token', 'stETH')
        self._pooled_eth: float = 0.0

    @property
    def shares_to_steth(self) -> float:
        """Get factor for shares to stETH conversion."""
        if self._total_supply == 0:
            return 0
        return self._pooled_eth / self._total_supply

    @property
    def steth_to_shares(self) -> float:
        """Get factor for stETH to shares conversion."""
        if self._pooled_eth == 0:
            return 0
        return self._total_supply / self._pooled_eth

    def _shares_to_steth(self, shares_amount: float) -> float:
        """Convert amount of shares to amount of stETH."""
        return shares_amount * self.shares_to_steth

    def _steth_to_shares(self, steth_amount: float) -> float:
        """Convert amount of stETH to amount of shares."""
        return steth_amount * self.steth_to_shares

    def _rebase(self, shift: float) -> float:
        """Shift pooled eth with shift value."""
        self._pooled_eth += shift
        return self._pooled_eth

    def rebase_mul(self, factor: float) -> float:
        """
        Change total supply of token with mul by factor.

        Return new amount.
        """
        previous_total_supply = self._pooled_eth
        new_total_supply = self._pooled_eth * factor
        return self._rebase(new_total_supply - previous_total_supply)

    def rebase_sft(self, shift: float) -> float:
        """
        Change total supply of token by adding shift.
        """
        return self._rebase(shift)

    def total_supply(self) -> float:
        """Get amount of stETH, always equal to underlying eth."""
        return self._pooled_eth

    def balance_of(self, user: AddressT) -> float:
        """Get the balance of user in stETH."""
        shares_of_user = super().balance_of(user)
        return self._shares_to_steth(shares_of_user)

    def transfer(self, user: AddressT, to: AddressT, value: float) -> bool:
        """Transfer stETH from caller to the specific address."""
        value_in_shares = self._steth_to_shares(value)
        super().transfer(user, to, value_in_shares)
        return True

    def mint(self, user: AddressT, value: float) -> float:
        """Mint new tokens for user."""
        if self._pooled_eth == 0:
            self._pooled_eth += value
            return super().mint(user, value)

        value_in_shares = self._steth_to_shares(value)
        self._pooled_eth += value
        return super().mint(user, value_in_shares)

    def burn(self, user: AddressT, value: float) -> float:
        """Burn value of tokens from user balance."""
        value_in_shares = self._steth_to_shares(value)
        return super().burn(user, value_in_shares)

    def get_pooled_steth_by_shares(self, shares_amount: float) -> float:
        """Convert shares to steth."""
        return self._shares_to_steth(shares_amount)

    def get_shares_by_pooled_steth(self, steth_amount: float) -> float:
        """Convert steth to shares."""
        return self._steth_to_shares(steth_amount)


@lru_cache(1)
def get_steth() -> StETH:
    """Get cached instance of StETH."""
    return StETH()


def stake_eth(steth: StETH, user: AddressT, value: int) -> float:
    """Stake ethereum and get StETH, return amount of minted shares."""
    return steth.mint(user, value)
