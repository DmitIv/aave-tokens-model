def test_borrow_repay(
        steth, asteth, debtsteth,
        fixed_stake_eth, fixed_borrow_steth, fixed_repay_steth,
        fixed_deposit_steth,
        accounts
):
    a = accounts[0]
    b = accounts[1]

    assert fixed_stake_eth(a, 1000) == 1000
    assert fixed_stake_eth(b, 1000) == 1000

    assert fixed_deposit_steth(a, 1000) == 1000
    assert fixed_borrow_steth(b, 500) == 500

    assert steth.balance_of(a) == 0
    assert asteth.balance_of(a) == 1000
    assert steth.balance_of(asteth.address) == 500
    assert steth.balance_of(b) == 1500
    assert debtsteth.balance_of(b) == 500

    for i in range(1, 6):
        assert fixed_repay_steth(b, 100) == (500 - 100 * i)

    assert debtsteth.balance_of(b) == 0
    assert asteth.balance_of(a) == 1000
    assert steth.balance_of(asteth.address) == 1000
    assert steth.balance_of(b) == 1000
