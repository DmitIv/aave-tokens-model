from abc import ABC, abstractmethod

from aave_tokens_model.core.utilities.types import (
    AddressT, MSG
)


class ERC20(ABC):
    @abstractmethod
    def total_supply(self) -> int:
        """Get total amount of minted tokens."""
        pass

    @abstractmethod
    def balance_of(self, user: AddressT) -> int:
        """Get amount of tokens held by the specific user."""
        pass

    @abstractmethod
    def transfer(self, msg: MSG, to: AddressT, value: int) -> bool:
        """
        Transfer an amount from caller to the specific address.

        Return an indicator of transfer success.
        """
        pass

    @abstractmethod
    def transfer_from(
            self, msg: MSG, _from: AddressT, to: AddressT, value: int
    ) -> int:
        """Transfer tokens on behalf of from to the specific address."""
        pass

    @abstractmethod
    def approve(self, msg: MSG, spender: AddressT, value: int) -> bool:
        """Allow spender to withdraw from caller account up to value."""
        pass

    @abstractmethod
    def allowance(self, owner: AddressT, spender: AddressT) -> int:
        """Returns the amount which is allowed to withdraw from owner."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Get full name of token."""
        pass

    @property
    @abstractmethod
    def symbol(self) -> str:
        """Get symbol of token."""
        pass
