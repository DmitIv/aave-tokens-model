from aave_tokens_model.core.tokens.steth import stake_eth


def test_mint(steth, accounts):
    a = accounts[0]
    b = accounts[1]
    c = accounts[2]

    stake_eth(a, steth, 100)
    stake_eth(b, steth, 100)

    assert steth.balance_of(a.sender) == 100
    assert steth.balance_of(b.sender) == 100

    steth.rebase(steth.total_supply())

    assert steth.balance_of(a.sender) == 200
    assert steth.balance_of(b.sender) == 200

    stake_eth(c, steth, 100)

    assert steth.balance_of(c.sender) == 100
    assert steth.get_shares_by_pooled_steth(
        steth.balance_of(c.sender)
    ) != 100


def test_transfer(steth, accounts):
    d = accounts[3]
    e = accounts[4]

    stake_eth(d, steth, 17)
    stake_eth(e, steth, 17)

    steth.transfer(d, e.sender, 17)

    assert steth.balance_of(e.sender) == 34
