from uuid import uuid4

from .types import AddressT


def generate_address() -> AddressT:
    """Generate address as 20 bytes sequence."""
    return f'0x{uuid4().hex.zfill(40)}'
