from aave_tokens_model.core.tokens.atoken import (
    repay_steth, borrow_steth, deposit_steth
)
from aave_tokens_model.core.tokens.steth import stake_eth


def test_case_1(steth, asteth, debtsteth, accounts):
    """Deposit -> Borrow -> Rebase -> Repay -> Deposit -> Rebase"""
    a = accounts[0]
    b = accounts[1]
    c = accounts[2]

    stake_eth(a, steth, 1000)
    stake_eth(b, steth, 1000)

    deposit_steth(a.sender, steth, asteth, 500)
    deposit_steth(b.sender, steth, asteth, 500)

    borrow_steth(c, 500, steth, asteth, debtsteth)

    assert steth.balance_of(a.sender) == 500
    assert steth.balance_of(b.sender) == 500
    assert steth.balance_of(c.sender) == 500
    assert steth.balance_of(asteth.address) == 500

    assert asteth.balance_of(a.sender) == 500
    assert asteth.balance_of(b.sender) == 500

    assert debtsteth.balance_of(c.sender) == 500

    # Rebase x2
    steth.rebase(steth.total_supply())

    assert steth.balance_of(a.sender) == 1000
    assert steth.balance_of(b.sender) == 1000
    assert steth.balance_of(c.sender) == 1000
    assert steth.balance_of(asteth.address) == 1000

    assert 500 < asteth.balance_of(a.sender) < 1000
    assert 500 < asteth.balance_of(b.sender) < 1000

    a_before_repaying = asteth.balance_of(a.sender)
    b_before_repaying = asteth.balance_of(b.sender)

    assert debtsteth.balance_of(c.sender) == 500

    repay_steth(c, 500, steth, asteth, debtsteth)

    assert steth.balance_of(a.sender) == 1000
    assert steth.balance_of(b.sender) == 1000
    assert steth.balance_of(c.sender) == 500
    assert steth.balance_of(asteth.address) == 1500

    assert a_before_repaying <= asteth.balance_of(a.sender) < 1000
    assert b_before_repaying <= asteth.balance_of(b.sender) < 1000

    assert debtsteth.balance_of(c.sender) == 0

    d = accounts[3]

    stake_eth(d, steth, 100)
    deposit_steth(d.sender, steth, asteth, 50)

    assert steth.balance_of(a.sender) == 1000
    assert steth.balance_of(b.sender) == 1000
    assert steth.balance_of(c.sender) == 500
    assert steth.balance_of(asteth.address) == 1550

    assert a_before_repaying <= asteth.balance_of(a.sender) < 1000
    assert b_before_repaying <= asteth.balance_of(b.sender) < 1000
    assert steth.balance_of(d.sender) < asteth.balance_of(d.sender)

    # Rebase x2
    steth.rebase(steth.total_supply())

    assert steth.balance_of(a.sender) == 2000
    assert steth.balance_of(b.sender) == 2000
    assert steth.balance_of(c.sender) == 1000
    assert steth.balance_of(d.sender) == 100
    assert steth.balance_of(asteth.address) == 3100

    assert 1000 < asteth.balance_of(a.sender) < 2000
    assert 1000 < asteth.balance_of(b.sender) < 2000
    # !!
    assert steth.balance_of(d.sender) < asteth.balance_of(d.sender)
