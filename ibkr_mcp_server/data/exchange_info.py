"""Exchange information and trading hours for international markets."""

from typing import Dict, List, Optional, Tuple
from datetime import time, datetime, timezone
import pytz
import logging


# Exchange metadata with trading hours and settlement info
EXCHANGE_INFO = {
    # European Exchanges
    'XETRA': {
        'name': 'Frankfurt Stock Exchange',
        'country': 'Germany',
        'currency': 'EUR',
        'timezone': 'Europe/Berlin',
        'trading_hours': {
            'open': time(9, 0),    # 09:00 CET
            'close': time(17, 30)  # 17:30 CET
        },
        'settlement': 'T+2',
        'market_maker_hours': {
            'open': time(8, 0),
            'close': time(22, 0)
        }
    },
    'LSE': {
        'name': 'London Stock Exchange',
        'country': 'United Kingdom',
        'currency': 'GBP',
        'timezone': 'Europe/London',
        'trading_hours': {
            'open': time(8, 0),    # 08:00 GMT/BST
            'close': time(16, 30)  # 16:30 GMT/BST
        },
        'settlement': 'T+2',
        'market_maker_hours': {
            'open': time(7, 15),
            'close': time(17, 30)
        }
    },
    'SBF': {
        'name': 'Euronext Paris',
        'country': 'France',
        'currency': 'EUR',
        'timezone': 'Europe/Paris',
        'trading_hours': {
            'open': time(9, 0),    # 09:00 CET
            'close': time(17, 30)  # 17:30 CET
        },
        'settlement': 'T+2',
        'market_maker_hours': {
            'open': time(7, 15),
            'close': time(18, 30)
        }
    },
    'AEB': {
        'name': 'Euronext Amsterdam',
        'country': 'Netherlands',
        'currency': 'EUR',
        'timezone': 'Europe/Amsterdam',
        'trading_hours': {
            'open': time(9, 0),    # 09:00 CET
            'close': time(17, 30)  # 17:30 CET
        },
        'settlement': 'T+2',
        'market_maker_hours': {
            'open': time(7, 15),
            'close': time(18, 30)
        }
    },
    'SWX': {
        'name': 'SIX Swiss Exchange',
        'country': 'Switzerland',
        'currency': 'CHF',
        'timezone': 'Europe/Zurich',
        'trading_hours': {
            'open': time(9, 0),    # 09:00 CET
            'close': time(17, 30)  # 17:30 CET
        },
        'settlement': 'T+2',
        'market_maker_hours': {
            'open': time(8, 0),
            'close': time(18, 0)
        }
    },
    'KFX': {
        'name': 'Nasdaq Copenhagen',
        'country': 'Denmark',
        'currency': 'DKK',
        'timezone': 'Europe/Copenhagen',
        'trading_hours': {
            'open': time(9, 0),    # 09:00 CET
            'close': time(17, 0)   # 17:00 CET
        },
        'settlement': 'T+2',
        'market_maker_hours': {
            'open': time(8, 0),
            'close': time(18, 0)
        }
    },
    
    # Asian Exchanges
    'TSE': {
        'name': 'Tokyo Stock Exchange',
        'country': 'Japan',
        'currency': 'JPY',
        'timezone': 'Asia/Tokyo',
        'trading_hours': {
            'morning_open': time(9, 0),   # 09:00 JST
            'morning_close': time(11, 30), # 11:30 JST (lunch break)
            'afternoon_open': time(12, 30), # 12:30 JST
            'afternoon_close': time(15, 0)  # 15:00 JST
        },
        'settlement': 'T+2',
        'has_lunch_break': True
    },
    'SEHK': {
        'name': 'Stock Exchange of Hong Kong',
        'country': 'Hong Kong',
        'currency': 'HKD',
        'timezone': 'Asia/Hong_Kong',
        'trading_hours': {
            'morning_open': time(9, 30),   # 09:30 HKT
            'morning_close': time(12, 0),  # 12:00 HKT (lunch break)
            'afternoon_open': time(13, 0), # 13:00 HKT
            'afternoon_close': time(16, 0) # 16:00 HKT
        },
        'settlement': 'T+2',
        'has_lunch_break': True
    },
    'KSE': {
        'name': 'Korea Exchange',
        'country': 'South Korea',
        'currency': 'KRW',
        'timezone': 'Asia/Seoul',
        'trading_hours': {
            'open': time(9, 0),    # 09:00 KST
            'close': time(15, 30)  # 15:30 KST
        },
        'settlement': 'T+2'
    },
    'ASX': {
        'name': 'Australian Securities Exchange',
        'country': 'Australia',
        'currency': 'AUD',
        'timezone': 'Australia/Sydney',
        'trading_hours': {
            'open': time(10, 0),   # 10:00 AEST/AEDT
            'close': time(16, 0)   # 16:00 AEST/AEDT
        },
        'settlement': 'T+2',
        'pre_open': {
            'start': time(7, 0),   # Pre-open phase
            'end': time(10, 0)
        }
    },
    
    # US Exchanges (for reference)
    'SMART': {
        'name': 'IBKR Smart Routing',
        'country': 'United States',
        'currency': 'USD',
        'timezone': 'America/New_York',
        'trading_hours': {
            'open': time(9, 30),   # 09:30 EST/EDT
            'close': time(16, 0)   # 16:00 EST/EDT
        },
        'settlement': 'T+2',
        'extended_hours': {
            'pre_market_open': time(4, 0),
            'after_hours_close': time(20, 0)
        }
    },
    
    # Forex Exchange
    'IDEALPRO': {
        'name': 'IBKR Forex Exchange',
        'country': 'Global',
        'currency': 'Multiple',
        'timezone': 'UTC',
        'trading_hours': {
            'open': time(22, 0),   # Sunday 22:00 UTC
            'close': time(22, 0)   # Friday 22:00 UTC
        },
        'settlement': 'T+2',
        'continuous_trading': True
    }
}


class ExchangeManager:
    """Manages exchange-specific operations and validation."""
    
    def __init__(self):
        self.exchanges = EXCHANGE_INFO
        self.logger = logging.getLogger(__name__)
    
    def get_exchange_info(self, exchange: str) -> Optional[Dict]:
        """Get comprehensive exchange information with JSON-serializable time formats."""
        info = self.exchanges.get(exchange.upper())
        if not info:
            return None
        
        # Create a copy to avoid modifying the original
        info_copy = info.copy()
        
        # Convert time objects to strings for JSON serialization
        if 'trading_hours' in info_copy and isinstance(info_copy['trading_hours'], dict):
            trading_hours = info_copy['trading_hours'].copy()
            for key, value in trading_hours.items():
                if hasattr(value, 'strftime'):  # Check if it's a time object
                    trading_hours[key] = value.strftime('%H:%M')
            info_copy['trading_hours'] = trading_hours
        
        # Also handle market_maker_hours if present
        if 'market_maker_hours' in info_copy and isinstance(info_copy['market_maker_hours'], dict):
            mm_hours = info_copy['market_maker_hours'].copy()
            for key, value in mm_hours.items():
                if hasattr(value, 'strftime'):  # Check if it's a time object
                    mm_hours[key] = value.strftime('%H:%M')
            info_copy['market_maker_hours'] = mm_hours
        
        return info_copy
    
    def get_trading_hours(self, exchange: str) -> Optional[Dict]:
        """Get trading hours for an exchange."""
        info = self.get_exchange_info(exchange)
        return info.get('trading_hours') if info else None
    
    def get_timezone(self, exchange: str) -> Optional[str]:
        """Get timezone for an exchange."""
        info = self.get_exchange_info(exchange)
        return info.get('timezone') if info else None
    
    def get_currency(self, exchange: str) -> Optional[str]:
        """Get primary currency for an exchange."""
        info = self.get_exchange_info(exchange)
        return info.get('currency') if info else None
    
    def is_market_open(self, exchange: str, current_time: datetime = None) -> bool:
        """Check if market is currently open using pandas-market-calendars."""
        # Import here to avoid circular imports
        try:
            from ibkr_mcp_server.market_status import market_status_manager
            return market_status_manager.is_market_open(exchange, current_time)
        except Exception as e:
            self.logger.error(f"Error checking market status with market_status_manager: {e}")
            # Fallback to simple time-based check
            return self._simple_market_check(exchange, current_time)
    
    def _simple_market_check(self, exchange: str, current_time: datetime = None) -> bool:
        """Simple fallback market check without time objects."""
        if not current_time:
            current_time = datetime.now(timezone.utc)
        
        # Simple weekday check - avoid time object serialization issues
        if current_time.weekday() >= 5:  # Weekend
            return False
        
        # Forex is special case
        if exchange.upper() == 'IDEALPRO':
            weekday = current_time.weekday()
            hour = current_time.hour
            
            if weekday == 5:  # Saturday
                return False
            elif weekday == 6:  # Sunday  
                return hour >= 22
            elif weekday == 4:  # Friday
                return hour < 22
            else:
                return True
        
        # For other exchanges, assume open during business hours UTC
        hour = current_time.hour
        return 8 <= hour <= 20  # Rough business hours
    
    def get_settlement_info(self, exchange: str) -> Optional[str]:
        """Get settlement period for an exchange."""
        info = self.get_exchange_info(exchange)
        return info.get('settlement') if info else None
    
    def validate_currency_for_exchange(self, exchange: str, currency: str) -> bool:
        """Validate if currency is correct for exchange."""
        exchange_currency = self.get_currency(exchange)
        return exchange_currency == currency.upper() if exchange_currency else False
    
    def get_supported_exchanges(self) -> List[str]:
        """Get list of all supported exchanges."""
        return list(self.exchanges.keys())
    
    def get_market_status_summary(self) -> Dict[str, bool]:
        """Get market open/closed status for all exchanges."""
        current_time = datetime.now(timezone.utc)
        status = {}
        
        for exchange in self.exchanges.keys():
            status[exchange] = self.is_market_open(exchange, current_time)
        
        return status
    
    def get_next_market_open(self, exchange: str) -> Optional[datetime]:
        """Get next market open time for an exchange."""
        # Simplified implementation - could be enhanced with holiday calendars
        info = self.get_exchange_info(exchange)
        if not info:
            return None
        
        # This is a basic implementation
        # Production version would need proper holiday calendar integration
        current_time = datetime.now(timezone.utc)
        market_tz = pytz.timezone(info['timezone'])
        
        # Convert to market time
        market_time = current_time.astimezone(market_tz)
        
        # If it's weekend, return Monday morning
        if market_time.weekday() >= 5:
            # Calculate days until Monday
            days_ahead = 7 - market_time.weekday()  # Saturday=5, Sunday=6
            if market_time.weekday() == 6:  # Sunday
                days_ahead = 1
            
            next_monday = market_time.replace(
                hour=info['trading_hours'].get('open', time(9, 0)).hour,
                minute=info['trading_hours'].get('open', time(9, 0)).minute,
                second=0,
                microsecond=0
            ) + datetime.timedelta(days=days_ahead)
            
            return next_monday.astimezone(timezone.utc)
        
        return None
    
    def is_extended_hours_supported(self, exchange: str) -> bool:
        """Check if exchange supports extended hours trading."""
        info = self.get_exchange_info(exchange)
        return bool(info and info.get('extended_hours')) if info else False


# Global exchange manager instance
exchange_manager = ExchangeManager()
