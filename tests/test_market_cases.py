def test_case_1(
        steth, asteth, debtsteth,
        fixed_stake_eth, fixed_deposit_steth,
        fixed_borrow_steth, fixed_repay_steth,
        accounts
):
    """Deposit -> Borrow -> Rebase -> Repay -> Deposit -> Rebase"""
    a = accounts[0]
    b = accounts[1]
    c = accounts[2]

    assert fixed_stake_eth(a, 1000) == 1000
    assert fixed_stake_eth(b, 1000) == 1000

    assert fixed_deposit_steth(a, 500) == 500
    assert fixed_deposit_steth(b, 500) == 500

    assert fixed_borrow_steth(c, 500) == 500

    assert steth.balance_of(a) == 500
    assert steth.balance_of(b) == 500
    assert steth.balance_of(c) == 500
    assert steth.balance_of(asteth.address) == 500

    assert asteth.balance_of(a) == 500
    assert asteth.balance_of(b) == 500

    assert debtsteth.balance_of(c) == 500

    # Rebase x2
    assert steth.total_supply() * 2 == steth.rebase_mul(2.0)

    assert steth.balance_of(a) == 1000
    assert steth.balance_of(b) == 1000
    assert steth.balance_of(c) == 1000
    assert steth.balance_of(asteth.address) == 1000

    fair_sharing = 500 / 2
    expected_asteth_balance = 1000 - fair_sharing
    assert asteth.balance_of(a) == expected_asteth_balance
    assert asteth.balance_of(b) == expected_asteth_balance

    assert debtsteth.balance_of(c) == 500

    # Repay
    assert fixed_repay_steth(c, 500) == 0

    assert steth.balance_of(a) == 1000
    assert steth.balance_of(b) == 1000
    assert steth.balance_of(c) == 500
    assert steth.balance_of(asteth.address) == 1500

    expected_asteth_balance = asteth.total_supply() / 2
    assert asteth.balance_of(a) == expected_asteth_balance
    assert asteth.balance_of(b) == expected_asteth_balance

    assert debtsteth.balance_of(c) == 0

    d = accounts[3]

    fixed_stake_eth(d, 100)
    fixed_deposit_steth(d, 50)

    assert steth.balance_of(a) == 1000
    assert steth.balance_of(b) == 1000
    assert steth.balance_of(c) == 500
    assert steth.balance_of(asteth.address) == 1550

    assert asteth.balance_of(a) == expected_asteth_balance
    assert asteth.balance_of(b) == expected_asteth_balance
    assert steth.balance_of(d) == asteth.balance_of(d)

    # Rebase x2
    steth.rebase_mul(2.0)

    assert steth.balance_of(a) == 2000
    assert steth.balance_of(b) == 2000
    assert steth.balance_of(c) == 1000
    assert steth.balance_of(d) == 100
    assert steth.balance_of(asteth.address) == 3100

    assert asteth.balance_of(a) == expected_asteth_balance * 2 < 2000
    assert asteth.balance_of(b) == expected_asteth_balance * 2 < 2000
    assert steth.balance_of(d) == asteth.balance_of(d)
