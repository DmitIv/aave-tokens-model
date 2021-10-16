from typing import Dict

from aave_tokens_model.core.tokens.erc20 import ERC20
from aave_tokens_model.core.utilities.restriction import require
from aave_tokens_model.core.utilities.types import (
    AddressT, MSG
)


class StETH(ERC20):
    def __init__(self):
        self._name: str = 'steth'
        self._total_shares: float = 0
        self._total_eth: float = 0
        self._shares: Dict[AddressT, float] = {}
        self._allowances: Dict[AddressT, Dict[AddressT, float]] = {}

    def _shares2steth(self, shares_amount: float) -> float:
        """Convert amount of shares to amount of stETH."""
        return shares_amount * self._total_eth / self._total_shares

    def _steth2shares(self, steth_amount: float) -> float:
        """Convert amount of stETH to amount of shares."""
        return steth_amount * self._total_shares / self._total_eth

    def rebase(self, amount: float) -> float:
        """
        Change total supply of token.

        Return new amount.
        """
        self._total_eth += amount
        return self._total_eth

    @property
    def name(self) -> str:
        return self._name

    @property
    def symbol(self) -> str:
        return self._name

    def total_supply(self) -> float:
        """Get amount of stETH, always equal to underlying eth."""
        return self._total_eth

    def balance_of(self, user: AddressT) -> float:
        """Get the balance of user in stETH."""
        return self._shares2steth(self._shares.get(user, 0))

    def transfer(self, msg: MSG, to: AddressT, value: float) -> bool:
        """Transfer stETH from caller to the specific address."""
        if value == 0:
            return False
        value_in_shares = self._steth2shares(value)
        require(
            self._shares.get(msg.sender, 0) >= value_in_shares,
            'not enough balance'
        )

        self._shares[msg.sender] -= value_in_shares
        self._shares[to] = self._shares.get(to, 0) + value_in_shares

        return True

    def transfer_from(
            self, msg: MSG, _from: AddressT, to: AddressT, value: int
    ) -> float:
        """Transfer stETH on behalf of from to the address."""
        if value == 0:
            return False
        value_in_shares = self._steth2shares(value)
        require(
            self._allowances.get(_from, 0).get(
                msg.sender, 0
            ) >= value_in_shares,
            'not enough allowance'
        )
        require(
            self._shares.get(_from, 0) >= value_in_shares,
            'not enough balance'
        )

        self._allowances[_from][msg.sender] -= value_in_shares
        self._shares[_from] -= value_in_shares
        self._shares[to] = self._shares.get(to, 0) + value_in_shares

        return self._allowances[_from][msg.sender]

    def approve(self, msg: MSG, spender: AddressT, value: int) -> bool:
        """Allow spender to withdraw from caller account."""
        value_in_shares = self._steth2shares(value)
        require(
            self._shares.get(msg.sender, 0) >= value_in_shares,
            'not enough balance'
        )

        caller_allowances = self._allowances.setdefault(msg.sender, {})
        caller_allowances[spender] = caller_allowances.get(
            spender, 0
        ) + value_in_shares

        return True

    def allowance(self, owner: AddressT, spender: AddressT) -> float:
        """Returns the amount which is allowed to withdraw from owner."""
        return self._allowances.get(owner, {}).get(spender, 0)

    def mint(self, user: AddressT, value: float) -> float:
        """Mint new tokens for user."""
        if value == 0:
            return self._shares.get(user, 0)
        if self._total_shares == 0:
            self._shares[user] = value
            self._total_shares += value
            self._total_eth += value

            return self._shares[user]

        value_in_shares = self._steth2shares(value)

        self._shares[user] = self._shares.get(user, 0) + value_in_shares
        self._total_shares += value_in_shares
        self._total_eth += value

        return self._shares[user]

    def burn(self, user: AddressT, value: float) -> float:
        """Burn value of tokens from user balance."""
        if value == 0:
            return self._shares.get(user, 0)
        value_in_shares = self._steth2shares(value)

        require(
            self._shares.get(user, 0) >= value_in_shares,
            'not enough balance'
        )

        self._shares[user] -= value_in_shares
        self._total_eth -= value
        self._total_shares -= value_in_shares

        return self._shares[user]

    def get_pooled_steth_by_shares(self, shares_amount: float) -> float:
        """Convert shares to steth."""
        return self._shares2steth(shares_amount)

    def get_shares_by_pooled_steth(self, steth_amount: float) -> float:
        """Convert steth to shares."""
        return self._steth2shares(steth_amount)


def stake_eth(msg: MSG, steth: StETH, value: int) -> float:
    """Stake ethereum and get StETH, return amount of minted shares."""
    return steth.mint(msg.sender, value)
