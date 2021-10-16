from aave_tokens_model.core.tokens.atoken import borrow_steth, repay_steth
from aave_tokens_model.core.tokens.atoken import deposit_steth
from aave_tokens_model.core.tokens.steth import stake_eth


def test_borrow_repay(steth, asteth, debtsteth, accounts):
    a = accounts[0]
    b = accounts[1]

    stake_eth(a, steth, 1000)
    stake_eth(b, steth, 1000)

    deposit_steth(a.sender, steth, asteth, 1000)
    borrow_steth(b, 500, steth, asteth, debtsteth)

    assert steth.balance_of(a.sender) == 0
    assert asteth.balance_of(a.sender) == 1000
    assert steth.balance_of(asteth.address) == 500
    assert steth.balance_of(b.sender) == 1500
    assert debtsteth.balance_of(b.sender) == 500

    for _ in range(5):
        repay_steth(b, 100, steth, asteth, debtsteth)

    assert debtsteth.balance_of(b.sender) == 0
    assert asteth.balance_of(a.sender) == 1000
    assert steth.balance_of(asteth.address) == 1000
    assert steth.balance_of(b.sender) == 1000
