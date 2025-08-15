"""Reference data for international trading capabilities."""

from .forex_pairs import forex_manager, MAJOR_FOREX_PAIRS, SUPPORTED_CURRENCIES
from .exchange_info import exchange_manager, EXCHANGE_INFO

__all__ = [
    'forex_manager',
    'exchange_manager',
    'MAJOR_FOREX_PAIRS',
    'SUPPORTED_CURRENCIES',
    'EXCHANGE_INFO'
]
