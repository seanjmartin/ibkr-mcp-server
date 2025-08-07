"""Enhanced test logging utilities for IBKR paper tests

Provides detailed API response logging, performance metrics, and failure analysis.
"""

import time
import json
import asyncio
from typing import Any, Dict, Optional, Callable
from contextlib import asynccontextmanager


class TestLogger:
    """Enhanced logging for paper tests with API response tracking"""
    
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.start_time = None
        self.end_time = None
        self.api_calls = []
        
    def log_start(self):
        """Log test start time"""
        self.start_time = time.time()
        print(f"\n{'='*50}")
        print(f"[TEST] {self.test_name}")
        print(f"[START] {time.strftime('%H:%M:%S', time.localtime(self.start_time))}")
        print(f"{'='*50}")
        
    def log_api_call(self, tool_name: str, arguments: Dict, response_data: Any, duration: float, success: bool = True, error: Optional[str] = None):
        """Log detailed API call information"""
        call_info = {
            'tool_name': tool_name,
            'arguments': arguments,
            'duration_ms': round(duration * 1000, 2),
            'success': success,
            'timestamp': time.strftime('%H:%M:%S', time.localtime()),
            'error': error
        }
        
        print(f"\n[API] {tool_name}")
        print(f"   Arguments: {arguments}")
        print(f"   Duration: {call_info['duration_ms']}ms")
        print(f"   Success: {success}")
        
        if success and response_data:
            # Try to extract meaningful data from response
            if hasattr(response_data, '__iter__') and len(response_data) > 0:
                first_item = response_data[0]
                if hasattr(first_item, 'text'):
                    response_text = first_item.text
                    call_info['response_preview'] = response_text[:200] + "..." if len(response_text) > 200 else response_text
                    print(f"   Response Preview: {call_info['response_preview']}")
                    
                    # Extract key information based on tool type
                    self._extract_key_info(tool_name, response_text)
                else:
                    call_info['response_type'] = str(type(first_item))
                    print(f"   Response Type: {call_info['response_type']}")
            else:
                call_info['response_data'] = str(response_data)
                print(f"   Response Data: {call_info['response_data']}")
                
        elif error:
            print(f"   ERROR: {error}")
            
        self.api_calls.append(call_info)
        
    def _extract_key_info(self, tool_name: str, response_text: str):
        """Extract key information based on tool type"""
        response_lower = response_text.lower()
        
        if 'connection' in tool_name:
            # Extract account info
            if 'du' in response_lower:
                account_start = response_lower.find('du')
                account_info = response_text[account_start:account_start+20].split()[0] if account_start != -1 else "Unknown"
                print(f"   Account Detected: {account_info}")
                
        elif 'account' in tool_name or 'summary' in tool_name:
            # Extract balance info
            for currency in ['usd', 'eur', 'gbp']:
                if currency in response_lower:
                    print(f"   Contains {currency.upper()} balance information")
                    
        elif 'market_data' in tool_name or 'quote' in tool_name:
            # Extract price info
            if '$' in response_text or 'EUR' in response_text or 'JPY' in response_text:
                print(f"   Contains price data")
            if 'bid' in response_lower and 'ask' in response_lower:
                print(f"   Contains bid/ask spread data")
                
        elif 'forex' in tool_name or 'currency' in tool_name:
            # Extract currency info
            for pair in ['eurusd', 'gbpusd', 'usdjpy']:
                if pair in response_lower:
                    print(f"   Contains {pair.upper()} rate data")
                    
    def log_performance_warning(self, duration: float):
        """Log performance warnings for slow operations"""
        if duration > 5.0:
            print(f"   [SLOW] Response: {duration:.2f}s (>5s threshold)")
        elif duration > 2.0:
            print(f"   [MEDIUM] Response: {duration:.2f}s (>2s threshold)")
        else:
            print(f"   [FAST] Response: {duration:.2f}s")
            
    def log_end(self, success: bool = True, error: Optional[str] = None):
        """Log test completion with summary"""
        self.end_time = time.time()
        total_duration = self.end_time - self.start_time if self.start_time else 0
        
        print(f"\n{'='*50}")
        print(f"[COMPLETE] {self.test_name}")
        print(f"[DURATION] {total_duration:.2f}s")
        print(f"[API CALLS] {len(self.api_calls)}")
        
        if self.api_calls:
            avg_duration = sum(call['duration_ms'] for call in self.api_calls) / len(self.api_calls)
            print(f"[AVG] API Response: {avg_duration:.1f}ms")
            
            # Show slowest call
            slowest = max(self.api_calls, key=lambda x: x['duration_ms'])
            print(f"[SLOWEST] {slowest['tool_name']} ({slowest['duration_ms']}ms)")
            
        if success:
            print(f"[STATUS] PASSED")
        else:
            print(f"[STATUS] FAILED")
            if error:
                print(f"[ERROR] {error}")
                
        print(f"{'='*50}\n")
        
        # Performance analysis
        if total_duration > 10:
            print(f"[ALERT] Performance: Test took {total_duration:.2f}s (>10s)")
        elif total_duration > 5:
            print(f"[WARNING] Performance: Test took {total_duration:.2f}s (>5s)")


@asynccontextmanager
async def enhanced_test_logging(test_name: str):
    """Context manager for enhanced test logging"""
    logger = TestLogger(test_name)
    logger.log_start()
    
    try:
        yield logger
        logger.log_end(success=True)
    except Exception as e:
        logger.log_end(success=False, error=str(e))
        raise


async def log_api_call_with_timing(logger: TestLogger, tool_name: str, arguments: Dict, api_call_func: Callable):
    """Execute API call with detailed timing and logging"""
    call_start = time.time()
    
    try:
        result = await api_call_func()
        call_end = time.time()
        duration = call_end - call_start
        
        logger.log_api_call(tool_name, arguments, result, duration, success=True)
        logger.log_performance_warning(duration)
        
        return result
        
    except Exception as e:
        call_end = time.time()
        duration = call_end - call_start
        
        logger.log_api_call(tool_name, arguments, None, duration, success=False, error=str(e))
        raise
