from typing import Optional

from aave_tokens_model.core.utilities.types import Revert


def require(
        condition: bool, description: Optional[str] = None
) -> None:
    """Revert execution if condition is false."""
    if description is None:
        description = 'require failed'

    if not condition:
        raise Revert(description)


NOT_ENOUGH_BALANCE = 'not enough balance'
