from aave_tokens_model.core.tokens.atoken import deposit_steth
from aave_tokens_model.core.tokens.steth import stake_eth


def test_mint_rebase(steth, asteth, accounts):
    a = accounts[0]
    b = accounts[1]

    stake_eth(a, steth, 1000)
    stake_eth(b, steth, 1000)

    deposit_steth(a.sender, steth, asteth, 150)
    deposit_steth(b.sender, steth, asteth, 11)

    assert asteth.balance_of(a.sender) == 150
    assert asteth.balance_of(b.sender) == 11

    steth.rebase(steth.total_supply())

    assert asteth.balance_of(a.sender) == 300
    assert asteth.balance_of(b.sender) == 22


def test_transfer_rebase(steth, asteth, accounts):
    c = accounts[2]
    d = accounts[3]

    stake_eth(c, steth, 1000)
    stake_eth(d, steth, 1000)

    deposit_steth(c.sender, steth, asteth, 43)
    deposit_steth(d.sender, steth, asteth, 77)

    assert asteth.balance_of(c.sender) == 43
    assert asteth.balance_of(d.sender) == 77

    asteth.transfer(c, d.sender, 13)
    steth.rebase(steth.total_supply())

    assert asteth.balance_of(c.sender) == 60
    assert asteth.balance_of(d.sender) == 90 * 2
