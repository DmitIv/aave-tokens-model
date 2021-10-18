from collections import namedtuple
from typing import Tuple
from functools import lru_cache

from loguru import logger

from aave_tokens_model.core.tokens.erc20 import ERC20
from aave_tokens_model.core.tokens.steth import StETH, get_steth
from aave_tokens_model.core.tokens.vdebtsteth import VDebtStETH, get_debtsteth
from aave_tokens_model.core.utilities.types import AddressT


class AStETH(ERC20):
    def __init__(self, steth: StETH, debtsteth: VDebtStETH):
        super().__init__('aToken implementation for stETH', 'AStETH')

        self._steth = steth
        self._debtsteth = debtsteth

        self._total_shares: float = 0.0
        self._liq_index: float = 1.0

    def _print_log(self, action, *args, **kwargs) -> None:
        borrowed_shares, borrowed_steth = self._borrowed_steth()
        logger.debug(
            f'total shares = {self._total_shares}; '
            f'total supply = {self.total_supply()}; '
            f'borrowed shares = {borrowed_shares}; '
            f'borrowed steth = {borrowed_steth}'
        )
        super()._print_log(action, *args, **kwargs)

    @property
    def liq_index(self) -> float:
        """Get current liquidity index."""
        return self._liq_index

    @ERC20._log
    def _increase_liq_index(self, shift: float) -> float:
        self._liq_index += shift
        return self._liq_index

    @ERC20._log
    def increase_liq_index_mul(self, factor: float) -> float:
        """Increase liq index by factor."""
        previous_liq_index = self._liq_index
        new_liq_index = previous_liq_index * factor
        return self._increase_liq_index(new_liq_index - previous_liq_index)

    @ERC20._log
    def increase_liq_index_sft(self, shift: float) -> float:
        """Increase liq index by adding the shift."""
        return self._increase_liq_index(shift)

    def _borrowed_steth(self) -> Tuple[float, float]:
        """Get amounts of borrowed shares and borrowed steth."""
        return self._debtsteth.get_borrowed_state()

    _State = namedtuple(
        '_State', ['total_supply', 'balance_of']
    )

    @ERC20._log
    def _mint_scaled(self, user: AddressT, amount: float) -> float:
        """Convert amount from total amounts to internal and mint it value."""
        internal_before = self._State(
            total_supply=super().total_supply(),
            balance_of=super().balance_of(user),
        )

        if internal_before.total_supply == 0:
            amount = self._steth.get_shares_by_pooled_steth(amount)
            return super().mint(user, amount)

        scaled_before = self._State(
            total_supply=self._scaled_total_supply(),
            balance_of=self._scaled_balance_of(user)
        )
        other_before = scaled_before.total_supply - scaled_before.balance_of

        if other_before == 0:
            c = internal_before.total_supply / scaled_before.total_supply
            amount *= c
            return super().mint(user, amount)

        scaled_after = self._State(
            total_supply=scaled_before.total_supply + amount,
            balance_of=scaled_before.balance_of + amount
        )

        a = internal_before.total_supply * scaled_after.balance_of
        b = scaled_after.total_supply * internal_before.balance_of
        amount = (a - b) / other_before
        return super().mint(user, amount)

    def _scaled_total_supply(self) -> float:
        """Get a total supply of aToken without compounded interest."""
        borrowed_shares, borrowed_steth = self._borrowed_steth()
        held_shares = self._total_shares - borrowed_shares
        held_steth = self._steth.get_pooled_steth_by_shares(held_shares)
        scaled_total_supply = held_steth + borrowed_steth

        return scaled_total_supply

    def _scaled_balance_of(self, user: AddressT) -> float:
        """Get a balance of user without interest."""
        user_shares = super().balance_of(user)
        if user_shares == 0:
            return 0
        scaled_total_supply = self._scaled_total_supply()
        c = scaled_total_supply / super().total_supply()
        scaled_balance_of = user_shares * c

        return scaled_balance_of

    def _scaled_value(self, value: float) -> float:
        return value / self._liq_index

    def total_supply(self) -> float:
        """Get total supply of aToken (with interest)."""
        return self._scaled_total_supply() * self._liq_index

    def balance_of(self, user: AddressT) -> float:
        """Get balance of user (with interest)."""
        return self._scaled_balance_of(user) * self._liq_index

    @ERC20._log
    def transfer(self, user: AddressT, to: AddressT, value: float) -> bool:
        """Transfer astETH between addresses."""
        scaled_value = self._scaled_value(value)
        total_supply_internal = super().total_supply()
        scaled_total_supply = self._scaled_total_supply()
        c = total_supply_internal / scaled_total_supply
        transfer_amount_internal = scaled_value * c

        return super().transfer(user, to, transfer_amount_internal)

    @ERC20._log
    def mint(self, user: AddressT, value: float) -> float:
        """Mint new astETH for income stETH."""
        scaled_value = self._scaled_value(value)
        minted = self._mint_scaled(user, scaled_value)
        new_shares = self._steth.get_shares_by_pooled_steth(scaled_value)
        self._total_shares += new_shares

        return minted


@lru_cache(1)
def get_asteth() -> AStETH:
    """Get cached instance of AStETH"""
    return AStETH(get_steth(), get_debtsteth())


def deposit_steth(
        steth: StETH, asteth: AStETH, user: AddressT, value: float
) -> float:
    """Deposit steth and mint equality amount of astETH for user."""
    steth.transfer(user, asteth.address, value)
    return asteth.mint(user, value)


def borrow_steth(
        steth: StETH, debtsteth: VDebtStETH, asteth: AStETH,
        user: AddressT, value: float
) -> float:
    """Borrow steth and mint debt tokens for user."""
    steth.transfer(asteth.address, user, value)
    return debtsteth.mint(user, value)


def repay_steth(
        steth: StETH, debtsteth: VDebtStETH, asteth: AStETH,
        user: AddressT, value: float,
) -> float:
    """Repay steth and burn debt tokens for user."""
    steth.transfer(user, asteth.address, value)
    return debtsteth.burn(user, value)
