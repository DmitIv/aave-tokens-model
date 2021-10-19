from functools import partial
from typing import Optional

from aave_tokens_model.core.tokens import (
    get_asteth, get_steth, get_debtsteth,
    deposit_steth, stake_eth, borrow_steth, repay_steth
)
from aave_tokens_model.core.utilities import generate_address

stake = partial(stake_eth, get_steth())
deposit = partial(deposit_steth, get_steth(), get_asteth())
borrow = partial(borrow_steth, get_steth(), get_debtsteth(), get_asteth())
repay = partial(repay_steth, get_steth(), get_debtsteth(), get_asteth())


def rebase(factor: float) -> float:
    return get_steth().rebase_mul(factor)


class Account:
    def __init__(self, steth_amount: Optional[int] = None):
        if steth_amount is None:
            steth_amount = 0
        self._address = generate_address()

        if steth_amount != 0:
            stake(self._address, steth_amount)
            assert get_steth().balance_of(self._address) == steth_amount

    @property
    def address(self) -> str:
        return self._address


def main():
    get_steth().switch_up_logger(True)
    get_asteth().switch_up_logger(True)
    get_debtsteth().switch_up_logger(True)

    get_new_acc = Account

    a = get_new_acc(steth_amount=1000)
    b = get_new_acc(steth_amount=1000)
    c = get_new_acc()

    all_accounts = {'a': a, 'b': b, 'c': c}

    def _acc_info(name: str, acc: Account) -> str:
        address = acc.address
        return (
            f'Address of {name} = {address}; '
            f'stETH balance = {get_steth().balance_of(address)}; '
            f'aStETH balance = {get_asteth().balance_of(address)}; '
            f'debtStETH balance = {get_debtsteth().balance_of(address)}'
        )

    def _all_accounts_info() -> str:
        return '\n'.join((
            _acc_info(name, acc) for name, acc in all_accounts.items()
        ))

    def _balance_of_asteth() -> str:
        address = get_asteth().address
        return (
            f'Address of aStETH = {address}; '
            f'stETH balance = {get_steth().balance_of(address)}; '
            f'total supply = {get_asteth().total_supply()}; '
            f'total shares = {get_asteth()._total_shares}'  # noqa
        )

    def _block_header(name: str) -> str:
        name = f'  {name}  '
        name = name.ljust(70, '=')
        name = name.rjust(110, '=')

        return name

    def _block_end() -> str:
        return '=' * 110

    def _single_block(name: str) -> str:
        elements = [
            _block_header(name),
            _all_accounts_info(),
            _balance_of_asteth(),
            _block_end()
        ]

        return '\n'.join(elements)

    # Initial state
    print(_single_block('Initial state'))

    # Deposit #1
    deposit(a.address, 500)
    deposit(b.address, 500)
    print(_single_block('Deposit #1'))

    # Borrow #1
    borrow(c.address, 500)
    print(_single_block('Borrow #1'))

    # Rebase #1; x2
    rebase(2.0)
    print(_single_block('Rebase #1'))

    # Repay #1
    repay(c.address, 500)
    print(_single_block('Repay #1'))

    # Rebase #2
    rebase(2.0)
    print(_single_block('Rebase #2'))

    # Deposit #2
    d = get_new_acc(steth_amount=1000)
    all_accounts['d'] = d
    deposit(d.address, 500)
    print(f'Sum of shares: {sum(get_asteth()._balances.values())}')  # noqa
    print(_single_block('Deposit #2'))

    # Rebase #3
    rebase(2.0)
    print(f'Internal balances: {repr(get_asteth()._balances)}')
    print(_single_block('Rebase #3'))

    # Borrow #2
    borrow(c.address, 500)
    print(_single_block('Borrow #2'))

    # Rebase #4
    rebase(2.0)
    print(_single_block('Rebase #4'))

    # Repay #2
    repay(c.address, 500)
    print(_single_block('Repay #2'))

    if __name__ == '__main__':
        main()
