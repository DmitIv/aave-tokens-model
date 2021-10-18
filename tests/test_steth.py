def test_mint(steth, fixed_stake_eth, accounts):
    a = accounts[0]
    b = accounts[1]
    c = accounts[2]

    assert fixed_stake_eth(a, 100) == 100
    assert fixed_stake_eth(b, 100) == 100

    assert steth.balance_of(a) == 100
    assert steth.balance_of(b) == 100

    previous_total_supply = steth.total_supply()
    assert steth.rebase_mul(2.0) == 2 * previous_total_supply

    assert steth.balance_of(a) == 200
    assert steth.balance_of(b) == 200

    assert fixed_stake_eth(c, 100) != 100
    assert steth.balance_of(c) == 100


def test_transfer(steth, fixed_stake_eth, accounts):
    d = accounts[3]
    e = accounts[4]

    fixed_stake_eth(d, 17)
    fixed_stake_eth(e, 17)

    assert steth.transfer(d, e, 17)
    assert steth.balance_of(e) == 34
