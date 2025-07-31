#!/usr/bin/env python3
"""
Enhanced market data method that supports both stocks and forex
"""

async def get_enhanced_market_data(self, symbols: str) -> List[Dict]:
    """Get real-time market quotes for symbols (stocks and forex)."""
    try:
        if not await self._ensure_connected():
            raise ConnectionError("Not connected to IBKR")
        
        symbol_list = [s.strip().upper() for s in symbols.split(',')]
        contracts = []
        
        # Create contracts based on symbol type
        for symbol in symbol_list:
            if self._is_forex_symbol(symbol):
                # Create forex contract
                from ib_async import Forex
                contract = Forex(symbol)
                contracts.append(contract)
            else:
                # Create stock contract
                from ib_async import Stock
                contract = Stock(symbol, 'SMART', 'USD')
                contracts.append(contract)
        
        # Qualify contracts first
        qualified = await self.ib.qualifyContractsAsync(*contracts)
        
        if not qualified:
            return [{"error": "No valid contracts found"}]
        
        # Get tickers
        tickers = await self.ib.reqTickersAsync(*qualified)
        
        results = []
        for ticker in tickers:
            results.append({
                "symbol": ticker.contract.symbol,
                "last": safe_float(ticker.last),
                "bid": safe_float(ticker.bid),
                "ask": safe_float(ticker.ask),
                "close": safe_float(ticker.close),
                "volume": safe_int(ticker.volume),
                "contract_id": ticker.contract.conId,
                "contract_type": ticker.contract.secType
            })
        
        return results
        
    except Exception as e:
        self.logger.error(f"Enhanced market data request failed: {e}")
        raise RuntimeError(f"IBKR API error: {str(e)}")

def _is_forex_symbol(self, symbol: str) -> bool:
    """Check if symbol is a forex pair."""
    # Common forex pairs
    forex_pairs = {
        'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD',
        'EURGBP', 'EURJPY', 'GBPJPY', 'CHFJPY', 'EURCHF', 'AUDJPY', 'CADJPY',
        'NZDJPY', 'EURAUD', 'EURNZD', 'GBPAUD', 'GBPNZD', 'AUDCAD', 'AUDNZD'
    }
    return symbol in forex_pairs
