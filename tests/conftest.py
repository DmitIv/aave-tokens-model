import pytest

from aave_tokens_model.core.tokens.atoken import AToken
from aave_tokens_model.core.tokens.steth import StETH
from aave_tokens_model.core.tokens.vdebttoken import VDebtToken
from aave_tokens_model.core.utilities.types import MSG


@pytest.fixture(scope='module')
def steth() -> StETH:
    """Get steth"""
    return StETH()


@pytest.fixture(scope='module')
def debtsteth(steth) -> VDebtToken:
    """Get DebtStETH"""
    return VDebtToken(steth)


@pytest.fixture(scope='module')
def asteth(steth, debtsteth) -> AToken:
    """Get astETH"""
    return AToken(steth, debtsteth)


@pytest.fixture(scope='module')
def accounts():
    return [
        MSG(
            '0x' + str(sender).zfill(40), 10000000000
        )
        for sender in range(10)
    ]
