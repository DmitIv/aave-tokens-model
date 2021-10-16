from collections import namedtuple
from typing import Tuple
from uuid import uuid4

from aave_tokens_model.core.tokens.aerc20 import AERC20
from aave_tokens_model.core.tokens.erc20 import ERC20
from aave_tokens_model.core.tokens.steth import StETH
from aave_tokens_model.core.tokens.vdebttoken import VDebtToken
from aave_tokens_model.core.utilities.types import (
    AddressT, MSG
)


class AToken(ERC20):
    def __init__(
            self,
            steth: StETH,
            debtsteth: VDebtToken
    ):
        self._address = f'0x{uuid4().hex.zfill(40)}'
        self._name = 'astETH'
        self._underlaying_erc20 = AERC20()
        self._underlaying_steth = steth
        self._debtsteth = debtsteth

        self._total_shares: float = 0.0
        self._liq_index: float = 1.0

    def _borrowed_steth(self) -> Tuple[float, float]:
        """Get amounts of borrowed shares and borrowed steth."""
        return self._debtsteth.get_borrowed_state()

    _State = namedtuple(
        '_State', ['total_supply', 'balance_of']
    )

    def _mint_scaled(self, user: AddressT, amount: float) -> None:
        """Convert amount from total amounts to internal and mint it value."""
        internal_before = self._State(
            total_supply=self._underlaying_erc20.total_supply(),
            balance_of=self._underlaying_erc20.balance_of(user),
        )

        if internal_before.total_supply == 0:
            self._underlaying_erc20.mint(
                user,
                self._underlaying_steth.get_shares_by_pooled_steth(amount)
            )
            return

        scaled_before = self._State(
            total_supply=self._scaled_total_supply(),
            balance_of=self._scaled_balance_of(user)
        )
        other_before = scaled_before.total_supply - scaled_before.balance_of

        if other_before == 0:
            factor = (
                    internal_before.total_supply / scaled_before.total_supply
            )
            self._underlaying_erc20.mint(
                user,
                amount * factor
            )
            return

        scaled_after = self._State(
            total_supply=scaled_before.total_supply + amount,
            balance_of=scaled_before.balance_of + amount
        )

        a = internal_before.total_supply * scaled_after.balance_of
        b = scaled_after.total_supply * internal_before.balance_of
        amount = (a - b) / other_before
        self._underlaying_erc20.mint(user, amount)

    def _scaled_total_supply(self) -> float:
        """Get a total supply of aToken without compounded interest."""
        borrowed_shares, borrowed_steth = self._borrowed_steth()
        held_steth = self._underlaying_steth.get_pooled_steth_by_shares(
            self._total_shares - borrowed_shares
        )

        return held_steth + borrowed_steth

    def _scaled_balance_of(self, user: AddressT) -> float:
        """Get a balance of user without interest."""
        user_shares = self._underlaying_erc20.balance_of(user)
        scaled_total_supply = self._scaled_total_supply()
        return user_shares * scaled_total_supply / self._total_shares

    @property
    def name(self) -> str:
        """Get token name."""
        return self._name

    @property
    def symbol(self) -> str:
        """Get token symbol."""
        return self._name

    @property
    def liq_index(self) -> float:
        """Get current liquidity index."""
        return self._liq_index

    @liq_index.setter
    def liq_index(self, new_liq_index: float) -> None:
        """Set new liquidity index."""
        if new_liq_index < 0:
            raise ValueError('liquidity index should be a pos number.')
        self._liq_index = new_liq_index

    @property
    def address(self) -> AddressT:
        """Get address of contract."""
        return self._address

    def total_supply(self) -> float:
        """Get total supply of aToken (with interest)."""
        return self._scaled_total_supply() * self._liq_index

    def balance_of(self, user: AddressT) -> float:
        """Get balance of user (with interest)."""
        return self._scaled_balance_of(user) * self._liq_index

    def transfer(self, msg: MSG, to: AddressT, value: float) -> bool:
        """Transfer aToken between addresses."""
        scaled_value = value / self._liq_index
        total_supply_internal = self._underlaying_erc20.total_supply()
        scaled_total_supply = self._scaled_total_supply()
        transfer_amount_internal = (
                scaled_value * total_supply_internal / scaled_total_supply
        )
        return self._underlaying_erc20.transfer(
            msg, to, transfer_amount_internal
        )

    def mint(self, user: AddressT, value: float) -> float:
        """Mint new aToken for income stETH."""
        value_scaled = value / self._liq_index

        self._mint_scaled(user, value_scaled)
        self._total_shares += (
            self._underlaying_steth.get_shares_by_pooled_steth(
                value_scaled
            )
        )

        return self._underlaying_erc20.balance_of(user)

    def allowance(self, owner: AddressT, spender: AddressT) -> int:
        """Out of modeling."""
        raise NotImplementedError('out of modeling.')

    def approve(self, msg: MSG, spender: AddressT, value: int) -> bool:
        """Out of modeling."""
        raise NotImplementedError('out of modeling.')

    def transfer_from(
            self, msg: MSG, _from: AddressT, to: AddressT, value: int
    ) -> int:
        """Out of modeling."""
        raise NotImplementedError('out of modeling.')


def deposit_steth(user: AddressT, steth: StETH, asteth: AToken, value: float):
    """Deposit steth and mint equality amount of astETH for user."""
    steth.transfer(MSG(user, 0), asteth.address, value)
    asteth.mint(user, value)


def borrow_steth(
        msg: MSG, value: float,
        steth: StETH, asteth: AToken, debtsteth: VDebtToken
) -> float:
    """Borrow steth and mint debt tokens for user."""
    steth.transfer(MSG(asteth.address, 0), msg.sender, value)
    return debtsteth.mint(msg.sender, value)


def repay_steth(
        msg: MSG, value: float,
        steth: StETH, asteth: AToken, debtsteth: VDebtToken
) -> float:
    """Repay steth and burn debt tokens for user."""
    steth.transfer(msg, asteth.address, value)
    return debtsteth.burn(msg.sender, value)
