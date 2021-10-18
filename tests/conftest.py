from functools import partial

import pytest

from aave_tokens_model.core.utilities import generate_address
from aave_tokens_model.core.tokens import (
    AStETH, VDebtStETH, StETH,
    deposit_steth, borrow_steth, repay_steth, stake_eth
)


@pytest.fixture(scope='module')
def steth() -> StETH:
    """Get steth"""
    return StETH()


@pytest.fixture(scope='module')
def fixed_stake_eth(steth):
    """Get stake function with fixed steth contract."""
    return partial(stake_eth, steth)


@pytest.fixture(scope='module')
def debtsteth(steth) -> VDebtStETH:
    """Get DebtStETH"""
    return VDebtStETH(steth)


@pytest.fixture(scope='module')
def asteth(steth, debtsteth) -> AStETH:
    """Get astETH"""
    return AStETH(steth, debtsteth)


@pytest.fixture(scope='module')
def fixed_deposit_steth(steth, debtsteth, asteth):
    return partial(deposit_steth, steth, asteth)


@pytest.fixture(scope='module')
def fixed_borrow_steth(steth, debtsteth, asteth):
    """Get borrow function with fixed steth and debsteth."""
    return partial(borrow_steth, steth, debtsteth, asteth)


@pytest.fixture(scope='module')
def fixed_repay_steth(steth, debtsteth, asteth):
    """Get repay function with fixed steth and debsteth."""
    return partial(repay_steth, steth, debtsteth, asteth)


@pytest.fixture(scope='module')
def accounts():
    """Get 10 pseudo-accounts"""
    return [
        generate_address()
        for _ in range(10)
    ]
