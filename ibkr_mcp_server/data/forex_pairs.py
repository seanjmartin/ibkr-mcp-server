"""Forex pair definitions and metadata for IBKR MCP Server."""

from typing import Dict, List, Optional, Set
import logging


# Major forex pairs with comprehensive metadata
MAJOR_FOREX_PAIRS = {
    # Major pairs (USD-based)
    'EURUSD': {
        'base': 'EUR',
        'quote': 'USD', 
        'name': 'Euro/US Dollar',
        'pip_value': 0.0001,
        'min_size': 25000,
        'typical_spread': 0.1,
        'category': 'major',
        'session_hours': '24/5'
    },
    'GBPUSD': {
        'base': 'GBP',
        'quote': 'USD',
        'name': 'British Pound/US Dollar',
        'pip_value': 0.0001,
        'min_size': 25000,
        'typical_spread': 0.2,
        'category': 'major',
        'session_hours': '24/5'
    },
    'USDJPY': {
        'base': 'USD',
        'quote': 'JPY',
        'name': 'US Dollar/Japanese Yen',
        'pip_value': 0.01,
        'min_size': 25000,
        'typical_spread': 0.1,
        'category': 'major',
        'session_hours': '24/5'
    },
    'USDCHF': {
        'base': 'USD',
        'quote': 'CHF',
        'name': 'US Dollar/Swiss Franc',
        'pip_value': 0.0001,
        'min_size': 25000,
        'typical_spread': 0.2,
        'category': 'major',
        'session_hours': '24/5'
    },
    'AUDUSD': {
        'base': 'AUD',
        'quote': 'USD',
        'name': 'Australian Dollar/US Dollar',
        'pip_value': 0.0001,
        'min_size': 25000,
        'typical_spread': 0.2,
        'category': 'major',
        'session_hours': '24/5'
    },
    'USDCAD': {
        'base': 'USD',
        'quote': 'CAD',
        'name': 'US Dollar/Canadian Dollar',
        'pip_value': 0.0001,
        'min_size': 25000,
        'typical_spread': 0.2,
        'category': 'major',
        'session_hours': '24/5'
    },
    'NZDUSD': {
        'base': 'NZD',
        'quote': 'USD',
        'name': 'New Zealand Dollar/US Dollar',
        'pip_value': 0.0001,
        'min_size': 25000,
        'typical_spread': 0.3,
        'category': 'major',
        'session_hours': '24/5'
    },

    # Cross pairs (non-USD)
    'EURGBP': {
        'base': 'EUR',
        'quote': 'GBP',
        'name': 'Euro/British Pound',
        'pip_value': 0.0001,
        'min_size': 25000,
        'typical_spread': 0.3,
        'category': 'cross',
        'session_hours': '24/5'
    },
    'EURJPY': {
        'base': 'EUR',
        'quote': 'JPY',
        'name': 'Euro/Japanese Yen',
        'pip_value': 0.01,
        'min_size': 25000,
        'typical_spread': 0.2,
        'category': 'cross',
        'session_hours': '24/5'
    },
    'GBPJPY': {
        'base': 'GBP',
        'quote': 'JPY',
        'name': 'British Pound/Japanese Yen',
        'pip_value': 0.01,
        'min_size': 25000,
        'typical_spread': 0.3,
        'category': 'cross',
        'session_hours': '24/5'
    },
    'CHFJPY': {
        'base': 'CHF',
        'quote': 'JPY',
        'name': 'Swiss Franc/Japanese Yen',
        'pip_value': 0.01,
        'min_size': 25000,
        'typical_spread': 0.4,
        'category': 'cross',
        'session_hours': '24/5'
    },
    'EURCHF': {
        'base': 'EUR',
        'quote': 'CHF',
        'name': 'Euro/Swiss Franc',
        'pip_value': 0.0001,
        'min_size': 25000,
        'typical_spread': 0.3,
        'category': 'cross',
        'session_hours': '24/5'
    },
    'AUDJPY': {
        'base': 'AUD',
        'quote': 'JPY',
        'name': 'Australian Dollar/Japanese Yen',
        'pip_value': 0.01,
        'min_size': 25000,
        'typical_spread': 0.3,
        'category': 'cross',
        'session_hours': '24/5'
    },
    'CADJPY': {
        'base': 'CAD',
        'quote': 'JPY',
        'name': 'Canadian Dollar/Japanese Yen',
        'pip_value': 0.01,
        'min_size': 25000,
        'typical_spread': 0.4,
        'category': 'cross',
        'session_hours': '24/5'
    },
    'NZDJPY': {
        'base': 'NZD',
        'quote': 'JPY',
        'name': 'New Zealand Dollar/Japanese Yen',
        'pip_value': 0.01,
        'min_size': 25000,
        'typical_spread': 0.4,
        'category': 'cross',
        'session_hours': '24/5'
    },
    'EURAUD': {
        'base': 'EUR',
        'quote': 'AUD',
        'name': 'Euro/Australian Dollar',
        'pip_value': 0.0001,
        'min_size': 25000,
        'typical_spread': 0.4,
        'category': 'cross',
        'session_hours': '24/5'
    },
    'EURNZD': {
        'base': 'EUR',
        'quote': 'NZD',
        'name': 'Euro/New Zealand Dollar',
        'pip_value': 0.0001,
        'min_size': 25000,
        'typical_spread': 0.5,
        'category': 'cross',
        'session_hours': '24/5'
    },
    'GBPAUD': {
        'base': 'GBP',
        'quote': 'AUD',
        'name': 'British Pound/Australian Dollar',
        'pip_value': 0.0001,
        'min_size': 25000,
        'typical_spread': 0.5,
        'category': 'cross',
        'session_hours': '24/5'
    },
    'GBPNZD': {
        'base': 'GBP',
        'quote': 'NZD',
        'name': 'British Pound/New Zealand Dollar',
        'pip_value': 0.0001,
        'min_size': 25000,
        'typical_spread': 0.6,
        'category': 'cross',
        'session_hours': '24/5'
    },
    'AUDCAD': {
        'base': 'AUD',
        'quote': 'CAD',
        'name': 'Australian Dollar/Canadian Dollar',
        'pip_value': 0.0001,
        'min_size': 25000,
        'typical_spread': 0.4,
        'category': 'cross',
        'session_hours': '24/5'
    },
    'AUDNZD': {
        'base': 'AUD',
        'quote': 'NZD',
        'name': 'Australian Dollar/New Zealand Dollar',
        'pip_value': 0.0001,
        'min_size': 25000,
        'typical_spread': 0.4,
        'category': 'cross',
        'session_hours': '24/5'
    }
}

# Supported currencies
SUPPORTED_CURRENCIES = {
    'USD', 'EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'NZD', 'HKD', 'KRW', 'DKK', 'SEK', 'NOK'
}


class ForexPairManager:
    """Manages forex pair information and validation."""
    
    def __init__(self):
        self.pairs = MAJOR_FOREX_PAIRS
        self.supported_currencies = SUPPORTED_CURRENCIES
        self.logger = logging.getLogger(__name__)
    
    def get_pair_info(self, pair: str) -> Optional[Dict]:
        """Get comprehensive information about a forex pair."""
        return self.pairs.get(pair.upper())
    
    def is_valid_pair(self, pair: str) -> bool:
        """Check if forex pair is supported."""
        return pair.upper() in self.pairs
    
    def get_base_currency(self, pair: str) -> Optional[str]:
        """Get base currency of a forex pair."""
        info = self.get_pair_info(pair)
        return info['base'] if info else None
    
    def get_quote_currency(self, pair: str) -> Optional[str]:
        """Get quote currency of a forex pair.""" 
        info = self.get_pair_info(pair)
        return info['quote'] if info else None
    
    def get_inverse_pair(self, pair: str) -> Optional[str]:
        """Get inverse pair if it exists."""
        info = self.get_pair_info(pair)
        if not info:
            return None
        
        inverse = f"{info['quote']}{info['base']}"
        return inverse if self.is_valid_pair(inverse) else None
    
    def calculate_pip_value(self, pair: str, position_size: float) -> float:
        """Calculate pip value for a position."""
        info = self.get_pair_info(pair)
        if not info:
            return 0.0
        
        pip_value = info['pip_value']
        return pip_value * position_size
    
    def get_pairs_by_currency(self, currency: str) -> List[str]:
        """Get all pairs containing a specific currency."""
        currency = currency.upper()
        pairs = []
        
        for pair, info in self.pairs.items():
            if info['base'] == currency or info['quote'] == currency:
                pairs.append(pair)
        
        return pairs
    
    def get_pairs_by_category(self, category: str) -> List[str]:
        """Get pairs by category (major, cross, exotic)."""
        return [pair for pair, info in self.pairs.items() 
                if info.get('category') == category.lower()]
    
    def validate_currency_pair_format(self, pair: str) -> bool:
        """Validate forex pair format (6 characters, valid currencies)."""
        if not pair or len(pair) != 6:
            return False
        
        base = pair[:3].upper()
        quote = pair[3:].upper()
        
        return (base in self.supported_currencies and 
                quote in self.supported_currencies and
                base != quote)
    
    def get_minimum_size(self, pair: str) -> int:
        """Get minimum position size for a forex pair."""
        info = self.get_pair_info(pair)
        return info.get('min_size', 25000) if info else 25000
    
    def get_all_supported_pairs(self) -> List[str]:
        """Get list of all supported forex pairs."""
        return list(self.pairs.keys())


# Global forex manager instance
forex_manager = ForexPairManager()
