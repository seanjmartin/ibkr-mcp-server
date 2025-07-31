"""International market trading management for IBKR MCP Server."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from ib_async import IB, Stock, Index, Contract

from ..data import international_db, exchange_manager
from ..utils import safe_float, safe_int, ValidationError
from ..enhanced_validators import InternationalValidator


class InternationalManager:
    """Manages international market operations with symbol resolution and validation."""
    
    def __init__(self, ib_client: IB):
        self.ib = ib_client
        self.symbol_db = international_db
        self.exchange_mgr = exchange_manager
        self.validator = InternationalValidator()
        self.logger = logging.getLogger(__name__)
        
        # Symbol resolution cache
        self.resolution_cache = {}
        self.cache_duration = 300  # 5 minutes for symbol resolution
    
    async def get_international_market_data(self, symbols: str, auto_detect: bool = True) -> List[Dict]:
        """Get market data for international stocks with auto-detection."""
        try:
            if not self.ib or not self.ib.isConnected():
                raise ConnectionError("Not connected to IBKR")
            
            # Parse symbol specifications
            symbol_specs = self._parse_international_symbols(symbols, auto_detect)
            
            if not symbol_specs:
                return []
            
            # Create contracts
            contracts_with_specs = []
            for spec in symbol_specs:
                try:
                    contract = self._create_contract_from_spec(spec)
                    if contract:
                        contracts_with_specs.append((contract, spec))
                except Exception as e:
                    self.logger.warning(f"Failed to create contract for {spec}: {e}")
                    continue
            
            if not contracts_with_specs:
                raise ValidationError("No valid contracts could be created")
            
            # Qualify contracts
            contracts = [c[0] for c in contracts_with_specs]
            qualified = await self.ib.qualifyContractsAsync(*contracts)
            
            if not qualified:
                raise ValidationError("Could not qualify any international contracts")
            
            # Get market data
            tickers = await self.ib.reqTickersAsync(*qualified)
            
            # Format results
            results = []
            for i, ticker in enumerate(tickers):
                if i < len(contracts_with_specs):
                    original_spec = contracts_with_specs[i][1]
                    result = self._format_international_ticker(ticker, original_spec)
                    results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"International market data request failed: {e}")
            raise
    
    def _parse_international_symbols(self, symbols: str, auto_detect: bool) -> List[Dict]:
        """Parse international symbol specifications with auto-detection."""
        results = []
        
        for symbol_spec in symbols.split(','):
            symbol_spec = symbol_spec.strip().upper()
            
            if not symbol_spec:
                continue
            
            if '.' in symbol_spec:
                # Explicit format: SYMBOL.EXCHANGE.CURRENCY
                parts = symbol_spec.split('.')
                spec = {
                    'symbol': parts[0],
                    'exchange': parts[1] if len(parts) > 1 else 'SMART',
                    'currency': parts[2] if len(parts) > 2 else 'USD',
                    'type': 'stock',
                    'source': 'explicit'
                }
            elif auto_detect:
                # Try auto-detection from database
                symbol_info = self.symbol_db.lookup_symbol(symbol_spec)
                if symbol_info:
                    spec = {
                        'symbol': symbol_spec,
                        'exchange': symbol_info['exchange'],
                        'currency': symbol_info['currency'],
                        'type': 'stock',
                        'name': symbol_info['name'],
                        'country': symbol_info['country'],
                        'sector': symbol_info['sector'],
                        'source': 'database'
                    }
                else:
                    # Check if it might be a forex pair
                    from ..data import forex_manager
                    if forex_manager.is_valid_pair(symbol_spec):
                        spec = {
                            'symbol': symbol_spec,
                            'exchange': 'IDEALPRO',
                            'currency': None,
                            'type': 'forex',
                            'source': 'forex_detection'
                        }
                    else:
                        # Default to US stock
                        spec = {
                            'symbol': symbol_spec,
                            'exchange': 'SMART',
                            'currency': 'USD',
                            'type': 'stock',
                            'source': 'default_us'
                        }
            else:
                # No auto-detection, default to US stock
                spec = {
                    'symbol': symbol_spec,
                    'exchange': 'SMART',
                    'currency': 'USD',
                    'type': 'stock',
                    'source': 'no_autodetect'
                }
            
            results.append(spec)
        
        return results
    
    def _create_contract_from_spec(self, spec: Dict) -> Optional[Contract]:
        """Create IBKR contract from symbol specification."""
        try:
            if spec['type'] == 'stock':
                return Stock(spec['symbol'], spec['exchange'], spec['currency'])
            elif spec['type'] == 'forex':
                from ib_async import Forex
                return Forex(spec['symbol'])
            elif spec['type'] == 'index':
                return Index(spec['symbol'], spec['exchange'], spec['currency'])
            else:
                self.logger.warning(f"Unknown contract type: {spec['type']}")
                return None
        except Exception as e:
            self.logger.error(f"Failed to create contract from spec {spec}: {e}")
            return None
    
    def _format_international_ticker(self, ticker, original_spec: Dict) -> Dict:
        """Format international ticker data into standardized response."""
        contract = ticker.contract
        
        # Get market status
        market_status = "unknown"
        if contract.exchange:
            market_status = "open" if self.exchange_mgr.is_market_open(contract.exchange) else "closed"
        
        # Get exchange info
        exchange_info = self.exchange_mgr.get_exchange_info(contract.exchange)
        
        result = {
            "symbol": contract.symbol,
            "exchange": contract.exchange,
            "currency": contract.currency,
            "name": original_spec.get('name', ''),
            "country": original_spec.get('country', exchange_info.get('country', '') if exchange_info else ''),
            "sector": original_spec.get('sector', ''),
            "contract_type": original_spec.get('type', 'stock'),
            "source": original_spec.get('source', 'unknown'),
            "last": safe_float(ticker.last),
            "bid": safe_float(ticker.bid),
            "ask": safe_float(ticker.ask),
            "close": safe_float(ticker.close),
            "high": safe_float(ticker.high),
            "low": safe_float(ticker.low),
            "volume": safe_int(ticker.volume),
            "contract_id": contract.conId,
            "market_status": market_status,
            "exchange_timezone": exchange_info.get('timezone', '') if exchange_info else '',
            "settlement": exchange_info.get('settlement', '') if exchange_info else '',
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return result
    
    def resolve_symbol(self, symbol: str, exchange: str = None, currency: str = None) -> Dict:
        """Resolve symbol with comprehensive information and validation."""
        try:
            symbol = symbol.upper().strip()
            
            # Check cache first
            cache_key = f"{symbol}_{exchange}_{currency}"
            cached_result = self._get_cached_resolution(cache_key)
            if cached_result:
                return cached_result
            
            # Try database lookup
            matches = self.symbol_db.resolve_symbol(symbol, exchange, currency)
            
            result = {
                "symbol": symbol,
                "matches": matches,
                "resolution_method": "database" if matches else "none",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # If no database matches, try intelligent guessing
            if not matches:
                guessed_matches = self._guess_symbol_info(symbol, exchange, currency)
                if guessed_matches:
                    result["matches"] = guessed_matches
                    result["resolution_method"] = "guessed"
            
            # Add additional information
            if matches or result.get("matches"):
                best_match = (matches or result["matches"])[0]
                exchange_info = self.exchange_mgr.get_exchange_info(best_match['exchange'])
                if exchange_info:
                    result["exchange_info"] = {
                        "name": exchange_info['name'],
                        "country": exchange_info['country'],
                        "timezone": exchange_info['timezone'],
                        "trading_hours": exchange_info.get('trading_hours', {}),
                        "settlement": exchange_info.get('settlement', ''),
                        "market_open": self.exchange_mgr.is_market_open(best_match['exchange'])
                    }
            
            # Cache the result
            self._cache_resolution(cache_key, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Symbol resolution failed for {symbol}: {e}")
            return {
                "symbol": symbol,
                "matches": [],
                "resolution_method": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def _guess_symbol_info(self, symbol: str, exchange: str = None, currency: str = None) -> List[Dict]:
        """Attempt to guess symbol information based on patterns."""
        guesses = []
        
        # If exchange and currency provided, use them
        if exchange and currency:
            if self.exchange_mgr.validate_currency_for_exchange(exchange, currency):
                guesses.append({
                    'symbol': symbol,
                    'exchange': exchange.upper(),
                    'currency': currency.upper(),
                    'name': f"{symbol} (guessed)",
                    'country': self.exchange_mgr.get_exchange_info(exchange.upper()).get('country', ''),
                    'sector': 'Unknown',
                    'market_cap': 'Unknown',
                    'primary': True
                })
        
        # Try common exchange patterns based on symbol format
        if symbol.isdigit():
            # Numeric symbols - likely Asian markets
            if len(symbol) == 4:
                # Could be Japanese stock
                guesses.append({
                    'symbol': symbol,
                    'exchange': 'TSE',
                    'currency': 'JPY',
                    'name': f"{symbol} (guessed Japanese stock)",
                    'country': 'Japan',
                    'sector': 'Unknown',
                    'primary': False
                })
            elif len(symbol) == 5:
                # Could be Hong Kong stock
                guesses.append({
                    'symbol': symbol.zfill(5),  # Pad with leading zeros
                    'exchange': 'SEHK',
                    'currency': 'HKD',
                    'name': f"{symbol} (guessed Hong Kong stock)",
                    'country': 'Hong Kong',
                    'sector': 'Unknown',
                    'primary': False
                })
        
        return guesses
    
    def _cache_resolution(self, cache_key: str, result: Dict) -> None:
        """Cache symbol resolution result."""
        self.resolution_cache[cache_key] = {
            'data': result,
            'timestamp': datetime.now(timezone.utc).timestamp()
        }
    
    def _get_cached_resolution(self, cache_key: str) -> Optional[Dict]:
        """Get cached symbol resolution if still valid."""
        cache_entry = self.resolution_cache.get(cache_key)
        if not cache_entry:
            return None
        
        # Check if cache is still valid
        if datetime.now(timezone.utc).timestamp() - cache_entry['timestamp'] > self.cache_duration:
            del self.resolution_cache[cache_key]
            return None
        
        return cache_entry['data']
    
    def get_supported_exchanges(self) -> List[Dict]:
        """Get list of supported international exchanges with details."""
        exchanges = []
        
        for exchange_code in self.exchange_mgr.get_supported_exchanges():
            info = self.exchange_mgr.get_exchange_info(exchange_code)
            if info:
                exchanges.append({
                    'code': exchange_code,
                    'name': info['name'],
                    'country': info['country'],
                    'currency': info['currency'],
                    'timezone': info['timezone'],
                    'settlement': info.get('settlement', ''),
                    'market_open': self.exchange_mgr.is_market_open(exchange_code)
                })
        
        return exchanges
    
    def get_market_status_summary(self) -> Dict:
        """Get market open/closed status for all supported exchanges."""
        return self.exchange_mgr.get_market_status_summary()
    
    def validate_trading_hours(self, exchange: str) -> Dict:
        """Validate if market is open and get trading hours info."""
        exchange_info = self.exchange_mgr.get_exchange_info(exchange)
        if not exchange_info:
            return {
                'valid': False,
                'error': f'Unknown exchange: {exchange}'
            }
        
        is_open = self.exchange_mgr.is_market_open(exchange)
        
        return {
            'valid': True,
            'exchange': exchange,
            'market_open': is_open,
            'timezone': exchange_info['timezone'],
            'trading_hours': exchange_info.get('trading_hours', {}),
            'has_lunch_break': exchange_info.get('has_lunch_break', False),
            'settlement': exchange_info.get('settlement', ''),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def clear_cache(self) -> None:
        """Clear symbol resolution cache."""
        self.resolution_cache.clear()
        self.logger.info("International symbol resolution cache cleared")
