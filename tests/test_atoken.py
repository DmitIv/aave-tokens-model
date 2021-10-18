from aave_tokens_model.core.tokens.atoken import deposit_steth
from aave_tokens_model.core.tokens.steth import stake_eth


def test_mint_rebase(
        steth, asteth,
        fixed_stake_eth, fixed_deposit_steth,
        accounts
):
    a = accounts[0]
    b = accounts[1]

    assert fixed_stake_eth(a, 1000) == 1000
    assert fixed_stake_eth(b, 1000) == 1000

    assert fixed_deposit_steth(a, 150) == 150
    assert fixed_deposit_steth(b, 11) == 11

    assert asteth.balance_of(a) == 150
    assert asteth.balance_of(b) == 11

    assert steth.total_supply() * 2 == steth.rebase_mul(2.0)

    assert asteth.balance_of(a) == 300
    assert asteth.balance_of(b) == 22


def test_transfer_rebase(
        steth, asteth,
        fixed_stake_eth, fixed_deposit_steth,
        accounts
):
    c = accounts[2]
    d = accounts[3]

    fixed_stake_eth(c, 1000)
    fixed_stake_eth(d, 1000)
    fixed_deposit_steth(c, 43)
    fixed_deposit_steth(d, 77)
    assert asteth.balance_of(c) == 43
    assert asteth.balance_of(d) == 77

    asteth.transfer(c, d, 13)
    assert steth.total_supply() * 2 == steth.rebase_mul(2.0)

    assert asteth.balance_of(c) == 60
    assert asteth.balance_of(d) == 90 * 2
