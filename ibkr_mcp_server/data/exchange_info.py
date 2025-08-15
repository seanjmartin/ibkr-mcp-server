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
    'BIT': {
        'name': 'Borsa Italiana',
        'country': 'Italy',
        'currency': 'EUR',
        'timezone': 'Europe/Rome',
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
    'MIL': {
        'name': 'Milan Stock Exchange',
        'country': 'Italy',
        'currency': 'EUR',
        'timezone': 'Europe/Rome',
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
    'BME': {
        'name': 'Bolsas y Mercados Españoles',
        'country': 'Spain',
        'currency': 'EUR',
        'timezone': 'Europe/Madrid',
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
    'BVME': {
        'name': 'Madrid Stock Exchange',
        'country': 'Spain',
        'currency': 'EUR',
        'timezone': 'Europe/Madrid',
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
    'VIX': {
        'name': 'Vienna Stock Exchange',
        'country': 'Austria',
        'currency': 'EUR',
        'timezone': 'Europe/Vienna',
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
    'BEL': {
        'name': 'Euronext Brussels',
        'country': 'Belgium',
        'currency': 'EUR',
        'timezone': 'Europe/Brussels',
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
    'OSE': {
        'name': 'Oslo Stock Exchange',
        'country': 'Norway',
        'currency': 'NOK',
        'timezone': 'Europe/Oslo',
        'trading_hours': {
            'open': time(9, 0),    # 09:00 CET
            'close': time(16, 30)  # 16:30 CET
        },
        'settlement': 'T+2',
        'market_maker_hours': {
            'open': time(8, 0),
            'close': time(17, 30)
        }
    },
    'OMX': {
        'name': 'Nasdaq Stockholm',
        'country': 'Sweden',
        'currency': 'SEK',
        'timezone': 'Europe/Stockholm',
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
    'HEX': {
        'name': 'Nasdaq Helsinki',
        'country': 'Finland',
        'currency': 'EUR',
        'timezone': 'Europe/Helsinki',
        'trading_hours': {
            'open': time(10, 0),   # 10:00 EET
            'close': time(18, 30)  # 18:30 EET
        },
        'settlement': 'T+2',
        'market_maker_hours': {
            'open': time(9, 0),
            'close': time(19, 0)
        }
    },
    'WSE': {
        'name': 'Warsaw Stock Exchange',
        'country': 'Poland',
        'currency': 'PLN',
        'timezone': 'Europe/Warsaw',
        'trading_hours': {
            'open': time(9, 0),    # 09:00 CET
            'close': time(17, 0)   # 17:00 CET
        },
        'settlement': 'T+2',
        'market_maker_hours': {
            'open': time(8, 30),
            'close': time(17, 30)
        }
    },
    'IBIS2': {
        'name': 'Xetra (Alternative Code)',
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
    
    # US Exchanges
    'NYSE': {
        'name': 'New York Stock Exchange',
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
    'NASDAQ': {
        'name': 'NASDAQ Stock Market',
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
    'ARCA': {
        'name': 'NYSE Arca',
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
    'BATS': {
        'name': 'Cboe BZX Exchange',
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
    'IEX': {
        'name': 'Investors Exchange',
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
    
    # Canadian Exchanges
    'TSX': {
        'name': 'Toronto Stock Exchange',
        'country': 'Canada',
        'currency': 'CAD',
        'timezone': 'America/Toronto',
        'trading_hours': {
            'open': time(9, 30),   # 09:30 EST/EDT
            'close': time(16, 0)   # 16:00 EST/EDT
        },
        'settlement': 'T+2',
        'extended_hours': {
            'pre_market_open': time(7, 0),
            'after_hours_close': time(17, 0)
        }
    },
    'TSXV': {
        'name': 'TSX Venture Exchange',
        'country': 'Canada',
        'currency': 'CAD',
        'timezone': 'America/Toronto',
        'trading_hours': {
            'open': time(9, 30),   # 09:30 EST/EDT
            'close': time(16, 0)   # 16:00 EST/EDT
        },
        'settlement': 'T+2',
        'extended_hours': {
            'pre_market_open': time(7, 0),
            'after_hours_close': time(17, 0)
        }
    },
    
    # Latin American Exchanges
    'B3': {
        'name': 'B3 Stock Exchange',
        'country': 'Brazil',
        'currency': 'BRL',
        'timezone': 'America/Sao_Paulo',
        'trading_hours': {
            'open': time(10, 0),   # 10:00 BRT
            'close': time(17, 0)   # 17:00 BRT
        },
        'settlement': 'T+2',
        'market_maker_hours': {
            'open': time(9, 45),
            'close': time(17, 30)
        }
    },
    'MEXI': {
        'name': 'Mexican Stock Exchange',
        'country': 'Mexico',
        'currency': 'MXN',
        'timezone': 'America/Mexico_City',
        'trading_hours': {
            'open': time(8, 30),   # 08:30 CST/CDT
            'close': time(15, 0)   # 15:00 CST/CDT
        },
        'settlement': 'T+2',
        'market_maker_hours': {
            'open': time(8, 0),
            'close': time(15, 30)
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
    'TWSE': {
        'name': 'Taiwan Stock Exchange',
        'country': 'Taiwan',
        'currency': 'TWD',
        'timezone': 'Asia/Taipei',
        'trading_hours': {
            'open': time(9, 0),    # 09:00 CST
            'close': time(13, 30)  # 13:30 CST
        },
        'settlement': 'T+2',
        'has_lunch_break': False
    },
    'SSE': {
        'name': 'Shanghai Stock Exchange',
        'country': 'China',
        'currency': 'CNY',
        'timezone': 'Asia/Shanghai',
        'trading_hours': {
            'morning_open': time(9, 30),   # 09:30 CST
            'morning_close': time(11, 30), # 11:30 CST (lunch break)
            'afternoon_open': time(13, 0), # 13:00 CST
            'afternoon_close': time(15, 0) # 15:00 CST
        },
        'settlement': 'T+1',
        'has_lunch_break': True
    },
    'SZSE': {
        'name': 'Shenzhen Stock Exchange',
        'country': 'China',
        'currency': 'CNY',
        'timezone': 'Asia/Shanghai',
        'trading_hours': {
            'morning_open': time(9, 30),   # 09:30 CST
            'morning_close': time(11, 30), # 11:30 CST (lunch break)
            'afternoon_open': time(13, 0), # 13:00 CST
            'afternoon_close': time(15, 0) # 15:00 CST
        },
        'settlement': 'T+1',
        'has_lunch_break': True
    },
    'BSE': {
        'name': 'Bombay Stock Exchange',
        'country': 'India',
        'currency': 'INR',
        'timezone': 'Asia/Kolkata',
        'trading_hours': {
            'open': time(9, 15),   # 09:15 IST
            'close': time(15, 30)  # 15:30 IST
        },
        'settlement': 'T+2',
        'pre_open': {
            'start': time(9, 0),
            'end': time(9, 15)
        }
    },
    'NSE': {
        'name': 'National Stock Exchange of India',
        'country': 'India',
        'currency': 'INR',
        'timezone': 'Asia/Kolkata',
        'trading_hours': {
            'open': time(9, 15),   # 09:15 IST
            'close': time(15, 30)  # 15:30 IST
        },
        'settlement': 'T+2',
        'pre_open': {
            'start': time(9, 0),
            'end': time(9, 15)
        }
    },
    'SGX': {
        'name': 'Singapore Exchange',
        'country': 'Singapore',
        'currency': 'SGD',
        'timezone': 'Asia/Singapore',
        'trading_hours': {
            'open': time(9, 0),    # 09:00 SGT
            'close': time(17, 0)   # 17:00 SGT
        },
        'settlement': 'T+2',
        'market_maker_hours': {
            'open': time(8, 30),
            'close': time(17, 30)
        }
    },
    'SET': {
        'name': 'Stock Exchange of Thailand',
        'country': 'Thailand',
        'currency': 'THB',
        'timezone': 'Asia/Bangkok',
        'trading_hours': {
            'morning_open': time(10, 0),   # 10:00 ICT
            'morning_close': time(12, 30), # 12:30 ICT (lunch break)
            'afternoon_open': time(14, 30), # 14:30 ICT
            'afternoon_close': time(16, 30) # 16:30 ICT
        },
        'settlement': 'T+2',
        'has_lunch_break': True
    },
    'IDX': {
        'name': 'Indonesia Stock Exchange',
        'country': 'Indonesia',
        'currency': 'IDR',
        'timezone': 'Asia/Jakarta',
        'trading_hours': {
            'morning_open': time(9, 0),    # 09:00 WIB
            'morning_close': time(11, 30), # 11:30 WIB (lunch break)
            'afternoon_open': time(13, 30), # 13:30 WIB
            'afternoon_close': time(16, 0)  # 16:00 WIB
        },
        'settlement': 'T+2',
        'has_lunch_break': True
    },
    'KLSE': {
        'name': 'Bursa Malaysia',
        'country': 'Malaysia',
        'currency': 'MYR',
        'timezone': 'Asia/Kuala_Lumpur',
        'trading_hours': {
            'morning_open': time(9, 0),    # 09:00 MYT
            'morning_close': time(12, 30), # 12:30 MYT (lunch break)
            'afternoon_open': time(14, 0), # 14:00 MYT
            'afternoon_close': time(17, 0) # 17:00 MYT
        },
        'settlement': 'T+2',
        'has_lunch_break': True
    },
    'NZX': {
        'name': 'New Zealand Exchange',
        'country': 'New Zealand',
        'currency': 'NZD',
        'timezone': 'Pacific/Auckland',
        'trading_hours': {
            'open': time(10, 0),   # 10:00 NZST/NZDT
            'close': time(16, 45)  # 16:45 NZST/NZDT
        },
        'settlement': 'T+2',
        'pre_open': {
            'start': time(9, 30),
            'end': time(10, 0)
        }
    },
    
    # Middle East & Africa Exchanges
    'TASE': {
        'name': 'Tel Aviv Stock Exchange',
        'country': 'Israel',
        'currency': 'ILS',
        'timezone': 'Asia/Jerusalem',
        'trading_hours': {
            'open': time(9, 0),    # 09:00 IST
            'close': time(17, 25)  # 17:25 IST
        },
        'settlement': 'T+2',
        'market_maker_hours': {
            'open': time(8, 30),
            'close': time(18, 0)
        }
    },
    'TADAWUL': {
        'name': 'Saudi Stock Exchange',
        'country': 'Saudi Arabia',
        'currency': 'SAR',
        'timezone': 'Asia/Riyadh',
        'trading_hours': {
            'open': time(10, 0),   # 10:00 AST
            'close': time(15, 0)   # 15:00 AST
        },
        'settlement': 'T+2',
        'market_maker_hours': {
            'open': time(9, 30),
            'close': time(15, 30)
        }
    },
    'EGX': {
        'name': 'Egyptian Exchange',
        'country': 'Egypt',
        'currency': 'EGP',
        'timezone': 'Africa/Cairo',
        'trading_hours': {
            'open': time(10, 0),   # 10:00 EET
            'close': time(14, 30)  # 14:30 EET
        },
        'settlement': 'T+2',
        'market_maker_hours': {
            'open': time(9, 30),
            'close': time(15, 0)
        }
    },
    'JSE': {
        'name': 'Johannesburg Stock Exchange',
        'country': 'South Africa',
        'currency': 'ZAR',
        'timezone': 'Africa/Johannesburg',
        'trading_hours': {
            'open': time(9, 0),    # 09:00 SAST
            'close': time(17, 0)   # 17:00 SAST
        },
        'settlement': 'T+3',
        'market_maker_hours': {
            'open': time(8, 30),
            'close': time(17, 30)
        }
    },
    
    # Additional European Exchanges
    'LSEETF': {
        'name': 'London Stock Exchange ETF Segment',
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
    'GETTEX': {
        'name': 'Gettex Exchange',
        'country': 'Germany',
        'currency': 'EUR',
        'timezone': 'Europe/Berlin',
        'trading_hours': {
            'open': time(8, 0),    # 08:00 CET
            'close': time(22, 0)   # 22:00 CET
        },
        'settlement': 'T+2',
        'continuous_trading': True
    },
    'TRADEGATE': {
        'name': 'Tradegate Exchange',
        'country': 'Germany',
        'currency': 'EUR',
        'timezone': 'Europe/Berlin',
        'trading_hours': {
            'open': time(8, 0),    # 08:00 CET
            'close': time(22, 0)   # 22:00 CET
        },
        'settlement': 'T+2',
        'continuous_trading': True
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
