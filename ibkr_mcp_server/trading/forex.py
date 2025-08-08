"""Forex trading management for IBKR MCP Server."""

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Union
from decimal import Decimal

from ib_async import IB, Forex, MarketOrder, LimitOrder, StopOrder, StopLimitOrder

from ..data import forex_manager as forex_db
from ..utils import safe_float, safe_int, ValidationError, ConnectionError
from ..enhanced_validators import ForexValidator, ForexTradingDisabledError
from ..enhanced_config import enhanced_settings


class ForexManager:
    """Manages forex trading operations with comprehensive validation and caching."""
    
    def __init__(self, ib_client: IB):
        self.ib = ib_client
        self.forex_db = forex_db
        self.validator = ForexValidator()
        self.logger = logging.getLogger(__name__)
        
        # Rate caching
        self.rate_cache = {}
        self.cache_duration = 5  # seconds
        
        # Performance tracking
        self.request_count = 0
        self.last_request_time = 0
    
    async def get_forex_rates(self, currency_pairs) -> List[Dict]:
        """Get real-time forex rates with intelligent caching."""
        try:
            if not self.ib or not self.ib.isConnected():
                raise ConnectionError("Not connected to IBKR")
            
            # Check if forex trading is enabled
            if not enhanced_settings.enable_forex_trading:
                raise ForexTradingDisabledError("Forex trading is disabled in configuration")
            
            # Parse and validate pairs - handle both string and list inputs
            if isinstance(currency_pairs, str):
                pairs = [p.strip().upper() for p in currency_pairs.split(',')]
            elif isinstance(currency_pairs, list):
                pairs = [str(p).strip().upper() for p in currency_pairs]
            else:
                raise ValidationError(f"currency_pairs must be string or list, got {type(currency_pairs)}")
            
            # Validate all pairs
            invalid_pairs = []
            for pair in pairs:
                if not self.forex_db.is_valid_pair(pair):
                    invalid_pairs.append(pair)
            
            if invalid_pairs:
                raise ValidationError(f"Invalid forex pairs: {', '.join(invalid_pairs)}")
            
            # Check cache and determine what needs fetching
            cached_results = []
            uncached_pairs = []
            
            for pair in pairs:
                cached_rate = self._get_cached_rate(pair)
                if cached_rate:
                    cached_results.append(cached_rate)
                else:
                    uncached_pairs.append(pair)
            
            # Fetch uncached rates
            fresh_results = []
            if uncached_pairs:
                fresh_results = await self._fetch_live_rates(uncached_pairs)
                
                # Cache the fresh results
                for result in fresh_results:
                    self._cache_rate(result)
            
            # Combine and return results
            all_results = cached_results + fresh_results
            
            # Sort by pair name for consistency
            all_results.sort(key=lambda x: x['pair'])
            
            return all_results
            
        except Exception as e:
            self.logger.error(f"Failed to get forex rates: {e}")
            raise
    
    async def _fetch_live_rates(self, pairs: List[str]) -> List[Dict]:
        """Fetch live rates from IBKR for specific pairs."""
        try:
            # Create forex contracts
            contracts = [Forex(pair) for pair in pairs]
            
            # Qualify contracts
            qualified = await self.ib.qualifyContractsAsync(*contracts)
            
            if not qualified:
                raise ValidationError("Could not qualify forex contracts")
            
            # Get tickers
            tickers = await self.ib.reqTickersAsync(*qualified)
            
            # Format results
            results = []
            for ticker in tickers:
                if ticker.contract and ticker.contract.symbol:
                    result = self._format_forex_ticker(ticker)
                    results.append(result)
            
            self.request_count += 1
            self.last_request_time = time.time()
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to fetch live rates: {e}")
            raise
    
    def _format_forex_ticker(self, ticker) -> Dict:
        """Format forex ticker data into standardized response."""
        contract = ticker.contract
        raw_symbol = contract.symbol
        
        # Handle IBKR's modified symbols for paper trading
        # IBKR sometimes returns just base currency (EUR, GBP) instead of pair (EURUSD, GBPUSD)
        if len(raw_symbol) == 3:
            # Try to reconstruct the full pair name
            # Most common pairs are vs USD
            pair = f"{raw_symbol}USD"
            base_currency = raw_symbol
            quote_currency = "USD"
        elif len(raw_symbol) == 6:
            pair = raw_symbol
            base_currency = raw_symbol[:3]
            quote_currency = raw_symbol[3:]
        else:
            # Fallback to raw symbol
            pair = raw_symbol
            base_currency = raw_symbol[:3] if len(raw_symbol) >= 3 else raw_symbol
            quote_currency = raw_symbol[3:] if len(raw_symbol) >= 6 else ""
        
        # Get pair metadata
        pair_info = self.forex_db.get_pair_info(pair)
        
        result = {
            "pair": pair,  # Use reconstructed pair name
            "base_currency": pair_info.get('base', base_currency) if pair_info else base_currency,
            "quote_currency": pair_info.get('quote', quote_currency) if pair_info else quote_currency,
            "name": pair_info.get('name', f"{base_currency}/{quote_currency}") if pair_info else f"{base_currency}/{quote_currency}",
            "last": safe_float(ticker.last),
            "bid": safe_float(ticker.bid),
            "ask": safe_float(ticker.ask),
            "close": safe_float(ticker.close),
            "high": safe_float(ticker.high),
            "low": safe_float(ticker.low),
            "volume": safe_int(ticker.volume),
            "spread": safe_float(ticker.ask) - safe_float(ticker.bid) if ticker.ask and ticker.bid else 0.0,
            "pip_value": pair_info.get('pip_value', 0.0001) if pair_info else 0.0001,
            "contract_id": contract.conId,
            "raw_contract_symbol": raw_symbol,  # Include original for debugging
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return result
    
    def _cache_rate(self, rate_data: Dict) -> None:
        """Cache forex rate with timestamp."""
        cache_key = rate_data['pair']
        self.rate_cache[cache_key] = {
            'data': rate_data,
            'timestamp': time.time()
        }
    
    def _get_cached_rate(self, pair: str) -> Optional[Dict]:
        """Get cached forex rate if still valid."""
        cache_entry = self.rate_cache.get(pair)
        if not cache_entry:
            return None
        
        # Check if cache is still valid
        if time.time() - cache_entry['timestamp'] > self.cache_duration:
            del self.rate_cache[pair]
            return None
        
        return cache_entry['data']
    
    async def convert_currency(self, amount: float, from_currency: str, 
                             to_currency: str) -> Dict:
        """Convert currency using live forex rates with intelligent pair resolution."""
        try:
            # Input validation
            if amount <= 0:
                raise ValidationError("Amount must be positive")
            
            from_curr = from_currency.upper().strip()
            to_curr = to_currency.upper().strip()
            
            # Same currency check
            if from_curr == to_curr:
                return {
                    "original_amount": amount,
                    "from_currency": from_curr,
                    "to_currency": to_curr,
                    "exchange_rate": 1.0,
                    "converted_amount": amount,
                    "conversion_method": "same_currency",
                    "rate_timestamp": datetime.now(timezone.utc).isoformat(),
                    "conversion_timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Find the best conversion path
            rate_info = await self._get_conversion_rate(from_curr, to_curr)
            
            if not rate_info:
                raise ValidationError(f"Cannot get exchange rate for {from_curr} to {to_curr}")
            
            # Calculate converted amount
            converted_amount = amount * rate_info['rate']
            
            return {
                "original_amount": amount,
                "from_currency": from_curr,
                "to_currency": to_curr,
                "exchange_rate": rate_info['rate'],
                "converted_amount": round(converted_amount, 6),
                "conversion_method": rate_info['method'],
                "pair_used": rate_info['pair_used'],
                "rate_timestamp": rate_info['rate_timestamp'],
                "conversion_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Currency conversion failed: {e}")
            raise
    
    async def _get_conversion_rate(self, from_curr: str, to_curr: str) -> Optional[Dict]:
        """Get conversion rate using the best available path."""
        # Try direct pair first
        direct_pair = f"{from_curr}{to_curr}"
        if self.forex_db.is_valid_pair(direct_pair):
            rates = await self.get_forex_rates(direct_pair)
            if rates and self._is_valid_rate(rates[0]['last']):
                return {
                    'rate': rates[0]['last'],
                    'method': 'direct',
                    'pair_used': direct_pair,
                    'rate_timestamp': rates[0]['timestamp']
                }
        
        # Try inverse pair
        inverse_pair = f"{to_curr}{from_curr}"
        if self.forex_db.is_valid_pair(inverse_pair):
            rates = await self.get_forex_rates(inverse_pair)
            if rates and self._is_valid_rate(rates[0]['last']) and rates[0]['last'] > 0:
                return {
                    'rate': 1.0 / rates[0]['last'],
                    'method': 'inverse',
                    'pair_used': inverse_pair,
                    'rate_timestamp': rates[0]['timestamp']
                }
        
        # Try cross-currency conversion through USD (prevent infinite recursion)
        if from_curr != 'USD' and to_curr != 'USD':
            try:
                # Convert from_curr to USD, then USD to to_curr
                from_to_usd = await self._get_conversion_rate(from_curr, 'USD')
                usd_to_target = await self._get_conversion_rate('USD', to_curr)
                
                if (from_to_usd and usd_to_target and 
                    self._is_valid_rate(from_to_usd['rate']) and 
                    self._is_valid_rate(usd_to_target['rate'])):
                    cross_rate = from_to_usd['rate'] * usd_to_target['rate']
                    return {
                        'rate': cross_rate,
                        'method': 'cross_via_usd',
                        'pair_used': f"{from_to_usd['pair_used']}+{usd_to_target['pair_used']}",
                        'rate_timestamp': datetime.now(timezone.utc).isoformat()
                    }
            except Exception as e:
                self.logger.warning(f"Cross-currency conversion failed: {e}")
        
        # For paper trading or when no real rates available, use mock rates
        mock_rate = self._get_mock_conversion_rate(from_curr, to_curr)
        if mock_rate:
            return mock_rate
        
        return None
    
    def _is_valid_rate(self, rate: float) -> bool:
        """Check if a rate is valid (not nan, None, or zero)."""
        import math
        return rate is not None and not math.isnan(rate) and rate > 0
    
    def _get_mock_conversion_rate(self, from_curr: str, to_curr: str) -> Optional[Dict]:
        """Get mock conversion rates for paper trading when real rates unavailable."""
        # Common forex pair mock rates (approximations for testing)
        mock_rates = {
            'EURUSD': 1.0850, 'GBPUSD': 1.2650, 'USDJPY': 110.25, 'USDCHF': 0.9200,
            'AUDUSD': 0.6750, 'USDCAD': 1.3500, 'NZDUSD': 0.6200,
            'EURGBP': 0.8580, 'EURJPY': 119.72, 'GBPJPY': 139.56, 'CHFJPY': 119.84,
            'EURCHF': 0.9982, 'AUDJPY': 74.42, 'CADJPY': 81.67, 'NZDJPY': 68.36
        }
        
        # Try direct pair
        direct_pair = f"{from_curr}{to_curr}"
        if direct_pair in mock_rates:
            self.logger.info(f"Using mock rate for {direct_pair}: {mock_rates[direct_pair]}")
            return {
                'rate': mock_rates[direct_pair],
                'method': 'mock_direct',
                'pair_used': direct_pair,
                'rate_timestamp': datetime.now(timezone.utc).isoformat()
            }
        
        # Try inverse pair
        inverse_pair = f"{to_curr}{from_curr}"
        if inverse_pair in mock_rates:
            mock_rate = 1.0 / mock_rates[inverse_pair]
            self.logger.info(f"Using mock inverse rate for {direct_pair}: {mock_rate}")
            return {
                'rate': mock_rate,
                'method': 'mock_inverse',
                'pair_used': inverse_pair,
                'rate_timestamp': datetime.now(timezone.utc).isoformat()
            }
        
        # Try cross-currency through USD
        if from_curr != 'USD' and to_curr != 'USD':
            from_usd_pair = f"{from_curr}USD"
            usd_to_pair = f"USD{to_curr}"
            
            from_rate = mock_rates.get(from_usd_pair)
            to_rate = mock_rates.get(usd_to_pair)
            
            if not from_rate:
                usd_from_pair = f"USD{from_curr}"
                if usd_from_pair in mock_rates:
                    from_rate = 1.0 / mock_rates[usd_from_pair]
            
            if not to_rate:
                to_usd_pair = f"{to_curr}USD"
                if to_usd_pair in mock_rates:
                    to_rate = 1.0 / mock_rates[to_usd_pair]
            
            if from_rate and to_rate:
                cross_rate = from_rate * to_rate
                self.logger.info(f"Using mock cross rate for {from_curr}/{to_curr}: {cross_rate}")
                return {
                    'rate': cross_rate,
                    'method': 'mock_cross_usd',
                    'pair_used': f"{from_usd_pair or 'USD'+from_curr}+{usd_to_pair or to_curr+'USD'}",
                    'rate_timestamp': datetime.now(timezone.utc).isoformat()
                }
        
        return None
    
    def get_supported_pairs(self) -> List[str]:
        """Get list of all supported forex pairs."""
        return self.forex_db.get_all_supported_pairs()
    
    def get_pair_info(self, pair: str) -> Optional[Dict]:
        """Get comprehensive information about a forex pair."""
        return self.forex_db.get_pair_info(pair)
    
    def validate_pair(self, pair: str) -> bool:
        """Validate if forex pair is supported."""
        return self.forex_db.is_valid_pair(pair)
    
    def get_minimum_size(self, pair: str) -> int:
        """Get minimum position size for a forex pair."""
        return self.forex_db.get_minimum_size(pair)
    
    def get_cache_stats(self) -> Dict:
        """Get caching performance statistics."""
        return {
            "cached_pairs": len(self.rate_cache),
            "total_requests": self.request_count,
            "last_request_time": self.last_request_time,
            "cache_duration_seconds": self.cache_duration
        }
    
    def clear_cache(self) -> None:
        """Clear all cached forex rates."""
        self.rate_cache.clear()
        self.logger.info("Forex rate cache cleared")
