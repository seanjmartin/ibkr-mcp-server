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
        
        # Symbol resolution cache with enhanced monitoring
        self.resolution_cache = {}
        self.cache_duration = 300  # 5 minutes for symbol resolution
        
        # PHASE 2 ADDITIONS: Cache statistics
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'invalidations': 0,
            'memory_usage': 0,
            'last_cleanup': datetime.now(timezone.utc),
            'total_requests': 0
        }
        
        # Cache configuration
        self.max_cache_size = 1000  # Maximum cache entries
        self.cache_cleanup_interval = 3600  # 1 hour cleanup cycle
        
        # Connection state tracking for cache invalidation
        self._last_connection_state = False
    
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
            qualified_raw = await self.ib.qualifyContractsAsync(*contracts)
            
            # Filter out None values from qualification results
            qualified = [contract for contract in qualified_raw if contract is not None]
            
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
        
        # Handle both string and list inputs for backward compatibility
        if isinstance(symbols, list):
            symbol_list = symbols
        else:
            symbol_list = symbols.split(',')
        
        for symbol_spec in symbol_list:
            if isinstance(symbol_spec, str):
                symbol_spec = symbol_spec.strip().upper()
            else:
                symbol_spec = str(symbol_spec).strip().upper()
            
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
            from ib_async import Stock, Forex, Index
            
            if spec['type'] == 'stock':
                contract = Stock(spec['symbol'], spec['exchange'], spec['currency'])
                # Ensure secType is set
                if not hasattr(contract, 'secType') or not contract.secType:
                    contract.secType = 'STK'
                return contract
            elif spec['type'] == 'forex':
                contract = Forex(spec['symbol'])
                # Ensure secType is set
                if not hasattr(contract, 'secType') or not contract.secType:
                    contract.secType = 'CASH'
                return contract
            elif spec['type'] == 'index':
                contract = Index(spec['symbol'], spec['exchange'], spec['currency'])
                # Ensure secType is set
                if not hasattr(contract, 'secType') or not contract.secType:
                    contract.secType = 'IND'
                return contract
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
    
    async def resolve_symbol(self, symbol: str, exchange: str = None, currency: str = None) -> Dict:
        """Resolve symbol with comprehensive information and validation via IBKR API.
        
        Returns live validated data from IBKR API or fails clearly if API unavailable.
        No database fallback - trading system requires live API connectivity.
        """
        try:
            symbol = symbol.upper().strip()
            
            # Check connection state changes
            self._check_connection_state_change()
            
            # Check cache first
            cache_key = f"{symbol}_{exchange}_{currency}"
            cached_result = self._get_cached_resolution(cache_key)
            if cached_result:
                return cached_result
            
            # Require IBKR API connection for symbol resolution
            if not self.ib or not self.ib.isConnected():
                raise ConnectionError("IBKR API connection required for symbol resolution. Cannot provide stale database data.")
            
            # Get initial symbol specifications from database for contract creation
            db_matches = self.symbol_db.resolve_symbol(symbol, exchange, currency)
            potential_specs = db_matches if db_matches else self._guess_symbol_info(symbol, exchange, currency)
            
            if not potential_specs:
                return {
                    "symbol": symbol,
                    "matches": [],
                    "resolution_method": "none",
                    "error": f"No symbol specifications found for {symbol}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Create contracts for API validation
            contracts_to_qualify = []
            for spec in potential_specs[:3]:  # Limit to top 3 candidates for performance
                try:
                    contract = self._create_contract_from_spec(spec)
                    if contract:
                        contracts_to_qualify.append((contract, spec))
                except Exception as e:
                    self.logger.warning(f"Failed to create contract for {spec}: {e}")
                    continue
            
            if not contracts_to_qualify:
                return {
                    "symbol": symbol,
                    "matches": [],
                    "resolution_method": "contract_creation_failed",
                    "error": f"Could not create valid contracts for {symbol}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Validate contracts with IBKR API with retry logic
            qualified = await self._qualify_contracts_with_retry([c[0] for c in contracts_to_qualify])
            
            if not qualified:
                return {
                    "symbol": symbol,
                    "matches": [],
                    "resolution_method": "none",
                    "error": f"Symbol {symbol} not found in IBKR database",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Format qualified contracts as matches
            validated_matches = []
            for i, qualified_contract in enumerate(qualified):
                if i < len(contracts_to_qualify):
                    original_spec = contracts_to_qualify[i][1]
                    validated_match = {
                        'symbol': qualified_contract.symbol,
                        'exchange': qualified_contract.exchange,
                        'currency': qualified_contract.currency,
                        'type': original_spec.get('type', 'stock'),
                        'name': getattr(qualified_contract, 'longName', '') or original_spec.get('name', ''),
                        'contract_id': qualified_contract.conId,
                        'primary': i == 0,  # First match is primary
                        'validated': True,
                        'country': original_spec.get('country', ''),
                        'isin': getattr(qualified_contract, 'isin', '') or original_spec.get('isin', '')
                    }
                    validated_matches.append(validated_match)
            
            # Build result with validated data
            result = {
                "symbol": symbol,
                "matches": validated_matches,
                "resolution_method": "api_validated",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Add exchange information for best match
            if validated_matches:
                best_match = validated_matches[0]
                result["exchange_info"] = {
                    "exchange": best_match['exchange'],
                    "currency": best_match['currency'],
                    "market_status": "open",  # Simplified for now
                    "validated": True
                }
            
            # Cache the API-validated result
            self._cache_resolution(cache_key, result)
            
            return result
            
        except ConnectionError:
            # Re-raise connection errors to maintain clear API requirement
            raise
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
    
    async def _qualify_contracts_with_retry(self, contracts: List[Contract], max_retries: int = 3) -> List[Contract]:
        """Qualify contracts with IBKR API with retry logic for transient failures."""
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                # Check connection before each attempt
                if not self.ib or not self.ib.isConnected():
                    raise ConnectionError("IBKR API connection lost")
                
                # Attempt to qualify contracts
                qualified_raw = await self.ib.qualifyContractsAsync(*contracts)
                qualified = [contract for contract in qualified_raw if contract is not None]
                
                self.logger.debug(f"Successfully qualified {len(qualified)}/{len(contracts)} contracts on attempt {attempt + 1}")
                return qualified
                
            except Exception as e:
                last_exception = e
                self.logger.warning(f"Contract qualification attempt {attempt + 1} failed: {e}")
                
                # Don't retry for certain types of errors
                if isinstance(e, ConnectionError) or "connection" in str(e).lower():
                    if attempt < max_retries - 1:
                        # Wait with exponential backoff before retry
                        wait_time = 2 ** attempt  # 1s, 2s, 4s
                        self.logger.info(f"Retrying contract qualification in {wait_time} seconds...")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        # Final attempt failed
                        break
                else:
                    # Non-connection error - don't retry
                    break
        
        # All retries exhausted
        self.logger.error(f"Contract qualification failed after {max_retries} attempts. Last error: {last_exception}")
        raise last_exception if last_exception else Exception("Contract qualification failed")
    
    def _cache_resolution(self, cache_key: str, result: Dict) -> None:
        """Cache symbol resolution result with statistics tracking."""
        # PHASE 2: Memory management - cleanup if needed
        if len(self.resolution_cache) >= self.max_cache_size:
            self._cleanup_old_cache_entries()
        
        self.resolution_cache[cache_key] = {
            'data': result,
            'timestamp': datetime.now(timezone.utc).timestamp(),
            'hit_count': 0  # Track popularity for LRU cleanup
        }
        
        # Update statistics
        self.cache_stats['memory_usage'] = len(self.resolution_cache)
        self.logger.debug(f"Cached resolution for {cache_key}")
    
    def _get_cached_resolution(self, cache_key: str) -> Optional[Dict]:
        """Get cached symbol resolution if still valid, with hit tracking."""
        self.cache_stats['total_requests'] += 1
        
        cache_entry = self.resolution_cache.get(cache_key)
        if not cache_entry:
            self.cache_stats['misses'] += 1
            return None
        
        # Check if cache is still valid
        if datetime.now(timezone.utc).timestamp() - cache_entry['timestamp'] > self.cache_duration:
            del self.resolution_cache[cache_key]
            self.cache_stats['invalidations'] += 1
            self.cache_stats['misses'] += 1
            return None
        
        # Cache hit - update statistics and popularity
        self.cache_stats['hits'] += 1
        cache_entry['hit_count'] = cache_entry.get('hit_count', 0) + 1
        
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
        self.cache_stats['invalidations'] += len(self.resolution_cache)
        self.cache_stats['memory_usage'] = 0
        self.logger.info("International symbol resolution cache cleared")
    
    def get_cache_statistics(self) -> Dict:
        """Get comprehensive cache performance statistics."""
        total_requests = self.cache_stats['total_requests']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_size': len(self.resolution_cache),
            'max_cache_size': self.max_cache_size,
            'memory_usage_pct': (len(self.resolution_cache) / self.max_cache_size * 100),
            'hit_rate_pct': round(hit_rate, 2),
            'total_hits': self.cache_stats['hits'],
            'total_misses': self.cache_stats['misses'],
            'total_requests': total_requests,
            'invalidations': self.cache_stats['invalidations'],
            'last_cleanup': self.cache_stats['last_cleanup'].isoformat(),
            'cache_duration_seconds': self.cache_duration
        }
    
    def _cleanup_old_cache_entries(self) -> None:
        """Remove old or least-used cache entries to manage memory."""
        current_time = datetime.now(timezone.utc).timestamp()
        entries_to_remove = []
        
        # Find expired entries
        for key, entry in self.resolution_cache.items():
            if current_time - entry['timestamp'] > self.cache_duration:
                entries_to_remove.append(key)
        
        # If still over capacity, remove least popular entries
        if len(self.resolution_cache) - len(entries_to_remove) >= self.max_cache_size:
            # Sort by hit count (ascending) to remove least popular first
            sorted_entries = sorted(
                [(k, v) for k, v in self.resolution_cache.items() if k not in entries_to_remove],
                key=lambda x: x[1].get('hit_count', 0)
            )
            
            # Remove oldest entries until under capacity
            target_size = self.max_cache_size * 0.8  # Leave 20% headroom
            entries_needed = len(self.resolution_cache) - len(entries_to_remove) - int(target_size)
            
            for i in range(min(entries_needed, len(sorted_entries))):
                entries_to_remove.append(sorted_entries[i][0])
        
        # Remove identified entries
        for key in entries_to_remove:
            if key in self.resolution_cache:
                del self.resolution_cache[key]
                self.cache_stats['invalidations'] += 1
        
        self.cache_stats['last_cleanup'] = datetime.now(timezone.utc)
        self.logger.info(f"Cache cleanup removed {len(entries_to_remove)} entries")
    
    def _check_connection_state_change(self) -> bool:
        """Check if connection state changed and invalidate cache if needed."""
        current_state = self.ib and self.ib.isConnected()
        
        if self._last_connection_state != current_state:
            if not current_state:  # Disconnected
                self.logger.warning("IBKR connection lost - clearing symbol resolution cache")
                self.clear_cache()
            else:  # Reconnected
                self.logger.info("IBKR connection restored")
            
            self._last_connection_state = current_state
            return True
        
        return False
