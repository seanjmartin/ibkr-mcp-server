"""International symbol database for global stock trading."""

from typing import Dict, List, Optional, Set
import logging


# International stock symbols with exchange and currency mapping
INTERNATIONAL_SYMBOLS = {
    # European Stocks - Netherlands (AEB/Euronext Amsterdam)
    'ASML': {
        'exchange': 'AEB',
        'currency': 'EUR',
        'name': 'ASML Holding NV',
        'country': 'Netherlands',
        'sector': 'Technology',
        'market_cap': 'Large',
        'isin': 'NL0010273215'
    },
    'UNA': {
        'exchange': 'AEB',
        'currency': 'EUR',
        'name': 'Unilever NV',
        'country': 'Netherlands',
        'sector': 'Consumer Goods',
        'market_cap': 'Large',
        'isin': 'NL0000009355'
    },
    
    # European Stocks - Germany (XETRA/Frankfurt)
    'SAP': {
        'exchange': 'XETRA',
        'currency': 'EUR',
        'name': 'SAP SE',
        'country': 'Germany',
        'sector': 'Technology',
        'market_cap': 'Large',
        'isin': 'DE0007164600'
    },
    'SIE': {
        'exchange': 'XETRA',
        'currency': 'EUR',
        'name': 'Siemens AG',
        'country': 'Germany',
        'sector': 'Industrial',
        'market_cap': 'Large',
        'isin': 'DE0007236101'
    },
    
    # European Stocks - UK (LSE/London)
    'VOD': {
        'exchange': 'LSE',
        'currency': 'GBP',
        'name': 'Vodafone Group PLC',
        'country': 'United Kingdom',
        'sector': 'Telecommunications',
        'market_cap': 'Large',
        'isin': 'GB00BH4HKS39'
    },
    'BP': {
        'exchange': 'LSE',
        'currency': 'GBP',
        'name': 'BP PLC',
        'country': 'United Kingdom',
        'sector': 'Energy',
        'market_cap': 'Large',
        'isin': 'GB0007980591'
    },
    
    # European Stocks - France (SBF/Euronext Paris)
    'MC': {
        'exchange': 'SBF',
        'currency': 'EUR',
        'name': 'LVMH Moet Hennessy Louis Vuitton SE',
        'country': 'France',
        'sector': 'Consumer Goods',
        'market_cap': 'Large',
        'isin': 'FR0000121014'
    },
    'OR': {
        'exchange': 'SBF',
        'currency': 'EUR',
        'name': "L'Oreal SA",
        'country': 'France',
        'sector': 'Consumer Goods',
        'market_cap': 'Large',
        'isin': 'FR0000120321'
    },
    
    # European Stocks - Switzerland (SWX/SIX Swiss)
    'NESN': {
        'exchange': 'SWX',
        'currency': 'CHF',
        'name': 'Nestle SA',
        'country': 'Switzerland',
        'sector': 'Consumer Goods',
        'market_cap': 'Large',
        'isin': 'CH0038863350'
    },
    'ROG': {
        'exchange': 'SWX',
        'currency': 'CHF',
        'name': 'Roche Holding AG',
        'country': 'Switzerland',
        'sector': 'Healthcare',
        'market_cap': 'Large',
        'isin': 'CH0012032048'
    },
    
    # European Stocks - Denmark (KFX/Nasdaq Copenhagen)
    'NOVO-B': {
        'exchange': 'KFX',
        'currency': 'DKK',
        'name': 'Novo Nordisk A/S',
        'country': 'Denmark',
        'sector': 'Healthcare',
        'market_cap': 'Large',
        'isin': 'DK0060534915'
    },
    
    # Asian Stocks - Japan (TSE/Tokyo)
    '7203': {
        'exchange': 'TSE',
        'currency': 'JPY',
        'name': 'Toyota Motor Corp',
        'country': 'Japan',
        'sector': 'Automotive',
        'market_cap': 'Large',
        'isin': 'JP3633400001'
    },
    '6758': {
        'exchange': 'TSE',
        'currency': 'JPY',
        'name': 'Sony Group Corp',
        'country': 'Japan',
        'sector': 'Technology',
        'market_cap': 'Large',
        'isin': 'JP3435000009'
    },
    '9984': {
        'exchange': 'TSE',
        'currency': 'JPY',
        'name': 'SoftBank Group Corp',
        'country': 'Japan',
        'sector': 'Technology',
        'market_cap': 'Large',
        'isin': 'JP3436100006'
    },
    
    # Asian Stocks - Hong Kong (SEHK/Hong Kong)
    '00700': {
        'exchange': 'SEHK',
        'currency': 'HKD',
        'name': 'Tencent Holdings Ltd',
        'country': 'China',
        'sector': 'Technology',
        'market_cap': 'Large',
        'isin': 'KYG875721634'
    },
    '00941': {
        'exchange': 'SEHK',
        'currency': 'HKD',
        'name': 'China Mobile Ltd',
        'country': 'China',
        'sector': 'Telecommunications',
        'market_cap': 'Large',
        'isin': 'HK0000545716'
    },
    '2330': {
        'exchange': 'SEHK',
        'currency': 'HKD',
        'name': 'Taiwan Semiconductor Manufacturing',
        'country': 'Taiwan',
        'sector': 'Technology',
        'market_cap': 'Large',
        'isin': 'TW0002330008'
    },
    
    # Asian Stocks - Korea (KSE/Korea Exchange)
    '005930': {
        'exchange': 'KSE',
        'currency': 'KRW',
        'name': 'Samsung Electronics Co Ltd',
        'country': 'South Korea',
        'sector': 'Technology',
        'market_cap': 'Large',
        'isin': 'KR7005930003'
    },
    
    # Asian Stocks - Australia (ASX/Australian Securities)
    'CBA': {
        'exchange': 'ASX',
        'currency': 'AUD',
        'name': 'Commonwealth Bank of Australia',
        'country': 'Australia',
        'sector': 'Financial',
        'market_cap': 'Large',
        'isin': 'AU000000CBA7'
    },
    'BHP': {
        'exchange': 'ASX',
        'currency': 'AUD',
        'name': 'BHP Group Ltd',
        'country': 'Australia',
        'sector': 'Materials',
        'market_cap': 'Large',
        'isin': 'AU000000BHP4'
    },
    'CSL': {
        'exchange': 'ASX',
        'currency': 'AUD',
        'name': 'CSL Ltd',
        'country': 'Australia',
        'sector': 'Healthcare',
        'market_cap': 'Large',
        'isin': 'AU000000CSL8'
    }
}


class InternationalSymbolDatabase:
    """Manages international symbol resolution and validation."""
    
    def __init__(self):
        self.symbols = INTERNATIONAL_SYMBOLS
        self.logger = logging.getLogger(__name__)
        self._build_indices()
    
    def _build_indices(self):
        """Build lookup indices for efficient searching."""
        self.by_exchange = {}
        self.by_currency = {}
        self.by_country = {}
        self.by_sector = {}
        
        for symbol, info in self.symbols.items():
            # Index by exchange
            exchange = info['exchange']
            if exchange not in self.by_exchange:
                self.by_exchange[exchange] = []
            self.by_exchange[exchange].append(symbol)
            
            # Index by currency
            currency = info['currency']
            if currency not in self.by_currency:
                self.by_currency[currency] = []
            self.by_currency[currency].append(symbol)
            
            # Index by country
            country = info['country']
            if country not in self.by_country:
                self.by_country[country] = []
            self.by_country[country].append(symbol)
            
            # Index by sector
            sector = info['sector'] 
            if sector not in self.by_sector:
                self.by_sector[sector] = []
            self.by_sector[sector].append(symbol)
    
    def lookup_symbol(self, symbol: str) -> Optional[Dict]:
        """Look up comprehensive symbol information."""
        return self.symbols.get(symbol.upper())
    
    def resolve_symbol(self, symbol: str, exchange: str = None, currency: str = None) -> List[Dict]:
        """Resolve symbol with optional filters."""
        symbol = symbol.upper()
        matches = []
        
        if symbol in self.symbols:
            info = self.symbols[symbol]
            
            # Apply filters
            if exchange and info['exchange'] != exchange.upper():
                return matches
            if currency and info['currency'] != currency.upper():
                return matches
            
            matches.append({
                'symbol': symbol,
                'exchange': info['exchange'],
                'currency': info['currency'],
                'name': info['name'],
                'country': info['country'],
                'sector': info['sector'],
                'market_cap': info['market_cap'],
                'isin': info['isin'],
                'primary': True
            })
        
        return matches
    
    def get_symbols_by_exchange(self, exchange: str) -> List[str]:
        """Get all symbols for a specific exchange."""
        return self.by_exchange.get(exchange.upper(), [])
    
    def get_symbols_by_currency(self, currency: str) -> List[str]:
        """Get all symbols for a specific currency."""
        return self.by_currency.get(currency.upper(), [])
    
    def get_symbols_by_country(self, country: str) -> List[str]:
        """Get all symbols for a specific country."""
        return self.by_country.get(country, [])
    
    def get_symbols_by_sector(self, sector: str) -> List[str]:
        """Get all symbols for a specific sector."""
        return self.by_sector.get(sector, [])
    
    def validate_symbol(self, symbol: str, exchange: str, currency: str) -> bool:
        """Validate symbol exists with specified exchange and currency."""
        info = self.lookup_symbol(symbol)
        if not info:
            return False
        
        return (info['exchange'] == exchange.upper() and 
                info['currency'] == currency.upper())
    
    def get_supported_exchanges(self) -> Set[str]:
        """Get set of all supported exchanges."""
        return set(self.by_exchange.keys())
    
    def get_supported_currencies(self) -> Set[str]:
        """Get set of all supported currencies."""
        return set(self.by_currency.keys())
    
    def get_supported_countries(self) -> Set[str]:
        """Get set of all supported countries."""
        return set(self.by_country.keys())
    
    def search_symbols(self, search_term: str) -> List[Dict]:
        """Search symbols by name or symbol."""
        search_term = search_term.lower()
        matches = []
        
        for symbol, info in self.symbols.items():
            if (search_term in symbol.lower() or 
                search_term in info['name'].lower()):
                matches.append({
                    'symbol': symbol,
                    'name': info['name'],
                    'exchange': info['exchange'],
                    'currency': info['currency'],
                    'country': info['country']
                })
        
        return matches


# Global symbol database instance
international_db = InternationalSymbolDatabase()
