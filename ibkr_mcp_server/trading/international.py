"""International market trading management for IBKR MCP Server."""

import asyncio
import difflib
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple

from ib_async import IB, Stock, Index, Contract

from ..data import exchange_manager
from ..utils import safe_float, safe_int, ValidationError
from ..enhanced_validators import InternationalValidator


class InternationalManager:
    """Manages international market operations with symbol resolution and validation."""
    
    def __init__(self, ib_client: IB):
        self.ib = ib_client
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
        
        # PHASE 4.2 ADDITIONS: API call count tracking
        self.api_call_stats = {
            'req_contract_details_calls': 0,
            'req_matching_symbols_calls': 0,
            'total_api_calls': 0,
            'last_api_call': None,
            'api_calls_per_hour': [],
            'last_hour_calls': 0
        }
        
        # PHASE 4.2 ADDITIONS: Fuzzy search accuracy metrics
        self.fuzzy_search_stats = {
            'fuzzy_searches_attempted': 0,
            'fuzzy_searches_successful': 0,
            'fuzzy_accuracy_rate': 0.0,
            'fuzzy_avg_confidence': 0.0,
            'fuzzy_matches_found': [],
            'fuzzy_search_patterns': {}
        }
        
        # PHASE 4.3 ADDITIONS: Rate limiting for fuzzy search
        self.rate_limiting = {
            'last_fuzzy_search': None,
            'fuzzy_search_degraded': False,
            'api_calls_this_hour': 0,
            'api_rate_limit_start': datetime.now(timezone.utc)
        }
        
        # Cache configuration
        self.max_cache_size = 1000  # Maximum cache entries
        self.cache_cleanup_interval = 3600  # 1 hour cleanup cycle
        
        # Connection state tracking for cache invalidation
        self._last_connection_state = False
    
    async def get_international_market_data(self, symbols: str, auto_detect: bool = True) -> List[Dict]:
        """Get market data for international stocks with auto-detection and delayed data fallback."""
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
            
            # Try to get market data with enhanced error handling and delayed data fallback
            tickers = await self._get_market_data_with_fallback(qualified)
            
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
    
    async def _get_market_data_with_fallback(self, qualified_contracts):
        """Get market data with fallback to delayed data on subscription errors."""
        import asyncio
        
        try:
            # First attempt: Try to get real-time market data
            tickers = await self.ib.reqTickersAsync(*qualified_contracts)
            
            # Check if we received valid price data
            has_valid_data = any(
                hasattr(ticker, 'last') and ticker.last and ticker.last > 0 
                for ticker in tickers
            )
            
            if has_valid_data:
                self.logger.info(f"Successfully retrieved real-time market data for {len(tickers)} symbols")
                return tickers
            else:
                self.logger.warning("Real-time market data returned zero prices, attempting delayed data fallback")
                
        except Exception as e:
            error_msg = str(e).lower()
            if "10089" in error_msg or "subscription" in error_msg or "market data" in error_msg:
                self.logger.warning(f"Market data subscription error detected: {e}")
                self.logger.info("Attempting to request delayed market data as fallback")
            else:
                # Re-raise non-subscription related errors
                raise
        
        # Fallback: Try to request delayed market data
        try:
            # Switch to delayed market data mode (market data type 3 = delayed)
            for contract in qualified_contracts:
                self.ib.reqMarketDataType(3)  # 3 = delayed frozen data
                
            # Wait a moment for the market data type to be set
            await asyncio.sleep(0.5)
            
            # Request tickers again with delayed data mode
            delayed_tickers = await self.ib.reqTickersAsync(*qualified_contracts)
            
            # Check if delayed data has better results
            has_delayed_data = any(
                hasattr(ticker, 'last') and ticker.last and ticker.last > 0 
                for ticker in delayed_tickers
            )
            
            if has_delayed_data:
                self.logger.info(f"Successfully retrieved delayed market data for {len(delayed_tickers)} symbols")
                # Add data type indicator to the tickers
                for ticker in delayed_tickers:
                    ticker._data_type = "delayed"
                return delayed_tickers
            else:
                self.logger.warning("Both real-time and delayed data returned zero prices")
                
        except Exception as delayed_error:
            self.logger.error(f"Delayed market data request also failed: {delayed_error}")
        
        # Final fallback: Return the original tickers with metadata about the issue
        if 'tickers' in locals():
            for ticker in tickers:
                ticker._data_type = "unavailable"
                ticker._data_issue = "Market data subscription required for live prices"
            return tickers
        else:
            # If we can't get any tickers, create placeholder ones
            placeholder_tickers = []
            for contract in qualified_contracts:
                # Create a minimal ticker object with contract info but no prices
                class PlaceholderTicker:
                    def __init__(self, contract):
                        self.contract = contract
                        self.last = 0.0
                        self.bid = 0.0
                        self.ask = 0.0
                        self.close = 0.0
                        self.high = 0.0
                        self.low = 0.0
                        self.volume = 0
                        self._data_type = "unavailable"
                        self._data_issue = "Market data subscription required"
                
                placeholder_tickers.append(PlaceholderTicker(contract))
            
            return placeholder_tickers
    
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
                    # Default to US stock with SMART routing
                    spec = {
                        'symbol': symbol_spec,
                        'exchange': 'SMART',
                        'currency': 'USD',
                        'type': 'stock',
                        'source': 'smart_routing'
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
        
        # Add diagnostic information for zero price issue debugging
        # Helper function to safely serialize datetime objects and other non-serializable types
        def safe_serialize(obj):
            if obj is None:
                return None
            if hasattr(obj, 'isoformat'):  # datetime objects
                return obj.isoformat()
            if hasattr(obj, '__dict__'):  # Complex objects - convert to string
                return str(obj)
            return obj
        
        raw_price_data = {
            "raw_last": safe_serialize(ticker.last),
            "raw_bid": safe_serialize(ticker.bid),
            "raw_ask": safe_serialize(ticker.ask),
            "raw_close": safe_serialize(ticker.close),
            "raw_high": safe_serialize(ticker.high),
            "raw_low": safe_serialize(ticker.low),
            "raw_volume": safe_serialize(ticker.volume),
            "raw_last_type": type(ticker.last).__name__,
            "raw_bid_type": type(ticker.bid).__name__,
            "market_data_type": ticker.marketDataType if hasattr(ticker, 'marketDataType') else 'unknown',
            "time": safe_serialize(ticker.time) if hasattr(ticker, 'time') else None,
            "halted": ticker.halted if hasattr(ticker, 'halted') else None,
            "delayed": ticker.delayed if hasattr(ticker, 'delayed') else None
        }
        
        # Determine data availability status
        data_status = "real-time"
        data_message = None
        
        if hasattr(ticker, '_data_type'):
            data_status = ticker._data_type
            if hasattr(ticker, '_data_issue'):
                data_message = ticker._data_issue
        elif hasattr(ticker, 'delayed') and ticker.delayed:
            data_status = "delayed"
        
        # Check if we have zero price data and provide explanation
        has_price_data = (safe_float(ticker.last) > 0 or 
                         safe_float(ticker.bid) > 0 or 
                         safe_float(ticker.ask) > 0)
        
        if not has_price_data:
            data_status = "unavailable"
            if not data_message:
                data_message = "Market data subscription required for live prices. " \
                             "Paper trading accounts may have limited real-time data access. " \
                             "Consider enabling delayed data in IB Gateway or upgrading to live account with market data subscriptions."
        
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
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data_status": data_status,
            "data_message": data_message,
            "has_price_data": has_price_data,
            "debug_raw_data": raw_price_data  # Temporary diagnostic data
        }
        
        # Log diagnostic information for troubleshooting
        self.logger.info(f"Market data debug for {contract.symbol}: {raw_price_data}")
        
        return result
    
    async def resolve_symbol(
        self, 
        symbol: str, 
        exchange: str = None, 
        currency: str = None,
        sec_type: str = "STK",
        fuzzy_search: bool = True,
        include_alternatives: bool = False,
        max_results: int = 5,
        prefer_native_exchange: bool = False
    ) -> Dict:
        """
        Unified symbol resolution for all exchanges and security types.
        
        Args:
            symbol: Symbol, company name, CUSIP, ISIN, or FIGI
            exchange: Specific exchange (None = auto-detect via SMART)
            currency: Target currency (None = auto-detect)
            sec_type: Security type (STK, OPT, FUT, etc.)
            fuzzy_search: Enable company name and partial symbol matching
            include_alternatives: Return alternative identifiers (CUSIP, ISIN, etc.)
            max_results: Maximum number of results to return (1-16)
        
        Returns:
            {
                "symbol": "AAPL",  # Original input symbol for backwards compatibility
                "matches": [
                    {
                        "symbol": "AAPL",
                        "name": "Apple Inc.",
                        "conid": 265598,
                        "exchange": "SMART", 
                        "primary_exchange": "NASDAQ",
                        "currency": "USD",
                        "sec_type": "STK",
                        "country": "United States",
                        "isin": "US0378331005",
                        "cusip": "037833100",
                        "trading_hours": "09:30-16:00 EST",
                        "confidence": 1.0
                    }
                ],
                "cache_info": {
                    "cache_hit": False,
                    "cache_key": "aapl_smart_usd_stk"
                },
                "resolution_method": "exact_symbol|fuzzy_search|alternative_id"
            }
        """
        try:
            original_symbol = symbol
            symbol = symbol.upper().strip()
            
            # Check connection state changes
            self._check_connection_state_change()
            
            # Enhanced cache key with new parameters including prefer_native_exchange
            cache_key = f"{symbol}_{exchange}_{currency}_{sec_type}_{max_results}_{prefer_native_exchange}"
            cached_result = self._get_cached_resolution(cache_key)
            if cached_result:
                cached_result["cache_info"] = {"cache_hit": True, "cache_key": cache_key}
                # Add symbol field for backwards compatibility if not present
                if "symbol" not in cached_result:
                    cached_result["symbol"] = original_symbol
                return cached_result
            
            # Require IBKR API connection for symbol resolution
            if not self.ib or not self.ib.isConnected():
                raise ConnectionError("IBKR API connection required for symbol resolution. Cannot provide stale database data.")
            
            # Determine resolution strategy based on input pattern
            resolution_method = "exact_symbol"
            matches = []
            
            if self._is_exact_symbol(original_symbol):
                # Direct symbol lookup
                matches = await self._resolve_exact_symbol(symbol, exchange, currency, sec_type)
                resolution_method = "exact_symbol"
                
            elif self._is_alternative_id(original_symbol):
                # CUSIP/ISIN/ConID lookup
                matches = await self._resolve_alternative_id(symbol, exchange, currency, sec_type)
                resolution_method = "alternative_id"
                
            elif fuzzy_search and self._looks_like_company_name(original_symbol):
                # Fuzzy search for company names
                matches = await self._resolve_fuzzy_search(original_symbol, exchange, currency, sec_type)
                resolution_method = "fuzzy_search"
                
            elif fuzzy_search:
                # If fuzzy_search=True is explicitly requested, try fuzzy search even if it doesn't look like a company name
                # This handles cases like "Apple" that could be company names but don't meet typical patterns
                try:
                    matches = await self._resolve_fuzzy_search(original_symbol, exchange, currency, sec_type)
                    if matches:
                        resolution_method = "fuzzy_search"
                    else:
                        # If fuzzy search fails, fall back to exact symbol
                        matches = await self._resolve_exact_symbol(symbol, exchange, currency, sec_type)
                        resolution_method = "exact_symbol"
                except Exception:
                    # If fuzzy search fails, fall back to exact symbol
                    matches = await self._resolve_exact_symbol(symbol, exchange, currency, sec_type)
                    resolution_method = "exact_symbol"
                
            else:
                # Fall back to exact symbol if fuzzy search disabled
                matches = await self._resolve_exact_symbol(symbol, exchange, currency, sec_type)
                resolution_method = "exact_symbol"
            
            # If no matches found and original resolution method failed, update method to 'none'
            if not matches:
                resolution_method = "none"
            
            # Apply native exchange preference if requested
            if prefer_native_exchange and matches and not exchange:
                matches = await self._apply_native_exchange_preference(matches, symbol)
            
            # Calculate confidence scores for matches
            for match in matches:
                match["confidence"] = self._calculate_confidence_score(match, original_symbol, exchange or "SMART")
                if include_alternatives:
                    # Add alternative identifiers if requested
                    await self._add_alternative_identifiers(match)
            
            # Sort by confidence score (highest first)
            matches.sort(key=lambda x: x.get("confidence", 0), reverse=True)
            
            # Limit results to max_results (1-16)
            max_results = max(1, min(16, max_results))  # Clamp between 1-16
            matches = matches[:max_results]
            
            # Build result
            result = {
                "symbol": original_symbol,  # Add symbol field for backwards compatibility
                "matches": matches,
                "resolution_method": resolution_method,
                "query_info": {
                    "original_query": original_symbol,
                    "fuzzy_search_used": fuzzy_search and (self._looks_like_company_name(original_symbol) or fuzzy_search),
                    "total_matches": len(matches)
                },
                "cache_info": {
                    "cache_hit": False,
                    "cache_key": cache_key
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Add exchange information for best match (backwards compatibility)
            if matches:
                best_match = matches[0]
                result["exchange_info"] = {
                    "exchange": best_match.get('exchange', ''),
                    "currency": best_match.get('currency', ''),
                    "validated": True
                }
            
            # Cache the result
            self._cache_resolution(cache_key, result)
            
            return result
            
        except ConnectionError:
            # Re-raise connection errors to maintain clear API requirement
            raise
        except Exception as e:
            self.logger.error(f"Symbol resolution failed for {original_symbol}: {e}")
            return {
                "symbol": original_symbol,  # Add symbol field for backwards compatibility
                "matches": [],
                "resolution_method": "error",
                "query_info": {
                    "original_query": original_symbol,
                    "fuzzy_search_used": False,
                    "total_matches": 0
                },
                "cache_info": {
                    "cache_hit": False,
                    "cache_key": cache_key if 'cache_key' in locals() else f"{symbol}_error"
                },
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    

    
    def _is_exact_symbol(self, input_str: str) -> bool:
        """Detect if input looks like stock symbol."""
        # Allow symbols with dots (e.g., BRK.A, BRK.B) and alphanumeric symbols (e.g., 7203)
        if len(input_str) > 10:  # Too long for a symbol
            return False
            
        # Standard symbols: all uppercase letters, possibly with dots
        if input_str.isupper() and all(c.isalpha() or c == '.' for c in input_str):
            return True
            
        # Numeric symbols (e.g., Japanese stocks like 7203)
        if input_str.isdigit() and len(input_str) <= 6:
            return True
            
        # Mixed alphanumeric (e.g., some European symbols)
        if input_str.isupper() and input_str.isalnum() and len(input_str) <= 6:
            return True
            
        return False
    
    def _looks_like_company_name(self, input_str: str) -> bool:
        """Detect if input looks like company name."""
        # Allow company names like "Apple", "Tesla", "Microsoft"
        # Criteria: length >= 3, has lowercase letters or spaces, not all uppercase (unless has space)
        if len(input_str) < 3:
            return False
        
        has_space = ' ' in input_str
        has_lowercase = any(c.islower() for c in input_str)
        is_all_uppercase = input_str.isupper()
        
        # Company name patterns:
        # 1. Has spaces (e.g., "Apple Inc", "Microsoft Corp")
        # 2. Mixed case (e.g., "Apple", "Tesla", "McDonald")
        # 3. All uppercase but has spaces (e.g., "APPLE INC")
        return has_space or has_lowercase or (is_all_uppercase and has_space)
    
    def _is_alternative_id(self, input_str: str) -> bool:
        """Detect CUSIP, ISIN, ConID patterns."""
        # ConID: pure numeric, 6-9 digits
        if input_str.isdigit() and len(input_str) in [6, 7, 8, 9]:
            return True
            
        # CUSIP: 9 characters, first 8 alphanumeric, last is check digit
        # Must not be a common word (avoid false positives like "Microsoft")
        if (len(input_str) == 9 and 
            input_str[:8].isalnum() and 
            not input_str.isalpha() and  # Not purely alphabetic
            not any(c.islower() for c in input_str)):  # Not mixed case (company names)
            return True
            
        # ISIN: 12 characters, first 2 letters (country code), then 9 alphanumeric, then check digit
        if (len(input_str) == 12 and 
            input_str[:2].isalpha() and 
            input_str[2:11].isalnum() and 
            input_str[11].isdigit()):
            return True
            
        return False

    def _extract_country_from_contract(self, contract_detail):
        """Extract country information from IBKR contract details."""
        try:
            # Try to get country from contract details
            if hasattr(contract_detail, 'marketRule'):
                # Use market rule to infer country (simple mapping)
                if contract_detail.contract.exchange in ['NASDAQ', 'NYSE', 'SMART']:
                    return 'United States'
                elif contract_detail.contract.exchange == 'AEB':
                    return 'Netherlands'
                elif contract_detail.contract.exchange == 'XETRA':
                    return 'Germany'
                elif contract_detail.contract.exchange == 'TSE':
                    return 'Japan'
                elif contract_detail.contract.exchange == 'LSE':
                    return 'United Kingdom'
            
            # Fallback to currency-based mapping
            currency_country_map = {
                'USD': 'United States',
                'EUR': 'Eurozone',
                'JPY': 'Japan',
                'GBP': 'United Kingdom',
                'CAD': 'Canada',
                'AUD': 'Australia',
                'CHF': 'Switzerland'
            }
            
            return currency_country_map.get(contract_detail.contract.currency, 'Unknown')
        except Exception:
            return 'Unknown'
    
    async def _resolve_exact_symbol(self, symbol: str, exchange: str = None, currency: str = None, sec_type: str = "STK") -> List[Dict]:
        """Resolve exact symbol via direct IBKR API call."""
        try:
            from ib_async import Stock
            
            # Create contract with SMART routing for auto-detection
            contract = Stock(
                symbol=symbol.upper(),
                exchange=exchange or "SMART", 
                currency=currency or "USD"
            )
            
            # Single API call to IBKR
            details = await self.ib.reqContractDetailsAsync(contract)
            
            if not details:
                return []
            
            # Format results from real IBKR data
            matches = []
            for detail in details:
                contract = detail.contract
                
                # Extract real metadata from IBKR
                match = {
                    'symbol': contract.symbol,
                    'name': getattr(contract, 'longName', contract.symbol),  # Real company name
                    'conid': contract.conId,
                    'exchange': contract.exchange,
                    'primary_exchange': getattr(contract, 'primaryExchange', contract.exchange),
                    'currency': contract.currency,
                    'sec_type': sec_type,
                    'country': self._extract_country_from_contract(detail),
                    'validated': True
                }
                
                # Add alternative IDs if available
                if hasattr(detail, 'secIdList'):
                    for sec_id in detail.secIdList:
                        if sec_id.tag == "ISIN":
                            match["isin"] = sec_id.value
                        elif sec_id.tag == "CUSIP":
                            match["cusip"] = sec_id.value
                
                matches.append(match)
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Exact symbol resolution failed for {symbol}: {e}")
            return []
    
    async def _resolve_alternative_id(self, identifier: str, exchange: str = None, currency: str = None, sec_type: str = "STK") -> List[Dict]:
        """Resolve alternative identifiers (CUSIP, ISIN, ConID)."""
        try:
            from ib_async import Stock
            
            contract = None
            
            if identifier.isdigit() and len(identifier) in [6, 7, 8, 9]:
                # Likely ConID
                contract = Stock(conId=int(identifier))
            elif len(identifier) == 9 and identifier[:8].isalnum():
                # CUSIP pattern
                contract = Stock(secIdType="CUSIP", secId=identifier)
            elif len(identifier) == 12 and identifier[:2].isalpha():
                # ISIN pattern
                contract = Stock(secIdType="ISIN", secId=identifier)
            
            if not contract:
                return []
            
            # For ISIN and CUSIP, use reqContractDetailsAsync to get all possibilities
            # then filter for the best match
            if hasattr(contract, 'secIdType'):
                details = await self.ib.reqContractDetailsAsync(contract)
                
                if not details:
                    return []
                
                # If multiple contracts, prefer USD currency, then SMART exchange
                best_detail = None
                for detail in details:
                    if not best_detail:
                        best_detail = detail
                    elif (detail.contract.currency == 'USD' and 
                          best_detail.contract.currency != 'USD'):
                        best_detail = detail
                    elif (detail.contract.currency == best_detail.contract.currency and
                          detail.contract.exchange == 'SMART'):
                        best_detail = detail
                
                contract = best_detail.contract
                
            else:
                # ConID - just qualify it
                qualified = await self._qualify_contracts_with_retry([contract])
                if not qualified:
                    return []
                contract = qualified[0]
            
            # Format result
            match = {
                'symbol': contract.symbol,
                'exchange': contract.exchange,
                'currency': contract.currency,
                'sec_type': sec_type,
                'name': getattr(contract, 'longName', ''),
                'conid': contract.conId,
                'primary_exchange': getattr(contract, 'primaryExchange', ''),
                'validated': True
            }
            
            return [match]
            
        except Exception as e:
            self.logger.error(f"Alternative ID resolution failed for {identifier}: {e}")
            return []
    
    async def _resolve_fuzzy_search(self, query: str, exchange: str = None, currency: str = None, sec_type: str = "STK") -> List[Dict]:
        """Resolve using fuzzy search (company names) with rate limiting and cache-first strategy."""
        try:
            # PHASE 4.2: Track fuzzy search attempt
            self.fuzzy_search_stats['fuzzy_searches_attempted'] += 1
            
            # PHASE 4.3: Enforce rate limiting with graceful degradation
            rate_limit_passed = await self._enforce_rate_limiting()
            if not rate_limit_passed:
                # Return empty results when rate limited - graceful degradation
                self.logger.debug(f"Fuzzy search rate limited for query: {query}")
                return []
            
            # PHASE 4.3: Cache-first strategy - check if we have cached fuzzy results
            fuzzy_cache_key = f"fuzzy_{query.lower().strip()}_{exchange}_{currency}_{sec_type}"
            cached_fuzzy_result = self._get_cached_resolution(fuzzy_cache_key)
            if cached_fuzzy_result:
                self.logger.debug(f"Returning cached fuzzy search result for: {query}")
                # Return the matches array from cached result
                return cached_fuzzy_result.get('matches', [])
            
            # For now, implement basic fuzzy search using existing database
            # In the future, this could use IBKR's reqMatchingSymbols API
            
            fuzzy_matches = []
            matched_company = None
            
            # Check if query matches known company names in our database
            company_name_mappings = {
                'apple': 'AAPL',
                'microsoft': 'MSFT', 
                'google': 'GOOGL',
                'tesla': 'TSLA',
                'amazon': 'AMZN',
                'meta': 'META',
                'netflix': 'NFLX',
                'nvidia': 'NVDA',
                'asml': 'ASML',
                'sap': 'SAP',
                'toyota': '7203',
                'samsung': '005930'
            }
            
            query_lower = query.lower().strip()
            
            # Look for exact company name matches
            for company_name, symbol in company_name_mappings.items():
                if company_name in query_lower or query_lower in company_name:
                    matched_company = company_name
                    # Resolve the matched symbol using exact symbol resolution
                    exact_matches = await self._resolve_exact_symbol(symbol, exchange, currency, sec_type)
                    fuzzy_matches.extend(exact_matches)
            
            # PHASE 4.3: Cache the fuzzy search results
            if fuzzy_matches:
                fuzzy_result = {
                    'matches': fuzzy_matches,
                    'resolution_method': 'fuzzy_search',
                    'matched_company': matched_company,
                    'query': query
                }
                self._cache_resolution(fuzzy_cache_key, fuzzy_result)
                self.logger.debug(f"Cached fuzzy search result for: {query}")
            
            # PHASE 4.2: Track fuzzy search results and accuracy
            if fuzzy_matches:
                self.fuzzy_search_stats['fuzzy_searches_successful'] += 1
                
                # Calculate confidence score for fuzzy match
                confidence = self._calculate_fuzzy_confidence(query, matched_company, fuzzy_matches)
                
                # Update accuracy tracking
                self._update_fuzzy_accuracy_metrics(query, matched_company, fuzzy_matches, confidence)
            
            # Update overall accuracy rate
            total_attempts = self.fuzzy_search_stats['fuzzy_searches_attempted']
            if total_attempts > 0:
                self.fuzzy_search_stats['fuzzy_accuracy_rate'] = (
                    self.fuzzy_search_stats['fuzzy_searches_successful'] / total_attempts
                )
            
            return fuzzy_matches
            
        except Exception as e:
            self.logger.error(f"Fuzzy search failed for {query}: {e}")
            return []
    
    def _calculate_confidence_score(self, match: Dict, query: str, exchange_preference: str) -> float:
        """
        Calculate confidence score (0.0 to 1.0) for symbol resolution.
        
        Factors:
        - Exact symbol match: +0.4
        - Exchange preference match: +0.2  
        - Native exchange bonus: +0.15
        - Currency preference (USD): +0.1 (or +0.15 for native)
        - String similarity: +0.3 (for fuzzy matches)
        """
        import difflib
        
        score = 0.0
        
        # Exact symbol match bonus
        if match.get('symbol', '').lower() == query.lower():
            score += 0.4
        
        # Native exchange bonus (higher than general exchange preference)
        if match.get('is_native_exchange', False):
            score += 0.15
        elif match.get('is_preferred_international', False):
            score += 0.1
        elif match.get('exchange') == exchange_preference or match.get('exchange') == 'SMART':
            score += 0.2
        
        # Currency preference - higher bonus for native currency
        if match.get('is_native_exchange', False):
            # Native exchange gets currency bonus regardless of currency
            score += 0.15
        elif match.get('currency') == 'USD':
            # USD bias for non-native exchanges
            score += 0.1
        
        # String similarity for fuzzy matches
        if query.lower() != match.get('symbol', '').lower():
            similarity = difflib.SequenceMatcher(None, query.lower(), match.get('symbol', '').lower()).ratio()
            score += similarity * 0.3
        
        return min(score, 1.0)  # Cap at 1.0
    
    async def _add_alternative_identifiers(self, match: Dict):
        """Add alternative identifiers (CUSIP, ISIN) to match if available."""
        try:
            # Alternative identifiers are already included in the contract details
            # This method can be expanded to fetch additional identifiers if needed
            pass
        except Exception as e:
            self.logger.warning(f"Failed to add alternative identifiers: {e}")
    
    async def _apply_native_exchange_preference(self, matches: List[Dict], symbol: str) -> List[Dict]:
        """Apply native exchange preference for international stocks."""
        
        # Known international stocks and their native exchanges
        NATIVE_EXCHANGE_MAP = {
            # European stocks
            'SAP': {'exchange': 'XETRA', 'currency': 'EUR', 'country': 'Germany'},
            'ASML': {'exchange': 'AEB', 'currency': 'EUR', 'country': 'Netherlands'},
            'NESN': {'exchange': 'SWX', 'currency': 'CHF', 'country': 'Switzerland'},
            'NOVN': {'exchange': 'SWX', 'currency': 'CHF', 'country': 'Switzerland'},
            'ROG': {'exchange': 'SWX', 'currency': 'CHF', 'country': 'Switzerland'},
            'ADYEN': {'exchange': 'AEB', 'currency': 'EUR', 'country': 'Netherlands'},
            'LVMH': {'exchange': 'SBF', 'currency': 'EUR', 'country': 'France'},
            'TOTAL': {'exchange': 'SBF', 'currency': 'EUR', 'country': 'France'},
            'SANOFI': {'exchange': 'SBF', 'currency': 'EUR', 'country': 'France'},
            
            # Italian stocks
            'ENI': {'exchange': 'BIT', 'currency': 'EUR', 'country': 'Italy'},
            'ENEL': {'exchange': 'BIT', 'currency': 'EUR', 'country': 'Italy'},
            'UCG': {'exchange': 'BIT', 'currency': 'EUR', 'country': 'Italy'},  # UniCredit
            'ISP': {'exchange': 'BIT', 'currency': 'EUR', 'country': 'Italy'},  # Intesa Sanpaolo
            
            # Spanish stocks  
            'SAN': {'exchange': 'BME', 'currency': 'EUR', 'country': 'Spain'},  # Santander
            'IBE': {'exchange': 'BME', 'currency': 'EUR', 'country': 'Spain'},  # Iberdrola
            'TEF': {'exchange': 'BME', 'currency': 'EUR', 'country': 'Spain'},  # Telefonica
            'BBVA': {'exchange': 'BME', 'currency': 'EUR', 'country': 'Spain'},
            
            # Austrian stocks
            'AMS': {'exchange': 'VIX', 'currency': 'EUR', 'country': 'Austria'},  # AMS-Osram
            
            # Nordic stocks
            'EQNR': {'exchange': 'OSE', 'currency': 'NOK', 'country': 'Norway'},  # Equinor
            'DNB': {'exchange': 'OSE', 'currency': 'NOK', 'country': 'Norway'},
            'VOLV-B': {'exchange': 'OMX', 'currency': 'SEK', 'country': 'Sweden'},  # Volvo
            'ERIC': {'exchange': 'OMX', 'currency': 'SEK', 'country': 'Sweden'},  # Ericsson
            'NOK1V': {'exchange': 'HEX', 'currency': 'EUR', 'country': 'Finland'},  # Nokia
            
            # Polish stocks
            'PKN': {'exchange': 'WSE', 'currency': 'PLN', 'country': 'Poland'},  # PKN Orlen
            'PZU': {'exchange': 'WSE', 'currency': 'PLN', 'country': 'Poland'},
            
            # UK stocks  
            'BARC': {'exchange': 'LSE', 'currency': 'GBP', 'country': 'United Kingdom'},
            'BP': {'exchange': 'LSE', 'currency': 'GBP', 'country': 'United Kingdom'},
            'SHEL': {'exchange': 'LSE', 'currency': 'GBP', 'country': 'United Kingdom'},
            'VODAFONE': {'exchange': 'LSE', 'currency': 'GBP', 'country': 'United Kingdom'},
            
            # Asian stocks
            '7203': {'exchange': 'TSE', 'currency': 'JPY', 'country': 'Japan'},  # Toyota
            '6758': {'exchange': 'TSE', 'currency': 'JPY', 'country': 'Japan'},  # Sony
            '9984': {'exchange': 'TSE', 'currency': 'JPY', 'country': 'Japan'},  # SoftBank
            'TSM': {'exchange': 'TWSE', 'currency': 'TWD', 'country': 'Taiwan'},  # TSMC
            '2330': {'exchange': 'TWSE', 'currency': 'TWD', 'country': 'Taiwan'},  # TSMC
            '005930': {'exchange': 'KSE', 'currency': 'KRW', 'country': 'South Korea'},  # Samsung
            
            # US stocks (major NYSE/NASDAQ listings)
            'AAPL': {'exchange': 'NASDAQ', 'currency': 'USD', 'country': 'United States'},
            'MSFT': {'exchange': 'NASDAQ', 'currency': 'USD', 'country': 'United States'},
            'GOOGL': {'exchange': 'NASDAQ', 'currency': 'USD', 'country': 'United States'},
            'TSLA': {'exchange': 'NASDAQ', 'currency': 'USD', 'country': 'United States'},
            'NVDA': {'exchange': 'NASDAQ', 'currency': 'USD', 'country': 'United States'},
            'JPM': {'exchange': 'NYSE', 'currency': 'USD', 'country': 'United States'},
            'JNJ': {'exchange': 'NYSE', 'currency': 'USD', 'country': 'United States'},
            'V': {'exchange': 'NYSE', 'currency': 'USD', 'country': 'United States'},
            'PG': {'exchange': 'NYSE', 'currency': 'USD', 'country': 'United States'},
            'HD': {'exchange': 'NYSE', 'currency': 'USD', 'country': 'United States'},
            
            # Canadian stocks
            'SHOP': {'exchange': 'TSX', 'currency': 'CAD', 'country': 'Canada'},
            'RY': {'exchange': 'TSX', 'currency': 'CAD', 'country': 'Canada'},
            'TD': {'exchange': 'TSX', 'currency': 'CAD', 'country': 'Canada'},
            'BNS': {'exchange': 'TSX', 'currency': 'CAD', 'country': 'Canada'},
            'CNR': {'exchange': 'TSX', 'currency': 'CAD', 'country': 'Canada'},
            
            # Brazilian stocks
            'PETR4': {'exchange': 'B3', 'currency': 'BRL', 'country': 'Brazil'},
            'VALE3': {'exchange': 'B3', 'currency': 'BRL', 'country': 'Brazil'},
            'ITUB4': {'exchange': 'B3', 'currency': 'BRL', 'country': 'Brazil'},
            'BBDC4': {'exchange': 'B3', 'currency': 'BRL', 'country': 'Brazil'},
            
            # Mexican stocks
            'AMXL': {'exchange': 'MEXI', 'currency': 'MXN', 'country': 'Mexico'},
            'CEMEXCPO': {'exchange': 'MEXI', 'currency': 'MXN', 'country': 'Mexico'},
            
            # Taiwan stocks
            '2330': {'exchange': 'TWSE', 'currency': 'TWD', 'country': 'Taiwan'},  # TSMC
            '2454': {'exchange': 'TWSE', 'currency': 'TWD', 'country': 'Taiwan'},  # MediaTek
            '2317': {'exchange': 'TWSE', 'currency': 'TWD', 'country': 'Taiwan'},  # Hon Hai
            
            # Chinese stocks
            '000001': {'exchange': 'SZSE', 'currency': 'CNY', 'country': 'China'},  # Ping An Bank
            '600036': {'exchange': 'SSE', 'currency': 'CNY', 'country': 'China'},  # China Merchants Bank
            '000002': {'exchange': 'SZSE', 'currency': 'CNY', 'country': 'China'},  # Vanke
            '600519': {'exchange': 'SSE', 'currency': 'CNY', 'country': 'China'},  # Kweichow Moutai
            
            # Indian stocks
            'RELIANCE': {'exchange': 'NSE', 'currency': 'INR', 'country': 'India'},
            'TCS': {'exchange': 'NSE', 'currency': 'INR', 'country': 'India'},
            'HDFCBANK': {'exchange': 'NSE', 'currency': 'INR', 'country': 'India'},
            'INFY': {'exchange': 'NSE', 'currency': 'INR', 'country': 'India'},
            'HINDUNILVR': {'exchange': 'NSE', 'currency': 'INR', 'country': 'India'},
            
            # Singapore stocks
            'D05': {'exchange': 'SGX', 'currency': 'SGD', 'country': 'Singapore'},  # DBS
            'O39': {'exchange': 'SGX', 'currency': 'SGD', 'country': 'Singapore'},  # OCBC
            'U11': {'exchange': 'SGX', 'currency': 'SGD', 'country': 'Singapore'},  # UOB
            
            # Thai stocks
            'PTT': {'exchange': 'SET', 'currency': 'THB', 'country': 'Thailand'},
            'KBANK': {'exchange': 'SET', 'currency': 'THB', 'country': 'Thailand'},
            'SCB': {'exchange': 'SET', 'currency': 'THB', 'country': 'Thailand'},
            
            # Indonesian stocks
            'BBCA': {'exchange': 'IDX', 'currency': 'IDR', 'country': 'Indonesia'},  # Bank Central Asia
            'BBRI': {'exchange': 'IDX', 'currency': 'IDR', 'country': 'Indonesia'},  # Bank Rakyat
            'BMRI': {'exchange': 'IDX', 'currency': 'IDR', 'country': 'Indonesia'},  # Bank Mandiri
            
            # Malaysian stocks
            'MAYBANK': {'exchange': 'KLSE', 'currency': 'MYR', 'country': 'Malaysia'},
            'TENAGA': {'exchange': 'KLSE', 'currency': 'MYR', 'country': 'Malaysia'},
            'CIMB': {'exchange': 'KLSE', 'currency': 'MYR', 'country': 'Malaysia'},
            
            # New Zealand stocks
            'FPH': {'exchange': 'NZX', 'currency': 'NZD', 'country': 'New Zealand'},  # Fisher & Paykel Healthcare
            'SPK': {'exchange': 'NZX', 'currency': 'NZD', 'country': 'New Zealand'},  # Spark New Zealand
            
            # Israeli stocks
            'TEVA': {'exchange': 'TASE', 'currency': 'ILS', 'country': 'Israel'},
            'CHKP': {'exchange': 'TASE', 'currency': 'ILS', 'country': 'Israel'},  # Check Point
            
            # South African stocks
            'NPN': {'exchange': 'JSE', 'currency': 'ZAR', 'country': 'South Africa'},  # Naspers
            'SBK': {'exchange': 'JSE', 'currency': 'ZAR', 'country': 'South Africa'},  # Standard Bank
        }
        
        symbol_upper = symbol.upper()
        
        # Check if this symbol has a known native exchange
        if symbol_upper in NATIVE_EXCHANGE_MAP:
            native_info = NATIVE_EXCHANGE_MAP[symbol_upper]
            
            try:
                # Try to resolve on the native exchange
                native_matches = await self._resolve_exact_symbol(
                    symbol_upper, 
                    exchange=native_info['exchange'], 
                    currency=native_info['currency']
                )
                
                if native_matches:
                    # Tag native exchange matches with higher preference
                    for match in native_matches:
                        match['is_native_exchange'] = True
                        match['native_country'] = native_info['country']
                    
                    # Combine with existing matches, but prioritize native
                    combined_matches = native_matches + [m for m in matches if m.get('exchange') != native_info['exchange']]
                    
                    self.logger.info(f"Found native exchange for {symbol}: {native_info['exchange']} ({native_info['currency']})")
                    return combined_matches
                    
            except Exception as e:
                self.logger.warning(f"Failed to resolve {symbol} on native exchange {native_info['exchange']}: {e}")
        
        # If no native exchange mapping or resolution failed, apply heuristic preferences
        if len(matches) > 1:
            # Prefer non-US exchanges for obviously international symbols
            international_matches = []
            us_matches = []
            
            for match in matches:
                exchange = match.get('exchange', '')
                currency = match.get('currency', '')
                
                # Classify as international if:
                # - Non-USD currency AND non-US exchange
                # - Known international exchanges
                if (currency != 'USD' and exchange not in ['SMART', 'NYSE', 'NASDAQ', 'AMEX']) or \
                   exchange in ['AEB', 'XETRA', 'LSE', 'SWX', 'SBF', 'TSE', 'TWSE', 'KSE', 'IBIS']:
                    match['is_preferred_international'] = True
                    international_matches.append(match)
                else:
                    us_matches.append(match)
            
            # If we found international matches, prioritize them
            if international_matches:
                self.logger.info(f"Prioritizing international exchanges for {symbol}: {[m.get('exchange') for m in international_matches]}")
                return international_matches + us_matches
        
        # Return original matches if no preference can be applied
        return matches
    
    async def _qualify_contracts_with_retry(self, contracts: List[Contract], max_retries: int = 3) -> List[Contract]:
        """Qualify contracts with IBKR API with retry logic for transient failures."""
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                # Check connection before each attempt
                if not self.ib or not self.ib.isConnected():
                    raise ConnectionError("IBKR API connection lost")
                
                # PHASE 4.2: Track API call attempt
                self.api_call_stats['total_api_calls'] += 1
                self.api_call_stats['req_contract_details_calls'] += 1
                self.api_call_stats['last_api_call'] = datetime.now(timezone.utc)
                
                # Update hourly call tracking
                self._update_hourly_api_calls()
                
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
        cache_size = len(self.resolution_cache)
        self.resolution_cache.clear()
        self.cache_stats['invalidations'] += cache_size
        self.cache_stats['memory_usage'] = 0
        self.logger.info(f"International symbol resolution cache cleared ({cache_size} entries)")
    
    def _update_hourly_api_calls(self) -> None:
        """Update hourly API call tracking for rate monitoring."""
        now = datetime.now(timezone.utc)
        current_hour = now.replace(minute=0, second=0, microsecond=0)
        
        # Keep only last 24 hours of data
        self.api_call_stats['api_calls_per_hour'] = [
            (hour, count) for hour, count in self.api_call_stats['api_calls_per_hour']
            if hour >= current_hour - timedelta(hours=24)
        ]
        
        # Update current hour count
        hour_found = False
        for i, (hour, count) in enumerate(self.api_call_stats['api_calls_per_hour']):
            if hour == current_hour:
                self.api_call_stats['api_calls_per_hour'][i] = (hour, count + 1)
                hour_found = True
                break
        
        if not hour_found:
            self.api_call_stats['api_calls_per_hour'].append((current_hour, 1))
        
        # Update last hour calls count
        self.api_call_stats['last_hour_calls'] = sum(
            count for hour, count in self.api_call_stats['api_calls_per_hour']
            if hour >= now - timedelta(hours=1)
        )
    
    def _calculate_fuzzy_confidence(self, query: str, matched_company: str, matches: List[Dict]) -> float:
        """Calculate confidence score for fuzzy search match."""
        if not matched_company or not matches:
            return 0.0
        
        # Base confidence starts at 0.5 for any match
        confidence = 0.5
        
        # Boost for exact company name match
        query_lower = query.lower().strip()
        if matched_company == query_lower:
            confidence += 0.3
        elif matched_company in query_lower:
            confidence += 0.2
        elif query_lower in matched_company:
            confidence += 0.1
        
        # Boost for multiple matches (indicates good symbol)
        if len(matches) > 1:
            confidence += 0.1
        
        # Cap at 1.0
        return min(confidence, 1.0)
    
    def _update_fuzzy_accuracy_metrics(self, query: str, matched_company: str, matches: List[Dict], confidence: float) -> None:
        """Update fuzzy search accuracy metrics and patterns."""
        # Track confidence scores for average calculation
        confidence_scores = self.fuzzy_search_stats.get('confidence_scores', [])
        confidence_scores.append(confidence)
        
        # Keep only last 100 confidence scores for rolling average
        if len(confidence_scores) > 100:
            confidence_scores = confidence_scores[-100:]
        
        self.fuzzy_search_stats['confidence_scores'] = confidence_scores
        self.fuzzy_search_stats['fuzzy_avg_confidence'] = sum(confidence_scores) / len(confidence_scores)
        
        # Track successful match patterns for learning
        if matched_company:
            pattern_key = f"{query.lower()}->{matched_company}"
            if pattern_key not in self.fuzzy_search_stats['fuzzy_search_patterns']:
                self.fuzzy_search_stats['fuzzy_search_patterns'][pattern_key] = 0
            self.fuzzy_search_stats['fuzzy_search_patterns'][pattern_key] += 1
        
        # Track recent matches for analysis (keep last 50)
        match_record = {
            'query': query,
            'matched_company': matched_company,
            'matches_found': len(matches),
            'confidence': confidence,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        fuzzy_matches = self.fuzzy_search_stats['fuzzy_matches_found']
        fuzzy_matches.append(match_record)
        if len(fuzzy_matches) > 50:
            self.fuzzy_search_stats['fuzzy_matches_found'] = fuzzy_matches[-50:]
    
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
    
    # PHASE 4.3 ADDITIONS: Rate limiting helper functions
    
    def _should_rate_limit_fuzzy_search(self) -> bool:
        """Check if fuzzy search should be rate limited (1-second interval)."""
        if not self.rate_limiting['last_fuzzy_search']:
            return False
        
        time_since_last = datetime.now(timezone.utc) - self.rate_limiting['last_fuzzy_search']
        return time_since_last.total_seconds() < 1.0
    
    def _update_fuzzy_search_timing(self) -> None:
        """Update the timestamp of the last fuzzy search for rate limiting."""
        self.rate_limiting['last_fuzzy_search'] = datetime.now(timezone.utc)
    
    def _should_degrade_fuzzy_search(self) -> bool:
        """Check if fuzzy search should be degraded due to rate limits."""
        # Check if we're already in degraded mode
        if self.rate_limiting['fuzzy_search_degraded']:
            # Check if we can exit degraded mode (after 1 minute)
            if self.rate_limiting['last_fuzzy_search']:
                time_since_last = datetime.now(timezone.utc) - self.rate_limiting['last_fuzzy_search']
                if time_since_last.total_seconds() > 60:
                    self.rate_limiting['fuzzy_search_degraded'] = False
                    self.logger.info("Fuzzy search rate limiting degraded mode disabled")
                    return False
            return True
        
        # Check if we should enter degraded mode based on API call frequency
        current_time = datetime.now(timezone.utc)
        hour_start = current_time.replace(minute=0, second=0, microsecond=0)
        
        # Count API calls in the current hour
        api_calls_this_hour = 0
        for hour_time, count in self.api_call_stats.get('api_calls_per_hour', []):
            if hour_time >= hour_start:
                api_calls_this_hour += count
        
        # Enable degraded mode if too many API calls (threshold: 100 per hour)
        if api_calls_this_hour > 100:
            self.rate_limiting['fuzzy_search_degraded'] = True
            self.logger.warning(f"Fuzzy search degraded mode enabled: {api_calls_this_hour} API calls this hour")
            return True
        
        return False
    
    async def _enforce_rate_limiting(self) -> bool:
        """Enforce rate limiting for fuzzy searches with graceful degradation."""
        # Check if we should rate limit
        if self._should_rate_limit_fuzzy_search():
            self.logger.debug("Fuzzy search rate limited (1-second interval not met)")
            return False
        
        # Check if we should degrade performance
        if self._should_degrade_fuzzy_search():
            self.logger.debug("Fuzzy search degraded due to high API usage")
            return False
        
        # Update timing for successful rate limit check
        self._update_fuzzy_search_timing()
        return True
    
    def _track_api_call(self, api_method: str) -> None:
        """Track API call for performance monitoring."""
        self.api_call_stats[f'{api_method}_calls'] += 1
        self.api_call_stats['total_api_calls'] += 1
        self.api_call_stats['last_api_call'] = datetime.now(timezone.utc)
        
        # Track API calls per hour for rate limiting analysis
        current_hour = datetime.now(timezone.utc).hour
        if not self.api_call_stats['api_calls_per_hour']:
            self.api_call_stats['api_calls_per_hour'] = [0] * 24
        
        if len(self.api_call_stats['api_calls_per_hour']) <= current_hour:
            self.api_call_stats['api_calls_per_hour'].extend([0] * (current_hour + 1 - len(self.api_call_stats['api_calls_per_hour'])))
        
        self.api_call_stats['api_calls_per_hour'][current_hour] += 1
        self.api_call_stats['last_hour_calls'] = self.api_call_stats['api_calls_per_hour'][current_hour]
    
    def _track_fuzzy_search_result(self, query: str, matches: List[Dict], success: bool) -> None:
        """Track fuzzy search accuracy metrics."""
        self.fuzzy_search_stats['fuzzy_searches_attempted'] += 1
        
        if success and matches:
            self.fuzzy_search_stats['fuzzy_searches_successful'] += 1
            
            # Track matches found
            self.fuzzy_search_stats['fuzzy_matches_found'].append({
                'query': query,
                'matches_count': len(matches),
                'best_confidence': max(match.get('confidence', 0) for match in matches) if matches else 0,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            # Update average confidence
            confidences = [match.get('confidence', 0) for match in matches]
            if confidences:
                total_confidence = sum(confidences)
                avg_confidence = total_confidence / len(confidences)
                
                # Running average calculation
                current_avg = self.fuzzy_search_stats['fuzzy_avg_confidence']
                successful_searches = self.fuzzy_search_stats['fuzzy_searches_successful']
                
                self.fuzzy_search_stats['fuzzy_avg_confidence'] = (
                    (current_avg * (successful_searches - 1) + avg_confidence) / successful_searches
                )
            
            # Track search patterns for analysis
            query_pattern = 'company_name' if ' ' in query or any(c.islower() for c in query) else 'symbol_like'
            if query_pattern not in self.fuzzy_search_stats['fuzzy_search_patterns']:
                self.fuzzy_search_stats['fuzzy_search_patterns'][query_pattern] = {'attempts': 0, 'successes': 0}
            
            self.fuzzy_search_stats['fuzzy_search_patterns'][query_pattern]['attempts'] += 1
            if success:
                self.fuzzy_search_stats['fuzzy_search_patterns'][query_pattern]['successes'] += 1
        
        # Update accuracy rate
        if self.fuzzy_search_stats['fuzzy_searches_attempted'] > 0:
            self.fuzzy_search_stats['fuzzy_accuracy_rate'] = (
                self.fuzzy_search_stats['fuzzy_searches_successful'] / 
                self.fuzzy_search_stats['fuzzy_searches_attempted']
            )
    
    def get_performance_metrics(self) -> Dict:
        """Get comprehensive performance metrics for monitoring."""
        return {
            'cache_stats': self.cache_stats.copy(),
            'api_call_stats': self.api_call_stats.copy(),
            'fuzzy_search_stats': self.fuzzy_search_stats.copy(),
            'cache_hit_rate': (
                self.cache_stats['hits'] / max(1, self.cache_stats['total_requests'])
            ),
            'cache_size': len(self.resolution_cache),
            'cache_memory_usage': self.cache_stats['memory_usage'],
            'api_calls_today': self.api_call_stats['total_api_calls'],
            'fuzzy_search_accuracy': self.fuzzy_search_stats['fuzzy_accuracy_rate'],
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
