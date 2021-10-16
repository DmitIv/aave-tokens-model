from typing import Dict

from aave_tokens_model.core.tokens.erc20 import ERC20
from aave_tokens_model.core.utilities.restriction import require
from aave_tokens_model.core.utilities.types import AddressT, MSG


class AERC20(ERC20):
    def __init__(self):
        self._name: str = 'aaveERC20'
        self._total_amount: float = 0
        self._balances: Dict[AddressT, float] = {}
        self._allowances: Dict[AddressT, Dict[AddressT, float]] = {}

    @property
    def name(self) -> str:
        return self._name

    @property
    def symbol(self) -> str:
        return self._name

    def total_supply(self) -> float:
        """Get amount of token."""
        return self._total_amount

    def balance_of(self, user: AddressT) -> float:
        """Get the balance of user."""
        return self._balances.get(user, 0)

    def transfer(self, msg: MSG, to: AddressT, value: float) -> bool:
        """Transfer token from caller to the specific address."""
        if value == 0:
            return False

        require(
            self._balances.get(msg.sender, 0) >= value,
            'not enough balance'
        )

        self._balances[msg.sender] -= value
        self._balances[to] = self._balances.get(to, 0) + value

        return True

    def transfer_from(
            self, msg: MSG, _from: AddressT, to: AddressT, value: int
    ) -> float:
        """Transfer token on behalf of from to the address."""
        if value == 0:
            return self._allowances.get(_from, {}).get(msg.sender, 0)

        require(
            self._allowances.get(_from, 0).get(
                msg.sender, 0
            ) >= value,
            'not enough allowance'
        )
        require(
            self._balances.get(_from, 0) >= value,
            'not enough balance'
        )

        self._allowances[_from][msg.sender] -= value
        self._balances[_from] -= value
        self._balances[to] = self._balances.get(to, 0) + value

        return self._allowances[_from][msg.sender]

    def approve(self, msg: MSG, spender: AddressT, value: int) -> bool:
        """Allow spender to withdraw from caller account."""
        require(
            self._balances.get(msg.sender, 0) >= value,
            'not enough balance'
        )

        caller_allowances = self._allowances.setdefault(msg.sender, {})
        caller_allowances[spender] = caller_allowances.get(
            spender, 0
        ) + value

        return True

    def allowance(self, owner: AddressT, spender: AddressT) -> float:
        """Returns the amount which is allowed to withdraw from owner."""
        return self._allowances.get(owner, {}).get(spender, 0)

    def mint(self, user: AddressT, value: float) -> float:
        """Mint new tokens for user."""
        self._balances[user] = self._balances.get(user, 0) + value
        self._total_amount += value

        return self._balances[user]

    def burn(self, user: AddressT, value: float) -> float:
        """Burn value of tokens from user balance."""
        if value == 0:
            return self._balances.get(user, 0)
        require(
            self._balances[user] >= value,
            'not enough balance'
        )

        self._balances[user] -= value
        self._total_amount -= value

        return self._balances[user]
